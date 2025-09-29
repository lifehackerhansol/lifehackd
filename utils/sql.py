#
# Copyright (C) 2021-present lifehackerhansol
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import contextlib
import logging
import os
from datetime import datetime

import aiomysql
from pymysql.err import OperationalError
from discord.utils import time_snowflake


log = logging.getLogger("bot")


class SQLDB():
    pool: aiomysql.Pool

    def __init__(self, bot):
        self.bot = bot

    @contextlib.asynccontextmanager
    async def acquire_pool_cursor(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                yield cursor

    async def initialize(self):
        # Perform migrations
        self.pool = await aiomysql.create_pool(host=self.bot.config['MYSQL_HOST'],
                                               port=self.bot.config['MYSQL_PORT'],
                                               user=self.bot.config['MYSQL_USER'],
                                               password=self.bot.config['MYSQL_PASS'],
                                               db=self.bot.config['MYSQL_DB'],
                                               loop=self.bot.loop,
                                               autocommit=True)

        async with self.acquire_pool_cursor() as cursor:
            version = await cursor.execute("SELECT id FROM db_info")
            if not version:
                revision = 0
            else:
                ret = await cursor.fetchone()
                revision = ret["id"]

            updates = os.listdir("dbupdate")

            for i, x in enumerate(updates):
                updates[i] = x.replace(".sql", "")
            to_update = []

            for i in updates:
                if int(i) > revision:
                    to_update.append(int(i))

            if not to_update:
                log.info("Database is up to date.")
            else:
                to_update.sort()
                log.info(f"Updating database from {revision} to {to_update[-1]}")
                for i in to_update:
                    with open(f"dbupdate/{i}.sql", "r") as f:
                        commands = f.read().split(';')
                        for j in commands:
                            try:
                                await cursor.execute(j)
                            except OperationalError:
                                # Due to the nature of split() sometimes newlines get added here
                                # which freaks out pymysql
                                print("Command skipped: ", j)
                await cursor.execute(f"UPDATE db_info SET id={to_update[-1]}")
                log.info(f"Updated database from {revision} to {to_update[-1]}")

    def generate_id(self) -> int:
        return time_snowflake(datetime.now())

    async def get_guild(self, guild_id: int):
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"SELECT * FROM guilds WHERE id={guild_id};")
            return await cursor.fetchall()

    async def add_guild(self, guild_id: int):
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"INSERT INTO guilds (id) VALUES ({guild_id});")

    async def get_warns(self, user_id: int, guild_id: int):
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"SELECT * FROM warns WHERE user_id={user_id} AND guild_id={guild_id};")
            return await cursor.fetchall()

    async def add_warn(self, user_id: int, issuer_id: int, guild_id: int, reason: str):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(
                f"INSERT INTO warns (id, user_id, issuer_id, guild_id, reason) VALUES ({self.generate_id()}, {user_id}, {issuer_id}, {guild_id}, '{reason}');"
            )

    async def remove_warn(self, user_id: int, guild_id: int, index: int):
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"SELECT * FROM warns WHERE user_id={user_id} AND guild_id={guild_id};")
            warns = await cursor.fetchall()
            warnid = warns[index - 1]["id"]
            await cursor.execute(f"DELETE FROM warns WHERE id={warnid};")

    async def add_modrole(self, guild_id: int, role_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"INSERT INTO modroles (id, guild_id) VALUES ({role_id}, {guild_id});")

    async def get_modroles(self, guild_id: int):
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"SELECT id FROM modroles WHERE guild_id={guild_id};")
            return await cursor.fetchall()

    async def remove_modrole(self, guild_id: int, role_id: int) -> int:
        modroles = await self.get_modroles(guild_id)
        if not modroles:
            return 1
        for role in modroles:
            if role_id == role['id']:
                async with self.acquire_pool_cursor() as cursor:
                    await cursor.execute(f"DELETE FROM modroles WHERE id={role_id} AND guild_id={guild_id};")
                return 0
        return 2

    async def add_muterole(self, guild_id: int, role_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"UPDATE guilds SET mute_id={role_id} WHERE id={guild_id};")

    async def get_muterole(self, guild_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            return None
        return guild[0]['mute_id']

    async def remove_muterole(self, guild_id: int, role_id: int) -> int:
        muterole = await self.get_muterole(guild_id)
        if not muterole:
            return 1
        if muterole == role_id:
            async with self.acquire_pool_cursor() as cursor:
                await cursor.execute(f"UPDATE guilds SET mute_id=NULL WHERE id={guild_id};")
            return 0
        return 2

    async def add_logchannel(self, guild_id: int, channel_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"UPDATE guilds SET logchannel_id={channel_id} WHERE id={guild_id};")

    async def get_logchannel(self, guild_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            return None
        return guild[0]['logchannel_id']

    async def remove_logchannel(self, guild_id: int, channel_id: int) -> int:
        logchannel = await self.get_logchannel(guild_id)
        if not logchannel:
            return 1
        if logchannel == channel_id:
            async with self.acquire_pool_cursor() as cursor:
                await cursor.execute(f"UPDATE guilds SET logchannel_id=NULL WHERE id={guild_id};")
            return 0
        return 2

    async def get_invitefilter(self, guild_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            return None
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"SELECT * FROM invitefilter WHERE guild_id={guild_id};")
            return await cursor.fetchall()

    async def add_invitefilter(self, guild_id: int, invite: str, alias: str):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(
                f"INSERT INTO invitefilter (id, guild_id, invite, alias) VALUES ({self.generate_id()}, {guild_id}, '{invite}', '{alias}');"
            )

    async def remove_invitefilter(self, guild_id: int, alias):
        async with self.acquire_pool_cursor() as cursor:
            await cursor.execute(f"SELECT * FROM invitefilter WHERE guild_id={guild_id} AND alias={alias};")
            invite = await cursor.fetchall()
            inviteid = invite[0]["id"]
            await cursor.execute(f"DELETE FROM invitefilter WHERE id={inviteid};")
