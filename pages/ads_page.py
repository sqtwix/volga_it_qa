import allure
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By

from config.settings import urls
from pages.base_page import BasePage


class AdsPage(BasePage):
    # Локаторы страницы
    PAGE_TITLE = (By.CSS_SELECTOR, "h1")
    PAGE_TEXT = (By.CSS_SELECTOR, ".entry-content p")

    # Локаторы рекламного модального окна
    AD_OVERLAY = (By.ID, "pum-1272")
    AD_CONTAINER = (By.ID, "popmake-1272")
    AD_TITLE = (By.ID, "pum_popup_title_1272")
    AD_CONTENT = (By.CSS_SELECTOR, "#popmake-1272 .pum-content p")
    AD_CLOSE_BUTTON = (By.CSS_SELECTOR, "#popmake-1272 button.pum-close")

    def open_page(self):
        with allure.step("Открытие страницы календаря"):
            self.open(getattr(urls, "ADS_URL", "https://practice-automation.com/ads/"))

    def wait_for_ad_to_appear(self, timeout: float = 6.0):
        """Ожидание автоматического появления рекламы (таймер сайта: ~4.5 сек)."""
        with allure.step(f"Ожидание появления рекламного окна (таймаут: {timeout}с)"):
            try:
                element = self.find_element(self.AD_CONTAINER, timeout=timeout)
                return element.is_displayed()
            except (TimeoutException, NoSuchElementException):
                return False

    def is_ad_displayed(self) -> bool:
        """Мгновенная проверка видимости окна без долгого ожидания."""
        with allure.step("Мгновенная проверка видимости рекламы"):
            try:
                element = self.find_element(self.AD_CONTAINER, timeout=0.5)
                return element.is_displayed()
            except (TimeoutException, NoSuchElementException):
                return False

    def get_ad_title(self, timeout: float = 2.0) -> str:
        with allure.step("Получение заголовка рекламы"):
            try:
                return self.find_element(self.AD_TITLE, timeout=timeout).text.strip()
            except (TimeoutException, NoSuchElementException):
                return ""

    def get_ad_text(self, timeout: float = 2.0) -> str:
        with allure.step("Получения текста рекламы"):
            try:
                return self.find_element(self.AD_CONTENT, timeout=timeout).text.strip()
            except (TimeoutException, NoSuchElementException):
                return ""

    def close_ad(self):
        with allure.step("Закрытие окна рекламы"):
            self.click(self.AD_CLOSE_BUTTON)

    def is_ad_closed(self, timeout: float = 3.0) -> bool:
        with allure.step("Проверка закрытия окна"):
            try:
                return self.is_invisible(self.AD_OVERLAY, timeout=timeout)
            except TimeoutException:
                return False

    def close_by_esc(self):
        with allure.step("Попытка закрыть через клавишу ecs"):
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def click_outside_ad(self):
        with allure.step("Попытка закрытия кликом по оверлею (мимо рекламного окна)"):
            self.click(self.AD_OVERLAY)

    def is_page_header_interactive(self) -> bool:
        with allure.step("Проверка доступности элементов основной страницы после закрытия рекламы"):
            try:
                header = self.find_element(self.PAGE_TITLE, timeout=2.0)
                return header.is_displayed()
            except (TimeoutException, NoSuchElementException):
                return False
