"""모든 Page Object에서 공통으로 사용하는 기본 동작."""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    DEFAULT_TIMEOUT = 10

    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

    def open(self, path: str = "") -> None:
        """기본 URL과 상대 경로를 조합하여 페이지를 연다."""
        normalized_path = path if path.startswith("/") else f"/{path}" if path else ""
        self.driver.get(f"{self.base_url}{normalized_path}")

    def wait_until_visible(self, locator: tuple[str, str]):
        """요소가 화면에 표시될 때까지 기다린 뒤 반환한다."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_until_clickable(self, locator: tuple[str, str]):
        """요소를 클릭할 수 있을 때까지 기다린 뒤 반환한다."""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_until_url_contains(self, text: str) -> None:
        """현재 URL에 특정 문자열이 포함될 때까지 기다린다."""
        self.wait.until(EC.url_contains(text))
