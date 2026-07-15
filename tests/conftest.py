"""pytest 공통 fixture와 실패 증적 저장 설정."""

from __future__ import annotations

from datetime import datetime
from html import escape
import inspect
from pathlib import Path
import re

import pytest
from pytest_metadata.plugin import metadata_key
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from tests.utils.config import (
    get_base_url,
    get_supabase_key,
    get_supabase_url,
    get_test_account,
    is_headless,
)
from tests.utils.supabase_api import SupabaseApi


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"


def _safe_filename(value: str) -> str:
    """파일명으로 사용할 수 없는 문자를 치환한다."""
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value)


def pytest_configure(config: pytest.Config) -> None:
    """HTML 리포트 환경 정보를 포트폴리오 목적에 맞게 한국어화한다."""
    metadata = config.stash[metadata_key]
    key_translations = {
        "Python": "Python 버전",
        "Platform": "실행 플랫폼",
        "Packages": "설치 패키지",
        "Plugins": "pytest 플러그인",
    }

    for original, translated in key_translations.items():
        if original in metadata:
            metadata[translated] = metadata.pop(original)

    metadata["프로젝트"] = "Pa-Bi Auction QA Automation Portfolio"
    metadata["테스트 대상"] = get_base_url()


def pytest_html_report_title(report) -> None:
    """브라우저 탭과 본문에 표시되는 보고서 제목을 지정한다."""
    report.title = "Pa-Bi Auction QA 자동화 테스트 보고서"


def pytest_html_results_summary(prefix, summary, postfix, session) -> None:
    """실행 목적 안내와 pytest-html 기본 문구의 한국어화를 추가한다."""
    prefix.append(
        """
        <section class="qa-report-intro">
          <div>
            <span class="qa-report-badge">위험 기반 회귀 테스트</span>
            <p>입찰·경매 종료·낙찰·개인정보 권한을 중심으로 UI와 API를 검증합니다.</p>
          </div>
          <div class="qa-report-scope">Selenium UI · Supabase API · pytest</div>
        </section>
        <script>
          window.addEventListener("DOMContentLoaded", () => {
            document.documentElement.lang = "ko";

            const setText = (selector, value) => {
              const element = document.querySelector(selector);
              if (element) element.textContent = value;
            };

            setText("#environment-header h2", "테스트 환경");
            setText(".summary__data > h2", "실행 요약");
            setText("p.filter", "체크박스를 선택하여 결과를 필터링할 수 있습니다.");
            setText("#show_all_details", "모든 상세 결과 펼치기");
            setText("#hide_all_details", "모든 상세 결과 접기");

            const generated = document.querySelector("body > p");
            if (generated) {
              generated.innerHTML = generated.innerHTML
                .replace("Report generated on ", "보고서 생성: ")
                .replace(" at ", " ")
                .replace(" by ", " · 생성 도구: ");
            }

            const noResultTemplate = document.querySelector(
              "#template_results-table__body--empty"
            );
            const noResultCell = noResultTemplate?.content.querySelector("td");
            if (noResultCell) {
              noResultCell.textContent = "조건에 맞는 결과가 없습니다. 필터를 확인해주세요.";
            }

            const labels = {
              passed: "통과",
              failed: "실패",
              error: "오류",
              skipped: "건너뜀",
              xfailed: "알려진 결함",
              xpassed: "예상 외 통과",
              rerun: "재실행",
            };

            document.querySelectorAll(".filters span").forEach((element) => {
              const outcome = Object.keys(labels).find((name) =>
                element.classList.contains(name)
              );
              const count = element.textContent.match(/\\d+/)?.[0];
              if (outcome && count) {
                element.textContent = `${count} ${labels[outcome]}`;
              }
            });

            const runCount = document.querySelector(".run-count");
            if (runCount) {
              runCount.textContent = runCount.textContent.replace(
                /^(\\d+) tests? took (.+)$/,
                "총 $1개 테스트 · 소요 시간 $2"
              );
            }

            const translateResultCells = () => {
              document.querySelectorAll("#results-table td.col-result").forEach((cell) => {
                const key = cell.textContent.trim().toLowerCase();
                if (labels[key]) cell.textContent = labels[key];
              });
            };

            translateResultCells();
            const resultsTable = document.querySelector("#results-table");
            if (resultsTable) {
              new MutationObserver(translateResultCells).observe(resultsTable, {
                childList: true,
                subtree: true,
              });
            }
          });
        </script>
        """
    )


def pytest_html_results_table_header(cells) -> None:
    """결과 표 컬럼을 한국어로 표시하고 검증 목적 컬럼을 추가한다."""
    translations = {
        ">Result<": ">결과<",
        ">Test<": ">테스트 ID<",
        ">Duration<": ">소요 시간<",
        ">Links<": ">첨부<",
    }
    for index, cell in enumerate(cells):
        for original, translated in translations.items():
            cell = cell.replace(original, translated)
        cells[index] = cell
    cells.insert(2, '<th class="qa-purpose">검증 목적</th>')


def pytest_html_results_table_row(report, cells) -> None:
    """테스트 함수의 한글 설명을 검증 목적 컬럼에 추가한다."""
    description = escape(getattr(report, "description", "-") or "-")
    cells.insert(2, f'<td class="col-purpose">{description}</td>')


def pytest_html_results_table_html(report, data) -> None:
    """상세 결과의 기본 로그 안내 문구를 한국어로 표시한다."""
    for index, content in enumerate(data):
        data[index] = content.replace(
            "No log output captured.",
            "캡처된 로그가 없습니다.",
        )


@pytest.fixture(scope="session")
def base_url() -> str:
    """테스트 세션에서 공통으로 사용할 기본 URL."""
    return get_base_url()


@pytest.fixture(scope="session")
def supabase_api() -> SupabaseApi:
    """API 검증과 테스트 데이터 정리에 사용할 Supabase 클라이언트."""
    return SupabaseApi(get_supabase_url(), get_supabase_key())


@pytest.fixture(scope="session")
def seller_account():
    return get_test_account("TEST_SELLER")


@pytest.fixture(scope="session")
def bidder_a_account():
    return get_test_account("TEST_BIDDER_A")


@pytest.fixture(scope="session")
def bidder_b_account():
    return get_test_account("TEST_BIDDER_B")


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

    # 테스트 흐름을 가리는 Chrome 비밀번호 저장 및 유출 경고 UI를 비활성화한다.
    # 이 설정은 WebDriver가 생성한 임시 Chrome 프로필에만 적용된다.
    password_manager_prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    }
    options.add_experimental_option("prefs", password_manager_prefs)

    # Selenium 4.6 이상에서는 Selenium Manager가 적합한 드라이버를 자동 관리한다.
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(30)

    yield browser

    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """리포트 설명을 추가하고 UI 테스트 실패 시 화면을 저장한다."""
    outcome = yield
    report = outcome.get_result()
    report.description = inspect.getdoc(item.function) or "검증 목적 미작성"

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
