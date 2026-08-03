"""Eitaa Provider — production integration for Iranian messenger Eitaa.
Uses HTTP REST API at eitaayar.ir/api/{token}/methodName.
Supports: sendMessage, sendPhoto, editMessageText, getUpdates (polling).
"""
import asyncio, logging, aiohttp
from typing import Optional

logger = logging.getLogger(__name__)


class EitaaProvider:
    """Real Eitaa messenger provider."""
    BASE_URL = "https://eitaayar.ir/api"
    RATE_LIMIT = 5.0

    def __init__(self, token: str):
        self.token = token
        self._session: Optional[aiohttp.ClientSession] = None
        self._polling = False
        self._offset = 0
        self._handlers: list = []

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self._session

    def _api_url(self, method: str) -> str:
        return f"{self.BASE_URL}/{self.token}/{method}"

    async def send_message(self, chat_id: str, text: str, reply_markup=None, parse_mode: str = "HTML") -> dict:
        s = await self._get_session()
        p = {"chat_id": str(chat_id), "text": text}
        if reply_markup:
            p["reply_markup"] = self._serialize_keyboard(reply_markup)
        try:
            async with s.post(self._api_url("sendMessage"), json=p) as r:
                return await r.json()
        except Exception as e:
            logger.error(f"Eitaa sendMessage: {e}")
            return {"ok": False, "error": str(e)}

    async def send_photo(self, chat_id: str, photo: str, caption: Optional[str] = None, reply_markup=None) -> dict:
        s = await self._get_session()
        p = {"chat_id": str(chat_id), "photo": photo}
        if caption:
            p["caption"] = caption
        if reply_markup:
            p["reply_markup"] = self._serialize_keyboard(reply_markup)
        try:
            async with s.post(self._api_url("sendPhoto"), json=p) as r:
                return await r.json()
        except Exception as e:
            logger.error(f"Eitaa sendPhoto: {e}")
            return {"ok": False, "error": str(e)}

    async def get_updates(self, timeout: int = 30) -> list[dict]:
        s = await self._get_session()
        try:
            async with s.post(self._api_url("getUpdates"),
                              json={"offset": self._offset, "timeout": timeout}) as r:
                data = await r.json()
            if data.get("ok") and data.get("result"):
                for u in data["result"]:
                    uid = u.get("update_id", 0)
                    if uid >= self._offset:
                        self._offset = uid + 1
                return data["result"]
            return []
        except Exception as e:
            logger.error(f"Eitaa getUpdates: {e}")
            return []

    async def start_polling(self, interval: float = 0.5):
        self._polling = True
        logger.info("Eitaa polling started")
        while self._polling:
            try:
                for update in await self.get_updates(10):
                    for h in self._handlers:
                        try:
                            await h(update)
                        except Exception as e:
                            logger.error(f"Eitaa handler: {e}")
            except Exception as e:
                logger.error(f"Eitaa poll: {e}")
            await asyncio.sleep(interval)

    def stop_polling(self):
        self._polling = False

    def add_handler(self, handler):
        self._handlers.append(handler)

    def _serialize_keyboard(self, keyboard) -> Optional[dict]:
        if keyboard is None:
            return None
        if hasattr(keyboard, 'inline_keyboard'):
            return {
                "inline_keyboard": [
                    [{"text": b.text, "callback_data": b.callback_data} for b in row]
                    for row in keyboard.inline_keyboard
                ]
            }
        return None

    async def close(self):
        self.stop_polling()
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
