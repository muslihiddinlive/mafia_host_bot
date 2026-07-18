# Doimiy o'yinchi statistikasi (g'alaba/mag'lubiyat, croco/gallows natijalari).
# Avval MongoDB'da edi ('database.stats'), lekin bu ma'lumot economy kabi DOIMIY -
# vaqtinchalik emas - shuning uchun endi tgdb (fayl + Telegram-document) orqali saqlanadi.
# MongoDB faqat haqiqiy vaqtinchalik narsalar (faol o'yin holati, so'rovlar, ovoz berish)
# uchun qoladi.

from . import tgdb


def _key(chat_id, user_id):
    return f'{chat_id}:{user_id}'


def get(chat_id, user_id):
    """Mongo'dagi find_one({'id':.., 'chat':..}) o'rnini bosadi. Topilmasa None qaytaradi."""
    return tgdb.get('stats').get(_key(chat_id, user_id))


def get_chat_stats(chat_id):
    """Mongo'dagi find({'chat':..}) o'rnini bosadi - shu chatdagi barcha o'yinchilar statistikasi."""
    prefix = f'{chat_id}:'
    return [v for k, v in tgdb.get('stats').items() if k.startswith(prefix)]


def _increment_nested(record, dotted_key, amount):
    """'croco.win' kabi nuqtali kalitni record['croco']['win'] += amount ga aylantiradi."""
    parts = dotted_key.split('.')
    node = record
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    last = parts[-1]
    node[last] = node.get(last, 0) + amount


def increment(chat_id, user_id, name, inc_dict, save=True):
    """Mongo'dagi update_one({'id':,'chat':}, {'$set':{'name':}, '$inc': inc_dict}, upsert=True)
    o'rnini bosadi. inc_dict kalitlari 'croco.win' kabi nuqtali bo'lishi mumkin."""
    stats = tgdb.get('stats')
    key = _key(chat_id, user_id)
    record = stats.setdefault(key, {'id': user_id, 'chat': chat_id})
    if name is not None:
        record['name'] = name
    for dotted_key, amount in inc_dict.items():
        _increment_nested(record, dotted_key, amount)
    if save:
        tgdb.save()
    return record
