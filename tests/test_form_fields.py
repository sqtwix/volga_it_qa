import allure
import pytest
from pages.form_fields_page import FormFieldsPage


@pytest.fixture
def form_fields_page(driver):
    page = FormFieldsPage(driver)
    page.open_page()
    return page


@allure.feature("Поля форм")
@allure.suite("Тестирование страницы Form Fields")
class TestFormFieldsPositive:

    @allure.story("Заполнение формы")
    @allure.title("Заполнение поля Message списком Automation Tools через запятую")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_fill_message_with_automation_tools(self, form_fields_page):
        # 1. Извлекаем список инструментов через Selenium
        tools = form_fields_page.get_automation_tools_names()
        assert len(tools) > 0, "Список инструментов Automation Tools пуст или не найден в DOM"

        # 2. Формируем единую строку с разделением через запятую
        tools_text = ", ".join(tools)

        # 3. Заполняем поле Message
        form_fields_page.fill_message_field(tools_text)

        # 4. Проверяем, что значение в поле полностью совпадает со списком
        actual_message = form_fields_page.get_message_field_value()
        assert actual_message == tools_text, (
            f"Значение в поле Message не совпадает.\nОжидалось: '{tools_text}'\nПолучено: '{actual_message}'"
        )