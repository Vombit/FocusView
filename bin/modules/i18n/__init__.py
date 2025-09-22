# pylint: disable=global-statement
"""language management"""
from .en import translations as en_translations
from .ru import translations as ru_translations

translations = {
    "en": en_translations,
    "ru": ru_translations,
}

# default
CURRENT_LANG = "ru"


def set_language(lang_code):
    """pass"""
    global CURRENT_LANG
    if lang_code in translations:
        CURRENT_LANG = lang_code
    else:
        raise ValueError(
            f"Language '{lang_code}' not supported. Available: {list(translations.keys())}")


def tr(key):
    """Get element by key"""
    return translations[CURRENT_LANG].get(key, f"[{key}?]")
