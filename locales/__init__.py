"""
Locales Package - Multi-language support for Uzbek, Russian, English

This package contains all translations for:
- Main Bot (app/)
- Client Bot (client_bot/)

Usage:
    from locales import get_text, _

    # Get translated text
    text = get_text("welcome", "uz", name="John")
    # or shorthand
    text = _("welcome", "uz", name="John")
"""

from locales.translations import TRANSLATIONS, get_text, get_language_keyboard

# Shortcut function
_ = get_text

__all__ = [
    "TRANSLATIONS",
    "get_text",
    "get_language_keyboard",
    "_"
]
