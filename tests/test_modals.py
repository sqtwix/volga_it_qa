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
    """Позитивные сценарии работы с модальными окнами и контактной формой."""

    @allure.story("Simple Modal")
    @allure.title("Проверка заголовка и содержимого текста простого модального окна")
    @allure.severity(allure.severity_level.NORMAL)
    def test_simple_modal_content(self, modals_page):
        modals_page.open_simple_modal()

        assert modals_page.is_simple_modal_displayed(), "Simple Modal не отобразилось на экране"
        assert modals_page.get_simple_modal_title() == "Simple Modal", "Неверный заголовок окна"
        assert "Hi, I'm a simple modal." in modals_page.get_simple_modal_text(), (
            f"Текст окна отличается от ожидаемого: '{modals_page.get_simple_modal_text()}'"
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
    @allure.title("Закрытие модального окна с формой кнопкой-крестиком")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_modal_close_via_close_button(self, modals_page):
        modals_page.open_form_modal()
        assert modals_page.is_form_modal_displayed(), "Form Modal не отобразилось"

        modals_page.close_form_modal()
        assert modals_page.is_form_modal_closed(), "Form Modal не закрылось при клике на крестик"

    @allure.story("Form Modal")
    @allure.title("Повторное открытие Form Modal после закрытия")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_modal_reopen_cycle(self, modals_page):
        modals_page.open_form_modal()
        modals_page.close_form_modal()
        assert modals_page.is_form_modal_closed(), "Form Modal не закрылось"

        modals_page.open_form_modal()
        assert modals_page.is_form_modal_displayed(), "Form Modal не открылось повторно"

    @allure.story("Form Modal")
    @pytest.mark.parametrize(
        "name, email, text, description",
        [
            ("Иван", "qa_valid@example.com", "Текст сообщения", "все поля заполнены"),
            ("Иван", "", "Сообщение без email", "пустое необязательное поле email"),
            ("Иван", "qa_valid@example.com", "", "пустое необязательное поле текста"),
            ("Иван", "qa_valid@example.com", "Long_text_" * 15, "длинное текстовое сообщение"),
        ],
        ids=["all_fields", "no_email", "no_message", "long_text"]
    )
    @allure.severity(allure.severity_level.BLOCKER)
    def test_submit_form_modal_valid_data(self, modals_page, name: str, email: str, text: str, description: str):
        allure.dynamic.title(f"Успешная отправка формы ({description})")

        modals_page.open_form_modal()

        modals_page.type_name(name)
        modals_page.type_email(email)
        modals_page.type_message(text)

        modals_page.submit_form()

        details = modals_page.get_form_submission_details()
        assert "Thank you for your response" in details, "Отсутствует подтверждающий заголовок"
        assert name in details, f"Имя '{name}' не отобразилось в сводке"
        if email:
            assert email in details, f"Email '{email}' не отобразился в сводке"
        if text:
            assert text in details, f"Текст сообщения не отобразился в сводке"

    @allure.story("Form Modal")
    @allure.title("Возврат к исходной форме по ссылке '← Back' после успешной отправки")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_modal_go_back_after_submission(self, modals_page):
        modals_page.open_form_modal()

        modals_page.type_name("Иван")
        modals_page.type_email("back_test@example.com")
        modals_page.type_message("Проверка ссылки Back")

        modals_page.submit_form()

        assert "Thank you for your response" in modals_page.get_form_submission_details()

        modals_page.click_back_to_form()
        assert modals_page.is_form_inputs_visible(), "Форма не вернулась к полям ввода после клика '← Back'"


@allure.feature("Модальные окна")
@allure.suite("Тестирование страницы Modals")
class TestModalsNegative:
    """Негативные сценарии валидации полей и защитных механизмов окон."""

    @allure.feature("Модальные окна")
    @allure.suite("Тестирование страницы Modals")
    class TestModalsNegative:
        """Негативные сценарии валидации полей контактной формы."""

        @allure.story("Валидация поля Name")
        @pytest.mark.parametrize(
            "invalid_name, description",
            [
                ("", "пустая строка"),
                ("    ", "строка только из пробелов"),
            ],
            ids=["empty_name", "whitespace_name"]
        )
        @allure.severity(allure.severity_level.CRITICAL)
        def test_submit_form_invalid_name(self, modals_page, invalid_name: str, description: str):
            allure.dynamic.title(f"Отправка формы с невалидным именем: {description}")

            modals_page.open_form_modal()

            modals_page.type_name(invalid_name)
            modals_page.type_email("qa@example.com")
            modals_page.type_message("Текст")

            modals_page.submit_form()

            is_rejected = (
                    modals_page.is_name_error_displayed()
                    or "Thank you" not in modals_page.get_form_success_message(timeout=1.5)
            )
            assert is_rejected, f"Форма пропустила невалидное имя ({description})"

        @allure.story("Валидация поля Email")
        @pytest.mark.parametrize(
            "invalid_email, description",
            [
                ("plain_text", "текст без знака @ и домена"),
                ("user@", "нет доменной части"),
                ("@domain.com", "нет имени пользователя"),
            ],
            ids=["no_at", "no_domain", "no_user"]
        )
        @allure.severity(allure.severity_level.CRITICAL)
        def test_submit_form_invalid_email(self, modals_page, invalid_email: str, description: str):
            allure.dynamic.title(f"Отправка формы с невалидным email: {description}")

            modals_page.open_form_modal()

            modals_page.type_name("Иван")
            modals_page.type_email(invalid_email)
            modals_page.type_message("Текст")

            modals_page.submit_form()

            is_rejected = (
                    modals_page.is_email_error_displayed()
                    or "Thank you" not in modals_page.get_form_success_message(timeout=1.5)
            )
            assert is_rejected, f"Форма пропустила невалидный email ({description})"

    @allure.story("Защита окон")
    @allure.title("Попытка закрытия Simple Modal клавишей Escape (запрещено конфигурацией)")
    @allure.severity(allure.severity_level.MINOR)
    def test_simple_modal_does_not_close_on_escape(self, modals_page):
        modals_page.open_simple_modal()
        modals_page.close_modal_by_esc()

        assert modals_page.is_simple_modal_displayed(), (
            "Simple Modal закрылось по нажатию Escape, хотя esc_press=false"
        )

    @allure.story("Защита окон")
    @allure.title("Клик по фоновому оверлею не закрывает модальное окно (overlay_click=false)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_modal_does_not_close_on_overlay_click(self, modals_page):
        modals_page.open_form_modal()
        modals_page.click_outside_modal()

        assert modals_page.is_form_modal_displayed(), (
            "Модальное окно закрылось при клике на оверлей, хотя overlay_click отключен"
        )
