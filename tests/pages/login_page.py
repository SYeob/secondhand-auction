"""Pa-Bi 로그인 화면에서 사용하는 요소와 동작."""

from __future__ import annotations

from urllib.parse import urlparse

from selenium.webdriver.common.by import By

from tests.pages.base_page import BasePage


class LoginPage(BasePage):
    """로그인과 인증 필요 페이지 이동을 담당하는 Page Object."""

    LOGIN_PATH = "/auth"
    MY_PAGE_PATH = "/mypage"

    EMAIL_INPUT = (By.ID, "login-email")
    PASSWORD_INPUT = (By.ID, "login-password")
    LOGIN_BUTTON = (
        By.XPATH,
        "//form[.//*[@id='login-email']]//button[@type='submit']",
    )
    LOGIN_ERROR_TOAST = (
        By.XPATH,
        "//*[normalize-space()='이메일 또는 비밀번호가 올바르지 않습니다.']",
    )
    LOGOUT_BUTTON = (
        By.XPATH,
        "//button[.//span[normalize-space()='로그아웃']]",
    )
    LOGIN_NAV_BUTTON = (
        By.XPATH,
        "//button[.//span[normalize-space()='로그인']]",
    )

    def open_login(self) -> None:
        """로그인 화면을 연다."""
        self.open(self.LOGIN_PATH)
        self.wait_until_visible(self.EMAIL_INPUT)

    def login(self, email: str, password: str) -> None:
        """이메일과 비밀번호를 입력하고 로그인 버튼을 누른다."""
        email_input = self.wait_until_visible(self.EMAIL_INPUT)
        password_input = self.wait_until_visible(self.PASSWORD_INPUT)

        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)
        self.wait_until_clickable(self.LOGIN_BUTTON).click()

    def wait_for_login_success(self) -> None:
        """홈 화면 이동과 로그아웃 버튼 표시를 기다린다."""
        self.wait.until(lambda driver: urlparse(driver.current_url).path == "/")
        self.wait_until_visible(self.LOGOUT_BUTTON)

    def get_login_error_message(self) -> str:
        """로그인 실패 토스트의 문구를 반환한다."""
        return self.wait_until_visible(self.LOGIN_ERROR_TOAST).text.strip()

    def logout(self) -> None:
        """현재 계정에서 로그아웃하고 비로그인 홈 화면을 확인한다."""
        self.wait_until_clickable(self.LOGOUT_BUTTON).click()
        self.wait.until(lambda driver: urlparse(driver.current_url).path == "/")
        self.wait_until_visible(self.LOGIN_NAV_BUTTON)

    def reset_auth_session(self) -> None:
        """테스트 정리를 위해 브라우저의 Supabase 인증 세션을 제거한다."""
        self.open("/")
        self.driver.execute_script(
            "window.localStorage.clear(); window.sessionStorage.clear();"
        )
        self.driver.refresh()
        self.wait_until_visible(self.LOGIN_NAV_BUTTON)

    def open_my_page(self) -> None:
        """주소를 통해 마이페이지에 직접 접근한다."""
        self.open(self.MY_PAGE_PATH)

    def wait_for_auth_redirect(self) -> None:
        """비로그인 사용자가 로그인 화면으로 이동할 때까지 기다린다."""
        self.wait.until(
            lambda driver: urlparse(driver.current_url).path == self.LOGIN_PATH
        )
        self.wait_until_visible(self.EMAIL_INPUT)
