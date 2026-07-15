"""마이페이지 입찰 및 좋아요 목록 Page Object."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.pages.base_page import BasePage


class MyPage(BasePage):
    MY_PAGE_PATH = "/mypage"
    LIKES_TAB = (By.XPATH, "//*[@role='tab' and normalize-space()='좋아요한 상품']")

    def open_my_page(self) -> None:
        self.open(self.MY_PAGE_PATH)
        self.wait_until_visible((By.XPATH, "//h3[normalize-space()='마이페이지']"))

    def wait_for_bid_product(self, title: str) -> None:
        """기본 응찰 상품 탭에 지정한 상품이 표시되는지 확인한다."""
        self.wait_until_visible(self._product_title(title))

    def open_likes_tab(self) -> None:
        """좋아요한 상품 탭을 연다."""
        self.wait_until_clickable(self.LIKES_TAB).click()

    def wait_for_liked_product(self, title: str) -> None:
        self.wait_until_visible(self._product_title(title))

    def open_product(self, title: str) -> None:
        self.wait_until_clickable(self._product_title(title)).click()

    def wait_for_product_absent(self, title: str) -> bool:
        return self.wait.until(EC.invisibility_of_element_located(self._product_title(title)))

    @classmethod
    def _product_title(cls, title: str) -> tuple[str, str]:
        return (By.XPATH, f"//h3[normalize-space()={cls._xpath_literal(title)}]")

    @staticmethod
    def _xpath_literal(value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"
