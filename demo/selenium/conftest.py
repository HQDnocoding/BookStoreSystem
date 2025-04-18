import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    # Use this line instead of the prev if you wish to download the ChromeDriver binary on the fly
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.implicitly_wait(100)
    # Yield the WebDriver instance
    yield driver
    # Close the WebDriver instance
    driver.quit()

    # driver = uc.Chrome()
    # driver.maximize_window()
    # yield driver
    # if driver.service.process and driver.service.process.poll() is None:
    #     try:
    #         driver.quit()
    #     except OSError:
    #         pass


@pytest.fixture()
def chrome_browser():
    driver = webdriver.Chrome()

    # Use this line instead of the prev if you wish to download the ChromeDriver binary on the fly
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    driver.implicitly_wait(100)
    # Yield the WebDriver instance
    yield driver
    # Close the WebDriver instance
    driver.quit()
