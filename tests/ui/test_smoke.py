"""Pa-Bi Auction 홈 화면 Smoke Test."""

import pytest
from selenium.webdriver.common.by import By

from tests.pages.base_page import BasePage


@pytest.mark.smoke
@pytest.mark.ui
def test_home_page_is_displayed(driver, base_url):
    """홈 화면이 열리고 핵심 헤더 요소가 표시되는지 확인한다."""
    page = BasePage(driver, base_url)
    page.open("/")

    logo = page.wait_until_visible((By.LINK_TEXT, "Pa-Bi"))
    login_button = page.wait_until_visible((By.XPATH, "//button[.//span[normalize-space()='로그인']]"))
    search_input = page.wait_until_visible(
        (By.CSS_SELECTOR, "input[placeholder='검색어를 입력해 주세요']")
    )

    assert logo.is_displayed(), "Pa-Bi 로고가 표시되지 않았습니다."
    assert login_button.is_displayed(), "로그인 버튼이 표시되지 않았습니다."
    assert search_input.is_displayed(), "상품 검색 입력창이 표시되지 않았습니다."
    assert driver.current_url.rstrip("/") == base_url.rstrip("/")
