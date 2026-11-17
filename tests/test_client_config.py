# ============================================
#  tests/test_client_config.py - tests for env-based configuration
#  Verifies default resolution, env overrides, and invalid-int fallback
#  for API credentials, DC settings, and VibeClient construction.
# ============================================
import importlib

import pytest

from userapi import _config


def test_default_api_credentials():
    # With no env override, defaults are Vibe's public app credentials.
    api_id, api_hash = _config.get_api_credentials()
    assert api_id == _config.DEFAULT_API_ID
    assert api_hash == _config.DEFAULT_API_HASH


def test_default_dc_settings():
    host, port, dc_id = _config.get_dc_settings()
    assert host == "web.vibegram.chat"
    assert port == 443
    assert dc_id == 2


def test_api_credentials_env_override(monkeypatch):
    monkeypatch.setenv("VIBE_API_ID", "999")
    monkeypatch.setenv("VIBE_API_HASH", "deadbeef")
    api_id, api_hash = _config.get_api_credentials()
    assert api_id == 999
    assert api_hash == "deadbeef"


def test_dc_settings_env_override(monkeypatch):
    monkeypatch.setenv("VIBE_DC_HOST", "mirror.example.com")
    monkeypatch.setenv("VIBE_DC_PORT", "8443")
    monkeypatch.setenv("VIBE_DC_ID", "5")
    host, port, dc_id = _config.get_dc_settings()
    assert host == "mirror.example.com"
    assert port == 8443
    assert dc_id == 5


def test_invalid_int_falls_back_to_default(monkeypatch, capsys):
    monkeypatch.setenv("VIBE_DC_PORT", "not-a-number")
    _host, port, _dc_id = _config.get_dc_settings()
    assert port == _config.DEFAULT_DC_PORT
    captured = capsys.readouterr()
    assert "[_config] error" in captured.out


def test_empty_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("VIBE_API_ID", "")
    monkeypatch.setenv("VIBE_DC_PORT", "   ")
    api_id, _ = _config.get_api_credentials()
    _h, port, _d = _config.get_dc_settings()
    assert api_id == _config.DEFAULT_API_ID
    assert port == _config.DEFAULT_DC_PORT


def test_vibeclient_explicit_dc_override():
    from userapi.client import VibeClient
    c = VibeClient(dc_host="custom.host", dc_port=9000, dc_id=7)
    assert c._dc_host == "custom.host"
    assert c._dc_port == 9000
    assert c._dc_id == 7


def test_vibeclient_explicit_api_credentials():
    from userapi.client import VibeClient
    c = VibeClient(api_id=123, api_hash="abcdef")
    assert c._api_id == 123
    assert c._api_hash == "abcdef"


def test_vibeclient_defaults_match_config(monkeypatch):
    # No env override -> client defaults come from _config.
    for var in ("VIBE_DC_HOST", "VIBE_DC_PORT", "VIBE_DC_ID", "VIBE_API_ID", "VIBE_API_HASH"):
        monkeypatch.delenv(var, raising=False)
    # Reload _config so module-level constants reflect the cleared env.
    importlib.reload(_config)
    from userapi import client as client_mod
    importlib.reload(client_mod)
    c = client_mod.VibeClient()
    assert c._dc_host == _config.DEFAULT_DC_HOST
    assert c._dc_port == _config.DEFAULT_DC_PORT
    assert c._dc_id == _config.DEFAULT_DC_ID


def test_vibeclient_picks_up_env_dc(monkeypatch):
    monkeypatch.setenv("VIBE_DC_HOST", "env.host")
    monkeypatch.setenv("VIBE_DC_PORT", "7000")
    monkeypatch.setenv("VIBE_DC_ID", "9")
    importlib.reload(_config)
    from userapi import client as client_mod
    importlib.reload(client_mod)
    c = client_mod.VibeClient()
    assert c._dc_host == "env.host"
    assert c._dc_port == 7000
    assert c._dc_id == 9
