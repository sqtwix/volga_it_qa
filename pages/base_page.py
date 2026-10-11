import allure
from selenium.common import TimeoutException, WebDriverException, ElementNotInteractableException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import timeouts


class BasePage:
    PAGE_READY_LOCATOR: tuple[str, str] | None = None

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout=timeouts.DEFAULT)

    def open(
            self,
            url: str,
            ready_locator: tuple[str, str] | None = None,
            timeout: float | None = None,
    ):
        """
        Открывает страницу по URL.
        При таймауте отсекает зависшие внешние трекеры через window.stop(),
        но строго валидирует появление ключевого элемента страницы.
        Если элемент не появился или не задан — выбрасывает TimeoutException.
        """
        check_locator = ready_locator or self.PAGE_READY_LOCATOR
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        with allure.step(f"Переход по URL: {url}"):
            nav_timed_out = False
            try:
                self.driver.get(url)
            except TimeoutException as ex:
                nav_timed_out = True
                try:
                    self.driver.execute_script("window.stop();")
                except WebDriverException:
                    pass
                if not check_locator:
                    raise TimeoutException(
                        f"Навигация по URL '{url}' завершилась таймаутом. "
                        f"Локатор готовности страницы не был передан."
                    ) from ex
            if check_locator:
                with allure.step(f"Ожидание готовности страницы по элементу: {check_locator}"):
                    try:
                        wait.until(EC.visibility_of_element_located(check_locator))
                    except TimeoutException as exc:
                        status = "после window.stop()" if nav_timed_out else "штатная загрузка"
                        raise TimeoutException(
                            f"Страница '{url}' не готова к работе ({status}): "
                            f"обязательный элемент {check_locator} не появился в DOM за {wait._timeout}с."
                        ) from exc

    def find_element(self, locator: tuple[str, str], timeout: float | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        return wait.until(EC.visibility_of_element_located(locator))

    def find_elements(self, locator: tuple[str, str], timeout: float | None = None) -> list[WebElement]:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        return wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator: tuple[str, str], timeout: float | None = None):
        """Кликает по элементу со скроллом во вьюпорт при необходимости."""
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        element = wait.until(EC.element_to_be_clickable(locator))
        try:
            element.click()
        except ElementNotInteractableException:
            # Скроллим элемент в центр (решает проблему скролла внутри модальных окон)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element
            )
            element.click()

    def type_text(self, locator: tuple[str, str], text: str):
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.find_element(locator).text

    def is_invisible(self, locator: tuple[str, str], timeout: float | None = None) -> bool:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        return wait.until(EC.invisibility_of_element_located(locator))

    def is_clickable(self, locator: tuple[str, str], timeout: float | None = None) -> bool:
        """Возвращает True, если элемент отображается, включен и доступен для клика."""
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        try:
            return bool(wait.until(EC.element_to_be_clickable(locator)))
        except TimeoutException:
            return False

    def switch_to_new_window(self, original_window: str, timeout: float = 5.0):
        """Ожидает открытия новой вкладки и переключает фокус на неё."""
        WebDriverWait(self.driver, timeout).until(EC.number_of_windows_to_be(2))
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break

    def close_current_window_and_back(self, original_window: str):
        """Закрывает текущую вкладку и возвращает фокус на исходную."""
        self.driver.close()
        self.driver.switch_to.window(original_window)
