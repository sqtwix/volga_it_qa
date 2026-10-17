import allure
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import timeouts


class BasePage:
    """Общие ожидания и действия Selenium, используемые классами страниц."""

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
        Открывает страницу и ожидает видимость её ключевого элемента.
        При таймауте навигации завершает шаг ошибкой, сохраняя исходную причину.
        timeout задаёт ожидание элемента; таймаут навигации настроен у драйвера.
        """
        check_locator = ready_locator or self.PAGE_READY_LOCATOR
        element_timeout = timeouts.DEFAULT if timeout is None else timeout
        wait = WebDriverWait(self.driver, timeout=element_timeout)
        with allure.step(f"Переход по URL: {url}"):
            try:
                self.driver.get(url)
            except TimeoutException as ex:
                raise TimeoutException(
                    f"Навигация по URL '{url}' завершилась таймаутом. "
                    "Проверка готовности страницы не выполнялась."
                ) from ex
            if check_locator:
                with allure.step(f"Ожидание готовности страницы по элементу: {check_locator}"):
                    try:
                        wait.until(EC.visibility_of_element_located(check_locator))
                    except TimeoutException as exc:
                        raise TimeoutException(
                            f"Страница '{url}' не готова к работе: "
                            f"обязательный элемент {check_locator} не стал видимым за {element_timeout}с."
                        ) from exc

    def find_element(self, locator: tuple[str, str], timeout: float | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        return wait.until(EC.visibility_of_element_located(locator))

    def find_elements(self, locator: tuple[str, str], timeout: float | None = None) -> list[WebElement]:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        return wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator: tuple[str, str], timeout: float | None = None):
        """Выполняет обычный клик; ошибки взаимодействия передаются вызывающему коду."""
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        wait.until(EC.element_to_be_clickable(locator)).click()

    def click_via_javascript(self, locator: tuple[str, str]) -> None:
        """Явно выполняет программный клик по видимому элементу."""
        with allure.step(f"Программный JavaScript-клик по элементу: {locator}"):
            element = self.find_element(locator)
            self.driver.execute_script("arguments[0].click();", element)

    def clear_input(self, element: WebElement) -> None:
        """Очищает поле с клавиатуры с генерацией событий ввода."""
        with allure.step("Очистка поля ввода"):
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.BACKSPACE)

    def type_text(self, locator: tuple[str, str], text: str):
        element = self.find_element(locator)
        self.clear_input(element)
        element.send_keys(text)

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.find_element(locator).text

    def is_invisible(self, locator: tuple[str, str], timeout: float | None = None) -> bool:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout is not None else self.wait
        return wait.until(EC.invisibility_of_element_located(locator))

    def remains_visible(self, locator: tuple[str, str], timeout: float = 1.5) -> bool:
        """Возвращает True, если опрос каждые 0,1 секунды не обнаружил исчезновения элемента."""
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.1).until_not(
                EC.visibility_of_element_located(locator)
            )
            return False
        except TimeoutException:
            return True

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
