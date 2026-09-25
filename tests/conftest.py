import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def pytest_addoption(parser):
    """Позволяет передавать аргументы в консоли: pytest --browser=firefox --headless"""
    parser.addoption("--browser", action="store", default="chrome", help="chrome or firefox")
    parser.addoption("--headless", action="store_true", help="Run in headless mode")


@pytest.fixture(scope="function")
def driver(request):
    """Фикстура создания и завершения сессии браузера."""
    browser_name = request.config.getoption("--browser").lower()
    is_headless = request.config.getoption("--headless")

    if browser_name == "chrome":
        options = ChromeOptions()
        if is_headless:
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        driver_instance = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        options = FirefoxOptions()
        if is_headless:
            options.add_argument("-headless")
        driver_instance = webdriver.Firefox(options=options)
        driver_instance.set_window_size(1920, 1080)
    else:
        raise ValueError(f"Браузер {browser_name} не поддерживается")

    driver_instance.implicitly_wait(0)
    yield driver_instance
    driver_instance.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук Allure: автоматически делает скриншот экрана при падении теста."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver_instance = item.funcargs.get("driver")
        if driver_instance:
            allure.attach(
                driver_instance.get_screenshot_as_png(),
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG
            )
