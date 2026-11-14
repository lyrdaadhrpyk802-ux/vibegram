# ============================================
#  botapi/http_client.py - Vibe Bot HTTP API client
#  Telegram-compatible Bot API over HTTPS.
# ============================================
import asyncio
import json
from typing import Any, Dict, List, Optional

import aiohttp


DEFAULT_BASE_URL = "https://api.vibegram.chat"
DEFAULT_TIMEOUT = 60


class VibeBotAPIError(Exception):
    """Raised when the Vibe Bot API returns ok=false."""

    def __init__(self, method: str, error_code: int, description: str, raw: Dict[str, Any]):
        self.method = method
        self.error_code = error_code
        self.description = description
        self.raw = raw
        super().__init__(f"{method}: [{error_code}] {description}")


class VibeBotHTTP:
    """Async client for the Vibe Bot HTTP API (Telegram-compatible).

    Usage:
        async with VibeBotHTTP("YOUR_TOKEN") as bot:
            me = await bot.get_me()
            await bot.send_message(chat_id=123, text="hello")
    """

    def __init__(
        self,
        token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        if not token:
            raise ValueError("token is required")
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session
        self._owns_session = session is None

    def _endpoint(self, method: str) -> str:
        return f"{self._base_url}/bot{self._token}/{method}"

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._timeout)
            )
            self._owns_session = True
        return self._session

    async def call(self, method: str, **params: Any) -> Any:
        """Invoke a Bot API method and return the 'result' field."""
        session = await self._ensure_session()
        url = self._endpoint(method)

        # Strip None values so they are not sent
        payload = {k: v for k, v in params.items() if v is not None}

        try:
            async with session.post(url, json=payload) as resp:
                text = await resp.text()
        except aiohttp.ClientError as e:
            raise ConnectionError(f"{method}: network error: {e}") from e

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            raise ConnectionError(
                f"{method}: invalid JSON response (HTTP {resp.status}): {text[:200]}"
            )

        if not isinstance(data, dict) or not data.get("ok", False):
            raise VibeBotAPIError(
                method=method,
                error_code=int(data.get("error_code", resp.status)) if isinstance(data, dict) else resp.status,
                description=str(data.get("description", text[:200])) if isinstance(data, dict) else text[:200],
                raw=data if isinstance(data, dict) else {"raw": text},
            )

        return data.get("result")

    # ---- context manager ----
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._session = None

    # ---- identity / profile ----
    async def get_me(self) -> Dict[str, Any]:
        return await self.call("getMe")

    async def get_my_name(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        return await self.call("getMyName", language_code=language_code)

    async def set_my_name(self, name: str, language_code: Optional[str] = None) -> bool:
        return await self.call("setMyName", name=name, language_code=language_code)

    async def get_my_description(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        return await self.call("getMyDescription", language_code=language_code)

    async def set_my_description(self, description: str, language_code: Optional[str] = None) -> bool:
        return await self.call("setMyDescription", description=description, language_code=language_code)

    async def get_my_short_description(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        return await self.call("getMyShortDescription", language_code=language_code)

    async def set_my_short_description(self, short_description: str, language_code: Optional[str] = None) -> bool:
        return await self.call("setMyShortDescription", short_description=short_description, language_code=language_code)

    async def get_my_commands(self, scope: Optional[Dict] = None, language_code: Optional[str] = None) -> List[Dict]:
        return await self.call("getMyCommands", scope=scope, language_code=language_code)

    async def set_my_commands(self, commands: List[Dict], scope: Optional[Dict] = None, language_code: Optional[str] = None) -> bool:
        return await self.call("setMyCommands", commands=commands, scope=scope, language_code=language_code)

    async def delete_my_commands(self, scope: Optional[Dict] = None, language_code: Optional[str] = None) -> bool:
        return await self.call("deleteMyCommands", scope=scope, language_code=language_code)

    # ---- messaging ----
    async def send_message(
        self,
        chat_id: Any,
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Dict] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return await self.call(
            "sendMessage",
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            **kwargs,
        )

    # ---- updates (long polling) ----
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 30,
        allowed_updates: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        return await self.call(
            "getUpdates",
            offset=offset,
            limit=limit,
            timeout=timeout,
            allowed_updates=allowed_updates,
        )

    # ---- webhook ----
    async def set_webhook(
        self,
        url: str,
        secret_token: Optional[str] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None,
        drop_pending_updates: Optional[bool] = None,
    ) -> bool:
        return await self.call(
            "setWebhook",
            url=url,
            secret_token=secret_token,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
        )

    async def get_webhook_info(self) -> Dict[str, Any]:
        return await self.call("getWebhookInfo")

    async def delete_webhook(self, drop_pending_updates: Optional[bool] = None) -> bool:
        return await self.call("deleteWebhook", drop_pending_updates=drop_pending_updates)

    async def drop_pending_updates(self) -> bool:
        return await self.call("dropPendingUpdates")

    # ---- files ----
    async def get_file(self, file_id: str) -> Dict[str, Any]:
        """Return file metadata. Result includes 'file_id', 'file_unique_id',
        'file_size' and (if the server supports it) 'file_path'."""
        return await self.call("getFile", file_id=file_id)

    async def poll_updates(
        self,
        offset: Optional[int] = None,
        timeout: int = 30,
        allowed_updates: Optional[List[str]] = None,
    ):
        """Async generator that yields updates, tracking offset automatically."""
        current_offset = offset
        while True:
            updates = await self.get_updates(
                offset=current_offset,
                timeout=timeout,
                allowed_updates=allowed_updates,
            )
            if not updates:
                await asyncio.sleep(0.5)
                continue
            for update in updates:
                yield update
                current_offset = update.get("update_id", current_offset) + 1 if current_offset is not None else update.get("update_id", 0) + 1
