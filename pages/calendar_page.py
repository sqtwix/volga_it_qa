import allure
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from config.settings import urls
from pages.base_page import BasePage


class CalendarPage(BasePage):
    """Ввод даты, навигация по календарю и чтение результата отправки формы."""

    # Локаторы из HTML
    DATE_INPUT = (By.CSS_SELECTOR, "input[name*='date'], #g1065-1-selectorenteradate")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit'].pushbutton-wide")
    SUCCESS_HEADER = (By.CSS_SELECTOR, "h4[id^='contact-form-success-header']")
    SUBMITTED_DATE = (
        By.XPATH,
        "//div[contains(concat(' ', normalize-space(@class), ' '), "
        "' jetpack_forms_contact-form-success-summary ')]"
        "[.//div[@class='field-name' and normalize-space()='Select or enter a date:']]"
        "//div[@class='field-value']",
    )
    ERROR_CONTAINER = (By.ID, "g1065-1-selectorenteradate-text-error")
    ERROR_MESSAGE = (By.ID, "g1065-1-selectorenteradate-text-error-message")
    PICKER_CONTAINER = (By.CSS_SELECTOR, ".dp-cal")
    PICKER_MONTH_LABEL = (By.CSS_SELECTOR, ".dp-cal-month")
    PICKER_YEAR_LABEL = (By.CSS_SELECTOR, ".dp-cal-year")
    NEXT_MONTH_BUTTON = (By.CSS_SELECTOR, "button.dp-next")
    PREV_MONTH_BUTTON = (By.CSS_SELECTOR, "button.dp-prev")

    # Первичный признак загрузки страницы — видимое поле даты.
    PAGE_READY_LOCATOR = DATE_INPUT

    MONTH_NAMES = (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    )

    # Методы взаимодействия с элементами ввода данных

    def open_page(self):
        with allure.step("Открытие страницы календаря"):
            self.open(urls.CALENDAR_URL)

    def clear_date_input(self, element: WebElement | None = None):
        with allure.step("Очистка поля ввода даты"):
            input_element = element or self.find_element(self.DATE_INPUT)
            self.clear_input(input_element)

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
        with allure.step("Открытие дата-пикера кликом по полю ввода"):
            self.click(self.DATE_INPUT)
            self.get_picker_period()

    def _visible_picker(self) -> WebElement | None:
        for picker in self.driver.find_elements(*self.PICKER_CONTAINER):
            if picker.is_displayed():
                return picker
        return None

    def _read_picker_period(self) -> tuple[int, int] | None:
        """Читает год и месяц без вложенных ожиданий; перерисовка повторяется внешним wait."""
        try:
            picker = self._visible_picker()
            if picker is None:
                return None
            month = picker.find_element(*self.PICKER_MONTH_LABEL).text.strip()
            year = picker.find_element(*self.PICKER_YEAR_LABEL).text.strip()
            if month not in self.MONTH_NAMES or not year.isdecimal():
                return None
            return int(year), self.MONTH_NAMES.index(month) + 1
        except (NoSuchElementException, StaleElementReferenceException):
            return None

    def get_picker_period(self) -> tuple[int, int]:
        """Ожидает непустой заголовок и возвращает (год, месяц)."""
        return self.wait.until(
            lambda _: self._read_picker_period(),
            message="В видимом календаре не удалось прочитать месяц и год",
        )

    def _click_in_picker(self, locator: tuple[str, str]) -> None:
        """Ожидает доступный элемент внутри видимого календаря и выполняет обычный клик."""
        def find_clickable(_):
            try:
                picker = self._visible_picker()
                if picker is not None:
                    for element in picker.find_elements(*locator):
                        if element.is_displayed() and element.is_enabled():
                            return element
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            return False

        self.wait.until(find_clickable, message=f"В календаре недоступен элемент {locator}").click()

    def _change_picker_month(self, offset: int, locator: tuple[str, str]) -> None:
        """Сдвигает отображаемый период и ожидает точные месяц и год, включая смену года."""
        year, month = self.get_picker_period()
        expected_year, month_index = divmod(year * 12 + month - 1 + offset, 12)
        expected_period = expected_year, month_index + 1
        self._click_in_picker(locator)
        self.wait.until(
            lambda _: self._read_picker_period() == expected_period,
            message=f"Календарь не переключился на {expected_year:04d}-{month_index + 1:02d}",
        )

    def click_next_month_in_picker(self):
        with allure.step("Переключение на следующий месяц в календаре"):
            self._change_picker_month(1, self.NEXT_MONTH_BUTTON)

    def click_prev_month_in_picker(self):
        with allure.step("Переключение на предыдущий месяц в календаре"):
            self._change_picker_month(-1, self.PREV_MONTH_BUTTON)

    def select_day_in_picker(self, day: int):
        """Выбирает доступный день 1–31 текущего месяца, исключая соседние месяцы."""
        if not 1 <= day <= 31:
            raise ValueError("День должен быть в диапазоне от 1 до 31")
        with allure.step(f"Выбор дня {day} в активном месяце календаря"):
            day_locator = (
                By.XPATH,
                ".//button[contains(concat(' ', normalize-space(@class), ' '), ' dp-day ') "
                "and not(contains(concat(' ', normalize-space(@class), ' '), ' dp-edge-day ')) "
                "and not(contains(concat(' ', normalize-space(@class), ' '), ' dp-day-disabled ')) "
                f"and normalize-space()='{day}']"
            )
            self._click_in_picker(day_locator)

    def submit(self):
        with allure.step("Нажатие на кнопку Submit"):
            self.click(self.SUBMIT_BUTTON)

    # Методы взаимодействия с элементами получения результата

    def get_submitted_date(self) -> str:
        """Ожидает непустое значение даты в сводке отправки именно поля даты."""
        with allure.step("Получение отправленной даты из сводки формы"):
            def read_date(driver):
                try:
                    element = driver.find_element(*self.SUBMITTED_DATE)
                    return element.text.strip() if element.is_displayed() else False
                except (NoSuchElementException, StaleElementReferenceException):
                    return False

            return self.wait.until(read_date, message="В сводке отправки не появилась дата")

    def get_success_message(self, timeout: float = 10.0) -> str:
        with allure.step("Получение сообщения об успешной отправке формы"):
            try:
                return self.find_element(self.SUCCESS_HEADER, timeout=timeout).text
            except (TimeoutException, NoSuchElementException):
                return ""

    def get_error_message(self, timeout: float = 1.0) -> str:
        with allure.step("Получение текста ошибки валидации"):
            try:
                element = self.find_element(self.ERROR_MESSAGE, timeout=timeout)
                return element.text
            except (TimeoutException, NoSuchElementException):
                return ""

    def is_error_displayed(self) -> bool:
        with allure.step("Проверка наличия сообщения об ошибке"):
            try:
                error_element = self.find_element(self.ERROR_CONTAINER, timeout=1.5)
                has_class = "has-errors" in (error_element.get_attribute("class") or "")
                return has_class or bool(self.get_error_message(timeout=0.5))
            except (TimeoutException, NoSuchElementException):
                return False
