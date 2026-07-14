"""환경 변수 기반 테스트 설정."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def get_base_url() -> str:
    """테스트 대상 서비스의 기본 URL을 반환한다."""
    return os.getenv("BASE_URL", "http://127.0.0.1:8080").rstrip("/")


def is_headless() -> bool:
    """HEADLESS 환경 변수를 bool 값으로 변환한다."""
    return os.getenv("HEADLESS", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }
