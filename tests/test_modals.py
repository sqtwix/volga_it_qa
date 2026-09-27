import allure
import pytest

from pages.modals_page import ModalsPage


@pytest.fixture
def modals_page(driver):
    page = ModalsPage(driver)
    page.open_page()
    return page


@allure.feature("Модальные окна")
@allure.suite("Тестирование страницы Modals")
class TestModalsPositive:
    """Позитивные сценарии работы с модальными окнами и формой."""

    @allure.story("Simple Modal")
    @allure.title("Проверка заголовка и содержимого текста простого модального окна")
    @allure.severity(allure.severity_level.NORMAL)
    def test_simple_modal_content(self, modals_page):
        modals_page.open_simple_modal()

        assert modals_page.is_simple_modal_displayed(), "Simple Modal не отобразилось на экране"
        assert modals_page.get_simple_modal_title() == "Simple Modal", "Неверный заголовок окна"
        assert "Hi, I'm a simple modal." in modals_page.get_simple_modal_title(), (
            f"Текст окна отличается от ожидаемого: '{modals_page.get_simple_modal_title()}'"
        )

    @allure.story("Simple Modal")
    @allure.title("Повторное открытие простого окна после закрытия")
    @allure.severity(allure.severity_level.NORMAL)
    def test_simple_modal_reopen_cycle(self, modals_page):
        modals_page.open_simple_modal()
        modals_page.close_simple_modal()
        assert modals_page.is_simple_modal_closed(), "Окно не закрылось в первом цикле"

        modals_page.open_simple_modal()
        assert modals_page.is_simple_modal_displayed(), "Окно не открылось повторно"

    @allure.story("Form Modal")
    @allure.title("Закрытие модального окна с формой клавишей Escape")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_modal_close_via_esc(self, modals_page):
        modals_page.open_form_modal()
        assert modals_page.is_form_modal_displayed(), "Form Modal не отобразилось"

        modals_page.close_modal_by_esc()
        assert modals_page.is_form_modal_closed(), "Form Modal не закрылось при нажатии Escape"

    @allure.story("Form Modal")
    @allure.title("Успешная отправка контактной формы всеми валидными данными")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_submit_form_modal_valid_data(self, modals_page):
        modals_page.open_form_modal()

        modals_page.type_name("Марио")
        modals_page.type_email("a_test@example.com")
        modals_page.type_message("Тестовое сообщение для проверки отправки формы")

        modals_page.submit_form()

        success_msg = modals_page.get_form_success_message()
        assert "Thank you for your response" in success_msg, (
            f"Ожидалось сообщение подтверждения, получено: '{success_msg}'"
        )


@allure.feature("Модальные окна")
@allure.suite("Тестирование страницы Modals")
class TestModalsNegative:
    """Негативные сценарии валидации полей и управления окнами."""

    @allure.story("Валидация формы")
    @allure.title("Отправка формы с пустым обязательным полем Name")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_submit_form_without_required_name(self, modals_page):
        modals_page.open_form_modal()
        modals_page.fill_form(
            name="",
            email="valid_email@example.com",
            message="Тест без имени"
        )
        modals_page.submit_form()

        # Форма обязана подсветить ошибку поля Name или отклонить отправку
        is_rejected = modals_page.is_name_error_displayed() or "Thank you" not in modals_page.get_form_success_message(
            timeout=1.5)
        assert is_rejected, "Форма успешно отправилась без обязательного поля Name"

    @allure.story("Валидация формы")
    @allure.title("Отправка формы с некорректным форматом Email")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_submit_form_with_invalid_email(self, modals_page):
        modals_page.open_form_modal()
        modals_page.fill_form(
            name="Иван",
            email="plain_text_not_email",
            message="Тест с битым email"
        )
        modals_page.submit_form()

        is_rejected = modals_page.is_email_error_displayed() or "Thank you" not in modals_page.get_form_success_message(
            timeout=1.5)
        assert is_rejected, "Форма пропустила строку без символа @ и домена в поле Email"

    @allure.story("Управление окнами")
    @allure.title("Попытка закрытия Simple Modal клавишей Escape (запрещено конфигурацией)")
    @allure.severity(allure.severity_level.MINOR)
    def test_simple_modal_does_not_close_on_escape(self, modals_page):
        modals_page.open_simple_modal()
        modals_page.close_modal_by_esc()

        # В параметрах simple-modal указано: esc_press: false
        assert modals_page.is_simple_modal_displayed(), (
            "Simple Modal закрылось по нажатию Escape, хотя этот триггер для него отключен"
        )
