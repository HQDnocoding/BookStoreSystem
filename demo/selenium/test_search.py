import time

import pytest
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def test_open_university_exam_schedule(driver):
    driver.get("https://google.com")
    assert "Google" in driver.title, "Google homepage not loaded correctly"

    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "gLFyf"))
    )
    assert search_input is not None, "Search input not found on Google homepage"

    search_input.clear()
    search_input.send_keys("dai hoc mo hcm" + Keys.ENTER)

    time.sleep(5)

    uni_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.PARTIAL_LINK_TEXT, "TRƯỜNG ĐẠI HỌC MỞ TP HCM")
        )
    )
    assert uni_link is not None, "University link not found in search results"
    uni_link.click()

    assert "ou.edu.vn" in driver.current_url

    exam_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "LỊCH THI"))
    )
    assert exam_link is not None
    exam_link.click()

    time.sleep(10)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Lịch thi')]"))
    )

    assert "Lịch thi" in driver.page_source or "lịch thi" in driver.page_source.lower()


def test_game_cookie_clicker():
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    driver.get("https://orteil.dashnet.org/cookieclicker/")
    driver.maximize_window()

    cookie_id = "bigCookie"
    cookies_id = "cookies"
    product_price_prefix = "productPrice"
    product_prefix = "product"

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'English')]"))
    )
    language = driver.find_element(By.XPATH, "//*[contains(text(), 'English')]")
    language.click()

    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, cookie_id)))
    cookie = driver.find_element(By.ID, cookie_id)
    # while True:
    #     cookie.click()
    #     cookies


# bai 1: mo google vao trang ou, thanh quan, chon co so binh duong
# bai 2: vao google tim dh mo hcm tai hinh anh thu 3
