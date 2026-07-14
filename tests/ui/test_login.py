"""Pa-Bi Auction 로그인 UI 테스트."""

import os
from urllib.parse import urlparse

import pytest

from tests.pages.login_page import LoginPage


LOGIN_ERROR_MESSAGE = "이메일 또는 비밀번호가 올바르지 않습니다."


def _get_test_credentials() -> tuple[str, str]:
    """환경 변수에서 테스트 계정을 읽고 누락 여부를 확인한다."""
    email = os.getenv("TEST_USER_EMAIL", "").strip()
    password = os.getenv("TEST_USER_PASSWORD", "")

    missing_variables = [
        name
        for name, value in (
            ("TEST_USER_EMAIL", email),
            ("TEST_USER_PASSWORD", password),
        )
        if not value
    ]
    if missing_variables:
        pytest.fail(
            "로그인 테스트 환경 변수가 설정되지 않았습니다: "
            + ", ".join(missing_variables),
            pytrace=False,
        )

    return email, password


@pytest.mark.ui
@pytest.mark.regression
def test_login_succeeds_with_valid_credentials(driver, base_url):
    """유효한 계정으로 로그인하면 홈 화면에 로그인 상태가 표시된다."""
    email, password = _get_test_credentials()
    page = LoginPage(driver, base_url)

    page.open_login()
    page.login(email, password)
    page.wait_for_login_success()

    assert driver.current_url.rstrip("/") == base_url.rstrip("/")


@pytest.mark.ui
@pytest.mark.regression
def test_login_fails_with_invalid_password(driver, base_url):
    """등록된 이메일에 잘못된 비밀번호를 입력하면 오류가 표시된다."""
    email, password = _get_test_credentials()
    invalid_password = f"{password}_invalid"
    page = LoginPage(driver, base_url)

    page.open_login()
    page.login(email, invalid_password)

    assert page.get_login_error_message() == LOGIN_ERROR_MESSAGE


@pytest.mark.ui
@pytest.mark.regression
def test_unauthenticated_user_is_redirected_from_my_page(driver, base_url):
    """비로그인 사용자가 마이페이지에 직접 접근하면 로그인 화면으로 이동한다."""
    page = LoginPage(driver, base_url)

    page.open_my_page()
    page.wait_for_auth_redirect()

    assert urlparse(driver.current_url).path == LoginPage.LOGIN_PATH
