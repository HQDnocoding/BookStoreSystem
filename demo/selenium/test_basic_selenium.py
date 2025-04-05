import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def test_title(chrome_browser):
    """Test the title of the Python.org website"""
    chrome_browser.get("https://www.python.org")
    assert chrome_browser.title == "Welcome to Python.org"


def test_search(chrome_browser):
    """
    Test the search functionality of the DuckDuckGo website
    """
    url = "https://duckduckgo.com/"
    search_term = "Pytest with Eric"
    # Navigate to the Google home page.
    chrome_browser.get(url)

    # Find the search box using its name attribute value.
    search_box = chrome_browser.find_element(By.ID, value="searchbox_input")

    # Enter a search query and submit.
    search_box.send_keys(search_term + Keys.RETURN)

    time.sleep(5)

    # Assert that the title contains the search term.
    assert search_term in chrome_browser.title
