"""
config.py
---------
Barcha sozlamalarni environment variable'lardan o'qiydi (Render Dashboard >
Environment, yoki lokal ishlashda .env fayl orqali - pastga qarang).

Bu fayl GIT'GA TUSHADI (sirlarni o'zida saqlamaydi) - shuning uchun uni
o'zgartirib qayta joylashtirish shart emas, faqat Render'dagi Environment
qiymatlarini o'zgartirsangiz kifoya.

Majburiy qiymat topilmasa, dastur DARHOL to'xtaydi (fail-fast) - noto'g'ri
sozlama bilan "yarim ishlab" keyin g'alati xatoliklar berishidan ko'ra,
ishga tushishning o'zidayoq aniq xato ko'rsatish afzal.
"""

import os
import logging

from dotenv import load_dotenv

load_dotenv()  # Lokal ishlashda .env fayl bo'lsa, undan o'qiydi (Render'da .env fayl kerak emas - Environment sozlamalari to'g'ridan-to'g'ri os.environ'ga tushadi)


def _require(key):
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f'Majburiy environment variable topilmadi: {key}. '
            f'.env faylni yoki Render Dashboard > Environment boʻlimini tekshiring.'
        )
    return value


def _bool(key, default):
    value = os.environ.get(key)
    return default if value is None else value.strip().lower() in ('1', 'true', 'yes')


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
TOKEN = _require('TOKEN')  # @BotFather'dan olingan token
ADMIN_ID = int(_require('ADMIN_ID'))  # Sizning Telegram user ID'ingiz (superadmin)
DB_CHAT_ID = int(_require('DB_CHAT_ID'))  # Doimiy ma'lumotlar (pul, olmos, shop, statistika, config)
                                            # saqlanadigan yopiq supergroup ID. Bot shu yerda admin
                                            # bo'lishi kerak (pin, edit, delete, invite huquqlari bilan).
SKIP_PENDING = _bool('SKIP_PENDING', False)  # Bot ishga tushganda eski xabarlarni o'tkazib yuborish

# ---------------------------------------------------------------------------
# O'yin sozlamalari
# ---------------------------------------------------------------------------
PLAYERS_COUNT_TO_START = int(os.environ.get('PLAYERS_COUNT_TO_START', 4))
PLAYERS_COUNT_LIMIT = int(os.environ.get('PLAYERS_COUNT_LIMIT', 10))
REQUEST_OVERDUE_TIME = int(os.environ.get('REQUEST_OVERDUE_TIME', 10 * 60))
WORD_BASE = os.environ.get('WORD_BASE', '/root/words.txt')  # cp1251 kodli, har qatorda bitta so'z
DELETE_FROM_EVERYONE = _bool('DELETE_FROM_EVERYONE', False)

# ---------------------------------------------------------------------------
# Server / Webhook (Render Web Service)
# ---------------------------------------------------------------------------
SET_WEBHOOK = _bool('SET_WEBHOOK', True)  # False bo'lsa long polling ishlatiladi
if SET_WEBHOOK:
    # Render bergan ochiq manzil (masalan https://mening-botim.onrender.com).
    # RENDER_EXTERNAL_URL Render tomonidan avtomatik beriladi - qo'lda WEBHOOK_URL
    # kiritish shart emas, lekin xohlasangiz ustidan yozib qo'yishingiz mumkin.
    WEBHOOK_URL = (os.environ.get('RENDER_EXTERNAL_URL') or _require('WEBHOOK_URL')).rstrip('/')
    SERVER_PORT = int(os.environ.get('PORT', 8080))  # Render avtomatik beradi

# ---------------------------------------------------------------------------
LOGGER_LEVEL = getattr(logging, os.environ.get('LOGGER_LEVEL', 'INFO').upper(), logging.INFO)
