"""테스트 데이터 준비와 API 검증에 사용하는 Supabase REST 클라이언트."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests
from requests import Response

from tests.utils.config import AccountCredentials


@dataclass(frozen=True)
class AuthSession:
    access_token: str
    user_id: str
    email: str


class SupabaseApi:
    """비밀번호를 저장하거나 출력하지 않는 최소 Supabase API 래퍼."""

    TIMEOUT = 15

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def auth_response(self, account: AccountCredentials) -> Response:
        return requests.post(
            f"{self.base_url}/auth/v1/token",
            params={"grant_type": "password"},
            headers={"apikey": self.api_key, "Content-Type": "application/json"},
            json={"email": account.email, "password": account.password},
            timeout=self.TIMEOUT,
        )

    def sign_in(self, account: AccountCredentials) -> AuthSession:
        response = self.auth_response(account)
        if response.status_code != 200:
            raise AssertionError(
                f"Supabase 로그인 실패: status={response.status_code}, body={response.text}"
            )
        body = response.json()
        return AuthSession(
            access_token=body["access_token"],
            user_id=body["user"]["id"],
            email=body["user"]["email"],
        )

    def create_product(
        self,
        session: AuthSession,
        *,
        title: str,
        end_time: datetime,
        starting_price: int = 10_000,
        seller_phone: str = "010-1234-5678",
    ) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/rest/v1/products",
            params={
                "select": (
                    "id,title,current_price,end_time,seller_id,location,"
                    "image_url,category"
                )
            },
            headers=self._headers(session, prefer="return=representation"),
            json={
                "title": title,
                "description": "API 자동화 테스트용 상품입니다.",
                "location": "서울시 강남구",
                "category": "기타",
                "starting_price": starting_price,
                "current_price": starting_price,
                "image_url": "https://example.com/qa-api-test-image.jpg",
                "end_time": end_time.isoformat(),
                "seller_id": session.user_id,
                "seller_phone": seller_phone,
            },
            timeout=self.TIMEOUT,
        )
        self._assert_status(response, {201}, "상품 생성")
        return response.json()[0]

    def delete_product(self, session: AuthSession, product_id: str) -> None:
        response = requests.delete(
            f"{self.base_url}/rest/v1/products",
            params={"id": f"eq.{product_id}"},
            headers=self._headers(session),
            timeout=self.TIMEOUT,
        )
        self._assert_status(response, {200, 204}, "상품 삭제")

    def update_product_end_time(
        self,
        session: AuthSession,
        product_id: str,
        end_time: datetime,
    ) -> None:
        """판매자 권한으로 테스트 경매의 종료 시각을 변경한다."""
        response = requests.patch(
            f"{self.base_url}/rest/v1/products",
            params={"id": f"eq.{product_id}", "select": "id,end_time"},
            headers=self._headers(session, prefer="return=representation"),
            json={"end_time": end_time.isoformat()},
            timeout=self.TIMEOUT,
        )
        self._assert_status(response, {200}, "경매 종료 시각 변경")
        rows = response.json()
        if not rows or rows[0]["id"] != product_id:
            raise AssertionError(
                f"경매 종료 시각 변경 대상이 없습니다: {product_id}"
            )

    def bid_response(
        self,
        session: AuthSession,
        product_id: str,
        amount: int,
    ) -> Response:
        return requests.post(
            f"{self.base_url}/rest/v1/bids",
            params={"select": "id,product_id,user_id,bid_amount,created_at"},
            headers=self._headers(session, prefer="return=representation"),
            json={
                "product_id": product_id,
                "user_id": session.user_id,
                "bid_amount": amount,
            },
            timeout=self.TIMEOUT,
        )

    def place_bid(
        self,
        session: AuthSession,
        product_id: str,
        amount: int,
    ) -> dict[str, Any]:
        response = self.bid_response(session, product_id, amount)
        self._assert_status(response, {201}, "입찰 생성")
        return response.json()[0]

    def get_product(self, product_id: str) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/rest/v1/products",
            params={
                "id": f"eq.{product_id}",
                "select": "id,title,current_price,end_time,seller_id",
            },
            headers=self._headers(),
            timeout=self.TIMEOUT,
        )
        self._assert_status(response, {200}, "상품 조회")
        rows = response.json()
        if not rows:
            raise AssertionError(f"상품을 찾을 수 없습니다: {product_id}")
        return rows[0]

    def product_columns_response(
        self,
        product_id: str,
        select: str,
        session: AuthSession | None = None,
    ) -> Response:
        """컬럼 권한 자체를 검증하기 위한 원본 상품 조회 응답."""
        return requests.get(
            f"{self.base_url}/rest/v1/products",
            params={"id": f"eq.{product_id}", "select": select},
            headers=self._headers(session),
            timeout=self.TIMEOUT,
        )

    def get_bids(self, product_id: str) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/rest/v1/bids",
            params={
                "product_id": f"eq.{product_id}",
                "select": "id,user_id,bid_amount,created_at",
                "order": "bid_amount.desc,created_at.asc",
            },
            headers=self._headers(),
            timeout=self.TIMEOUT,
        )
        self._assert_status(response, {200}, "입찰 내역 조회")
        return response.json()

    def seller_contact_response(
        self,
        session: AuthSession | None,
        product_id: str,
    ) -> Response:
        return requests.post(
            f"{self.base_url}/rest/v1/rpc/get_seller_contact",
            headers=self._headers(session),
            json={"p_product_id": product_id},
            timeout=self.TIMEOUT,
        )

    def add_like(self, session: AuthSession, product_id: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/rest/v1/likes",
            params={"select": "id,user_id,product_id"},
            headers=self._headers(session, prefer="return=representation"),
            json={"user_id": session.user_id, "product_id": product_id},
            timeout=self.TIMEOUT,
        )
        self._assert_status(response, {201}, "좋아요 생성")
        return response.json()[0]

    def delete_like(self, session: AuthSession, product_id: str) -> None:
        response = requests.delete(
            f"{self.base_url}/rest/v1/likes",
            params={
                "user_id": f"eq.{session.user_id}",
                "product_id": f"eq.{product_id}",
            },
            headers=self._headers(session),
            timeout=self.TIMEOUT,
        )
        self._assert_status(response, {200, 204}, "좋아요 삭제")

    def _headers(
        self,
        session: AuthSession | None = None,
        *,
        prefer: str | None = None,
    ) -> dict[str, str]:
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        if session:
            headers["Authorization"] = f"Bearer {session.access_token}"
        if prefer:
            headers["Prefer"] = prefer
        return headers

    @staticmethod
    def _assert_status(response: Response, expected: set[int], action: str) -> None:
        if response.status_code not in expected:
            raise AssertionError(
                f"{action} 실패: status={response.status_code}, body={response.text}"
            )
