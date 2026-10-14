"""Xavfsizlik: initData validatsiyasi va JWT testlari."""

from __future__ import annotations

import time

import pytest

from app.core.security import (
    InitDataError,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_init_data,
)
from tests.conftest import TEST_BOT_TOKEN, make_init_data

USER = {"id": 555, "first_name": "Ali", "language_code": "uz"}


def test_valid_init_data():
    init_data = make_init_data(USER)
    parsed = verify_init_data(init_data)
    assert parsed["user"]["id"] == 555


def test_tampered_init_data_rejected():
    init_data = make_init_data(USER)
    tampered = init_data.replace("Ali", "Vali")
    with pytest.raises(InitDataError):
        verify_init_data(tampered)


def test_wrong_bot_token_rejected():
    init_data = make_init_data(USER, bot_token="999:OTHER_TOKEN")
    with pytest.raises(InitDataError):
        verify_init_data(init_data, bot_token=TEST_BOT_TOKEN)


def test_expired_init_data_rejected():
    old = int(time.time()) - 60 * 60 * 48  # 48 soat oldin
    init_data = make_init_data(USER, auth_date=old)
    with pytest.raises(InitDataError):
        verify_init_data(init_data, max_age=3600)


def test_empty_init_data_rejected():
    with pytest.raises(InitDataError):
        verify_init_data("")


def test_jwt_roundtrip():
    token = create_access_token("user-123")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_refresh_token_type():
    token = create_refresh_token("user-123")
    payload = decode_token(token)
    assert payload["type"] == "refresh"
