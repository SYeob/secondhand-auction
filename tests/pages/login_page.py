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

    def open_my_page(self) -> None:
        """주소를 통해 마이페이지에 직접 접근한다."""
        self.open(self.MY_PAGE_PATH)

    def wait_for_auth_redirect(self) -> None:
        """비로그인 사용자가 로그인 화면으로 이동할 때까지 기다린다."""
        self.wait.until(
            lambda driver: urlparse(driver.current_url).path == self.LOGIN_PATH
        )
        self.wait_until_visible(self.EMAIL_INPUT)
