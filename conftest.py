import pytest
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

admin_username = "user"
admin_password = "bitnami"

USD_to_EUR_ratio = 0.7846013289036545
USD_to_GBP_ratio = 0.6125083056478405

catalog_section = ["desktops", "laptop-notebook", "tablet", "smartphone", "camera", "mp3-players"]


def pytest_addoption(parser):
    parser.addoption("--browser",
                     default="chrome")
    parser.addoption("--headless",
                     action="store_true")
    parser.addoption("--base_url",
                     default="http://192.168.0.74:8081")
    parser.addoption("--remote_url",
                     default="http://192.168.0.74")
    parser.addoption("--log_level",
                     action="store",
                     default="DEBUG")
    parser.addoption("--machine",
                     default="local",
                     choices=["local", "remote"])
    parser.addoption("--bv",
                     action="store")
    parser.addoption("--vnc",
                     action="store_true")
    parser.addoption("--logs",
                     action="store_true")
    parser.addoption("--video",
                     action="store_true")


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base_url")


@pytest.fixture
def browser(request):
    _browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    log_level = request.config.getoption("--log_level")
    machine = request.config.getoption("--machine")
    executor = request.config.getoption("--remote_url")

    logger = logging.getLogger(request.node.name)
    file_handler = logging.FileHandler(f"logs/{request.node.name}.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    logger.setLevel(level=log_level)

    logger.info(f"======> Test {request.node.name} started")

    if machine == "local":

        if _browser == "firefox":
            options = FirefoxOptions()
            options.headless = headless
            driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()), options=options
            )
        elif _browser == "chrome":
            options = ChromeOptions()
            options.headless = headless
            driver = webdriver.Chrome(
                service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options
            )

    elif machine == "remote":
        if _browser == "chrome":
            options = ChromeOptions()
        elif _browser == "firefox":
            options = FirefoxOptions()
        _version = request.config.getoption("--bv")
        vnc = request.config.getoption("--vnc")
        video = request.config.getoption("--video")
        driver = webdriver.Remote(
            command_executor=f"{executor}:4444/wd/hub",
            desired_capabilities={"browserName": _browser,
                                  "browserVersion": _version,
                                  "selenoid:options": {
                                      "screenResolution": "1285x720",
                                      "name": "OTUS_homework_11",
                                      "enableVNC": vnc,
                                      "enableVideo": video
                                        }
                                  },
            options=options
        )

    logger.info(f"Browser:{_browser}")

    driver.log_level = log_level
    driver.logger = logger
    driver.test_name = request.node.name

    driver.maximize_window()

    yield driver

    logger.info(f"======> Test {request.node.name} finished")

    driver.quit()
