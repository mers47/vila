"""Eitaa Provider — production IR messenger. REST API eitaayar.ir/api/{token}/methodName."""
import asyncio, logging, aiohttp
from typing import Optional
logger = logging.getLogger(__name__)
class EitaaProvider:
    BASE_URL = "https://eitaayar.ir/api"
    RATE_LIMIT = 5.0
    def __init__(self, token: str):
        self.token = token; self._session = None; self._polling = False; self._offset = 0; self._handlers = []
    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self._session
    def _api_url(self, method): return f"{self.BASE_URL}/{self.token}/{method}"
    async def send_message(self, chat_id, text, reply_markup=None, parse_mode="HTML"):
        s = await self._get_session(); p = {"chat_id": str(chat_id), "text": text}
        if reply_markup: p["reply_markup"] = self._serialize_keyboard(reply_markup)
        try: async with s.post(self._api_url("sendMessage"), json=p) as r: return await r.json()
        except Exception as e: logger.error(f"Eitaa: {e}"); return {"ok": False, "error": str(e)}
    async def send_photo(self, chat_id, photo, caption=None, reply_markup=None):
        s = await self._get_session(); p = {"chat_id": str(chat_id), "photo": photo}
        if caption: p["caption"] = caption
        try: async with s.post(self._api_url("sendPhoto"), json=p) as r: return await r.json()
        except Exception as e: return {"ok": False, "error": str(e)}
    async def get_updates(self, timeout=30):
        s = await self._get_session()
        try:
            async with s.post(self._api_url("getUpdates"), json={"offset": self._offset, "timeout": timeout}) as r: data = await r.json()
            if data.get("ok") and data.get("result"):
                for u in data["result"]:
                    uid = u.get("update_id", 0)
                    if uid >= self._offset: self._offset = uid + 1
                return data["result"]
            return []
        except Exception as e: logger.error(f"Eitaa: {e}"); return []
    async def start_polling(self, interval=0.5):
        self._polling = True; logger.info("Eitaa polling started")
        while self._polling:
            try:
                for update in await self.get_updates(10):
                    for h in self._handlers:
                        try: await h(update)
                        except Exception as e: logger.error(f"Handler: {e}")
            except Exception as e: logger.error(f"Poll: {e}")
            await asyncio.sleep(interval)
    def stop_polling(self): self._polling = False
    def add_handler(self, h): self._handlers.append(h)
    def _serialize_keyboard(self, kb):
        if kb is None: return None
        if hasattr(kb, 'inline_keyboard'):
            return {"inline_keyboard": [[{"text": b.text, "callback_data": b.callback_data} for b in row] for row in kb.inline_keyboard]}
        return None
    async def close(self):
        self.stop_polling()
        if self._session and not self._session.closed: await self._session.close(); self._session = None
