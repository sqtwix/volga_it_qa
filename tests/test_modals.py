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
class TestSimpleModal:

    @allure.title("Открытие и закрытие простого модального окна через крестик")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_open_and_close_simple_modal(self, modals_page):
        modals_page.open_simple_modal()
        assert modals_page.is_simple_modal_displayed(), "Окно Simple Modal не отобразилось на экране"
        assert modals_page.get_simple_modal_title() == "Simple Modal", "Заголовок модального окна не совпадает"

        modals_page.close_simple_modal()
        assert modals_page.is_simple_modal_closed(), "Окно Simple Modal не закрылось после нажатия на крестик"
