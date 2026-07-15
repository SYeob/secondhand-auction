"""좋아요 추가, 목록 조회 및 해제 UI 테스트."""

from datetime import datetime, timedelta, timezone

import pytest

from tests.data.test_data import STARTING_PRICE, unique_title
from tests.pages.auction_page import AuctionPage
from tests.pages.login_page import LoginPage
from tests.pages.my_page import MyPage


pytestmark = [pytest.mark.ui, pytest.mark.p2, pytest.mark.regression]


def test_user_can_add_view_and_remove_like(
    driver,
    base_url,
    supabase_api,
    seller_account,
    bidder_a_account,
):
    """좋아요 상태와 마이페이지 관심 목록이 추가·해제 결과와 일치한다."""
    seller = supabase_api.sign_in(seller_account)
    product = supabase_api.create_product(
        seller,
        title=unique_title("QA-LIKE"),
        end_time=datetime.now(timezone.utc) + timedelta(minutes=5),
        starting_price=STARTING_PRICE,
    )

    try:
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        login_page.login(bidder_a_account.email, bidder_a_account.password)
        login_page.wait_for_login_success()

        auction_page = AuctionPage(driver, base_url)
        driver.get(f"{base_url}/product/{product['id']}")
        auction_page.wait_for_product(product["title"])
        auction_page.toggle_like(product["title"])
        auction_page.wait_for_like_added()

        my_page = MyPage(driver, base_url)
        my_page.open_my_page()
        my_page.open_likes_tab()
        my_page.wait_for_liked_product(product["title"])
        my_page.open_product(product["title"])

        auction_page.wait_for_product(product["title"])
        auction_page.toggle_like(product["title"])
        auction_page.wait_for_like_removed()

        my_page.open_my_page()
        my_page.open_likes_tab()
        assert my_page.wait_for_product_absent(product["title"])
    finally:
        supabase_api.delete_product(seller, product["id"])
