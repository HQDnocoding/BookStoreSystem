import time

import pytest
import requests
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def test_search_binh_duong_facility_of_open_university(driver):
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

    # Chờ đến khi phần tử 'Cơ sở 5' xuất hiện
    dia_diem_5 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//a[contains(@href, '/co-so-5/') and contains(., 'Địa điểm 5')]",
            )
        )
    )
    assert dia_diem_5 is not None, "Không tìm thấy liên kết đến Cơ sở 5"

    dia_diem_5.click()

    time.sleep(10)

    # Kiểm tra xem đã đến đúng trang Cơ sở 5 chưa
    WebDriverWait(driver, 10).until(EC.url_contains("/co-so-5/"))
    assert "/co-so-5/" in driver.current_url, "Không chuyển đến đúng trang Cơ sở 5"


def test_download_third_slide_image(driver):
    driver.get("https://ou.edu.vn")

    time.sleep(10)
    # Chờ tất cả slide được load
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".ms-slide .ms-slide-bgcont img")
        )
    )

    # Lấy tất cả ảnh trong các slide
    imgs = driver.find_elements(By.CSS_SELECTOR, ".ms-slide .ms-slide-bgcont img")

    print(f"Tổng số ảnh tìm được: {len(imgs)}")
    for i, img in enumerate(imgs):
        print(f"Ảnh {i+1}: {img.get_attribute('src')}")

    # Lọc ảnh thật
    valid_imgs = [img for img in imgs if "blank.gif" not in img.get_attribute("src")]
    assert len(valid_imgs) >= 1, f"Không đủ ảnh hợp lệ. Chỉ có {len(valid_imgs)}"

    img_url = valid_imgs[2].get_attribute("src")
    print(f"✅ Ảnh slide thứ 3 (hợp lệ): {img_url}")

    # Tải ảnh về
    response = requests.get(img_url)
    assert response.status_code == 200, f"Lỗi tải ảnh: {response.status_code}"

    with open("slide_thu_3.jpg", "wb") as f:
        f.write(response.content)

    print("✅ Ảnh slide thứ 3 đã được lưu thành 'slide_thu_3.jpg'")
