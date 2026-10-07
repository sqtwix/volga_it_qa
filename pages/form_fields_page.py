import allure
from selenium.webdriver.common.by import By
from config.settings import urls
from pages.base_page import BasePage


class FormFieldsPage(BasePage):
    # Локаторы раздела инструментов и поля Message
    AUTOMATION_TOOLS_ITEMS = (
        By.XPATH,
        "//*[contains(text(), 'Automation tools')]/following-sibling::ul[1]/li"
    )
    MESSAGE_TEXTAREA = (By.ID, "message")

    def open_page(self):
        with allure.step("Открытие страницы Form Fields"):
            self.open(urls.FORM_FIELDS_URL)

    def get_automation_tools_names(self) -> list[str]:
        """Получает список веб-элементов инструментов и преобразует их в список строк."""
        with allure.step("Получение списка названий инструментов из раздела 'Automation Tools'"):
            elements = self.find_elements(self.AUTOMATION_TOOLS_ITEMS)
            tools = [element.text.strip() for element in elements if element.text.strip()]
            return tools

    def fill_message_field(self, message: str):
        """Заполняет поле Message переданным текстом."""
        with allure.step(f"Заполнение поля Message текстом: '{message}'"):
            self.type_text(self.MESSAGE_TEXTAREA, message)

    def get_message_field_value(self) -> str:
        """Считывает текущее значение из textarea Message для валидации."""
        with allure.step("Получение текущего текста из поля Message"):
            element = self.find_element(self.MESSAGE_TEXTAREA)
            return element.get_attribute("value") or ""