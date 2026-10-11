import json

import allure
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config.settings import urls
from pages.base_page import BasePage


class AdsPage(BasePage):
    # Локаторы страницы
    PAGE_TITLE = (By.CSS_SELECTOR, "h1")
    PAGE_TEXT = (By.CSS_SELECTOR, ".entry-content p")

    # Элемент основной страницы, гарантированно видимый ДО появления рекламы
    PAGE_READY_LOCATOR = PAGE_TITLE

    # Локаторы рекламного модального окна
    AD_OVERLAY = (By.ID, "pum-1272")
    AD_CONTAINER = (By.ID, "popmake-1272")
    AD_TITLE = (By.ID, "pum_popup_title_1272")
    AD_CONTENT = (By.CSS_SELECTOR, "#popmake-1272 .pum-content p")
    AD_CLOSE_BUTTON = (By.CSS_SELECTOR, "#popmake-1272 button.pum-close")
    PAGE_LINK = (By.CSS_SELECTOR, ".entry-content a[href*='youtube.com']")
    BREADCRUMBS = (By.CSS_SELECTOR, ".breadcrumbs")
    FOOTER_LINK = (By.CSS_SELECTOR, "footer a[href*='automatenow']")
    ENTRY_CONTENT = (By.CSS_SELECTOR, ".entry-content")

    def open_page(self):
        with allure.step("Открытие страницы с рекламой"):
            self.open(urls.ADS_URL)

    def wait_for_ad_to_appear(self, timeout: float = 8.0):
        """Ожидает появления рекламного окна. При таймауте выбрасывает TimeoutException."""
        with allure.step(f"Ожидание появления рекламного окна (таймаут: {timeout}с)"):
            return self.find_element(self.AD_CONTAINER, timeout=timeout)

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
        with allure.step("Клик по левому краю оверлея"):
            overlay = self.find_element(self.AD_OVERLAY)
            # смещение влево, чтобы клик был не по центру
            offset_x = -(overlay.size["width"] // 2) + 20

            ActionChains(self.driver) \
                .move_to_element_with_offset(overlay, offset_x, 0) \
                .click() \
                .perform()

    def is_page_link_clickable(self, timeout: float = 3.0) -> bool:
        with allure.step("Проверка кликабельности ссылки статьи"):
            return self.is_clickable(self.PAGE_LINK, timeout=timeout)

    def get_close_button_attribute(self, attr_name: str) -> str:
        with allure.step(f"Получение атрибута '{attr_name}' у кнопки закрытия рекламы"):
            try:
                return self.find_element(self.AD_CLOSE_BUTTON).get_attribute(attr_name) or ""
            except (TimeoutException, NoSuchElementException):
                return ""

    def close_ad_via_keyboard_enter(self):
        with allure.step("Закрытие рекламы нажатием Enter на сфокусированной кнопке закрытия"):
            close_btn = self.find_element(self.AD_CLOSE_BUTTON)
            close_btn.send_keys(Keys.ENTER)

    def click_ad_content_body(self):
        with allure.step("Клик по внутреннему содержимому рекламы (тексту/контейнеру)"):
            self.click(self.AD_CONTENT)

    def try_click_page_link(self):
        """Пытается кликнуть по ссылке на странице (вызовет ошибку перехвата, если оверлей активен)."""
        with allure.step("Попытка клика по ссылке на основной странице"):
            self.click(self.PAGE_LINK)

    def get_page_tutorial_link_data(self) -> dict[str, str]:
        with allure.step("Получение параметров ссылки на видеоурок"):
            link_el = self.find_element(self.PAGE_LINK)
            return {
                "href": link_el.get_attribute("href") or "",
                "target": link_el.get_attribute("target") or "",
                "text": link_el.text.strip()
            }

    def get_ad_auto_open_delay(self) -> int:
        with allure.step("Получение времени задержки таймера авто-открытия из data-popmake"):
            overlay = self.find_element(self.AD_OVERLAY)
            popmake_data = overlay.get_attribute("data-popmake") or "{}"
            try:
                config = json.loads(popmake_data)
                triggers = config.get("triggers", [])
                for trigger in triggers:
                    if trigger.get("type") == "auto_open":
                        return int(trigger.get("settings", {}).get("delay", 0))
            except (json.JSONDecodeError, ValueError):
                pass
            return 0

    def get_breadcrumbs_text(self) -> str:
        with allure.step("Получение текста хлебных крошек"):
            return self.find_element(self.BREADCRUMBS).text.strip()

    def get_page_content_text(self) -> str:
        with allure.step("Получение полного текста статьи со страницы"):
            return self.find_element(self.ENTRY_CONTENT).text.strip()

    def has_ad_dismiss_cookies(self) -> bool:
        with allure.step("Проверка наличия кук, блокирующих показ рекламы"):
            cookies = self.driver.get_cookies()
            return any("pum" in c.get("name", "").lower() for c in cookies)

    def try_click_footer_link(self):
        with allure.step("Попытка клика по ссылке в футере"):
            self.click(self.FOOTER_LINK)

    def open_tutorial_link(self) -> str:
        """Кликает по ссылке, переключается на открывшуюся вкладку и возвращает исходный window_handle."""
        with allure.step("Клик по ссылке на видеоурок и переход на новую вкладку"):
            original_window = self.driver.current_window_handle
            self.click(self.PAGE_LINK)
            self.switch_to_new_window(original_window)
            return original_window

    def is_tutorial_page_opened(self, timeout: float = 5.0) -> bool:
        """Проверяет, что текущий URL содержит youtube.com."""
        with allure.step("Проверка открытия страницы YouTube"):
            try:
                return bool(
                    WebDriverWait(self.driver, timeout).until(
                        EC.url_contains("youtube.com")
                    )
                )
            except TimeoutException:
                return False
