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


from . import i18n
from . import economy
from .bot import bot
from .database import database, ReturnDocument
from .game import role_title

import random
from time import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiException


stages = {}


def add_stage(number, time=None, delete=False):
    def decorator(func):
        stages[number] = {'time': time, 'func': func, 'delete': delete}
        return func
    return decorator


def go_to_next_stage(game, inc=1):
    database.polls.delete_many({'chat': game['chat']})

    stage_number = 0 if game['stage'] == max(stages.keys()) + 1 - inc else game['stage'] + inc
    stage = stages[stage_number]
    if stage['delete']:
        database.games.delete_one({'_id': game['_id']})
        new_game = game
    else:
        time_inc = stage['time'](game) if callable(stage['time']) else stage['time']
        new_game = database.games.find_one_and_update(
            {'_id': game['_id']},
            {
                '$set': {
                    'next_stage_time': time() + (time_inc if isinstance(time_inc, (int, float)) else 0),
                    'stage': stage_number,
                    'played': []
                },
                '$inc': {'day_count': int(stage_number == 0)}},
            return_document=ReturnDocument.AFTER
        )

    try:
        stage['func'](new_game)
    except ApiException as exception:
        if exception.result.status_code == 403:
            database.games.delete_one({'_id': game['_id']})
            return

    return new_game


def format_roles(game, show_roles=False, condition=lambda p: p.get('alive', True)):
    return '\n'.join(
        [f'{i + 1}. {p["name"]}{" - " + role_title(p["role"], game["chat"]) if show_roles else ""}'
         for i, p in enumerate(game['players']) if condition(p)]
    )


@add_stage(-4, 90)
def first_stage():
    pass


@add_stage(-3, delete=True)
def cards_not_taken(game):
    bot.edit_message_text(
        i18n.t(game['chat'], 'game_over_no_cards'),
        chat_id=game['chat'],
        message_id=game['message_id']
    )


@add_stage(-2, 60)
def set_order(game):
    if not any(p['role'] == 'mafia' for p in game['players']):
        go_to_next_stage(game, inc=2)
        return

    chat = game['chat']
    keyboard = InlineKeyboardMarkup(row_width=8)
    keyboard.add(
        *[InlineKeyboardButton(
            text=f'{i + 1}',
            callback_data=f'append to order {i + 1}'
        ) for i, player in enumerate(game['players'])]
    )
    keyboard.row(
        InlineKeyboardButton(
            text=i18n.t(chat, 'meet_team_button'),
            callback_data='mafia team'
        )
    )
    finish_selection = i18n.t(chat, 'finish_selection_button')
    keyboard.row(
        InlineKeyboardButton(
            text=finish_selection,
            callback_data='end order'
        )
    )

    message_id = bot.send_message(
        chat,
        i18n.t(
            chat, 'don_choose_order_instruction',
            don=role_title('don', chat).capitalize(),
            finish_selection=finish_selection
        ),
        reply_markup=keyboard
    ).message_id

    database.games.update_one({'_id': game['_id']}, {'$set': {'message_id': message_id}})


@add_stage(-1, 5)
def get_order(game):
    chat = game['chat']
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=i18n.t(chat, 'get_order_button'),
            callback_data='get order'
        )
    )

    bot.edit_message_text(
        i18n.t(
            chat, 'don_order_given_to_mafia',
            don=role_title('don', chat).capitalize(),
            mafia=role_title('mafia', chat).capitalize()
        ),
        chat_id=chat,
        message_id=game['message_id'],
        reply_markup=keyboard
    )


@add_stage(0, lambda g: 90 + max(0, sum(p['alive'] for p in g['players']) - 4) * 35)
def discussion(game):
    chat = game['chat']
    if game['day_count'] > 1 and game.get('victim') is None:
        bot.edit_message_text(
            i18n.t(
                chat, 'morning_message',
                peaceful_night=i18n.t(chat, 'peaceful_night'),
                day=game['day_count'],
                order=format_roles(game)
            ),
            chat_id=chat,
            message_id=game['message_id']
        )
    else:
        if game['day_count'] > 1:
            database.games.update_one({'_id': game['_id']}, {'$unset': {'victim': True}})
        bot.send_message(
            chat,
            i18n.t(
                chat, 'morning_message',
                peaceful_night='',
                day=game['day_count'],
                order=format_roles(game)
            ),
        )


def get_votes(game):
    chat = game['chat']
    names = [(0, i18n.t(chat, 'dont_vote_option'))] + [(i + 1, p['name']) for i, p in enumerate(game['players']) if p['alive']]
    return '\n'.join([
        f'{i}. {name}' + (
            (': ' + ', '.join(str(v + 1) for v in game['vote'][str(i - 1)]))
            if str(i - 1) in game['vote'] else ''
        ) for i, name in names
    ])


@add_stage(1, 30)
def vote(game):
    chat = game['chat']
    keyboard = InlineKeyboardMarkup(row_width=8)
    keyboard.add(
        *[InlineKeyboardButton(
            text=f'{i + 1}',
            callback_data=f'vote {i + 1}'
        ) for i, player in enumerate(game['players']) if player['alive']]
    )
    keyboard.add(
        InlineKeyboardButton(
            text=i18n.t(chat, 'dont_vote_option'),
            callback_data='vote 0'
        )
    )

    message_id = bot.send_message(
        chat,
        i18n.t(chat, 'vote_time', vote=get_votes(game)),
        reply_markup=keyboard
    ).message_id

    database.games.update_one({'_id': game['_id']}, {'$set': {'message_id': message_id}})


@add_stage(2, 20)
def last_words_criminal(game):
    chat = game['chat']
    criminal = None
    if game['vote']:
        most_voted = max(game['vote'].values(), key=len)
        candidates = [int(i) for i, votes in game['vote'].items() if len(votes) == len(most_voted)]
        if len(candidates) == 1 and candidates[0] >= 0:
            criminal = candidates[0]

    saved_by_documents = criminal is not None and economy.use_item(game['players'][criminal]['id'], 'documents')

    if criminal is None:
        text = i18n.t(chat, 'town_no_criminal_chosen')
    elif saved_by_documents:
        text = i18n.t(
            chat, 'criminal_saved_by_documents',
            number=criminal + 1, name=game['players'][criminal]['name']
        )
    else:
        text = i18n.t(
            chat, 'town_voted_criminal_jailed',
            number=criminal + 1, name=game['players'][criminal]['name']
        )

    bot.edit_message_text(text, chat_id=chat, message_id=game['message_id'])

    update_dict = {'$set': {'vote': {}}}

    if criminal is not None and not saved_by_documents:
        update_dict['$set'][f'players.{criminal}.alive'] = False
        update_dict['$set']['victim'] = game['players'][criminal]['id']

    database.games.update_one({'_id': game['_id']}, update_dict)


@add_stage(3, 5)
def night(game):
    chat = game['chat']
    message_id = bot.send_message(
        chat,
        i18n.t(chat, 'night_falls_mafia_wakes', mafia=role_title('mafia', chat).capitalize())
    ).message_id
    database.games.update_one(
        {'_id': game['_id']},
        {
            '$unset': {'victim': True},
            '$set': {'message_id': message_id}
        }
    )


@add_stage(4, 5)
def shooting_stage(game):
    chat = game['chat']
    players = [(i, player) for i, player in enumerate(game['players']) if player['alive']]
    random.shuffle(players)

    keyboard = InlineKeyboardMarkup(row_width=8)
    keyboard.add(
        *[InlineKeyboardButton(
            text=f'{i + 1}',
            callback_data=f'shot {i + 1}'
        ) for i, player in players]
    )

    bot.edit_message_text(
        i18n.t(chat, 'mafia_choosing_victim', mafia=role_title('mafia', chat).capitalize()) + format_roles(game),
        chat_id=chat,
        message_id=game['message_id'],
        reply_markup=keyboard
    )


@add_stage(5, 10)
def don_stage(game):
    chat = game['chat']
    keyboard = InlineKeyboardMarkup(row_width=8)
    keyboard.add(
        *[InlineKeyboardButton(
            text=f'{i + 1}',
            callback_data=f'check don {i + 1}'
        ) for i, player in enumerate(game['players']) if player['alive']]
    )

    bot.edit_message_text(
        i18n.t(
            chat, 'mafia_sleeps_don_checks',
            mafia=role_title('mafia', chat).capitalize(), don=role_title('don', chat).capitalize()
        ) + format_roles(game),
        chat_id=chat,
        message_id=game['message_id'],
        reply_markup=keyboard
    )


@add_stage(6, 10)
def sheriff_stage(game):
    chat = game['chat']
    keyboard = InlineKeyboardMarkup(row_width=8)
    keyboard.add(
        *[InlineKeyboardButton(
            text=f'{i + 1}',
            callback_data=f'check sheriff {i + 1}'
        ) for i, player in enumerate(game['players']) if player['alive']]
    )

    bot.edit_message_text(
        i18n.t(
            chat, 'don_sleeps_sheriff_checks',
            don=role_title('don', chat).capitalize(), sheriff=role_title('sheriff', chat)
        ) + format_roles(game),
        chat_id=chat,
        message_id=game['message_id'],
        reply_markup=keyboard
    )


@add_stage(7, 20)
def last_words_victim(game):
    chat = game['chat']
    update_dict = {'$set': {'shots': []}}

    mafia_shot = False
    saved_by_protection = False
    victim = None
    if len(set(game['shots'])) == 1 and len(game['shots']) == sum(p['role'] in ('don', 'mafia') and p['alive'] for p in game['players']):
        victim = game['shots'][0]
        if game['players'][victim]['alive']:
            if economy.use_item(game['players'][victim]['id'], 'protection'):
                saved_by_protection = True
            else:
                mafia_shot = True
                update_dict['$set'][f'players.{victim}.alive'] = False
                update_dict['$set']['victim'] = game['players'][victim]['id']

    database.games.update_one({'_id': game['_id']}, update_dict)

    if saved_by_protection:
        bot.send_message(
            chat,
            i18n.t(chat, 'victim_saved_by_protection', number=victim + 1, name=game['players'][victim]['name'])
        )
        go_to_next_stage(game)
        return

    if not mafia_shot:
        go_to_next_stage(game)
        return

    bot.edit_message_text(
        i18n.t(
            chat, 'morning_victim_killed',
            number=victim + 1, name=game['players'][victim]['name']
        ),
        chat_id=chat,
        message_id=game['message_id']
    )
