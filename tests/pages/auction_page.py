"""경매 상품 상세 및 입찰 화면에서 사용하는 요소와 동작."""

from __future__ import annotations

from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

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
    WINNER_CONTACT_TRIGGER = (
        By.XPATH,
        "//*[@aria-haspopup='dialog']"
        "[.//*[contains(normalize-space(), '축하드립니다. 낙찰되었습니다')]]",
    )

    WINNER_CONTACT_DIALOG = (
        By.XPATH,
        "//*[@role='dialog']",
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

    def wait_for_bid_price_error(self, current_price: int) -> None:
        """현재가 이하 입찰에 대한 오류 문구를 확인한다."""
        message = (
            f"현재가({current_price:,}원)보다 높은 금액을 입력해주세요."
        )
        self.wait_until_visible(
            (By.XPATH, f"//*[normalize-space()='{message}']")
        )

    def wait_for_current_price(self, amount: int) -> None:
        """상품 상세 화면의 현재가가 지정한 금액인지 확인한다."""
        formatted_amount = f"{amount:,}원"
        self.wait_until_visible(
            (
                By.XPATH,
                "//span[normalize-space()='현재가']"
                f"/following-sibling::span[normalize-space()='{formatted_amount}']",
            )
        )

    def wait_for_auth_redirect(self) -> None:
        """비로그인 입찰 후 로그인 화면 이동을 확인한다."""
        self.wait.until(
            lambda driver: urlparse(driver.current_url).path == "/auth"
        )
        self.wait_until_visible((By.ID, "login-email"))

    def dismiss_winner_notification_if_present(self) -> None:
        """이전 낙찰 알림이 상세 화면을 가리면 닫는다."""
        try:
            button = WebDriverWait(self.driver, 2).until(
                lambda driver: driver.find_element(
                    By.XPATH, "//button[normalize-space()='나중에 보기']"
                )
            )
            if button.is_displayed():
                button.click()
        except TimeoutException:
            pass

    def wait_for_auction_ended(self) -> None:
        """상세 화면이 경매 종료 상태이고 입찰 버튼이 비활성화됐는지 확인한다."""
        button = self.wait_until_visible(
            (By.XPATH, "//button[normalize-space()='경매 종료']")
        )
        self.wait.until(lambda _driver: not button.is_enabled())

    def open_winner_contact(self) -> None:
        """낙찰 안내 카드를 클릭하고 연락처 다이얼로그가 열렸는지 확인한다."""
        trigger = self.wait_until_clickable(
            self.WINNER_CONTACT_TRIGGER
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            trigger,
        )
        trigger.click()

        self.wait_until_visible(
            self.WINNER_CONTACT_DIALOG
        )

    def wait_for_seller_phone(self, phone: str) -> None:
        """낙찰자 연락처 다이얼로그에 예상 전화번호가 표시되는지 확인한다."""
        phone_literal = self._xpath_literal(phone)

        self.wait_until_visible(
            (
                By.XPATH,
                "//*[@role='dialog']"
                f"//*[normalize-space()={phone_literal}]",
            )
        )

    def wait_for_loser_message(self) -> None:
        """비낙찰자에게 낙찰 실패 안내가 표시되는지 확인한다."""
        self.wait_until_visible(
            (
                By.XPATH,
                "//*[contains(normalize-space(), '아쉽게도 낙찰받지 못하셨습니다')]",
            )
        )

    def toggle_like(self, title: str) -> None:
        """상품 이미지 우측 상단의 좋아요 버튼을 누른다."""
        locator = (
            By.XPATH,
            f"//img[@alt={self._xpath_literal(title)}]/following-sibling::button[1]",
        )
        self.wait_until_clickable(locator).click()

    def wait_for_like_added(self) -> None:
        self.wait_until_visible(
            (By.XPATH, "//*[normalize-space()='좋아요가 추가되었습니다.']")
        )

    def wait_for_like_removed(self) -> None:
        self.wait_until_visible(
            (By.XPATH, "//*[normalize-space()='좋아요가 취소되었습니다.']")
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
