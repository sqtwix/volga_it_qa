import allure
from selenium.common import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import urls
from pages.base_page import BasePage


class ModalsPage(BasePage):
    """Действия с Simple Modal, Form Modal и проверка их состояния."""

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
    FORM_MODAL_CLOSE_BUTTON = (By.CSS_SELECTOR, "#popmake-674 button.pum-close")
    FORM_NAME_INPUT = (By.ID, "g1051-name")
    FORM_EMAIL_INPUT = (By.ID, "g1051-email")
    FORM_MESSAGE_INPUT = (By.ID, "contact-form-comment-g1051-message")
    FORM_SUBMIT_BUTTON = (By.CSS_SELECTOR, "#popmake-674 button[type='submit']")
    FORM_NAME_ERROR = (By.ID, "g1051-name-text-error")
    FORM_EMAIL_ERROR = (By.ID, "g1051-email-email-error")
    FORM_SUCCESS_SUMMARY = (By.CSS_SELECTOR, "#popmake-674 .jetpack_forms_contact-form-success-summary")

    FORM_SUCCESS_CONTAINER = (By.CSS_SELECTOR, "#popmake-674 div[id^='contact-form-success']")
    FORM_BACK_LINK = (By.CSS_SELECTOR,
                      "#popmake-674 a.go-back-message, #popmake-674 a[data-wp-on--click='actions.goBack']")

    # Первичный признак загрузки страницы — видимая кнопка Simple Modal.
    PAGE_READY_LOCATOR = SIMPLE_MODAL_BUTTON

    def open_page(self):
        with allure.step("Открытие страницы модальных окон"):
            self.open(urls.MODAL_URL)

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

    def is_simple_modal_closed(self) -> bool:
        with allure.step("Проверка полного закрытия Simple Modal (включая оверлей)"):
            try:
                return self.is_invisible(self.SIMPLE_MODAL_OVERLAY, timeout=3.0)
            except TimeoutException:
                return False

    def get_simple_modal_title(self) -> str:
        with allure.step("Получение заголовка Simple Modal"):
            return self.get_text(self.SIMPLE_MODAL_TITLE)

    def get_simple_modal_text(self) -> str:
        with allure.step("Получение основного текста из Simple Modal"):
            try:
                raw_text = self.find_element(self.SIMPLE_MODAL_TEXT, timeout=3.0).text.strip()
                return raw_text.replace("’", "'")
            except (TimeoutException, NoSuchElementException):
                return ""

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
        """Вводит сообщение порциями, проверяя значение после ввода и потери фокуса."""
        with allure.step("Заполнение формы сообщения"):
            input_element = self.find_element(self.FORM_MESSAGE_INPUT)
            self.clear_input(input_element)

            def wait_for_value(expected: str):
                try:
                    self.wait.until(
                        lambda driver: driver.find_element(
                            *self.FORM_MESSAGE_INPUT,
                        ).get_property("value") == expected,
                        message="Поле Message не содержит полный введённый текст",
                    )
                except TimeoutException as exc:
                    actual = self.driver.find_element(*self.FORM_MESSAGE_INPUT).get_property("value")
                    details = f"Ожидалось ({len(expected)}): {expected!r}\nПолучено: {actual!r}"
                    raise TimeoutException(f"Поле Message не сохранило введённый текст. {details}") from exc

            wait_for_value("")
            # Между порциями проверяем значение управляемого JavaScript поля.
            for offset in range(0, len(message), 20):
                input_element.send_keys(message[offset:offset + 20])
                wait_for_value(message[:offset + 20])
            input_element.send_keys(Keys.TAB)
            wait_for_value(message)

    def _prepare_submit_button(self) -> WebElement:
        """Прокручивает подложку, не меняя позицию Popup Maker, и ждёт свободную точку клика."""
        self.wait.until(EC.element_to_be_clickable(self.FORM_SUBMIT_BUTTON))
        previous_rect = None

        def ready_to_click(_):
            nonlocal previous_rect
            try:
                current = self.driver.find_element(*self.FORM_SUBMIT_BUTTON)
                if not current.is_displayed() or not current.is_enabled():
                    previous_rect = None
                    return False
                rect = self.driver.execute_script(
                    """
                    const el = arguments[0];
                    const overlay = arguments[1];
                    let r = el.getBoundingClientRect();
                    if (r.top < 0 || r.bottom > window.innerHeight) {
                        overlay.scrollTop += r.top + r.height / 2 - window.innerHeight / 2;
                        r = el.getBoundingClientRect();
                    }
                    const x = r.left + r.width / 2;
                    const y = r.top + r.height / 2;
                    if (r.width <= 0 || r.height <= 0 || x < 0 || y < 0 ||
                        x >= window.innerWidth || y >= window.innerHeight) return null;
                    const top = document.elementFromPoint(x, y);
                    if (!top || !(top === el || el.contains(top))) return null;
                    return [r.left, r.top, r.width, r.height];
                    """,
                    current,
                    self.driver.find_element(*self.FORM_MODAL_OVERLAY),
                )
                stable = rect is not None and rect == previous_rect
                previous_rect = rect
                return current if stable else False
            except (NoSuchElementException, StaleElementReferenceException):
                previous_rect = None
                return False

        return self.wait.until(
            ready_to_click,
            message="Кнопка Submit не заняла стабильное положение или перекрыта другим элементом",
        )

    def submit_form(self):
        """Нажимает Submit; только в Firefox допускает явный JS-обход ошибки взаимодействия.

        Применение обхода записывается отдельным шагом Allure. Ошибки других
        браузеров и исключения, отличные от ElementNotInteractableException,
        передаются вызывающему тесту.
        """
        with allure.step("Нажатие кнопки Submit внутри модального окна"):
            button = self._prepare_submit_button()
            try:
                button.click()
            except ElementNotInteractableException:
                if self.driver.capabilities.get("browserName", "").lower() != "firefox":
                    raise
                with allure.step("Обход ошибки прокрутки Submit в Firefox: JavaScript-клик"):
                    self.click_via_javascript(self.FORM_SUBMIT_BUTTON)

    def is_simple_modal_still_open(self, timeout: float = 1.5) -> bool:
        with allure.step(f"Simple Modal остаётся видимым в течение {timeout}с"):
            return self.remains_visible(self.SIMPLE_MODAL_CONTAINER, timeout)

    def is_form_modal_still_open(self, timeout: float = 1.5) -> bool:
        with allure.step(f"Form Modal остаётся видимым в течение {timeout}с"):
            return self.remains_visible(self.FORM_MODAL_CONTAINER, timeout)

    def get_form_submission_details(
        self, timeout: float = 30.0, expected_values: tuple[str, ...] = (),
    ) -> str:
        """Ожидает подтверждение и полные ожидаемые значения в DOM сводки.

        textContent читает текст без визуального обрезания длинных строк.
        Ожидаемые значения не сокращаются: неполная сводка завершится таймаутом.
        """
        def read_details(_):
            """Читает уже отрисованную сводку; перерисовку повторяет внешний wait."""
            try:
                summaries = self.driver.find_elements(*self.FORM_SUCCESS_SUMMARY)
                summary_text = "\n".join(
                    (row.get_property("textContent") or "").strip() for row in summaries
                ).strip()
                if not summary_text:
                    return False
                if not all(value in summary_text for value in expected_values if value):
                    return False
                container = self.driver.find_element(*self.FORM_SUCCESS_CONTAINER)
                if container.is_displayed():
                    details = (container.get_property("textContent") or "").strip()
                    if "Thank you for your response" in details:
                        return details
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            return False

        with allure.step("Получение полного текста сводки об отправке формы"):
            return WebDriverWait(self.driver, timeout).until(
                read_details,
                message="После отправки формы не появилась полная сводка с ожидаемыми данными",
            )

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

    def click_back_to_form(self):
        with allure.step("Нажать на ссылку '← Back' для возврата к полям формы"):
            self.click(self.FORM_BACK_LINK)

    def click_outside_modal(self):
        """Кликает по подложке в 20 пикселях от её левого края по центру высоты."""
        with allure.step("Кликнуть по фоновому оверлею за пределами окна"):
            overlay = self.find_element(self.FORM_MODAL_OVERLAY)
            # ActionChains отсчитывает смещение от центра элемента.
            offset_x = -(overlay.size["width"] // 2) + 20

            (
                ActionChains(self.driver)
                .move_to_element_with_offset(overlay, offset_x, 0)
                .click()
                .perform()
            )

    def is_form_inputs_visible(self) -> bool:
        with allure.step("Проверить отображение полей ввода формы"):
            try:
                return self.find_element(self.FORM_NAME_INPUT, timeout=2.0).is_displayed()
            except (TimeoutException, NoSuchElementException):
                return False

    def is_form_modal_closed(self) -> bool:
        with allure.step("Проверка закрытия Form Modal"):
            try:
                return self.is_invisible(self.FORM_MODAL_OVERLAY, timeout=3.0)
            except TimeoutException:
                return False
