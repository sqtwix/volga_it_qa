import allure
import pytest
from selenium.common import ElementClickInterceptedException, TimeoutException

from pages.ads_page import AdsPage


@pytest.fixture
def ads_page(driver):
    page = AdsPage(driver)
    page.open_page()
    return page


@allure.feature("Реклама")
@allure.suite("Тестирование всплывающей рекламы с таймером")
class TestAdsPositive:
    """Позитивные сценарии жизненного цикла рекламы и доступности страницы."""

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

        assert ads_page.is_ad_closed(), "Реклама не закрылась после клика по кнопке '×'"

    @allure.title("Закрытие рекламы с клавиатуры нажатием клавиши Enter на кнопке")
    @allure.severity(allure.severity_level.NORMAL)
    def test_close_ad_via_keyboard_enter(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.close_ad_via_keyboard_enter()

        assert ads_page.is_ad_closed(), "Реклама не закрылась при отправке клавиши Enter в кнопку закрытия"

    @allure.title("Проверка атрибутов доступности (A11y) у кнопки закрытия рекламы")
    @allure.severity(allure.severity_level.MINOR)
    def test_ad_close_button_accessibility_attributes(self, ads_page):
        ads_page.wait_for_ad_to_appear()

        aria_label = ads_page.get_close_button_attribute("aria-label")
        btn_type = ads_page.get_close_button_attribute("type")

        assert aria_label == "Close", f"Ожидался aria-label='Close', получено: '{aria_label}'"
        assert btn_type == "button", f"Ожидался type='button', получено: '{btn_type}'"

    @allure.title("Реклама остается на экране и не исчезает сама по себе")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ad_persists_on_screen_without_autoclose(self, ads_page):
        ads_page.wait_for_ad_to_appear()

        is_still_closed = ads_page.is_ad_closed(timeout=2.0)
        assert not is_still_closed, "Реклама самопроизвольно закрылась без действий пользователя"
        assert ads_page.is_ad_displayed(), "Реклама перестала отображаться на экране"

    @allure.title("Доступность элементов страницы после закрытия рекламы")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_elements_accessible_after_closing_ad(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.close_ad()
        assert ads_page.is_ad_closed()

        assert ads_page.is_page_header_interactive(), "Заголовок страницы недоступен после закрытия рекламы"

    @allure.title("Валидация ссылки на YouTube-урок в контенте страницы")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_tutorial_link_attributes(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.close_ad()
        assert ads_page.is_ad_closed()

        link_data = ads_page.get_page_tutorial_link_data()
        assert "youtube.com/watch?v=FZBGRjv0pqU" in link_data["href"], "Неверный URL в ссылке урока"
        assert link_data["target"] == "_blank", "Ссылка должна открываться в новой вкладке (target='_blank')"


@allure.feature("Реклама")
@allure.suite("Тестирование всплывающей рекламы с таймером")
class TestAdsNegative:
    """Негативные сценарии: защитные механизмы оверлея и блокировка фона."""

    @allure.title("Реклама не отображается мгновенно при загрузке (задержка таймера)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ad_is_not_displayed_immediately(self, ads_page):
        ads_page.driver.execute_script("window.location.reload();")
        assert not ads_page.is_ad_displayed(), "Реклама отобразилась раньше положенных 4.5 секунд"

    @allure.title("Оверлей рекламы блокирует клики по элементам страницы под ним")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_page_link_click_intercepted_by_ad_overlay(self, ads_page):
        ads_page.wait_for_ad_to_appear()

        with pytest.raises(ElementClickInterceptedException):
            ads_page.try_click_page_link()

    @allure.title("Клик по телу рекламы (мимо крестика) не приводит к закрытию")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ad_does_not_close_on_content_click(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.click_ad_content_body()

        assert not ads_page.is_ad_closed(timeout=1.5), "Реклама закрылась при клике по ее содержимому"
        assert ads_page.is_ad_displayed(), "Рекламное окно исчезло после клика по контенту"

    @allure.title("Реклама не закрывается клавишей Escape (конфигурация esc_press: false)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ad_does_not_close_on_escape(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.close_by_esc()

        assert not ads_page.is_ad_closed(timeout=1.5), "Реклама закрылась по Escape вопреки esc_press=false"

    @allure.title("Реклама не закрывается кликом по темной подложке (overlay_click: false)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ad_does_not_close_on_overlay_click(self, ads_page):
        ads_page.wait_for_ad_to_appear()
        ads_page.click_outside_ad()

        assert not ads_page.is_ad_closed(timeout=1.5), "Реклама закрылась при клике на оверлей"