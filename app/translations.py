"""
Translations module - Re-exports from locales package

This file is kept for backward compatibility.
All translations are now stored in the locales/ package.
"""

from locales import TRANSLATIONS, get_text, get_language_keyboard, _

__all__ = ["TRANSLATIONS", "get_text", "get_language_keyboard", "_"]
