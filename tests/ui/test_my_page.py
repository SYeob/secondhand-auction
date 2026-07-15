"""마이페이지 사용자별 입찰 내역 UI 테스트."""

from datetime import datetime, timedelta, timezone

import pytest

from tests.data.test_data import FIRST_BID_AMOUNT, STARTING_PRICE, unique_title
from tests.pages.login_page import LoginPage
from tests.pages.my_page import MyPage


pytestmark = [pytest.mark.ui, pytest.mark.p1, pytest.mark.regression]


def test_bidder_sees_own_bid_product_in_my_page(
    driver,
    base_url,
    supabase_api,
    seller_account,
    bidder_a_account,
):
    """입찰자는 자신이 입찰한 상품을 마이페이지에서 조회한다."""
    seller = supabase_api.sign_in(seller_account)
    bidder = supabase_api.sign_in(bidder_a_account)
    product = supabase_api.create_product(
        seller,
        title=unique_title("QA-MYPAGE"),
        end_time=datetime.now(timezone.utc) + timedelta(minutes=5),
        starting_price=STARTING_PRICE,
    )
    supabase_api.place_bid(bidder, product["id"], FIRST_BID_AMOUNT)

    try:
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        login_page.login(bidder_a_account.email, bidder_a_account.password)
        login_page.wait_for_login_success()

        my_page = MyPage(driver, base_url)
        my_page.open_my_page()
        my_page.wait_for_bid_product(product["title"])
    finally:
        supabase_api.delete_product(seller, product["id"])
