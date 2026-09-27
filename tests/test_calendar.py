import allure
import pytest

from pages.calendar_page import CalendarPage


@pytest.fixture
def calendar_page(driver):
    page = CalendarPage(driver)
    page.open_page()
    return page

THANK_YOU_LABEL = "Thank you"

@allure.feature("Календари")
@allure.suite("Тестирование страницы Calendars")
class TestCalendarsPositive:
    """Набор позитивных тестов на страницу календаря"""

    @allure.title("Выбор дня текущего месяца в датапикере")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_select_day_in_current_month(self, calendar_page):
        calendar_page.open_picker()
        calendar_page.select_day_in_picker(day=15)

        actual_value = calendar_page.get_input_value()
        assert actual_value.endswith("-15"), (
            f"Ожидался выбранный день '15' в конце даты, получено: '{actual_value}'"
        )

    @allure.title("Переключение на следующий месяц и выбор даты")
    @allure.severity(allure.severity_level.NORMAL)
    def test_select_day_in_next_month(self, calendar_page):
        calendar_page.open_picker()
        calendar_page.click_next_month_in_picker()
        calendar_page.select_day_in_picker(day=18)

        actual_value = calendar_page.get_input_value()
        assert actual_value.endswith("-18"), (
            f"Ожидался выбранный день '18' в конце даты, получено: '{actual_value}'"
        )

    @allure.title("Переключение на предыдущий месяц и выбор даты")
    @allure.severity(allure.severity_level.NORMAL)
    def test_picker_prev_month_navigation_and_selection(self, calendar_page):
        calendar_page.open_picker()
        calendar_page.click_prev_month_in_picker()
        calendar_page.select_day_in_picker(day=10)

        actual_value = calendar_page.get_input_value()
        assert actual_value.endswith("-10"), (
            f"Ожидался выбранный день '10' предыдущего месяца, получено: '{actual_value}'"
        )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "date_value, description",
        [
            ("2026-07-22", "Стандартная дата"),
            ("2024-02-29", "Високосный день"),
            ("2026-01-01", "Первый день года"),
            ("2026-12-31", "Последний день года"),
        ],
        ids=["standard", "leap_year", "first_day", "last_day"]
    )
    def test_type_valid_and_boundary_dates(self, calendar_page, date_value, description):
        allure.dynamic.title(f"Ввод с клавиатуры валидной даты: {description} ({date_value})")

        calendar_page.type_date(date_value)

        assert calendar_page.get_input_value() == date_value, (
            f"Значение в поле '{calendar_page.get_input_value()}' не совпадает с введенным: '{date_value}'"
        )
        assert not calendar_page.is_error_displayed(), f"Отображается ошибка для валидной даты: {date_value}"

    @allure.title("Очистка предварительно заполненного поля даты")
    @allure.severity(allure.severity_level.MINOR)
    def test_clear_filled_date_input(self, calendar_page):
        calendar_page.type_date("2026-05-18")
        assert calendar_page.get_input_value() == "2026-05-18", "Поле не заполнилось перед очисткой"

        calendar_page.clear_date_input()
        assert calendar_page.get_input_value() == "", "Поле ввода даты не очистилось"

    @allure.title("Успешная отправка формы с валидной датой")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_submit_form_with_valid_date(self, calendar_page):
        calendar_page.type_date("2026-11-05")
        calendar_page.submit()

        success_text = calendar_page.get_success_message()
        assert "Thank you for your response" in success_text, (
            f"Ожидалось сообщение подтверждения, получено: '{success_text}'"
        )


@allure.feature("Календари")
@allure.suite("Тестирование страницы Calendars")
class TestCalendarsNegative:
    """Набор негативных тестов валидации даты и формы (4 сценария)."""

    @allure.title("Ввод даты в неверном формате со слэшами (YYYY/MM/DD)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_type_invalid_format_slashes(self, calendar_page):
        calendar_page.type_date("2026/12/31")
        calendar_page.submit()

        is_invalid = calendar_page.is_error_displayed() or THANK_YOU_LABEL not in calendar_page.get_success_message()
        assert is_invalid, "Форма успешно отправилась с некорректным разделителем даты (/)"

    @allure.title("Ввод европейского формата даты (DD-MM-YYYY)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_type_invalid_format_european(self, calendar_page):
        calendar_page.type_date("31-12-2026")
        calendar_page.submit()

        is_invalid = calendar_page.is_error_displayed() or THANK_YOU_LABEL not in calendar_page.get_success_message()
        assert is_invalid, "Форма успешно отправилась с датой в формате DD-MM-YYYY вместо YYYY-MM-DD"

    @allure.title("Ввод несуществующей календарной даты (30 февраля)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_type_nonexistent_february_date(self, calendar_page):
        calendar_page.type_date("2026-02-30")
        calendar_page.submit()

        is_rejected = calendar_page.is_error_displayed() or THANK_YOU_LABEL not in calendar_page.get_success_message()
        assert is_rejected, "Форма пропустила несуществующую календарную дату: 2026-02-30"

    @allure.title("Ввод букв и специальных символов в поле даты")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_type_text_and_special_symbols(self, calendar_page):
        calendar_page.type_date("auto_test_!@#")
        calendar_page.submit()

        is_invalid = calendar_page.is_error_displayed() or THANK_YOU_LABEL not in calendar_page.get_success_message()
        assert is_invalid, "Форма отправилась с текстово-символьным значением вместо даты"
