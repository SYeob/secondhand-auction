"""pytest 공통 fixture와 실패 증적 저장 설정."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from tests.utils.config import get_base_url, is_headless


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"


def _safe_filename(value: str) -> str:
    """파일명으로 사용할 수 없는 문자를 치환한다."""
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value)


@pytest.fixture(scope="session")
def base_url() -> str:
    """테스트 세션에서 공통으로 사용할 기본 URL."""
    return get_base_url()


@pytest.fixture
def driver() -> WebDriver:
    """각 UI 테스트마다 독립적인 Chrome WebDriver를 제공한다."""
    options = Options()

    if is_headless():
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-default-browser-check")

    # Selenium 4.6 이상에서는 Selenium Manager가 적합한 드라이버를 자동 관리한다.
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(30)

    yield browser

    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """UI 테스트 실패 시 screenshots 폴더에 화면을 저장한다."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    browser = item.funcargs.get("driver")
    if browser is None:
        return

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = _safe_filename(item.nodeid)
    screenshot_path = SCREENSHOT_DIR / f"{timestamp}_{test_name}.png"

    try:
        browser.save_screenshot(str(screenshot_path))
        print(f"\n실패 스크린샷 저장: {screenshot_path}")
    except Exception as exc:
        print(f"\n스크린샷 저장 실패: {exc}")
