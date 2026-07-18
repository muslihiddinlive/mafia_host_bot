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


import config
from .bot import bot
from .database import database
from . import i18n
from . import stats

import re
import codecs
import random
from os.path import getsize


BASE_SIZE = getsize(config.WORD_BASE)


def get_word():
    with codecs.open(config.WORD_BASE, 'r', encoding='cp1251') as base:
        offset = random.randrange(BASE_SIZE)
        base.seek(offset)
        base.readline()
        word = base.readline()
    return word


def croco_suggestion(suggestion, game, user, message_id):
    if not re.search(r'\b{}\b'.format(game['word']), suggestion):
        return
    increments = {'croco.total': 1}
    if user['id'] == game['player']:
        increments['croco.cheat'] = 1
        answer = i18n.t(game['chat'], 'croco_cant_name_own_word')
    else:
        increments['croco.win'] = 1
        stats.increment(game['chat'], user['id'], user['full_name'], {'croco.guesses': 1})
        answer = i18n.t(game['chat'], 'croco_correct_word')
    bot.send_message(game['chat'], answer, reply_to_message_id=message_id)
    database.games.delete_one({'_id': game['_id']})
    stats.increment(game['chat'], game['player'], game['full_name'], increments)
