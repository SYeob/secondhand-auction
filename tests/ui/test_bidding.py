"""Pa-Bi Auction 핵심 입찰 UI 테스트."""

from datetime import datetime, timedelta
import os

import pytest

from tests.pages.auction_page import AuctionPage
from tests.pages.login_page import LoginPage
from tests.pages.register_product_page import RegisterProductPage


STARTING_PRICE = 10_000
BID_AMOUNT = 15_000


def _get_account(prefix: str) -> tuple[str, str]:
    """역할별 테스트 계정을 환경 변수에서 읽는다."""
    email_name = f"{prefix}_EMAIL"
    password_name = f"{prefix}_PASSWORD"
    email = os.getenv(email_name, "").strip()
    password = os.getenv(password_name, "")

    missing = [
        name
        for name, value in ((email_name, email), (password_name, password))
        if not value
    ]
    if missing:
        pytest.fail(
            "입찰 테스트 환경 변수가 설정되지 않았습니다: "
            + ", ".join(missing),
            pytrace=False,
        )
    return email, password


@pytest.mark.ui
@pytest.mark.p0
@pytest.mark.regression
def test_bidder_can_place_higher_bid(driver, base_url):
    """입찰자가 현재가보다 높은 금액으로 입찰하면 현재가가 갱신된다."""
    seller_email, seller_password = _get_account("TEST_SELLER")
    bidder_email, bidder_password = _get_account("TEST_BIDDER_A")

    if seller_email.lower() == bidder_email.lower():
        pytest.fail(
            "판매자와 입찰자는 서로 다른 계정을 사용해야 합니다.",
            pytrace=False,
        )

    unique_title = f"QA-BID-{datetime.now():%Y%m%d%H%M%S%f}"
    end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    login_page = LoginPage(driver, base_url)
    product_page = RegisterProductPage(driver, base_url)
    auction_page = AuctionPage(driver, base_url)
    product_created = False

    login_page.open_login()
    login_page.login(seller_email, seller_password)
    login_page.wait_for_login_success()

    try:
        product_page.open_register()
        product_page.register_product(
            title=unique_title,
            description="입찰 자동화 테스트용 상품입니다.",
            location="서울시 강남구",
            starting_price=STARTING_PRICE,
            image_url="https://example.com/qa-bid-test-image.jpg",
            end_time=end_time,
        )
        product_page.wait_for_registered_product(unique_title)
        product_created = True
        product_page.open_product(unique_title)
        product_url = driver.current_url

        login_page.logout()
        login_page.open_login()
        login_page.login(bidder_email, bidder_password)
        login_page.wait_for_login_success()

        driver.get(product_url)
        auction_page.wait_for_product(unique_title)
        auction_page.place_bid(BID_AMOUNT)
        auction_page.wait_for_bid_result(BID_AMOUNT)
    finally:
        if product_created:
            login_page.reset_auth_session()
            login_page.open_login()
            login_page.login(seller_email, seller_password)
            login_page.wait_for_login_success()
            product_page.open_product(unique_title)
            product_page.delete_open_product()
            assert product_page.is_product_absent(unique_title)
