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


ROLES = ('don', 'mafia', 'sheriff', 'peace')


def role_title(role, chat_id):
    return i18n.t(chat_id, f'role_{role}')


def stop_game(game, reason_key, **reason_kwargs):
    reason = i18n.t(game['chat'], reason_key, **reason_kwargs)
    roles_text = '\n'.join(
        f'{i + 1}. {p["name"]} - {role_title(p.get("role", "?"), game["chat"])}'
        for i, p in enumerate(game['players'])
    )
    bot.try_to_send_message(
        game['chat'],
        i18n.t(game['chat'], 'game_over_roles_reveal', reason=reason, roles=roles_text)
    )
    database.games.delete_one({'_id': game['_id']})

