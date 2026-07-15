"""경매 종료, 낙찰자 및 개인정보 권한 API 테스트."""

from datetime import datetime, timedelta, timezone

import pytest

from tests.data.test_data import (
    FIRST_BID_AMOUNT,
    SECOND_BID_AMOUNT,
    SELLER_PHONE,
    STARTING_PRICE,
    unique_title,
)


pytestmark = [pytest.mark.api, pytest.mark.p0, pytest.mark.regression]


@pytest.fixture(scope="module")
def ended_auction(
    supabase_api,
    seller_account,
    bidder_a_account,
    bidder_b_account,
):
    """두 입찰이 존재하고 종료 시간이 지난 경매를 제공한다."""
    seller = supabase_api.sign_in(seller_account)
    bidder_a = supabase_api.sign_in(bidder_a_account)
    bidder_b = supabase_api.sign_in(bidder_b_account)
    product = supabase_api.create_product(
        seller,
        title=unique_title("QA-API-CLOSE"),
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
            datetime.now(timezone.utc) - timedelta(seconds=1),
        )

        yield {
            "seller": seller,
            "bidder_a": bidder_a,
            "bidder_b": bidder_b,
            "product": product,
        }
    finally:
        supabase_api.delete_product(seller, product["id"])


def test_api_rejects_bid_after_auction_end(supabase_api, ended_auction):
    """종료 이후 입찰은 서버에서 거부되고 낙찰 가격이 바뀌지 않는다."""
    product_id = ended_auction["product"]["id"]

    response = supabase_api.bid_response(
        ended_auction["bidder_a"],
        product_id,
        SECOND_BID_AMOUNT + 5_000,
    )

    assert response.status_code in {400, 409, 422}
    assert supabase_api.get_product(product_id)["current_price"] == SECOND_BID_AMOUNT


def test_highest_bidder_is_winner_after_end(supabase_api, ended_auction):
    """종료 시점의 최고 금액과 최고 입찰자가 낙찰 결과가 된다."""
    product_id = ended_auction["product"]["id"]

    product = supabase_api.get_product(product_id)
    highest_bid = supabase_api.get_bids(product_id)[0]

    assert product["current_price"] == SECOND_BID_AMOUNT
    assert highest_bid["bid_amount"] == SECOND_BID_AMOUNT
    assert highest_bid["user_id"] == ended_auction["bidder_b"].user_id


def test_only_winner_can_read_seller_contact(supabase_api, ended_auction):
    """낙찰자는 연락처를 조회하지만 비낙찰자와 비로그인 사용자는 거부된다."""
    product_id = ended_auction["product"]["id"]

    winner_response = supabase_api.seller_contact_response(
        ended_auction["bidder_b"], product_id
    )
    loser_response = supabase_api.seller_contact_response(
        ended_auction["bidder_a"], product_id
    )
    anonymous_response = supabase_api.seller_contact_response(None, product_id)

    assert winner_response.status_code == 200
    assert winner_response.json()[0]["seller_phone"] == SELLER_PHONE
    assert loser_response.status_code in {400, 401, 403}
    assert anonymous_response.status_code in {401, 403, 404}


@pytest.mark.xfail(
    reason="DEF-002: products 테이블의 seller_phone 컬럼이 익명 REST 조회에 노출됨",
    strict=True,
)
def test_anonymous_cannot_select_seller_phone_column(supabase_api, ended_auction):
    """익명 사용자는 RPC를 우회해 seller_phone 컬럼을 직접 조회할 수 없어야 한다."""
    response = supabase_api.product_columns_response(
        ended_auction["product"]["id"],
        "seller_phone",
    )

    assert response.status_code in {401, 403}
