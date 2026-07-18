# Copyright (C) 2017, 2018, 2019, 2020  alfred richardsn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from .bot import bot
from .database import database
from . import i18n
from . import stats
from . import tgdb

import re
from enum import Enum, auto

stickman = [
    ('', '', ''),
    (' 0', '', ''),
    (' 0', ' |', ''),
    (' 0', '/|', ''),
    (' 0', '/|\\', ''),
    (' 0', '/|\\', '/'),
    (' 0', '/|\\', '/ \\')
]


def get_stats(game):
    stats = {int(id): {'name': name, 'right': 0, 'wrong': 0} for id, name in game['names'].items()}
    for key in ('right', 'wrong'):
        for user_id in game[key].values():
            stats[user_id][key] += 1
    return stats


def set_gallows(game, result, word, stats=None):
    chat = game['chat']
    if game['names']:
        if stats is None:
            stats = get_stats(game)
        users = sorted(stats.values(), key=lambda s: s['right'], reverse=True)
        players = '\n\n' + '\n'.join(f'{u["name"]}: ✔️{u["right"]} ❌{u["wrong"]}' for u in users)
    else:
        players = ''

    attempts = (
        f'\n{i18n.t(chat, "gallows_attempts_label")}: ' + ', '.join(game['wrong'])
        if game['wrong'] else ''
    )

    # ASCII rasm tildan mustaqil, shuning uchun tarjima lug'atida emas, shu yerda qoladi.
    ascii_art = (
        '<code>___________\n|         |\n|        %s\n|        %s\n|        %s\n|\n|</code>\n'
    ) % stickman[len(game['wrong'])]

    bot.edit_message_text(
        f'{ascii_art}{result}\n{i18n.t(chat, "gallows_word_label")}: {word}{attempts}{players}',
        chat_id=chat,
        message_id=game['message_id'],
        parse_mode='HTML'
    )


class GameResult(Enum):
    WIN = auto()
    LOSE = auto()


def end_game(game, game_result):
    chat = game['chat']
    if game_result == GameResult.WIN:
        result = i18n.t(chat, 'gallows_won')
    elif game_result == GameResult.LOSE:
        result = i18n.t(chat, 'gallows_lost')
    game_stats = get_stats(game)
    set_gallows(game, result, ' '.join(list(game['word'])), stats=game_stats)
    for id, s in game_stats.items():
        increments = {
            'gallows.right': s['right'],
            'gallows.wrong': s['wrong'],
            'gallows.total': 1
        }
        if game_result == GameResult.WIN and s['right']:
            increments['gallows.win'] = 1
        stats.increment(chat, id, s['name'], increments, save=False)
    tgdb.save()
    database.games.delete_one({'_id': game['_id']})


def gallows_suggestion(suggestion, game, user, message_id):
    game['names'][user['id']] = user['name']

    if len(suggestion) > 1:
        if re.search(r'\b{}\b'.format(game['word']), suggestion):
            for ch in game['word']:
                if ch not in game['right']:
                    game['right'][ch] = user['id']
            end_game(game, GameResult.WIN)
        return

    # DIQQAT: so'z bazasi (config.WORD_BASE) va harf tekshiruvi hozircha faqat rus
    # alifbosiga mo'ljallangan - buni boshqa tillarga o'tkazish alohida so'z bazasi talab qiladi.
    if not 'А' <= suggestion <= 'я':
        return

    if suggestion in game['wrong'] or suggestion in game['right']:
        bot.send_message(game['chat'], i18n.t(game['chat'], 'letter_already_chosen'))
        return

    word = list(game['word'])
    word_in_underlines = []
    has_letter = False
    for ch in word:
        if ch == suggestion:
            word_in_underlines.append(ch)
            has_letter = True
        elif ch in game['right']:
            word_in_underlines.append(ch)
        else:
            word_in_underlines.append('_')

    bot.safely_delete_message(chat_id=game['chat'], message_id=message_id)

    if has_letter:
        game['right'][suggestion] = user['id']
        if word_in_underlines == word:
            end_game(game, GameResult.WIN)
            return
        update = {
            f'right.{suggestion}': user['id'],
            f'names.{user["id"]}': user['name']
        }
    else:
        game['wrong'][suggestion] = user['id']
        if len(game['wrong']) >= len(stickman) - 1:
            end_game(game, GameResult.LOSE)
            return
        update = {
            f'wrong.{suggestion}': user['id'],
            f'names.{user["id"]}': user['name']
        }

    database.games.update_one({'_id': game['_id']}, {'$set': update})
    set_gallows(game, '', ' '.join(word_in_underlines))
