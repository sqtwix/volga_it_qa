import allure
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By

from config.settings import urls
from pages.base_page import BasePage


class ModalsPage(BasePage):
    # Локаторы из HTML
    SIMPLE_MODAL_BUTTON = (By.ID, "simpleModal")
    FORM_MODAL_BUTTON = (By.ID, "formModal")

    SIMPLE_MODAL_OVERLAY = (By.ID, "pum-1318")
    SIMPLE_MODAL_CONTAINER = (By.ID, "popmake-1318")
    SIMPLE_MODAL_TITLE = (By.ID, "pum_popup_title_1318")
    SIMPLE_MODAL_TEXT = (By.CSS_SELECTOR, "#popmake-1318 .pum-content p")
    SIMPLE_MODAL_CLOSE_BUTTON = (By.CSS_SELECTOR, "#popmake-1318 button.pum-close")

    FORM_MODAL_OVERLAY = (By.ID, "pum-674")
    FORM_MODAL_CONTAINER = (By.ID, "popmake-674")
    FORM_MODAL_TITLE = (By.ID, "pum_popup_title_674")
    FORM_MODAL_CLOSE_BUTTON = (By.CSS_SELECTOR, "#popmake-674 button.pum-close")
    FORM_NAME_INPUT = (By.ID, "g1051-name")
    FORM_EMAIL_INPUT = (By.ID, "g1051-email")
    FORM_MESSAGE_INPUT = (By.ID, "contact-form-comment-g1051-message")
    FORM_SUBMIT_BUTTON = (By.CSS_SELECTOR, "#popmake-674 button[type='submit']")
    FORM_SUCCESS_HEADER = (By.CSS_SELECTOR, "#popmake-674 h4[id^='contact-form-success-header']")
    FORM_NAME_ERROR = (By.ID, "g1051-name-text-error")
    FORM_EMAIL_ERROR = (By.ID, "g1051-email-email-error")

    def open_page(self):
        with allure.step("Открытие страницы модальных окон"):
            self.open(urls.MODAL_URL)

    def clear_input(self, element):
        with allure.step("Очистка поля ввода"):
            input_element = element
            input_element.send_keys(Keys.CONTROL + "a")
            input_element.send_keys(Keys.BACKSPACE)

    # Методы взаимодействия с Simple Modal

    def open_simple_modal(self):
        with allure.step("Нажатие кнопки открытия Simple Modal"):
            self.click(self.SIMPLE_MODAL_BUTTON)
            self.find_element(self.SIMPLE_MODAL_CONTAINER)

    def close_simple_modal(self):
        with allure.step("Закрытие Simple Modal"):
            self.click(self.SIMPLE_MODAL_CLOSE_BUTTON)

    def is_simple_modal_displayed(self):
        with allure.step("Проверка наличия Simple Modal"):
            try:
                element = self.find_element(self.SIMPLE_MODAL_CONTAINER, timeout=2.0)
                return element.is_displayed()
            except (TimeoutException, NoSuchElementException):
                return False

    def is_simple_modal_closed(self):
        with allure.step("Проверка закрытия Simple Modal"):
            try:
                return self.is_invisible(self.SIMPLE_MODAL_CONTAINER, timeout=3.0)
            except TimeoutException:
                return False

    def get_simple_modal_title(self) -> str:
        with allure.step("Получение заголовка Simple Modal"):
            return self.get_text(self.SIMPLE_MODAL_TITLE)

    # Методы взаимодействия с Form Modal

    def open_form_modal(self):
        with allure.step("Открытие Form Modal"):
            self.click(self.FORM_MODAL_BUTTON)
            self.find_element(self.FORM_MODAL_CONTAINER)

    def close_form_modal(self):
        with allure.step("Закрытие Form Modal"):
            self.click(self.FORM_MODAL_CLOSE_BUTTON)

    def close_modal_by_esc(self):
        with allure.step("Закрытие окна клавишей esc"):
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def is_form_modal_displayed(self):
        with allure.step("Проверка наличия Form Modal"):
            try:
                element = self.find_element(self.FORM_MODAL_CONTAINER, timeout=2.0)
                return element.is_displayed()
            except (TimeoutException, NoSuchElementException):
                return False

    def is_form_modal_closed(self):
        with allure.step("Проверка закрытия Form Modal"):
            try:
                return self.is_invisible(self.FORM_MODAL_CONTAINER, timeout=3.0)
            except TimeoutException:
                return False

    def get_form_modal_title(self) -> str:
        with allure.step("Получение заголовка Form Modal"):
            return self.get_text(self.FORM_MODAL_TITLE)

    def type_name(self, name: str):
        with allure.step("Заполнение формы имени"):
            input_element = self.find_element(self.FORM_NAME_INPUT)
            self.clear_input(input_element)
            input_element.send_keys(name)
            input_element.send_keys(Keys.TAB)

    def type_email(self, email: str):
        with allure.step("Заполнение формы почты"):
            input_element = self.find_element(self.FORM_EMAIL_INPUT)
            self.clear_input(input_element)
            input_element.send_keys(email)
            input_element.send_keys(Keys.TAB)

    def type_message(self, message: str):
        with allure.step("Заполнение формы сообщения"):
            input_element = self.find_element(self.FORM_MESSAGE_INPUT)
            self.clear_input(input_element)
            input_element.send_keys(message)
            input_element.send_keys(Keys.TAB)

    def submit_form(self):
        with allure.step("Нажатие кнопки Submit внутри модального окна"):
            self.click(self.FORM_SUBMIT_BUTTON)

    def get_form_success_message(self, timeout: float | None = None) -> str:
        with allure.step("Получение сообщения об успешной отправке формы"):
            try:
                return self.find_element(self.FORM_SUCCESS_HEADER, timeout=timeout).text
            except (TimeoutException, NoSuchElementException):
                return ""

    def is_name_error_displayed(self) -> bool:
        with allure.step("Проверка ошибки валидации поля Name"):
            try:
                element = self.find_element(self.FORM_NAME_ERROR, timeout=1.5)
                return "has-errors" in (element.get_attribute("class") or "") or bool(element.text.strip())
            except (TimeoutException, NoSuchElementException):
                return False

    def is_email_error_displayed(self) -> bool:
        with allure.step("Проверка ошибки валидации поля Email"):
            try:
                element = self.find_element(self.FORM_EMAIL_ERROR, timeout=1.5)
                return "has-errors" in (element.get_attribute("class") or "") or bool(element.text.strip())
            except (TimeoutException, NoSuchElementException):
                return False
