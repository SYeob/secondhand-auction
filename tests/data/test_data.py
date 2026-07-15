"""민감정보를 제외한 공통 테스트 데이터."""

from __future__ import annotations

from datetime import datetime, timezone


STARTING_PRICE = 10_000
FIRST_BID_AMOUNT = 15_000
SECOND_BID_AMOUNT = 20_000
SELLER_PHONE = "010-1234-5678"


def unique_title(prefix: str) -> str:
    """병렬 실행에서도 충돌하지 않는 상품명을 생성한다."""
    return f"{prefix}-{datetime.now(timezone.utc):%Y%m%d%H%M%S%f}"
