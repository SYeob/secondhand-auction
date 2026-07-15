"""Pa-Bi Auction 상품 등록 UI 테스트."""

from datetime import datetime, timedelta
import os

import pytest

from tests.pages.login_page import LoginPage
from tests.pages.register_product_page import RegisterProductPage


def _get_test_credentials() -> tuple[str, str]:
    """환경 변수에서 공통 테스트 계정을 읽는다."""
    email = os.getenv("TEST_USER_EMAIL", "").strip()
    password = os.getenv("TEST_USER_PASSWORD", "")
    if not email or not password:
        pytest.fail(
            "TEST_USER_EMAIL과 TEST_USER_PASSWORD를 설정해야 합니다.",
            pytrace=False,
        )
    return email, password


@pytest.mark.ui
@pytest.mark.regression
def test_authenticated_user_can_register_product(driver, base_url):
    """로그인 사용자가 유효한 경매 상품을 등록하고 삭제할 수 있다."""
    email, password = _get_test_credentials()
    unique_title = f"QA-AUTO-{datetime.now():%Y%m%d%H%M%S%f}"
    end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    login_page = LoginPage(driver, base_url)
    product_page = RegisterProductPage(driver, base_url)
    product_created = False

    login_page.open_login()
    login_page.login(email, password)
    login_page.wait_for_login_success()

    try:
        product_page.open_register()
        product_page.register_product(
            title=unique_title,
            description="Selenium 자동화 테스트용 상품입니다.",
            location="서울시 강남구",
            starting_price=10000,
            image_url="https://example.com/qa-test-image.jpg",
            end_time=end_time,
        )
        product_page.wait_for_registered_product(unique_title)
        product_created = True

        assert unique_title in driver.page_source
    finally:
        if product_created:
            product_page.open_product(unique_title)
            product_page.delete_open_product()
            assert product_page.is_product_absent(unique_title)
