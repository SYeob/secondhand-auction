"""경매 종료, 낙찰 결과 및 개인정보 접근 UI 테스트."""

from datetime import datetime, timedelta, timezone

import pytest

from tests.data.test_data import (
    FIRST_BID_AMOUNT,
    SECOND_BID_AMOUNT,
    SELLER_PHONE,
    STARTING_PRICE,
    unique_title,
)
from tests.pages.auction_page import AuctionPage
from tests.pages.login_page import LoginPage


pytestmark = [pytest.mark.ui, pytest.mark.p0, pytest.mark.regression]


@pytest.fixture(scope="module")
def ended_ui_auction(
    supabase_api,
    seller_account,
    bidder_a_account,
    bidder_b_account,
    base_url,
):
    """UI에서 즉시 종료 상태를 확인할 수 있는 경매를 준비한다."""
    seller = supabase_api.sign_in(seller_account)
    bidder_a = supabase_api.sign_in(bidder_a_account)
    bidder_b = supabase_api.sign_in(bidder_b_account)
    product = supabase_api.create_product(
        seller,
        title=unique_title("QA-UI-CLOSE"),
        end_time=datetime.now(timezone.utc) + timedelta(minutes=5),
        starting_price=STARTING_PRICE,
        seller_phone=SELLER_PHONE,
    )

    try:
        supabase_api.place_bid(bidder_a, product["id"], FIRST_BID_AMOUNT)
        supabase_api.place_bid(bidder_b, product["id"], SECOND_BID_AMOUNT)
        supabase_api.update_product_end_time(
            seller,
            product["id"],
            datetime.now(timezone.utc) - timedelta(minutes=5),
        )

        yield {
            "title": product["title"],
            "url": f"{base_url}/product/{product['id']}",
        }
    finally:
        supabase_api.delete_product(seller, product["id"])


def _login(driver, base_url, account) -> None:
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login(account.email, account.password)
    login_page.wait_for_login_success()


def test_winner_sees_auction_end_and_seller_contact(
    driver,
    base_url,
    bidder_b_account,
    ended_ui_auction,
):
    """최고 입찰자는 종료 상태와 판매자 연락처를 확인할 수 있다."""
    _login(driver, base_url, bidder_b_account)
    page = AuctionPage(driver, base_url)

    driver.get(ended_ui_auction["url"])
    page.dismiss_winner_notification_if_present()
    page.wait_for_product(ended_ui_auction["title"])
    page.wait_for_auction_ended()
    page.open_winner_contact()
    page.wait_for_seller_phone(SELLER_PHONE)


def test_non_winner_cannot_see_seller_contact(
    driver,
    base_url,
    bidder_a_account,
    ended_ui_auction,
):
    """입찰했지만 낙찰되지 않은 사용자는 판매자 연락처를 볼 수 없다."""
    _login(driver, base_url, bidder_a_account)
    page = AuctionPage(driver, base_url)

    driver.get(ended_ui_auction["url"])
    page.dismiss_winner_notification_if_present()
    page.wait_for_product(ended_ui_auction["title"])
    page.wait_for_auction_ended()
    page.wait_for_loser_message()

    assert SELLER_PHONE not in driver.page_source
