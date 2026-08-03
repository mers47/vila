"""Multi-Channel Gateway — single entry point for all platforms.
Routes incoming messages from any channel to unified dispatcher.
Core bot logic never knows which channel a message came from.
"""
import asyncio, logging
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)


class MultiChannelGateway:
    RATE_LIMITS = {"telegram": 30, "eitaa": 5, "rubika": 1}

    def __init__(self):
        self.providers: dict[str, object] = {}
        self._last_sent: dict[str, float] = defaultdict(float)

    async def register_eitaa(self, token: str) -> None:
        from bot.providers.eitaa_provider import EitaaProvider
        self.providers["eitaa"] = EitaaProvider(token=token)
        logger.info("Eitaa provider registered")

    async def register_rubika(self, auth: str) -> None:
        from bot.providers.rubika_provider import RubikaProvider
        provider = RubikaProvider(auth=auth)
        await provider.connect()
        self.providers["rubika"] = provider
        logger.info("Rubika provider registered")

    async def send_via(self, channel: str, chat_id: str, text: str, reply_markup=None, **kwargs) -> dict:
        provider = self.providers.get(channel)
        if not provider:
            return {"ok": False, "error": f"Unknown channel: {channel}"}

        await self._rate_limit(channel)
        result = await provider.send_message(chat_id, text, reply_markup, **kwargs)
        self._last_sent[channel] = asyncio.get_event_loop().time()
        return result

    async def _rate_limit(self, channel: str) -> None:
        max_rate = self.RATE_LIMITS.get(channel, 5)
        elapsed = asyncio.get_event_loop().time() - self._last_sent.get(channel, 0)
        min_interval = 1.0 / max_rate
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)

    async def close_all(self):
        for name, p in self.providers.items():
            if hasattr(p, 'close'):
                await p.close()
        logger.info("All providers closed")
