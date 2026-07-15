"""Supabase 인증 API 테스트."""

import pytest

from tests.utils.config import AccountCredentials


pytestmark = [pytest.mark.api, pytest.mark.p1, pytest.mark.regression]


def test_auth_api_returns_session_for_valid_credentials(
    supabase_api,
    seller_account,
):
    """유효한 계정은 access token과 동일한 사용자 이메일을 반환한다."""
    response = supabase_api.auth_response(seller_account)

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user"]["email"].lower() == seller_account.email.lower()


def test_auth_api_rejects_invalid_password(supabase_api, seller_account):
    """등록된 이메일에 잘못된 비밀번호를 사용하면 인증이 거부된다."""
    invalid_account = AccountCredentials(
        email=seller_account.email,
        password=f"{seller_account.password}_invalid",
    )

    response = supabase_api.auth_response(invalid_account)

    assert response.status_code == 400
    assert "access_token" not in response.json()
