"""Supabase 입찰 REST API 테스트."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from tests.data.test_data import (
    FIRST_BID_AMOUNT,
    SECOND_BID_AMOUNT,
    STARTING_PRICE,
    unique_title,
)


pytestmark = [pytest.mark.api, pytest.mark.p0, pytest.mark.regression]


@pytest.fixture
def active_auction(
    supabase_api,
    seller_account,
    bidder_a_account,
    bidder_b_account,
):
    """API 입찰 테스트용 진행 중 경매와 세 계정 세션을 제공한다."""
    seller = supabase_api.sign_in(seller_account)
    bidder_a = supabase_api.sign_in(bidder_a_account)
    bidder_b = supabase_api.sign_in(bidder_b_account)
    product = supabase_api.create_product(
        seller,
        title=unique_title("QA-API-BID"),
        end_time=datetime.now(timezone.utc) + timedelta(minutes=5),
        starting_price=STARTING_PRICE,
    )

    try:
        yield {
            "seller": seller,
            "bidder_a": bidder_a,
            "bidder_b": bidder_b,
            "product": product,
        }
    finally:
        supabase_api.delete_product(seller, product["id"])


def test_higher_bid_updates_current_price(supabase_api, active_auction):
    """현재가보다 높은 입찰은 저장되고 상품 현재가를 갱신한다."""
    product_id = active_auction["product"]["id"]

    bid = supabase_api.place_bid(
        active_auction["bidder_a"],
        product_id,
        FIRST_BID_AMOUNT,
    )
    product = supabase_api.get_product(product_id)

    assert bid["bid_amount"] == FIRST_BID_AMOUNT
    assert product["current_price"] == FIRST_BID_AMOUNT


@pytest.mark.parametrize(
    "invalid_amount",
    [STARTING_PRICE, STARTING_PRICE - 1_000],
    ids=["equal", "lower"],
)
def test_api_rejects_bid_at_or_below_current_price(
    supabase_api,
    active_auction,
    invalid_amount,
):
    """서버는 UI를 우회한 현재가 이하 입찰도 거부한다."""
    product_id = active_auction["product"]["id"]

    response = supabase_api.bid_response(
        active_auction["bidder_a"],
        product_id,
        invalid_amount,
    )

    assert response.status_code in {400, 409, 422}
    assert supabase_api.get_product(product_id)["current_price"] == STARTING_PRICE
    assert supabase_api.get_bids(product_id) == []


def test_highest_bidder_and_price_after_multiple_bids(
    supabase_api,
    active_auction,
):
    """두 사용자의 순차 입찰 후 더 높은 입찰자가 최고 입찰자가 된다."""
    product_id = active_auction["product"]["id"]

    supabase_api.place_bid(
        active_auction["bidder_a"], product_id, FIRST_BID_AMOUNT
    )
    supabase_api.place_bid(
        active_auction["bidder_b"], product_id, SECOND_BID_AMOUNT
    )

    product = supabase_api.get_product(product_id)
    bids = supabase_api.get_bids(product_id)

    assert product["current_price"] == SECOND_BID_AMOUNT
    assert bids[0]["bid_amount"] == SECOND_BID_AMOUNT
    assert bids[0]["user_id"] == active_auction["bidder_b"].user_id


def test_higher_amount_wins_when_two_users_bid_concurrently(
    supabase_api,
    active_auction,
):
    """동시 입찰 요청의 처리 순서와 무관하게 최고 금액이 현재가가 된다."""
    product_id = active_auction["product"]["id"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(
            supabase_api.bid_response,
            active_auction["bidder_a"],
            product_id,
            FIRST_BID_AMOUNT,
        )
        future_b = executor.submit(
            supabase_api.bid_response,
            active_auction["bidder_b"],
            product_id,
            SECOND_BID_AMOUNT,
        )
        response_a = future_a.result()
        response_b = future_b.result()

    product = supabase_api.get_product(product_id)
    bids = supabase_api.get_bids(product_id)

    assert response_b.status_code == 201
    assert response_a.status_code in {201, 400, 409, 422}
    assert product["current_price"] == SECOND_BID_AMOUNT
    assert bids[0]["bid_amount"] == SECOND_BID_AMOUNT
    assert bids[0]["user_id"] == active_auction["bidder_b"].user_id
