# Ko'p tillilik: har bir chat (guruh yoki shaxsiy) o'z tilini tanlashi mumkin.
# Standart til - 'uz'. Noma'lum kalit yoki til so'ralsa - 'ru'ga (asl til) qaytiladi,
# bu ham topilmasa - kalitning o'zi ko'rsatiladi (dastur hech qachon qulamasligi uchun).

from . import tgdb
from .translations import T, SUPPORTED_LANGUAGES, LANGUAGE_NAMES

DEFAULT_LANGUAGE = 'uz'


def get_language(chat_id):
    return tgdb.get('chat_languages').get(str(chat_id), DEFAULT_LANGUAGE)


def set_language(chat_id, lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return False
    tgdb.get('chat_languages')[str(chat_id)] = lang_code
    tgdb.save()
    return True


def t(chat_id, key, **kwargs):
    lang_code = get_language(chat_id)
    entry = T.get(key)
    if entry is None:
        return key
    template = entry.get(lang_code) or entry.get('ru') or next(iter(entry.values()))
    return template.format(**kwargs) if kwargs else template
