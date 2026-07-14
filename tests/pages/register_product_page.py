"""경매 상품 등록 화면에서 사용하는 요소와 동작."""

from __future__ import annotations

from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.pages.base_page import BasePage


class RegisterProductPage(BasePage):
    """상품 등록, 등록 결과 확인 및 테스트 상품 삭제를 담당한다."""

    REGISTER_PATH = "/register"

    TITLE_INPUT = (By.ID, "title")
    DESCRIPTION_INPUT = (By.ID, "description")
    LOCATION_INPUT = (By.ID, "location")
    STARTING_PRICE_INPUT = (By.ID, "startingPrice")
    END_TIME_INPUT = (By.ID, "endTime")
    REGISTER_BUTTON = (
        By.XPATH,
        "//button[@type='submit' and normalize-space()='상품 등록하기']",
    )
    DELETE_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(), '삭제하기')]",
    )
    CONFIRM_DELETE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='삭제']",
    )

    def open_register(self) -> None:
        """상품 등록 화면을 연다."""
        self.open(self.REGISTER_PATH)
        self.wait_until_visible(self.TITLE_INPUT)

    def register_product(
        self,
        *,
        title: str,
        description: str,
        location: str,
        starting_price: int,
        end_time: str,
    ) -> None:
        """필수 상품 정보를 입력하고 등록한다."""
        self.wait_until_visible(self.TITLE_INPUT).send_keys(title)
        self.wait_until_visible(self.DESCRIPTION_INPUT).send_keys(description)
        self.wait_until_visible(self.LOCATION_INPUT).send_keys(location)
        self.wait_until_visible(self.STARTING_PRICE_INPUT).send_keys(
            str(starting_price)
        )
        self._set_datetime_local(end_time)
        self.wait_until_clickable(self.REGISTER_BUTTON).click()

    def wait_for_registered_product(self, title: str) -> None:
        """홈 화면 이동 후 등록한 상품명이 표시될 때까지 기다린다."""
        self.wait.until(lambda driver: urlparse(driver.current_url).path == "/")
        self.wait_until_visible(self._product_title(title))

    def open_product(self, title: str) -> None:
        """홈 화면에서 지정한 상품 카드를 연다."""
        self.wait_until_clickable(self._product_title(title)).click()
        self.wait.until(
            lambda driver: urlparse(driver.current_url).path.startswith("/product/")
        )
        self.wait_until_visible((By.XPATH, f"//h1[normalize-space()={self._xpath_literal(title)}]"))

    def delete_open_product(self) -> None:
        """현재 열린 본인 상품을 삭제하고 홈 화면 복귀를 확인한다."""
        self.wait_until_clickable(self.DELETE_BUTTON).click()
        self.wait_until_clickable(self.CONFIRM_DELETE_BUTTON).click()
        self.wait.until(lambda driver: urlparse(driver.current_url).path == "/")

    def is_product_absent(self, title: str) -> bool:
        """홈 화면에 지정한 상품명이 없는지 확인한다."""
        return self.wait.until(EC.invisibility_of_element_located(self._product_title(title)))

    def _set_datetime_local(self, value: str) -> None:
        """브라우저 표시 형식에 영향받지 않고 datetime-local 값을 입력한다."""
        element = self.wait_until_visible(self.END_TIME_INPUT)
        self.driver.execute_script(
            """
            const input = arguments[0];
            const value = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype,
                'value'
            ).set;
            setter.call(input, value);
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element,
            value,
        )

    @classmethod
    def _product_title(cls, title: str) -> tuple[str, str]:
        return (By.XPATH, f"//h3[normalize-space()={cls._xpath_literal(title)}]")

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """동적으로 생성한 문자열을 XPath 문자열 리터럴로 변환한다."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"
