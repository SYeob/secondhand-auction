"""환경 변수 기반 테스트 설정."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class AccountCredentials:
    email: str
    # pytest가 fixture 지역 변수를 출력하더라도 비밀번호는 repr에 포함하지 않는다.
    password: str = field(repr=False)


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


def get_supabase_url() -> str:
    """Supabase 프로젝트 URL을 반환한다."""
    return _required_env("VITE_SUPABASE_URL").rstrip("/")


def get_supabase_key() -> str:
    """Supabase 공개(anon/publishable) 키를 반환한다."""
    return _required_env("VITE_SUPABASE_PUBLISHABLE_KEY")


def get_test_account(prefix: str) -> AccountCredentials:
    """TEST_SELLER 등 역할 접두사로 테스트 계정을 반환한다."""
    return AccountCredentials(
        email=_required_env(f"{prefix}_EMAIL").strip(),
        password=_required_env(f"{prefix}_PASSWORD"),
    )


def _required_env(name: str) -> str:
    value = os.getenv(name, "")
    if not value:
        raise ValueError(f"필수 환경 변수가 설정되지 않았습니다: {name}")
    return value
