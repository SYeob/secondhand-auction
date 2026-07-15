"""Pa-Bi Auction 핵심 입찰 UI 테스트."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import os

import pytest

from tests.pages.auction_page import AuctionPage
from tests.pages.login_page import LoginPage
from tests.pages.register_product_page import RegisterProductPage


STARTING_PRICE = 10_000
VALID_BID_AMOUNT = 15_000

pytestmark = [
    pytest.mark.ui,
    pytest.mark.p0,
    pytest.mark.regression,
]


@dataclass(frozen=True)
class AuctionContext:
    """테스트마다 생성한 경매 상품 정보."""

    title: str
    url: str


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


@pytest.fixture
def auction_context(driver, base_url):
    """판매자 상품을 준비하고 테스트 종료 후 삭제한다."""
    seller_email, seller_password = _get_account("TEST_SELLER")
    unique_title = f"QA-BID-{datetime.now():%Y%m%d%H%M%S%f}"
    end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    login_page = LoginPage(driver, base_url)
    product_page = RegisterProductPage(driver, base_url)
    product_created = False
    product_url = ""

    try:
        login_page.open_login()
        login_page.login(seller_email, seller_password)
        login_page.wait_for_login_success()

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

        yield AuctionContext(title=unique_title, url=product_url)
    finally:
        if product_created:
            login_page.reset_auth_session()
            login_page.open_login()
            login_page.login(seller_email, seller_password)
            login_page.wait_for_login_success()
            if product_url:
                driver.get(product_url)
            else:
                product_page.open_product(unique_title)
            product_page.delete_open_product()
            assert product_page.is_product_absent(unique_title)


def _login_as_bidder(driver, base_url) -> None:
    """입찰자 A로 로그인하고 판매자와 다른 계정인지 확인한다."""
    seller_email, _ = _get_account("TEST_SELLER")
    bidder_email, bidder_password = _get_account("TEST_BIDDER_A")

    if seller_email.lower() == bidder_email.lower():
        pytest.fail(
            "판매자와 입찰자는 서로 다른 계정을 사용해야 합니다.",
            pytrace=False,
        )

    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login(bidder_email, bidder_password)
    login_page.wait_for_login_success()


def test_bidder_can_place_higher_bid(driver, base_url, auction_context):
    """입찰자가 현재가보다 높은 금액으로 입찰하면 현재가가 갱신된다."""
    _login_as_bidder(driver, base_url)
    auction_page = AuctionPage(driver, base_url)

    driver.get(auction_context.url)
    auction_page.wait_for_product(auction_context.title)
    auction_page.place_bid(VALID_BID_AMOUNT)
    auction_page.wait_for_bid_result(VALID_BID_AMOUNT)


@pytest.mark.parametrize(
    "invalid_bid_amount",
    [STARTING_PRICE, STARTING_PRICE - 1_000],
    ids=["equal_to_current_price", "lower_than_current_price"],
)
def test_bidder_cannot_bid_at_or_below_current_price(
    driver,
    base_url,
    auction_context,
    invalid_bid_amount,
):
    """현재가와 같거나 낮은 금액의 입찰은 차단된다."""
    _login_as_bidder(driver, base_url)
    auction_page = AuctionPage(driver, base_url)

    driver.get(auction_context.url)
    auction_page.wait_for_product(auction_context.title)
    auction_page.place_bid(invalid_bid_amount)
    auction_page.wait_for_bid_price_error(STARTING_PRICE)
    auction_page.wait_for_current_price(STARTING_PRICE)


def test_unauthenticated_user_cannot_place_bid(driver, base_url, auction_context):
    """비로그인 사용자가 입찰을 확정하면 로그인 화면으로 이동한다."""
    auction_page = AuctionPage(driver, base_url)

    driver.get(auction_context.url)
    auction_page.wait_for_product(auction_context.title)
    auction_page.place_bid(VALID_BID_AMOUNT)
    auction_page.wait_for_auth_redirect()
