"""경매 상품 상세 및 입찰 화면에서 사용하는 요소와 동작."""

from __future__ import annotations

from selenium.webdriver.common.by import By

from tests.pages.base_page import BasePage


class AuctionPage(BasePage):
    """상품 상세 화면의 입찰 동작과 결과 확인을 담당한다."""

    BID_DIALOG_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='응찰하기']",
    )
    BID_AMOUNT_INPUT = (By.ID, "bid-amount")
    BID_CONFIRM_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='응찰 확인']",
    )

    def wait_for_product(self, title: str) -> None:
        """지정한 상품의 상세 화면이 표시될 때까지 기다린다."""
        self.wait_until_visible(
            (By.XPATH, f"//h1[normalize-space()={self._xpath_literal(title)}]")
        )

    def place_bid(self, amount: int) -> None:
        """입찰 다이얼로그에서 금액을 입력하고 확정한다."""
        self.wait_until_clickable(self.BID_DIALOG_BUTTON).click()
        amount_input = self.wait_until_visible(self.BID_AMOUNT_INPUT)
        amount_input.clear()
        amount_input.send_keys(str(amount))
        self.wait_until_clickable(self.BID_CONFIRM_BUTTON).click()

    def wait_for_bid_result(self, amount: int) -> None:
        """입찰 완료 문구와 변경된 현재가를 확인한다."""
        formatted_amount = f"{amount:,}원"
        self.wait_until_visible(
            (
                By.XPATH,
                f"//*[normalize-space()='{formatted_amount}에 응찰하셨습니다.']",
            )
        )
        self.wait_until_visible(
            (
                By.XPATH,
                "//span[normalize-space()='현재가']"
                f"/following-sibling::span[normalize-space()='{formatted_amount}']",
            )
        )

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """동적으로 생성한 문자열을 XPath 문자열 리터럴로 변환한다."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"
