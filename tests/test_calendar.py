from datetime import date

import allure
import pytest

from pages.calendar_page import CalendarPage


@pytest.fixture
def calendar_page(driver):
    page = CalendarPage(driver)
    page.open_page()
    return page


@allure.feature("Календари")
@allure.suite("Тестирование страницы Calendars")
class TestCalendarsPositive:
    """Набор позитивных тестов на страницу календаря"""

    @allure.title("Выбор дня текущего месяца в датапикере")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_select_day_in_current_month(self, calendar_page):
        """Проверяет полную дату после выбора 15-го числа текущего месяца."""
        target_day = 15
        expected_date = date.today().replace(day=target_day).isoformat()

        calendar_page.open_picker()
        calendar_page.select_day_in_picker(day=target_day)

        actual_value = calendar_page.get_input_value()
        assert actual_value == expected_date, (
            f"Ожидалась дата '{expected_date}', получено: '{actual_value}'"
        )

    @allure.title("Переключение на следующий месяц и выбор даты")
    @allure.severity(allure.severity_level.NORMAL)
    def test_select_day_in_next_month(self, calendar_page):
        """Проверяет следующий месяц и год по дате выбранного 18-го числа."""
        target_day = 18
        today = date.today()
        expected_year = today.year + 1 if today.month == 12 else today.year
        expected_month = 1 if today.month == 12 else today.month + 1
        expected_date = f"{expected_year:04d}-{expected_month:02d}-{target_day:02d}"

        calendar_page.open_picker()
        calendar_page.click_next_month_in_picker()
        calendar_page.select_day_in_picker(day=target_day)

        actual_value = calendar_page.get_input_value()
        assert actual_value == expected_date, (
            f"Ожидалась полная дата '{expected_date}', но получено: '{actual_value}'"
        )

    @allure.title("Переключение на предыдущий месяц (после перехода вперед) и выбор даты")
    @allure.severity(allure.severity_level.NORMAL)
    def test_picker_prev_month_navigation_and_selection(self, calendar_page):
        """Проверяет стрелку назад после перехода вперёд, возвращаясь в текущий месяц.

        Сценарий не проверяет доступность дат в месяцах раньше текущего.
        """
        target_day = 25
        today = date.today()
        expected_date = f"{today.year:04d}-{today.month:02d}-{target_day:02d}"

        calendar_page.open_picker()
        calendar_page.click_next_month_in_picker()
        calendar_page.click_prev_month_in_picker()
        calendar_page.select_day_in_picker(day=target_day)

        actual_value = calendar_page.get_input_value()
        assert actual_value == expected_date, (
            f"Ожидалась дата текущего месяца '{expected_date}' после возврата назад, получено: '{actual_value}'"
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
        """Проверяет подтверждение отправки и точную дату в сводке формы."""
        target_date = "2026-11-05"

        calendar_page.type_date(target_date)
        calendar_page.submit()

        success_text = calendar_page.get_success_message()

        assert "Thank you for your response" in success_text, (
            f"Форма не отправилась или текст успеха не найден. Получено: '{success_text}'"
        )
        submitted_date = calendar_page.get_submitted_date()
        assert submitted_date == target_date, (
            f"В сводке ожидалась дата '{target_date}', получено: '{submitted_date}'"
        )


@allure.feature("Календари")
@allure.suite("Тестирование страницы Calendars")
class TestCalendarsNegative:
    """Набор негативных тестов валидации даты и формы (4 сценария)."""

    @allure.title("Ввод даты в неверном формате со слэшами (YYYY/MM/DD)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_type_invalid_format_slashes(self, calendar_page):
        """Проверяет наличие ошибки и её текст при разделении даты слэшами."""
        calendar_page.type_date("2026/12/31")
        calendar_page.submit()

        assert calendar_page.is_error_displayed(), (
            "Сообщение об ошибке валидации формата даты не отобразилось"
        )

        error_text = calendar_page.get_error_message()
        assert "Please enter a valid date" in error_text, (
            f"Неожиданный текст ошибки: '{error_text}'"
        )

    @allure.title("Ввод европейского формата даты (DD-MM-YYYY)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_type_invalid_format_european(self, calendar_page):
        calendar_page.type_date("31-12-2026")
        calendar_page.submit()

        assert calendar_page.is_error_displayed(), "Форма успешно отправилась с датой в формате DD-MM-YYYY вместо YYYY-MM-DD"

    @allure.title("Ввод несуществующей календарной даты (30 февраля)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_type_nonexistent_february_date(self, calendar_page):
        calendar_page.type_date("2026-02-30")
        calendar_page.submit()

        assert calendar_page.is_error_displayed(), "Форма пропустила несуществующую календарную дату: 2026-02-30"

    @allure.title("Ввод букв и специальных символов в поле даты")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_type_text_and_special_symbols(self, calendar_page):
        calendar_page.type_date("auto_test_!@#")
        calendar_page.submit()

        assert calendar_page.is_error_displayed(), "Форма отправилась с текстово-символьным значением вместо даты"
