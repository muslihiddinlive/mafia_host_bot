# Doimiy ma'lumotlar qatlami (economy, shop, config) - fayl + Telegram-document hibrid.
#
# Nega kerak: faol o'yin holati (games, polls) Mongo'da qoladi - ular vaqtinchalik.
# Lekin pul/olmos/shop/kanal/premium kabi QIMMATLI ma'lumotlar hech qachon yo'qolmasligi
# kerak - hatto Render kabi bepul hostingda disk har deploy'da tozalansa ham.
#
# Ishlash tartibi:
#   1. Barcha kategoriyalar (users, shop_config, ...) BITTA json faylda (data/db.json)
#      saqlanadi - runtime paytida shu fayl RAM'ga o'qiladi, tez ishlaydi, belgi limiti yo'q.
#   2. Har bir o'zgarishdan keyin fayl qayta yoziladi VA DB_CHAT_ID guruhiga document
#      sifatida yuboriladi/yangilanadi (edit_message_media - xabar ID o'zgarmaydi).
#   3. Shu xabar guruhda PIN qilinadi. Pin - qayerda so'nggi backup borligini bilish
#      uchun yagona manba: local pointer-fayl kerak emas, chunki u ham diskda o'chib
#      ketishi mumkin edi. get_chat().pinned_message orqali file_id har doim topiladi.
#   4. Disk tozalanib, local fayl topilmasa - bot shu pin qilingan file_id orqali
#      Telegramdan faylni qayta yuklab oladi va davom etadi. Hech narsa yo'qolmaydi.

import json
import os

import config
from .logger import logger
from .bot import bot

from telebot.types import InputMediaDocument


LOCAL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db.json')

DEFAULT_CACHE = {
    # user_id (str) -> {"balance": int($), "diamonds": int, "referrals": int, ...}
    'users': {},

    'shop_config': {
        'documents': 200,            # Hujjatlar - $
        'protection': 150,           # Ximoya - $
        'active_role_dollars': 300,  # Faol rol - $ (yoki quyidagi diamonds)
        'active_role_diamonds': 2,
        'double_vote_diamonds': 1,   # 2x ovoz - olmos
    },

    'channels_config': {
        'channels': [],  # [{"id": -100.., "title": "...", "reward": 10}, ...]
    },

    'premium_groups': {},  # chat_id (str) -> {"opener_id": ..., "entry_fee": 50, "win_reward": 30}

    'chat_languages': {},  # chat_id (str) -> til kodi ('ru'|'uz'|'tr'|'en'|'kk')

    # "{chat_id}:{user_id}" (str) -> {"id":, "chat":, "name":, "total":, "win":,
    #   "don":{"total":,"win":}, "mafia":{...}, "sheriff":{...}, "peace":{...},
    #   "croco":{"total":,"win":,"cheat":,"guesses":}, "gallows":{"total":,"win":,"right":,"wrong":}}
    # Doimiy statistika - avval MongoDB'da edi, lekin Mongo odatda vaqtinchalik hosting
    # diskida turadi (masalan Render) va redeploy'da o'chib ketardi. Endi bu yerda -
    # hech qachon yo'qolmaydi.
    'stats': {},

    'global_config': {
        'superadmins': [config.ADMIN_ID],
        'referral_reward': 10,
        'game_win_reward': 10,
        'stars_per_diamond': 10,
        'dollars_per_star': 10,
        'premium_group_diamond_cost': 5,
        'premium_group_diamond_cost_full': 100,
        'premium_group_entry_fee': 50,
        'premium_group_opener_share': 10,
    },
}

_cache = {}
_message_id = None  # DB_CHAT_ID dagi pin qilingan document xabarining ID'si (shu run uchun)


def _write_local():
    os.makedirs(os.path.dirname(LOCAL_FILE), exist_ok=True)
    with open(LOCAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(_cache, f, ensure_ascii=False, indent=2)


def _sync_to_telegram():
    """Local faylni DB_CHAT_ID guruhidagi document xabariga yuklaydi/yangilaydi."""
    global _message_id
    try:
        if _message_id is None:
            with open(LOCAL_FILE, 'rb') as f:
                message = bot.send_document(config.DB_CHAT_ID, f)
            bot.pin_chat_message(config.DB_CHAT_ID, message.message_id, disable_notification=True)
            _message_id = message.message_id
        else:
            with open(LOCAL_FILE, 'rb') as f:
                bot.edit_message_media(
                    media=InputMediaDocument(f),
                    chat_id=config.DB_CHAT_ID,
                    message_id=_message_id
                )
    except Exception:
        logger.error(
            'Telegram-DB ga sinxronlab bo\'lmadi (bot guruhdan chiqarilgan yoki '
            'huquqlar yetishmayotgan bo\'lishi mumkin). Local fayl bilan ishlash davom etadi.',
            exc_info=True
        )


def load_all():
    """Bot ishga tushganda va superadmin /reload buyrug'ini yozganda chaqiriladi."""
    global _cache, _message_id

    pinned_file_id = None
    try:
        chat = bot.get_chat(config.DB_CHAT_ID)
        if chat.pinned_message and chat.pinned_message.document:
            _message_id = chat.pinned_message.message_id
            pinned_file_id = chat.pinned_message.document.file_id
    except Exception:
        logger.error('DB_CHAT_ID guruhi holatini olib bo\'lmadi', exc_info=True)

    if os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
            _cache = json.load(f)
        logger.info('Telegram-DB local fayldan yuklandi.')

    elif pinned_file_id:
        # Disk tozalangan (masalan Render qayta deploy) - Telegramdagi pin'dan tiklaymiz
        file_info = bot.get_file(pinned_file_id)
        downloaded = bot.download_file(file_info.file_path)
        os.makedirs(os.path.dirname(LOCAL_FILE), exist_ok=True)
        with open(LOCAL_FILE, 'wb') as f:
            f.write(downloaded)
        with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
            _cache = json.load(f)
        logger.info('Telegram-DB disk tozalangandan keyin Telegram pin\'idan tiklandi!')

    else:
        # Birinchi marta - hech qanday joyda ma'lumot yo'q
        _cache = json.loads(json.dumps(DEFAULT_CACHE))  # chuqur nusxa
        _write_local()
        _sync_to_telegram()
        logger.info('Telegram-DB birinchi marta defaultlardan yaratildi.')

    return _cache


def save():
    """Istalgan kategoriya RAM'da (_cache) o'zgargandan keyin chaqiriladi.
    Local faylni qayta yozadi va Telegramdagi document'ni yangilaydi."""
    _write_local()
    _sync_to_telegram()


def get(category):
    return _cache[category]


def get_user(user_id):
    """Foydalanuvchi yozuvini qaytaradi, yo'q bo'lsa yangisini yaratadi.
    Buni chaqirgan kod, o'zgartirishdan keyin tgdb.save() ni chaqirishi kerak."""
    users = _cache['users']
    key = str(user_id)
    if key not in users:
        users[key] = {'balance': 0, 'diamonds': 0, 'referrals': 0, 'referred_by': None, 'items': {}}
    return users[key]


def is_superadmin(user_id):
    return user_id == config.ADMIN_ID or user_id in _cache['global_config']['superadmins']
