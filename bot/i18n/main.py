"""i18n main — locale resolution and string formatting."""
from __future__ import annotations
from functools import lru_cache
from html import escape as _html_escape
from typing import Any
from bot.misc import EnvKeys
from .strings import TRANSLATIONS, DEFAULT_LOCALE
from bot.logger_mesh import logger

def esc(value: Any) -> str:
    return _html_escape("" if value is None else str(value), quote=False)

@lru_cache(maxsize=1)
def get_locale() -> str:
    loc = EnvKeys.BOT_LOCALE.lower().strip()
    return loc if loc in TRANSLATIONS else DEFAULT_LOCALE

def localize(key: str, /, **kwargs: Any) -> str:
    loc = get_locale()
    text = TRANSLATIONS.get(loc, {}).get(key)
    if text is None:
        text = TRANSLATIONS.get(DEFAULT_LOCALE, {}).get(key)
    if text is None:
        text = key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to format translation key '{key}': {e}")
    return str(text)
