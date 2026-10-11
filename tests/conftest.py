import allure
import pytest
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def pytest_addoption(parser):
    """Позволяет передавать аргументы в консоли: pytest --browser=firefox --headless"""
    parser.addoption("--browser", action="store", default="chrome", help="chrome or firefox")
    parser.addoption("--headless", action="store_true", help="Run in headless mode")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Перехват отчетов для всех этапов жизненного цикла теста."""
    outcome = yield
    rep = outcome.get_result()

    setattr(item, f"rep_{rep.when}", rep)

    if rep.failed:
        driver = getattr(item, "_driver", None) or item.funcargs.get("driver", None)

        if driver is not None:
            try:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name=f"failure_{rep.when}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except WebDriverException:
                pass


@pytest.fixture(scope="function")
def driver(request):
    browser_name = request.config.getoption("--browser", default="firefox")
    is_headless = request.config.getoption("--headless")

    if browser_name == "firefox":
        options = FirefoxOptions()
        options.page_load_strategy = "eager"
        if is_headless:
            options.add_argument("-headless")
        driver_instance = webdriver.Firefox(options=options)
    elif browser_name == "chrome":
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        if is_headless:
            options.add_argument("-headless")
        driver_instance = webdriver.Chrome(options=options)
    else:
        raise ValueError(f"Неподдерживаемый браузер: {browser_name}")

    try:
        driver_instance.set_window_size(1920, 1080)
        driver_instance.set_page_load_timeout(15)

        request.node._driver = driver_instance

        yield driver_instance

    finally:
        if driver_instance is not None:
            try:
                driver_instance.quit()
            except WebDriverException:
                pass
