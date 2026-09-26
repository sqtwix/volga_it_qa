import allure
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from config.settings import urls
from pages.base_page import BasePage


class CalendarPage(BasePage):
    # Локаторы из HTML
    DATE_INPUT = (By.ID, "g1065-1-selectorenteradate")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit'].pushbutton-wide")
    SUCCESS_HEADER = (By.CSS_SELECTOR, "h4[id^='contact-form-success-header']")
    ERROR_CONTAINER = (By.ID, "g1065-1-selectorenteradate-text-error")
    ERROR_MESSAGE = (By.ID, "g1065-1-selectorenteradate-text-error-message")
    DATEPICKER_NEXT_MONTH = (By.CSS_SELECTOR, "#ui-datepicker-div .ui-datepicker-next")
    DATEPICKER_PREV_MONTH = (By.CSS_SELECTOR, "#ui-datepicker-div .ui-datepicker-prev")

    # Методы взаимодействия с элементами ввода данных

    def open_page(self):
        with allure.step("Открытие страницы календаря"):
            self.open(urls.CALENDAR)

    def clear_date_input(self, element: WebElement | None = None):
        with allure.step("Очистка поля ввода даты"):
            input_element = element or self.find_element(self.DATE_INPUT)
            input_element.send_keys(Keys.CONTROL + "a")
            input_element.send_keys(Keys.BACKSPACE)

    def type_date(self, date: str):
        with allure.step(f"Ввод даты с клавиатуры: {date}"):
            input_element = self.find_element(self.DATE_INPUT)
            self.clear_date_input(input_element)
            input_element.send_keys(date)
            input_element.send_keys(Keys.TAB)

    def get_input_value(self) -> str:
        with allure.step("Получение текущего значения из поля ввода даты"):
            return self.find_element(self.DATE_INPUT).get_attribute("value") or ""

    def open_picker(self):
        with allure.step("Открытие датапикера"):
            self.click(self.DATE_INPUT)

    def select_day_in_picker(self, day: int):
        with allure.step(f"Выбор дня {day} в активном календаре"):
            day_locator = (
                By.XPATH,
                f"//div[@id='ui-datepicker-div']//td[not(contains(@class, 'ui-datepicker-other-month'))]//a[text()='{day}']"
            )
            self.click(day_locator)

    def click_next_month_in_picker(self):
        with allure.step("Переключение календаря на следующий месяц"):
            self.click(self.DATEPICKER_NEXT_MONTH)

    def click_prev_month_in_picker(self):
        with allure.step("Переключение календаря на предыдущий месяц"):
            self.click(self.DATEPICKER_PREV_MONTH)

    def submit(self):
        with allure.step("Нажатие на кнопку Submit"):
            self.click(self.SUBMIT_BUTTON)

    # Методы взаимодействия с элементами получения результата

    def get_success_message(self) -> str:
        with allure.step("Получение сообщения об успешной отправке формы"):
            return self.get_text(self.SUCCESS_HEADER)

    def is_error_displayed(self) -> bool:
        with allure.step("Проверка наличия сообщения об ошибке"):
            try:
                error_element = self.find_element(self.ERROR_CONTAINER, timeout=3.0)
                return "has-errors" in (error_element.get_attribute("class") or "") or bool(self.get_error_message())
            except (TimeoutException, NoSuchElementException):
                return False

    def get_error_message(self) -> str:
        with allure.step("Получение текста ошибки валидации"):
            try:
                return self.get_text(self.ERROR_MESSAGE)
            except (TimeoutException, NoSuchElementException):
                return ""
