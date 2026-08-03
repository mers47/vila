"""Rubika Provider — IR messenger via rubpy 7.3.5."""
import asyncio, logging
logger = logging.getLogger(__name__)
class RubikaProvider:
    RATE_LIMIT = 1.0
    def __init__(self, auth: str, private_key: str = "", phone_number: str = ""):
        self.auth = auth; self.private_key = private_key; self.phone_number = phone_number
        self._client = None; self._polling = False; self._handlers = []
    async def connect(self):
        from rubpy import Client
        self._client = Client(name="CommerceAgentOS", auth=self.auth, private_key=self.private_key or None, phone_number=self.phone_number or None, parse_mode="HTML")
        async def handler(message):
            for h in self._handlers:
                try: await h(message)
                except Exception as e: logger.error(f"Rubika: {e}")
        self._client.on_message_updates()(handler)
        logger.info("Rubika connected"); return self._client
    def add_handler(self, h): self._handlers.append(h)
    async def send_message(self, chat_id, text, reply_markup=None):
        try: return await self._client.send_message(object_guid=str(chat_id), text=text)
        except Exception as e: logger.error(f"Rubika: {e}"); return {"ok": False, "error": str(e)}
    async def send_photo(self, chat_id, photo, caption=None):
        try: return await self._client.send_photo(object_guid=str(chat_id), photo=photo, caption=caption or "")
        except Exception as e: return {"ok": False, "error": str(e)}
    async def start_polling(self):
        self._polling = True; logger.info("Rubika running")
        await self._client.run_until_disconnected()
    def stop_polling(self):
        self._polling = False
        if self._client: self._client.disconnect()
    async def close(self): self.stop_polling()
