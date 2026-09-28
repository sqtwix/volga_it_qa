import allure
import pytest
from pages.ads_page import AdsPage


@pytest.fixture
def ads_page(driver):
    page = AdsPage(driver)
    page.open_page()
    return page


@allure.feature("Реклама")
@allure.suite("Тестирование всплывающей рекламы с таймером")
class TestAdsPositive:
    """Позитивные сценарии автоматического появления и закрытия рекламы."""

    @allure.title("Автоматическое появление рекламного окна через таймер (~4.5 сек)")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_ad_appears_automatically(self, ads_page):
        ad_appeared = ads_page.wait_for_ad_to_appear(timeout=8.0)
        assert ad_appeared, "Рекламное окно не появилось в течение 8 секунд"

    @allure.title("Валидация заголовка и содержимого текста рекламы")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ad_content_validation(self, ads_page):
        ads_page.wait_for_ad_to_appear()

        title = ads_page.get_ad_title()
        text = ads_page.get_ad_text()

        assert title == "Hi", f"Ожидался заголовок 'Hi', получено: '{title}'"
        assert text == "I am an ad.", f"Ожидался текст 'I am an ad.', получено: '{text}'"

    @allure.title("Успешное закрытие рекламы кликом по крестику")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_close_ad_via_close_button(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.close_ad()

        assert ads_page.is_ad_closed(), "Рекламное окно или оверлей не исчезли после клика на '×'"

    @allure.title("Доступность элементов страницы после закрытия рекламы")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_elements_accessible_after_closing_ad(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.close_ad()
        assert ads_page.is_ad_closed(), "Реклама не закрылась"

        assert ads_page.is_page_header_interactive(), "Основная страница недоступна после закрытия рекламы"

    @allure.title("Повторное появление рекламы при обновлении страницы")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ad_appears_again_on_page_reload(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.close_ad()
        assert ads_page.is_ad_closed()

        ads_page.driver.refresh()
        assert ads_page.wait_for_ad_to_appear(timeout=8.0), "Реклама не появилась повторно после обновления страницы"


@allure.feature("Реклама")
@allure.suite("Тестирование всплывающей рекламы с таймером")
class TestAdsNegative:
    """Негативные сценарии: проверка защитных механизмов от случайного закрытия."""

    @allure.title("Реклама не отображается мгновенно при первой загрузке страницы (задержка таймера)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ad_is_not_displayed_immediately(self, ads_page):
        is_instantly_visible = ads_page.is_ad_displayed()
        assert not is_instantly_visible, "Реклама отобразилась мгновенно, таймер задержки 4.5с не сработал"

    @allure.title("Реклама не закрывается нажатием клавиши Escape (esc_press: false)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ad_does_not_close_on_escape(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.close_by_esc()

        assert not ads_page.is_ad_closed(timeout=1.5), (
            "Реклама закрылась по клавише Escape, хотя в конфигурации esc_press=false"
        )

    @allure.title("Реклама не закрывается кликом по оверлею вне окна (overlay_click: false)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ad_does_not_close_on_overlay_click(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.click_outside_ad()

        assert not ads_page.is_ad_closed(timeout=1.5), (
            "Реклама закрылась при клике на темный фон, хотя overlay_click=false"
        )