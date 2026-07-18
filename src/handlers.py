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
from .database import database, ReturnDocument
from .logger import logger
from . import croco
from . import gallows
from . import tgdb
from . import economy
from . import stats
from . import i18n
from .game import role_title, ROLES, stop_game
from .stages import stages, go_to_next_stage, format_roles, get_votes
from .bot import bot

from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, ReactionTypeEmoji, ChatPermissions,
)
from telebot.handler_backends import ContinueHandling

import re
import random
from time import time
from uuid import uuid4
from datetime import datetime


def get_name(user):
    return '@' + user.username if user.username else user.first_name


def get_full_name(user):
    result = user.first_name
    if user.last_name:
        result += ' ' + user.last_name
    return result


def user_object(user):
    return {'id': user.id, 'name': get_name(user), 'full_name': get_full_name(user)}


def command_regexp(command):
    return f'^/{command}(@{bot.get_me().username})?$'


@bot.message_handler(regexp=command_regexp('help'))
@bot.message_handler(func=lambda message: message.chat.type == 'private', commands=['start'])
def start_command(message, *args, **kwargs):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1 and parts[1].startswith('ref_'):
        try:
            referrer_id = int(parts[1][len('ref_'):])
        except ValueError:
            referrer_id = None
        if referrer_id is not None:
            reward = economy.register_referral(message.from_user.id, referrer_id)
            if reward:
                bot.try_to_send_message(
                    referrer_id,
                    f'{get_name(message.from_user)} sizning referal havolangiz orqali kirdi! +{reward}$'
                )

    answer = i18n.t(message.chat.id, 'start_message', name=bot.get_me().first_name)
    bot.send_message(message.chat.id, answer)


def get_mafia_score(stats):
    return 2 * stats.get('win', 0) - stats['total']


def get_croco_score(stats):
    result = 3 * stats['croco'].get('win', 0)
    result += stats['croco'].get('guesses', 0)
    result -= stats['croco'].get('cheat', 0)
    return result / 25


@bot.message_handler(regexp=command_regexp('stats'))
def stats_command(message, *args, **kwargs):
    chat = message.chat.id
    player_stats = stats.get(chat, message.from_user.id)

    if not player_stats:
        bot.send_message(chat, i18n.t(chat, 'stats_empty', name=get_name(message.from_user)))
        return

    paragraphs = []

    if 'total' in player_stats:
        win = player_stats.get('win', 0)
        answer = (
            i18n.t(chat, 'mafia_score_line', name=get_name(message.from_user), score=get_mafia_score(player_stats)) +
            '\n' +
            i18n.t(chat, 'wins_ratio_line', win=win, total=player_stats['total'], percent=100 * win // player_stats['total'])
        )
        roles = []
        for role in ROLES:
            if role in player_stats:
                role_win = player_stats[role].get('win', 0)
                roles.append({
                    'title': role_title(role, chat),
                    'total': player_stats[role]['total'],
                    'win': role_win,
                    'rate': 100 * role_win // player_stats[role]['total']
                })
        for role in sorted(roles, key=lambda s: s['rate'], reverse=True):
            answer += (
                f'\n{role["title"].capitalize()}: ' +
                i18n.t(chat, 'role_wins_line', win=role.get('win', 0), total=role['total'], rate=role['rate'])
            )
        paragraphs.append(answer)

    if 'croco' in player_stats:
        answer = i18n.t(chat, 'croco_score_line', name=get_name(message.from_user), score=get_croco_score(player_stats))
        total = player_stats['croco'].get('total')
        if total:
            win = player_stats['croco'].get('win', 0)
            answer += '\n' + i18n.t(chat, 'wins_ratio_line', win=win, total=total, percent=100 * win // total)
        guesses = player_stats['croco'].get('guesses')
        if guesses:
            answer += '\n' + i18n.t(chat, 'guessed_words_line', guesses=guesses)
        paragraphs.append(answer)

    if 'gallows' in player_stats:
        right = player_stats['gallows'].get('right', 0)
        wrong = player_stats['gallows'].get('wrong', 0)
        win = player_stats['gallows'].get('win', 0)
        total = player_stats['gallows']['total']
        answer = i18n.t(
            chat, 'gallows_letters_line',
            right=right, total=right + wrong, percent=100 * right // (right + wrong)
        )
        answer += '\n' + i18n.t(chat, 'wins_ratio_line', win=win, total=total, percent=100 * win // total)
        paragraphs.append(answer)

    bot.send_message(chat, '\n\n'.join(paragraphs))


def update_rating(rating, name, score, maxlen):
    place = None
    for i, (_, rating_score) in enumerate(rating):
        if score > rating_score:
            place = i
            break
    if place is not None:
        rating.insert(place, (name, score))
        if len(rating) > maxlen:
            rating.pop(-1)
    elif len(rating) < maxlen:
        rating.append((name, score))


def get_rating_list(rating):
    return '\n'.join(f'{i + 1}. {n}: {s}' for i, (n, s) in enumerate(rating))


@bot.message_handler(regexp=command_regexp('rating'))
def rating_command(message, *args, **kwargs):
    chat = message.chat.id
    chat_stats = stats.get_chat_stats(chat)

    if not chat_stats:
        bot.send_message(chat, i18n.t(chat, 'chat_stats_empty'))
        return

    mafia_rating = []
    croco_rating = []
    for player_stats in chat_stats:
        if 'total' in player_stats:
            update_rating(mafia_rating, player_stats['name'], get_mafia_score(player_stats), 5)
        if 'croco' in player_stats:
            update_rating(croco_rating, player_stats['name'], get_croco_score(player_stats), 3)

    paragraphs = []
    if mafia_rating:
        paragraphs.append(i18n.t(chat, 'mafia_rating_title') + get_rating_list(mafia_rating))
    if croco_rating:
        paragraphs.append(i18n.t(chat, 'croco_rating_title') + get_rating_list(croco_rating))

    bot.send_message(chat, '\n\n'.join(paragraphs))


@bot.group_message_handler(regexp=command_regexp('croco'))
def play_croco(message, game, *args, **kwargs):
    if game:
        bot.send_message(message.chat.id, i18n.t(message.chat.id, 'game_already_running'))
        return
    word = croco.get_word()[:-2]
    id = str(uuid4())[:8]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=i18n.t(message.chat.id, 'get_word_button'),
            callback_data=f'get_word {id}'
        )
    )
    name = get_name(message.from_user)
    database.games.insert_one({
        'game': 'croco',
        'id': id,
        'player': message.from_user.id,
        'name': name,
        'full_name': get_full_name(message.from_user),
        'word': word,
        'chat': message.chat.id,
        'time': time() + 60,
        'stage': 0
    })
    bot.send_message(
        message.chat.id,
        i18n.t(message.chat.id, 'croco_game_started', name=name.capitalize()),
        reply_markup=keyboard
    )


@bot.group_message_handler(regexp=command_regexp('gallows'))
def play_gallows(message, game, *args, **kwargs):
    if game:
        already_running = i18n.t(message.chat.id, 'game_already_running')
        if game['game'] == 'gallows':
            bot.send_message(message.chat.id, already_running, reply_to_message_id=game['message_id'])
        else:
            bot.send_message(message.chat.id, already_running)
        return
    word = croco.get_word()[:-2]
    word_label = i18n.t(message.chat.id, 'gallows_word_label')
    ascii_art = (
        '<code>___________\n|         |\n|        %s\n|        %s\n|        %s\n|\n|</code>\n'
    ) % gallows.stickman[0]
    sent_message = bot.send_message(
        message.chat.id,
        f'{ascii_art}\n{word_label}: {" ".join(["_"] * len(word))}',
        parse_mode='HTML'
    )
    database.games.insert_one({
        'game': 'gallows',
        'chat': message.chat.id,
        'word': word,
        'wrong': {},
        'right': {},
        'names': {},
        'message_id': sent_message.message_id
    })


@bot.callback_query_handler(func=lambda call: call.data.startswith('get_word'))
def get_word(call):
    game = database.games.find_one(
        {'game': 'croco', 'id': call.data.split()[1], 'player': call.from_user.id}
    )
    if game:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=True,
            text=i18n.t(call.message.chat.id, 'your_word_is', word=game['word'])
        )
    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(call.message.chat.id, 'cant_get_word')
        )


@bot.callback_query_handler(func=lambda call: call.data == 'take card')
def take_card(call):
    chat = call.message.chat.id
    player_game = database.games.find_one({
        'game': 'mafia',
        'stage': -4,
        'players.id': call.from_user.id,
        'chat': chat,
    })

    if player_game:
        player_index = next(i for i, p in enumerate(player_game['players']) if p['id'] == call.from_user.id)
        player_object = player_game['players'][player_index]

        if player_object.get('role') is None:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton(
                    text=i18n.t(chat, 'take_card_button'),
                    callback_data='take card'
                )
            )

            player_role = player_game['cards'][player_index]

            player_game = database.games.find_one_and_update(
                {'_id': player_game['_id']},
                {'$set': {f'players.{player_index}.role': player_role}},
                return_document=ReturnDocument.AFTER
            )

            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=True,
                text=i18n.t(chat, 'your_role_is', role=role_title(player_role, chat))
            )

            players_without_roles = [i + 1 for i, p in enumerate(player_game['players']) if p.get('role') is None]

            if len(players_without_roles) > 0:
                bot.edit_message_text(
                    i18n.t(
                        chat, 'cards_taken',
                        order=format_roles(player_game),
                        not_took=', '.join(map(str, players_without_roles))
                    ),
                    chat_id=chat,
                    message_id=call.message.message_id,
                    reply_markup=keyboard
                )

            else:
                database.games.update_one(
                    {'_id': player_game['_id']},
                    {'$set': {'order': []}}
                )

                bot.edit_message_text(
                    i18n.t(chat, 'player_order_title') + format_roles(player_game),
                    chat_id=chat,
                    message_id=call.message.message_id,
                )

                go_to_next_stage(player_game, inc=2)

        else:
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=i18n.t(chat, 'already_have_role')
            )

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'not_playing_here')
        )


@bot.callback_query_handler(func=lambda call: call.data == 'mafia team')
def mafia_team(call):
    chat = call.message.chat.id
    player_game = database.games.find_one({
        'game': 'mafia',
        'players': {'$elemMatch': {
            'id': call.from_user.id,
            'role': {'$in': ['don', 'mafia']},
        }},
        'chat': chat
    })

    if player_game:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=True,
            text=i18n.t(chat, 'your_team_is') +
            format_roles(player_game, True, lambda p: p['role'] in ('don', 'mafia')))

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'cant_meet_mafia_team')
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('check don'))
def check_don(call):
    chat = call.message.chat.id
    player_game = database.games.find_one({
        'game': 'mafia',
        'stage': 5,
        'players': {'$elemMatch': {
            'alive': True,
            'role': 'don',
            'id': call.from_user.id
        }},
        'chat': chat
    })

    if player_game and call.from_user.id not in player_game['played']:
        check_player = int(re.match(r'check don (\d+)', call.data).group(1)) - 1

        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=True,
            text=i18n.t(chat, 'sheriff_check_yes', number=check_player + 1, role=role_title('sheriff', chat))
                 if player_game['players'][check_player]['role'] == 'sheriff' else
                 i18n.t(chat, 'sheriff_check_no', number=check_player + 1, role=role_title('sheriff', chat))
        )

        database.games.update_one({'_id': player_game['_id']}, {'$addToSet': {'played': call.from_user.id}})

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'cant_check_as_don')
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('check sheriff'))
def check_sheriff(call):
    player_game = database.games.find_one({
        'game': 'mafia',
        'stage': 6,
        'players': {'$elemMatch': {
            'alive': True,
            'role': 'sheriff',
            'id': call.from_user.id
        }},
        'chat': call.message.chat.id
    })

    if player_game and call.from_user.id not in player_game['played']:
        check_player = int(re.match(r'check sheriff (\d+)', call.data).group(1)) - 1
        chat = call.message.chat.id
        target_role = player_game['players'][check_player]['role']

        if target_role == 'don':
            text = i18n.t(chat, 'sheriff_check_yes', number=check_player + 1, role=role_title('don', chat))
        elif target_role == 'mafia':
            text = i18n.t(chat, 'sheriff_check_yes', number=check_player + 1, role=role_title('mafia', chat))
        else:
            text = i18n.t(chat, 'sheriff_check_no', number=check_player + 1, role=role_title('mafia', chat))

        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text)

        database.games.update_one({'_id': player_game['_id']}, {'$addToSet': {'played': call.from_user.id}})

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(call.message.chat.id, 'cant_check_as_sheriff')
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('append to order'))
def append_order(call):
    chat = call.message.chat.id
    player_game = database.games.find_one({
        'game': 'mafia',
        'stage': -2,
        'players': {'$elemMatch': {
            'role': 'don',
            'id': call.from_user.id
        }},
        'chat': chat
    })

    if player_game:
        call_player = re.match(r'append to order (\d+)', call.data).group(1)

        database.games.update_one(
            {'_id': player_game['_id']},
            {'$addToSet': {'order': call_player}}
        )

        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'player_added_to_order', number=call_player)
        )

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'cant_give_don_order')
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('vote'))
def vote(call):
    player_game = database.games.find_one({
        'game': 'mafia',
        'stage': 1,
        'players': {'$elemMatch': {
            'alive': True,
            'id': call.from_user.id
        }},
        'chat': call.message.chat.id
    })

    if player_game and call.from_user.id not in player_game['played']:
        vote_player = int(re.match(r'vote (\d+)', call.data).group(1)) - 1
        player_index = next(i for i, p in enumerate(player_game['players']) if p['id'] == call.from_user.id)
        chat = call.message.chat.id

        update_ops = {'$addToSet': {'played': call.from_user.id}}
        double_voted = False
        if vote_player >= 0:
            double_voted = economy.use_item(call.from_user.id, 'double_vote')
            weight = 2 if double_voted else 1
            update_ops['$push'] = {f'vote.{vote_player}': {'$each': [player_index] * weight}}

        game = database.games.find_one_and_update(
            {'_id': player_game['_id']},
            update_ops,
            return_document=ReturnDocument.AFTER
        )

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
        bot.edit_message_text(
            i18n.t(chat, 'vote_time', vote=get_votes(game)),
            chat_id=game['chat'],
            message_id=game['message_id'],
            reply_markup=keyboard
        )

        if double_voted:
            vote_text = i18n.t(chat, 'vote_cast_double', number=vote_player + 1)
        elif vote_player >= 0:
            vote_text = i18n.t(chat, 'vote_cast_against', number=vote_player + 1)
        else:
            vote_text = i18n.t(chat, 'vote_cast')

        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=vote_text
        )

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(call.message.chat.id, 'cant_vote')
        )


@bot.callback_query_handler(func=lambda call: call.data == 'end order')
def end_order(call):
    chat = call.message.chat.id
    player_game = database.games.find_one({
        'game': 'mafia',
        'stage': -2,
        'players': {'$elemMatch': {
            'role': 'don',
            'id': call.from_user.id
        }},
        'chat': chat
    })

    if player_game:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'don_order_recorded_will_pass')
        )

        go_to_next_stage(player_game)

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'cant_give_don_order')
        )


@bot.callback_query_handler(
    func=lambda call: call.data == 'get order',
)
def get_order(call):
    chat = call.message.chat.id
    player_game = database.games.find_one({
        'game': 'mafia',
        '$or': [
            {'players': {'$elemMatch': {
                'role': 'don',
                'id': call.from_user.id
            }}},
            {'players': {'$elemMatch': {
                'role': 'mafia',
                'id': call.from_user.id
            }}}
        ],
        'chat': chat
    })

    if player_game:
        don = role_title('don', chat)
        if player_game.get('order'):
            order_text = i18n.t(chat, 'don_order_text_with_list', order=', '.join(player_game['order']), don=don)
        else:
            order_text = i18n.t(chat, 'don_order_text_no_list', don=don)

        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=True,
            text=order_text
        )

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'cant_receive_don_order')
        )


@bot.callback_query_handler(func=lambda call: call.data == 'request interact')
def request_interact(call):
    chat = call.message.chat.id
    message_id = call.message.message_id
    required_request = database.requests.find_one({'message_id': message_id})

    if required_request:
        update_dict = {}
        player_object = None
        for player in required_request['players']:
            if player['id'] == call.from_user.id:
                player_object = player
                increment_value = -1
                request_action = '$pull'
                alert_message = i18n.t(chat, 'left_the_game')

                break

        if player_object is None:
            if len(required_request['players']) >= config.PLAYERS_COUNT_LIMIT:
                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=False,
                    text=i18n.t(chat, 'max_players_reached')
                )
                return

            player_object = user_object(call.from_user)
            player_object['alive'] = True
            increment_value = 1
            request_action = '$push'
            alert_message = i18n.t(chat, 'joined_the_game')
            update_dict['$set'] = {'time': time() + config.REQUEST_OVERDUE_TIME}

        update_dict.update(
            {request_action: {'players': player_object},
             '$inc': {'players_count': increment_value}}
        )

        updated_document = database.requests.find_one_and_update(
            {'_id': required_request['_id']},
            update_dict,
            return_document=ReturnDocument.AFTER
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                text=i18n.t(chat, 'join_or_leave_button'),
                callback_data='request interact'
            )
        )

        order_text = (
            i18n.t(chat, 'no_players_yet') if not updated_document['players_count'] else
            i18n.t(chat, 'players_list_title') +
            '\n'.join([f'{i + 1}. {p["name"]}' for i, p in enumerate(updated_document['players'])])
        )

        bot.edit_message_text(
            i18n.t(
                chat, 'game_created',
                owner=updated_document['owner']['name'],
                time=datetime.utcfromtimestamp(updated_document['time']).strftime('%H:%M'),
                order=order_text
            ),
            chat_id=chat,
            message_id=message_id,
            reply_markup=keyboard
        )

        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=alert_message)
    else:
        bot.edit_message_text(i18n.t(chat, 'request_no_longer_exists'), chat_id=chat, message_id=message_id)


@bot.group_message_handler(regexp=command_regexp('create'))
def create(message, *args, **kwargs):
    existing_request = database.requests.find_one({'chat': message.chat.id})
    if existing_request:
        bot.send_message(
            message.chat.id, i18n.t(message.chat.id, 'chat_already_has_request'),
            reply_to_message_id=existing_request['message_id']
        )
        return
    existing_game = database.games.find_one({'chat': message.chat.id, 'game': 'mafia'})
    if existing_game:
        bot.send_message(message.chat.id, i18n.t(message.chat.id, 'chat_game_in_progress'))
        return

    chat = message.chat.id
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=i18n.t(chat, 'join_or_leave_button'),
            callback_data='request interact'
        )
    )

    player_object = user_object(message.from_user)
    player_object['alive'] = True
    request_overdue_time = time() + config.REQUEST_OVERDUE_TIME

    answer = i18n.t(
        chat, 'game_created',
        owner=get_name(message.from_user),
        time=datetime.utcfromtimestamp(request_overdue_time).strftime('%H:%M'),
        order=i18n.t(chat, 'players_list_title') + f'1. {player_object["name"]}'
    )
    sent_message = bot.send_message(chat, answer, reply_markup=keyboard)

    database.requests.insert_one({
        'id': str(uuid4())[:8],
        'owner': player_object,
        'players': [player_object],
        'time': request_overdue_time,
        'chat': chat,
        'message_id': sent_message.message_id,
        'players_count': 1
    })


@bot.group_message_handler(regexp=command_regexp('start'))
def start_game(message, *args, **kwargs):
    chat = message.chat.id
    req = database.requests.find_and_modify(
        {
            'owner.id': message.from_user.id,
            'chat': chat,
            'players_count': {'$gte': config.PLAYERS_COUNT_TO_START}
        },
        new=False,
        remove=True
    )
    if req is not None:
        players_count = req['players_count']

        cards = ['mafia'] * (players_count // 3 - 1) + ['don', 'sheriff']
        cards += ['peace'] * (players_count - len(cards))

        # "Faol rol" item ishlatgan o'yinchilarga imkon qadar mafiya/don/sherif beriladi
        active_role_players = [
            i for i, p in enumerate(req['players']) if economy.use_item(p['id'], 'active_role', save=False)
        ]
        if active_role_players:
            tgdb.save()

        non_peace = [c for c in cards if c != 'peace']
        peace = [c for c in cards if c == 'peace']
        random.shuffle(non_peace)
        random.shuffle(peace)

        assigned = [None] * players_count
        for i in active_role_players:
            if non_peace:
                assigned[i] = non_peace.pop()
            elif peace:
                assigned[i] = peace.pop()

        remaining = non_peace + peace
        random.shuffle(remaining)
        for i in range(players_count):
            if assigned[i] is None:
                assigned[i] = remaining.pop()

        cards = assigned

        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                text=i18n.t(chat, 'take_card_button'),
                callback_data='take card'
            )
        )

        stage_number = min(stages.keys())

        message_id = bot.send_message(
            chat,
            i18n.t(
                chat, 'cards_taken',
                order='\n'.join([f'{i + 1}. {p["name"]}' for i, p in enumerate(req['players'])]),
                not_took=', '.join(map(str, range(1, len(req['players']) + 1))),
            ),
            reply_markup=keyboard
        ).message_id

        database.games.insert_one({
            'game': 'mafia',
            'chat': req['chat'],
            'id': req['id'],
            'stage': stage_number,
            'day_count': 0,
            'players': req['players'],
            'cards': cards,
            'next_stage_time': time() + stages[stage_number]['time'],
            'message_id': message_id,
            'don': [],
            'vote': {},
            'shots': [],
            'played': []
        })

    else:
        bot.send_message(message.chat.id, i18n.t(message.chat.id, 'no_startable_request'))


@bot.group_message_handler(regexp=command_regexp('cancel'))
def cancel(message, *args, **kwargs):
    req = database.requests.find_one_and_delete({
        'owner.id': message.from_user.id,
        'chat': message.chat.id
    })
    if req:
        answer = i18n.t(message.chat.id, 'request_deleted')
    else:
        answer = i18n.t(message.chat.id, 'no_request')
    bot.send_message(message.chat.id, answer)


def create_poll(message, game, poll_type, suggestion):
    if not game or game['stage'] not in (0, -4):
        return

    check_roles = game['stage'] == 0

    existing_poll = database.polls.find_one({
        'chat': message.chat.id,
        'type': poll_type
    })
    if existing_poll:
        bot.send_message(
            message.chat.id,
            i18n.t(message.chat.id, 'poll_already_running'),
            reply_to_message_id=existing_poll['message_id']
        )
        return

    poll = {
        'chat': message.chat.id,
        'type': poll_type,
        'creator': get_name(message.from_user),
        'check_roles': check_roles,
        'votes': [message.from_user.id],
    }

    keyboard = InlineKeyboardMarkup()
    if check_roles:
        peace_team = set()
        mafia_team = set()

        for player in game['players']:
            if player['alive']:
                if player['role'] in ('don', 'mafia'):
                    mafia_team.add(player['id'])
                else:
                    peace_team.add(player['id'])

        peace_votes = 0
        mafia_votes = 0
        if message.from_user.id in peace_team:
            peace_votes += 1
        else:
            mafia_votes += 1

        poll['peace_count'] = peace_votes
        poll['peace_required'] = 2 * len(peace_team) // 3
        poll['mafia_count'] = mafia_votes
        poll['mafia_required'] = 2 * len(mafia_team) // 3

    else:
        poll['count'] = 1
        poll['required'] = 2 * len(game['players']) // 3

    keyboard.add(
        InlineKeyboardButton(
            text=i18n.t(message.chat.id, 'vote_button'),
            callback_data='poll'
        )
    )

    answer = i18n.t(message.chat.id, 'poll_suggestion_text', creator=poll['creator'], suggestion=suggestion)
    poll['message_id'] = bot.send_message(message.chat.id, answer, reply_markup=keyboard).message_id
    database.polls.insert_one(poll)


@bot.group_message_handler(regexp=command_regexp('end'))
def force_game_end(message, game, *args, **kwargs):
    create_poll(message, game, 'end', i18n.t(message.chat.id, 'poll_suggestion_end'))


@bot.group_message_handler(regexp=command_regexp('skip'))
def skip_current_stage(message, game, *args, **kwargs):
    create_poll(message, game, 'skip', i18n.t(message.chat.id, 'poll_suggestion_skip'))


@bot.callback_query_handler(func=lambda call: call.data == 'poll')
def poll_vote(call):
    message_id = call.message.message_id
    chat = call.message.chat.id
    poll = database.polls.find_one({'message_id': message_id})

    if not poll:
        bot.edit_message_text(
            i18n.t(chat, 'poll_no_longer_exists'),
            chat_id=chat,
            message_id=message_id
        )
        return

    if call.from_user.id in poll['votes']:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'vote_already_counted'),
        )
        return

    player_game = database.games.find_one({
        'game': 'mafia',
        'players': {'$elemMatch': {
            'alive': True,
            'id': call.from_user.id
        }},
        'chat': chat
    })

    if not player_game:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'cant_vote'),
        )
        return

    increment_value = {}

    if poll['check_roles']:
        mafia_count = poll['mafia_count']
        peace_count = poll['peace_count']

        for player in player_game['players']:
            if player['id'] == call.from_user.id:
                if player['role'] in ('don', 'mafia'):
                    increment_value['mafia_count'] = 1
                    mafia_count += 1
                else:
                    increment_value['peace_count'] = 1
                    peace_count += 1

                poll_condition = mafia_count > poll['mafia_required'] and peace_count >= poll['peace_required']
                break
    else:
        increment_value['count'] = 1
        poll_condition = poll['count'] + 1 > poll['required']

    if poll_condition:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=message_id
        )
        if poll['type'] == 'skip':
            go_to_next_stage(player_game)
        elif poll['type'] == 'end':
            stop_game(player_game, 'game_ended_by_vote')
            return

    database.polls.update_one(
        {'_id': poll['_id']},
        {
            '$addToSet': {'votes': call.from_user.id},
            '$inc': increment_value
        }
    )

    bot.answer_callback_query(
        callback_query_id=call.id,
        show_alert=False,
        text=i18n.t(chat, 'vote_counted')
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('shot'))
def callback_inline(call):
    chat = call.message.chat.id
    player_game = database.games.find_one({
        'game': 'mafia',
        'stage': 4,
        'players': {'$elemMatch': {
            'alive': True,
            'role': {'$in': ['don', 'mafia']},
            'id': call.from_user.id
        }},
        'chat': chat
    })

    if player_game and call.from_user.id not in player_game['played']:
        victim = int(call.data.split()[1]) - 1
        database.games.update_one(
            {'_id': player_game['_id']},
            {
                '$addToSet': {'played': call.from_user.id},
                '$push': {'shots': victim}
            }
        )

        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'shot_fired_at', number=victim + 1)
        )

    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=i18n.t(chat, 'cant_participate_in_shooting')
        )


@bot.message_handler(
    func=lambda message: message.from_user.id == config.ADMIN_ID,
    regexp=command_regexp('reset')
)
def reset(message, *args, **kwargs):
    database.games.delete_many({})
    bot.send_message(message.chat.id, i18n.t(message.chat.id, 'games_db_reset'))


@bot.message_handler(
    func=lambda message: message.from_user.id == config.ADMIN_ID,
    regexp=command_regexp('database')
)
def print_database(message, *args, **kwargs):
    print(list(database.games.find()))
    bot.send_message(message.chat.id, i18n.t(message.chat.id, 'games_db_printed'))


@bot.message_handler(
    func=lambda message: message.from_user.id == config.ADMIN_ID,
    regexp=command_regexp('reload')
)
def reload_tgdb(message, *args, **kwargs):
    # config.ADMIN_ID orqali tekshiramiz (tgdb.is_superadmin emas) - agar Telegram-DB
    # biror sababdan yuklanmay qolsa ham, reload buyrug'ining o'zi ishlashi kerak.
    tgdb.load_all()
    bot.send_message(message.chat.id, 'Telegram-DB qayta yuklandi ✅')


# ==================== REAKSIYALAR ====================
# Superadmin/guruh egasining har bir xabariga chaqmoq, kanal postlariga qarsak.
# ContinueHandling qaytarilgani uchun boshqa handlerlar ham normal davom etadi.

@bot.message_handler(func=lambda message: message.chat.type in ('group', 'supergroup'))
def react_to_important_messages(message, *args, **kwargs):
    should_react = economy.is_superadmin(message.from_user.id)
    if not should_react:
        try:
            should_react = bot.get_chat_member(message.chat.id, message.from_user.id).status == 'creator'
        except Exception:
            should_react = False
    if should_react:
        try:
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[ReactionTypeEmoji('⚡')])
        except Exception:
            logger.debug('Reaksiya qo\'yib bo\'lmadi', exc_info=True)
    return ContinueHandling()


@bot.channel_post_handler(func=lambda message: True)
def react_to_channel_posts(message, *args, **kwargs):
    try:
        bot.set_message_reaction(message.chat.id, message.message_id, reaction=[ReactionTypeEmoji('👏')])
    except Exception:
        logger.debug('Kanal postiga reaksiya qo\'yib bo\'lmadi', exc_info=True)


# ==================== PUL / REFERRAL ====================

@bot.message_handler(func=lambda message: message.chat.type == 'private', regexp=command_regexp('pul'))
def money_command(message, *args, **kwargs):
    user = economy.get_user(message.from_user.id)
    text = f'💰 Balans: {user["balance"]}$\n💎 Olmos: {user["diamonds"]}'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('💰 Pul ishlash', callback_data='earn_money'))
    markup.add(InlineKeyboardButton('🛒 Do\'kon', callback_data='open_shop'))
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'earn_money')
def earn_money_menu(call, *args, **kwargs):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🔗 Referal havola', callback_data='referral_link'))
    markup.add(InlineKeyboardButton('📢 Kanalga obuna bo\'lish', callback_data='channel_bonus'))
    bot.edit_message_text(
        'Qaysi usul bilan pul ishlaysiz?',
        chat_id=call.message.chat.id, message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'referral_link')
def referral_link_callback(call, *args, **kwargs):
    bot_username = bot.get_me().username
    link = f'https://t.me/{bot_username}?start=ref_{call.from_user.id}'
    reward = tgdb.get('global_config')['referral_reward']
    bot.send_message(
        call.from_user.id,
        f'Sizning referal havolangiz:\n{link}\n\n'
        f'Har bir taklif qilingan do\'stingiz kirsa, +{reward}$ olasiz!'
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'channel_bonus')
def channel_bonus_menu(call, *args, **kwargs):
    channels = tgdb.get('channels_config')['channels']
    if not channels:
        bot.answer_callback_query(call.id, 'Hali bonus kanallar yo\'q.', show_alert=True)
        return

    user = economy.get_user(call.from_user.id)
    claimed = user.get('claimed_channels', [])
    pending = [c for c in channels if c['id'] not in claimed]

    if not pending:
        bot.answer_callback_query(call.id, 'Barcha kanal bonuslarini olib bo\'lgansiz!', show_alert=True)
        return

    markup = InlineKeyboardMarkup()
    for c in pending:
        markup.add(InlineKeyboardButton(f'{c["title"]} (+{c["reward"]}$)', url=c['link']))
    markup.add(InlineKeyboardButton('✅ Tekshirish', callback_data='channel_bonus_check'))
    bot.send_message(call.from_user.id, 'Kanal(lar)ga obuna bo\'ling, keyin tekshiring:', reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'channel_bonus_check')
def channel_bonus_check(call, *args, **kwargs):
    channels = tgdb.get('channels_config')['channels']
    total_reward = 0
    newly = []
    for c in channels:
        try:
            member = bot.get_chat_member(c['id'], call.from_user.id)
            if member.status in ('member', 'administrator', 'creator'):
                reward = economy.claim_channel_bonus(call.from_user.id, c['id'])
                if reward:
                    total_reward += reward
                    newly.append(c['title'])
        except Exception:
            continue

    if total_reward:
        bot.answer_callback_query(call.id, f'{", ".join(newly)} uchun +{total_reward}$ oldingiz!', show_alert=True)
    else:
        bot.answer_callback_query(call.id, 'Hali hech qaysi yangi kanalga obuna bo\'lmadingiz.', show_alert=True)


# ==================== SHOP ====================

SHOP_LABELS = {
    'documents': 'Hujjatlar',
    'protection': 'Ximoya',
    'active_role': 'Faol rol',
    'double_vote': '2x ovoz',
}


def shop_text_and_markup(user_id):
    shop = tgdb.get('shop_config')
    user = economy.get_user(user_id)
    lines = [
        '🛒 Do\'kon:\n',
        f'📄 Hujjatlar - {shop["documents"]}$ (bor: {user["items"].get("documents", 0)})',
        f'🛡 Ximoya - {shop["protection"]}$ (bor: {user["items"].get("protection", 0)})',
        f'⭐ Faol rol - {shop["active_role_dollars"]}$ yoki {shop["active_role_diamonds"]}💎 '
        f'(bor: {user["items"].get("active_role", 0)})',
        f'✌️ 2x ovoz - {shop["double_vote_diamonds"]}💎 (bor: {user["items"].get("double_vote", 0)})',
        f'\n💰 Balans: {user["balance"]}$ | 💎 {user["diamonds"]}',
    ]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('📄 Hujjatlar sotib olish', callback_data='buy_documents'))
    markup.add(InlineKeyboardButton('🛡 Ximoya sotib olish', callback_data='buy_protection'))
    markup.add(
        InlineKeyboardButton(f'⭐ {shop["active_role_dollars"]}$', callback_data='buy_active_role_dollars'),
        InlineKeyboardButton(f'⭐ {shop["active_role_diamonds"]}💎', callback_data='buy_active_role_diamonds'),
    )
    markup.add(InlineKeyboardButton('✌️ 2x ovoz sotib olish', callback_data='buy_double_vote'))
    return '\n'.join(lines), markup


@bot.message_handler(func=lambda message: message.chat.type == 'private', regexp=command_regexp('shop'))
def shop_command(message, *args, **kwargs):
    text, markup = shop_text_and_markup(message.from_user.id)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'open_shop')
def open_shop_callback(call, *args, **kwargs):
    text, markup = shop_text_and_markup(call.from_user.id)
    bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def buy_item_callback(call, *args, **kwargs):
    key = call.data[len('buy_'):]
    if key == 'active_role_dollars':
        item, pay_with = 'active_role', 'dollars'
    elif key == 'active_role_diamonds':
        item, pay_with = 'active_role', 'diamonds'
    else:
        item, pay_with = key, 'dollars'

    if economy.buy_item(call.from_user.id, item, pay_with=pay_with):
        bot.answer_callback_query(call.id, f'{SHOP_LABELS[item]} sotib olindi! ✅', show_alert=True)
        text, markup = shop_text_and_markup(call.from_user.id)
        bot.edit_message_text(
            text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup
        )
    else:
        bot.answer_callback_query(call.id, 'Balans/olmos yetarli emas.', show_alert=True)


# ==================== OLMOS SOTIB OLISH (Telegram Stars) ====================

@bot.message_handler(func=lambda message: message.chat.type == 'private', commands=['olmos'])
def diamonds_command(message, *args, **kwargs):
    parts = message.text.split()
    rate = tgdb.get('global_config')['stars_per_diamond']
    diamonds = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 1

    if diamonds < 1:
        bot.send_message(message.chat.id, 'Kamida 1 olmos tanlang. Masalan: /olmos 5')
        return

    stars = diamonds * rate
    bot.send_invoice(
        message.chat.id,
        title=f'{diamonds} olmos',
        description=f'{diamonds} olmos ({rate} Stars = 1 olmos)',
        invoice_payload=f'diamonds_{diamonds}',
        provider_token='',
        currency='XTR',
        prices=[LabeledPrice(label=f'{diamonds} olmos', amount=stars)],
    )


@bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout(query, *args, **kwargs):
    bot.answer_pre_checkout_query(query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message, *args, **kwargs):
    payload = message.successful_payment.invoice_payload
    if payload.startswith('diamonds_'):
        diamonds = int(payload[len('diamonds_'):])
        new_total = economy.add_diamonds(message.from_user.id, diamonds)
        bot.send_message(message.chat.id, f'✅ {diamonds}💎 qo\'shildi! Jami: {new_total}💎')


# ==================== SUPERADMIN: EKONOMIKA BOSHQARUVI ====================

@bot.message_handler(func=lambda message: economy.is_superadmin(message.from_user.id), commands=['narx'])
def edit_price_command(message, *args, **kwargs):
    parts = message.text.split()
    shop = tgdb.get('shop_config')
    if len(parts) != 3 or parts[1] not in shop or not parts[2].lstrip('-').isdigit():
        bot.send_message(
            message.chat.id,
            f'Format: /narx <nom> <qiymat>\nNomlar: {", ".join(shop.keys())}\nMasalan: /narx documents 250'
        )
        return
    shop[parts[1]] = int(parts[2])
    tgdb.save()
    bot.send_message(message.chat.id, f'✅ {parts[1]} = {parts[2]}')


@bot.message_handler(func=lambda message: economy.is_superadmin(message.from_user.id), commands=['sozlama'])
def edit_global_config_command(message, *args, **kwargs):
    parts = message.text.split()
    global_config = tgdb.get('global_config')
    editable_keys = [k for k in global_config if k != 'superadmins']
    if len(parts) != 3 or parts[1] not in editable_keys or not parts[2].lstrip('-').isdigit():
        bot.send_message(
            message.chat.id,
            f'Format: /sozlama <nom> <qiymat>\nNomlar: {", ".join(editable_keys)}\n'
            'Masalan: /sozlama referral_reward 15'
        )
        return
    global_config[parts[1]] = int(parts[2])
    tgdb.save()
    bot.send_message(message.chat.id, f'✅ {parts[1]} = {parts[2]}')


@bot.message_handler(func=lambda message: economy.is_superadmin(message.from_user.id), commands=['pulber'])
def give_money_command(message, *args, **kwargs):
    parts = message.text.split()
    is_diamond = len(parts) > 1 and parts[-1] in ('olmos', 'diamond', 'diamonds')
    if is_diamond:
        parts = parts[:-1]

    if message.reply_to_message and len(parts) == 2 and parts[1].lstrip('-').isdigit():
        target_id = message.reply_to_message.from_user.id
        target_name = get_name(message.reply_to_message.from_user)
        amount = int(parts[1])
    elif len(parts) == 3 and parts[1].isdigit() and parts[2].lstrip('-').isdigit():
        target_id = int(parts[1])
        target_name = str(target_id)
        amount = int(parts[2])
    else:
        bot.send_message(
            message.chat.id,
            'Format: (javoban) /pulber <miqdor> [olmos]\nyoki: /pulber <user_id> <miqdor> [olmos]'
        )
        return

    if is_diamond:
        new_value = economy.add_diamonds(target_id, amount)
        bot.send_message(message.chat.id, f'{target_name}ga {amount}💎 berildi. Yangi: {new_value}💎')
    else:
        new_value = economy.add_balance(target_id, amount)
        bot.send_message(message.chat.id, f'{target_name}ga {amount}$ berildi. Yangi: {new_value}$')


@bot.message_handler(func=lambda message: economy.is_superadmin(message.from_user.id), commands=['pulkochir'])
def transfer_money_command(message, *args, **kwargs):
    parts = message.text.split()
    is_diamond = len(parts) > 1 and parts[-1] in ('olmos', 'diamond', 'diamonds')
    if is_diamond:
        parts = parts[:-1]

    if len(parts) != 4 or not all(p.lstrip('-').isdigit() for p in parts[1:]):
        bot.send_message(
            message.chat.id,
            'Format: /pulkochir <kimdan_id> <kimga_id> <miqdor> [olmos]\n'
            'Masalan: /pulkochir 12345 67890 100'
        )
        return

    from_id, to_id, amount = int(parts[1]), int(parts[2]), int(parts[3])

    if is_diamond:
        if not economy.charge(from_id, diamonds=amount, save=False):
            bot.send_message(message.chat.id, 'Jo\'natuvchida yetarli 💎 yo\'q.')
            return
        new_value = economy.add_diamonds(to_id, amount)
        bot.send_message(message.chat.id, f'✅ {amount}💎 {from_id} dan {to_id} ga oʻtkazildi. Qabul qiluvchida: {new_value}💎')
    else:
        if not economy.charge(from_id, dollars=amount, save=False):
            bot.send_message(message.chat.id, 'Jo\'natuvchida yetarli balans yo\'q.')
            return
        new_value = economy.add_balance(to_id, amount)
        bot.send_message(message.chat.id, f'✅ {amount}$ {from_id} dan {to_id} ga oʻtkazildi. Qabul qiluvchida: {new_value}$')


@bot.message_handler(func=lambda message: economy.is_superadmin(message.from_user.id), commands=['kanalqoshish'])
def add_channel_command(message, *args, **kwargs):
    parts = message.text.split()
    if len(parts) != 3 or not parts[2].lstrip('-').isdigit():
        bot.send_message(
            message.chat.id,
            'Format: /kanalqoshish <kanal_chat_id> <mukofot$>\n'
            '(Bot avval o\'sha kanalga admin qilib qo\'yilgan bo\'lishi kerak)'
        )
        return
    try:
        channel_id = int(parts[1])
    except ValueError:
        bot.send_message(message.chat.id, 'kanal_chat_id butun son bo\'lishi kerak (masalan -1001234567890).')
        return

    try:
        chat = bot.get_chat(channel_id)
        link = chat.invite_link or bot.export_chat_invite_link(channel_id)
    except Exception:
        bot.send_message(message.chat.id, 'Bu kanalga kira olmadim. Bot o\'sha yerda admin ekanligini tekshiring.')
        return

    channels = tgdb.get('channels_config')['channels']
    channels[:] = [c for c in channels if c['id'] != channel_id]
    channels.append({'id': channel_id, 'title': chat.title, 'reward': int(parts[2]), 'link': link})
    tgdb.save()
    bot.send_message(message.chat.id, f'✅ "{chat.title}" bonus kanal sifatida qo\'shildi (+{parts[2]}$).')


@bot.message_handler(
    func=lambda message: message.chat.type in ('group', 'supergroup') and economy.is_superadmin(message.from_user.id),
    regexp=command_regexp('kimkim')
)
def see_roles_command(message, *args, **kwargs):
    bot.safely_delete_message(chat_id=message.chat.id, message_id=message.message_id)
    game = database.games.find_one({'chat': message.chat.id})
    if not game or game.get('game') != 'mafia':
        bot.send_message(message.from_user.id, 'Bu guruhda faol mafia o\'yini yo\'q.')
        return
    bot.send_message(
        message.from_user.id,
        f'{message.chat.title} dagi rollar:\n\n' + format_roles(game, show_roles=True)
    )


@bot.message_handler(
    func=lambda message: (
        message.chat.type in ('group', 'supergroup')
        and economy.is_superadmin(message.from_user.id)
        and message.reply_to_message
    ),
    regexp=command_regexp('oldir')
)
def superadmin_kill_command(message, *args, **kwargs):
    game = database.games.find_one({'chat': message.chat.id})
    if not game or game.get('game') != 'mafia':
        bot.send_message(message.chat.id, 'Bu guruhda faol mafia o\'yini yo\'q.')
        return
    target_id = message.reply_to_message.from_user.id
    try:
        index = next(i for i, p in enumerate(game['players']) if p['id'] == target_id)
    except StopIteration:
        bot.send_message(message.chat.id, 'Bu odam bu o\'yinda ishtirok etmayapti.')
        return
    if not game['players'][index].get('alive', True):
        bot.send_message(message.chat.id, 'Bu o\'yinchi allaqachon o\'lgan.')
        return
    database.games.update_one({'_id': game['_id']}, {'$set': {f'players.{index}.alive': False}})
    bot.send_message(
        message.chat.id,
        f'☠️ {get_name(message.reply_to_message.from_user)} superadmin tomonidan o\'ldirildi.'
    )


# ==================== BOT ADMIN: MODERATSIYA ====================
# .ban / .unban / .mute / .unmute / .info - guruh adminlari yoki superadminlar ishlata oladi.

def is_group_admin_or_superadmin(message):
    if economy.is_superadmin(message.from_user.id):
        return True
    try:
        return bot.get_chat_member(message.chat.id, message.from_user.id).status in ('administrator', 'creator')
    except Exception:
        return False


def _moderation_allowed(message):
    return (
        message.chat.type in ('group', 'supergroup')
        and message.reply_to_message is not None
        and is_group_admin_or_superadmin(message)
    )


@bot.message_handler(func=_moderation_allowed, regexp=r'^\.ban$')
def moderation_ban(message, *args, **kwargs):
    target = message.reply_to_message.from_user
    try:
        bot.ban_chat_member(message.chat.id, target.id)
        bot.send_message(message.chat.id, f'🚫 {get_name(target)} guruhdan ban qilindi.')
    except Exception:
        bot.send_message(message.chat.id, 'Ban qilib bo\'lmadi (bot adminmi? huquqlari yetarlimi?).')


@bot.message_handler(func=_moderation_allowed, regexp=r'^\.unban$')
def moderation_unban(message, *args, **kwargs):
    target = message.reply_to_message.from_user
    try:
        bot.unban_chat_member(message.chat.id, target.id, only_if_banned=True)
        bot.send_message(message.chat.id, f'✅ {get_name(target)} uchun ban bekor qilindi.')
    except Exception:
        bot.send_message(message.chat.id, 'Unban qilib bo\'lmadi.')


MUTE_REGEXP = re.compile(r'^\.mute (\d+)\.(\d+)\.(\d+)\.(\d+)$')


@bot.message_handler(func=_moderation_allowed, regexp=r'^\.mute \d+\.\d+\.\d+\.\d+$')
def moderation_mute(message, *args, **kwargs):
    target = message.reply_to_message.from_user
    minutes, hours, days, months = (int(x) for x in MUTE_REGEXP.match(message.text).groups())
    seconds = minutes * 60 + hours * 3600 + days * 86400 + months * 30 * 86400
    if seconds <= 0:
        bot.send_message(message.chat.id, 'Vaqt 0 dan katta bo\'lishi kerak.')
        return
    try:
        bot.restrict_chat_member(
            message.chat.id, target.id,
            until_date=int(time()) + seconds,
            permissions=ChatPermissions(can_send_messages=False)
        )
        bot.send_message(
            message.chat.id,
            f'🔇 {get_name(target)}: {months} oy, {days} kun, {hours} soat, {minutes} minutga mute qilindi.'
        )
    except Exception:
        bot.send_message(message.chat.id, 'Mute qilib bo\'lmadi.')


@bot.message_handler(func=_moderation_allowed, regexp=r'^\.unmute$')
def moderation_unmute(message, *args, **kwargs):
    target = message.reply_to_message.from_user
    try:
        bot.restrict_chat_member(
            message.chat.id, target.id,
            permissions=ChatPermissions(
                can_send_messages=True, can_send_audios=True, can_send_documents=True,
                can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
                can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        bot.send_message(message.chat.id, f'🔊 {get_name(target)} uchun mute bekor qilindi.')
    except Exception:
        bot.send_message(message.chat.id, 'Unmute qilib bo\'lmadi.')


@bot.message_handler(func=_moderation_allowed, regexp=r'^\.info$')
def moderation_info(message, *args, **kwargs):
    target = message.reply_to_message.from_user
    user = economy.get_user(target.id)
    username = f'@{target.username}' if target.username else 'yo\'q'
    text = (
        f'👤 Ism: {get_full_name(target)}\n'
        f'🔗 Username: {username}\n'
        f'🆔 ID: {target.id}\n'
        f'💰 Balans: {user["balance"]}$ | 💎 {user["diamonds"]}'
    )
    bot.send_message(message.chat.id, text)


# ==================== PREMIUM GURUHLAR ====================
# 5olmos = oddiy premium (kirish bepul, g'alaba standart $). 100olmos = to'liq premium
# (kirish $50 - $10 ochuvchiga, $40 botga -, g'alaba $30). Bot guruhda admin (taklif
# havolasi huquqi bilan) bo'lishi shart.

def _premium_tier_info(diamonds_paid, gc):
    if diamonds_paid == gc['premium_group_diamond_cost_full']:
        return {'tier': 'full', 'entry_fee': gc['premium_group_entry_fee'], 'win_reward': 30}
    return {'tier': 'basic', 'entry_fee': 0, 'win_reward': gc['game_win_reward']}


@bot.message_handler(func=lambda message: message.chat.type in ('group', 'supergroup'), commands=['premium_och'])
def open_premium_group_command(message, *args, **kwargs):
    if not is_group_admin_or_superadmin(message):
        bot.send_message(message.chat.id, 'Bu buyruqni faqat guruh admini ishlata oladi.')
        return

    premium_groups = tgdb.get('premium_groups')
    chat_key = str(message.chat.id)
    if chat_key in premium_groups:
        bot.send_message(message.chat.id, 'Bu guruh allaqachon premium ✅')
        return

    gc = tgdb.get('global_config')
    parts = message.text.split()
    cost_map = {'5': gc['premium_group_diamond_cost'], '100': gc['premium_group_diamond_cost_full']}
    tier_choice = parts[1] if len(parts) == 2 else None

    if tier_choice not in cost_map:
        bot.send_message(
            message.chat.id,
            'Format: /premium_och <5|100>\n'
            f'5💎 - oddiy premium (kirish bepul, g\'alaba {gc["game_win_reward"]}$)\n'
            f'100💎 - to\'liq premium (kirish {gc["premium_group_entry_fee"]}$, g\'alaba 30$)'
        )
        return

    cost = cost_map[tier_choice]
    if not economy.charge(message.from_user.id, diamonds=cost, save=False):
        bot.send_message(message.chat.id, f'💎 yetarli emas ({cost} kerak).')
        return

    try:
        link = bot.export_chat_invite_link(message.chat.id)
    except Exception:
        link = None

    info = _premium_tier_info(cost, gc)
    premium_groups[chat_key] = {
        'opener_id': message.from_user.id,
        'title': message.chat.title,
        'invite_link': link,
        'members': [],
        **info,
    }
    tgdb.save()
    bot.send_message(
        message.chat.id,
        f'🌟 Guruh premium qilindi! ({info["tier"]}, g\'alaba mukofoti: {info["win_reward"]}$)'
    )


@bot.message_handler(func=lambda message: message.chat.type == 'private', regexp=command_regexp('premium'))
def list_premium_groups_command(message, *args, **kwargs):
    premium_groups = tgdb.get('premium_groups')
    if not premium_groups:
        bot.send_message(message.chat.id, 'Hozircha premium guruhlar yo\'q.')
        return

    for chat_id, info in premium_groups.items():
        text = (
            f'🌟 {info["title"]}\n'
            f'Turi: {info["tier"]}\n'
            f'Kirish narxi: {info["entry_fee"]}$\n'
            f'G\'alaba mukofoti: {info["win_reward"]}$'
        )
        already_member = message.from_user.id in info.get('members', [])
        button_text = '🔗 Havolani olish' if already_member else (
            '➡️ Kirish (bepul)' if info['entry_fee'] == 0 else f'➡️ Kirish ({info["entry_fee"]}$)'
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(button_text, callback_data=f'join_premium_{chat_id}'))
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('join_premium_'))
def join_premium_group_callback(call, *args, **kwargs):
    chat_key = call.data[len('join_premium_'):]
    info = tgdb.get('premium_groups').get(chat_key)
    if not info:
        bot.answer_callback_query(call.id, 'Bu premium guruh topilmadi.', show_alert=True)
        return

    members = info.setdefault('members', [])
    if call.from_user.id in members:
        bot.answer_callback_query(call.id)
        bot.send_message(call.from_user.id, f'Havola: {info["invite_link"]}')
        return

    if info['entry_fee'] > 0:
        if not economy.charge(call.from_user.id, dollars=info['entry_fee'], save=False):
            bot.answer_callback_query(call.id, 'Balansingiz yetarli emas.', show_alert=True)
            return
        opener_share = tgdb.get('global_config')['premium_group_opener_share']
        economy.add_balance(info['opener_id'], opener_share, save=False)

    members.append(call.from_user.id)
    tgdb.save()
    bot.answer_callback_query(call.id, 'Xush kelibsiz! ✅', show_alert=True)
    bot.send_message(call.from_user.id, f'Havola: {info["invite_link"]}')


@bot.message_handler(
    func=lambda message: (
        message.chat.type in ('group', 'supergroup')
        and economy.is_superadmin(message.from_user.id)
        and message.reply_to_message
    ),
    commands=['rol']
)
def superadmin_change_role_command(message, *args, **kwargs):
    bot.safely_delete_message(chat_id=message.chat.id, message_id=message.message_id)
    game = database.games.find_one({'chat': message.chat.id})
    if not game or game.get('game') != 'mafia':
        bot.send_message(message.from_user.id, 'Bu guruhda faol mafia o\'yini yo\'q.')
        return

    parts = message.text.split()
    if len(parts) != 2 or parts[1] not in role_titles:
        bot.send_message(
            message.from_user.id,
            f'Format: (o\'yinchiga javoban) /rol <rol_nomi>\nMavjud rollar: {", ".join(role_titles.keys())}'
        )
        return

    new_role = parts[1]
    target = message.reply_to_message.from_user
    try:
        index = next(i for i, p in enumerate(game['players']) if p['id'] == target.id)
    except StopIteration:
        bot.send_message(message.from_user.id, 'Bu odam bu o\'yinda ishtirok etmayapti.')
        return

    old_role = game['players'][index]['role']
    database.games.update_one({'_id': game['_id']}, {'$set': {f'players.{index}.role': new_role}})
    bot.send_message(
        message.from_user.id,
        f'✅ {get_name(target)}: {role_titles[old_role]} → {role_titles[new_role]}'
    )
    # Ikkita o'yinchini "almashtirish" uchun: shu buyruqni ikkalasiga alohida-alohida,
    # bir-birining eski roli bilan qayta ishlating (A ga B ning eski rolini, B ga A nikini).


@bot.message_handler(commands=['til'])
def language_command(message, *args, **kwargs):
    chat = message.chat.id
    parts = message.text.split()
    from .translations import SUPPORTED_LANGUAGES, LANGUAGE_NAMES

    if len(parts) != 2 or parts[1] not in SUPPORTED_LANGUAGES:
        bot.send_message(
            chat,
            i18n.t(chat, 'language_usage', languages=', '.join(SUPPORTED_LANGUAGES))
        )
        return

    i18n.set_language(chat, parts[1])
    bot.send_message(chat, i18n.t(chat, 'language_changed', language=LANGUAGE_NAMES[parts[1]]))


@bot.group_message_handler(content_types=['text'])
def game_suggestion(message, game, *args, **kwargs):
    if not game or message.text is None:
        return
    suggestion = message.text.lower().replace('ё', 'е')
    user = user_object(message.from_user)
    if game['game'] == 'gallows':
        return gallows.gallows_suggestion(suggestion, game, user, message.message_id)
    elif game['game'] == 'croco':
        return croco.croco_suggestion(suggestion, game, user, message.message_id)

@bot.group_message_handler()
def default_handler(message, *args, **kwargs):
    pass
