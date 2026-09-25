from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import timeouts


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout=timeouts.DEFAULT)

    def open(self, url: str):
        self.driver.get(url)

    def find_element(self, locator: tuple[str, str], timeout: float | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout else self.wait
        return wait.until(EC.visibility_of_element_located(locator))

    def find_elements(self, locator: tuple[str, str], timeout: float | None = None) -> list[WebElement]:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout else self.wait
        return wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator: tuple[str, str], timeout: float | None = None):
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout else self.wait
        element = wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator: tuple[str, str], text: str):
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.find_element(locator).text

    def is_invisible(self, locator: tuple[str, str], timeout: float | None = None) -> bool:
        wait = WebDriverWait(self.driver, timeout=timeout) if timeout else self.wait
        return wait.until(EC.invisibility_of_element_located(locator))
