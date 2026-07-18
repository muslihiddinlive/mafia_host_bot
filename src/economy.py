# Ekonomika: balans/olmos boshqarish, referral, shop sotib olish, superadmin tekshiruvi.
# Ma'lumotlar tgdb.py orqali saqlanadi (fayl + Telegram-document hibrid).

from . import tgdb


def get_user(user_id):
    return tgdb.get_user(user_id)


def add_balance(user_id, amount, save=True):
    user = tgdb.get_user(user_id)
    user['balance'] += amount
    if save:
        tgdb.save()
    return user['balance']


def add_diamonds(user_id, amount, save=True):
    user = tgdb.get_user(user_id)
    user['diamonds'] += amount
    if save:
        tgdb.save()
    return user['diamonds']


def can_afford(user_id, dollars=0, diamonds=0):
    user = tgdb.get_user(user_id)
    return user['balance'] >= dollars and user['diamonds'] >= diamonds


def charge(user_id, dollars=0, diamonds=0, save=True):
    """Balans/olmosdan yechadi. Yetarli bo'lmasa False qaytaradi, hech narsa o'zgarmaydi."""
    user = tgdb.get_user(user_id)
    if user['balance'] < dollars or user['diamonds'] < diamonds:
        return False
    user['balance'] -= dollars
    user['diamonds'] -= diamonds
    if save:
        tgdb.save()
    return True


def reward_game_win(user_id, save=True):
    reward = tgdb.get('global_config')['game_win_reward']
    add_balance(user_id, reward, save=save)
    return reward


def register_referral(new_user_id, referrer_id):
    """/start ref_<id> orqali birinchi marta kirganda chaqiriladi.
    Muvaffaqiyatli bo'lsa mukofot summasini, aks holda None qaytaradi."""
    if new_user_id == referrer_id:
        return None
    user = tgdb.get_user(new_user_id)
    if user['referred_by'] is not None:
        return None  # allaqachon boshqa referral orqali kirgan
    referrer = tgdb.get_user(referrer_id)
    user['referred_by'] = referrer_id
    referrer['referrals'] += 1
    reward = tgdb.get('global_config')['referral_reward']
    referrer['balance'] += reward
    tgdb.save()
    return reward


def claim_channel_bonus(user_id, channel_id):
    """Superadmin qo'shgan bonus kanalga birinchi marta obuna tasdiqlanganda chaqiriladi."""
    user = tgdb.get_user(user_id)
    claimed = user.setdefault('claimed_channels', [])
    if channel_id in claimed:
        return None
    channels = tgdb.get('channels_config')['channels']
    channel = next((c for c in channels if c['id'] == channel_id), None)
    reward = channel['reward'] if channel else tgdb.get('global_config')['referral_reward']
    claimed.append(channel_id)
    user['balance'] += reward
    tgdb.save()
    return reward


ITEM_NAMES = {
    'documents': 'Hujjatlar',
    'protection': 'Ximoya',
    'active_role': 'Faol rol',
    'double_vote': '2x ovoz',
}


def shop_price(item):
    """Item narxini (dollars, diamonds) juftlik sifatida qaytaradi.
    active_role ikkala valyutada ham sotib olinishi mumkin - shuning uchun
    buy_item chaqirilganda pay_with orqali qaysi birligi tanlanganini ko'rsatasiz."""
    shop = tgdb.get('shop_config')
    prices = {
        'documents': (shop['documents'], 0),
        'protection': (shop['protection'], 0),
        'active_role': (shop['active_role_dollars'], shop['active_role_diamonds']),
        'double_vote': (0, shop['double_vote_diamonds']),
    }
    return prices[item]


def buy_item(user_id, item, pay_with='dollars'):
    """item: 'documents' | 'protection' | 'active_role' | 'double_vote'
    pay_with: 'dollars' | 'diamonds' (faqat active_role uchun ahamiyatli, chunki
    u ikkala valyutada ham sotib olinadi)."""
    dollars_price, diamonds_price = shop_price(item)

    if item == 'active_role' and pay_with == 'diamonds':
        dollars, diamonds = 0, diamonds_price
    elif item == 'active_role':
        dollars, diamonds = dollars_price, 0
    else:
        dollars, diamonds = dollars_price, diamonds_price

    if not charge(user_id, dollars=dollars, diamonds=diamonds, save=False):
        return False

    user = tgdb.get_user(user_id)
    items = user.setdefault('items', {})
    items[item] = items.get(item, 0) + 1
    tgdb.save()
    return True


def use_item(user_id, item, save=True):
    """O'yin ichida item ishlatilganda chaqiriladi (bir martalik) - inventardan 1 tasini kamaytiradi."""
    user = tgdb.get_user(user_id)
    items = user.setdefault('items', {})
    if items.get(item, 0) <= 0:
        return False
    items[item] -= 1
    if save:
        tgdb.save()
    return True


def is_superadmin(user_id):
    return tgdb.is_superadmin(user_id)


def stars_to_diamonds(stars):
    rate = tgdb.get('global_config')['stars_per_diamond']
    return stars // rate


def diamonds_to_stars(diamonds):
    rate = tgdb.get('global_config')['stars_per_diamond']
    return diamonds * rate
