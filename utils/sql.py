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

import logging
import os
import sqlite3
from datetime import datetime

import aiosqlite
from discord.utils import time_snowflake


log = logging.getLogger("bot")


class SQLDB():
    def __init__(self, bot):
        self.bot = bot
        self.dbpath = "data/lifehackd.db"

        # Perform migrations
        # Needs sqlite3 here because __init__ is not async
        conn = sqlite3.connect(self.dbpath)
        try:
            user_version = conn.execute("PRAGMA user_version")
            ret = user_version.fetchone()
            revision = ret[0]

        # if error, set to 0
        # breaks backward compatibility with pre-user_version dbs
        except sqlite3.Error:
            log.debug(f"{self.dbpath} has no user_version set. Applying all schemas...")
            revision = 0

        updates = os.listdir("dbupdate")

        for i, x in enumerate(updates):
            updates[i] = x.replace(".sql", "")
        to_update = []

        for i in updates:
            if int(i) > revision:
                to_update.append(int(i))

        if not to_update:
            log.info(f"{self.dbpath} is up to date.")
        else:
            to_update.sort()
            log.info(f"Updating {self.dbpath} from {revision} to {to_update[-1]}")
            for i in to_update:
                with open(f"dbupdate/{i}.sql", "r") as f:
                    conn.executescript(f.read())
            conn.execute(f"PRAGMA user_version={to_update[-1]}")
            log.info(f"Updated {self.dbpath} from {revision} to {to_update[-1]}")
            conn.close()

    def generate_id(self) -> int:
        return time_snowflake(datetime.now())

    async def get_guild(self, guild_id: int):
        async with aiosqlite.connect(self.dbpath) as conn:
            conn.row_factory = sqlite3.Row
            return await conn.execute_fetchall(f"SELECT * FROM guilds WHERE id={guild_id};")

    async def add_guild(self, guild_id: int):
        async with aiosqlite.connect(self.dbpath) as conn:
            await conn.execute_insert(f"INSERT INTO guilds (id) VALUES ({guild_id});")
            await conn.commit()

    async def get_warns(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.dbpath) as conn:
            conn.row_factory = sqlite3.Row
            return await conn.execute_fetchall(f"SELECT * FROM warns WHERE user_id={user_id} AND guild_id={guild_id};")

    async def add_warn(self, user_id: int, issuer_id: int, guild_id: int, reason: str):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with aiosqlite.connect(self.dbpath) as conn:
            await conn.execute_insert(
                f"INSERT INTO warns (id, user_id, issuer_id, guild_id, reason) VALUES ({self.generate_id()}, {user_id}, {issuer_id}, {guild_id}, '{reason}');"
            )
            await conn.commit()

    async def remove_warn(self, user_id: int, guild_id: int, index: int):
        async with aiosqlite.connect(self.dbpath) as conn:
            conn.row_factory = sqlite3.Row
            warns = await conn.execute_fetchall(f"SELECT * FROM warns WHERE user_id={user_id} AND guild_id={guild_id};")
            warnid = warns[index - 1]["id"]
            await conn.execute(f"DELETE FROM warns WHERE id={warnid};")
            await conn.commit()

    async def add_modrole(self, guild_id: int, role_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with aiosqlite.connect(self.dbpath) as conn:
            await conn.execute_insert(f"INSERT INTO modroles (id, guild_id) VALUES ({role_id}, {guild_id});")
            await conn.commit()

    async def get_modroles(self, guild_id: int):
        async with aiosqlite.connect(self.dbpath) as conn:
            conn.row_factory = sqlite3.Row
            return await conn.execute_fetchall(f"SELECT id FROM modroles WHERE guild_id={guild_id};")

    async def remove_modrole(self, guild_id: int, role_id: int) -> int:
        modroles = await self.get_modroles(guild_id)
        if not modroles:
            return 1
        for role in modroles:
            if role_id == role['id']:
                async with aiosqlite.connect(self.dbpath) as conn:
                    await conn.execute(f"DELETE FROM modroles WHERE id={role_id} AND guild_id={guild_id};")
                    await conn.commit()
                return 0
        return 2

    async def add_muterole(self, guild_id: int, role_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with aiosqlite.connect(self.dbpath) as conn:
            await conn.execute(f"UPDATE guilds SET mute_id={role_id} WHERE id={guild_id};")
            await conn.commit()

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
            async with aiosqlite.connect(self.dbpath) as conn:
                await conn.execute(f"UPDATE guilds SET mute_id=NULL WHERE id={guild_id};")
                await conn.commit()
            return 0
        return 2

    async def add_logchannel(self, guild_id: int, channel_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with aiosqlite.connect(self.dbpath) as conn:
            await conn.execute(f"UPDATE guilds SET logchannel_id={channel_id} WHERE id={guild_id};")
            await conn.commit()

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
            async with aiosqlite.connect(self.dbpath) as conn:
                await conn.execute(f"UPDATE guilds SET logchannel_id=NULL WHERE id={guild_id};")
                await conn.commit()
            return 0
        return 2

    async def get_invitefilter(self, guild_id: int):
        guild = await self.get_guild(guild_id)
        if not guild:
            return None
        async with aiosqlite.connect(self.dbpath) as conn:
            conn.row_factory = sqlite3.Row
            return await conn.execute_fetchall(f"SELECT * FROM invitefilter WHERE guild_id={guild_id};")

    async def add_invitefilter(self, guild_id: int, invite: str, alias: str):
        guild = await self.get_guild(guild_id)
        if not guild:
            await self.add_guild(guild_id)
        async with aiosqlite.connect(self.dbpath) as conn:
            await conn.execute_insert(
                f"INSERT INTO invitefilter (id, guild_id, invite, alias) VALUES ({self.generate_id()}, {guild_id}, '{invite}', '{alias}');"
            )
            await conn.commit()

    async def remove_invitefilter(self, guild_id: int, alias):
        async with aiosqlite.connect(self.dbpath) as conn:
            conn.row_factory = sqlite3.Row
            invite = await conn.execute_fetchall(f"SELECT * FROM invitefilter WHERE guild_id={guild_id} AND alias={alias};")
            inviteid = invite[0]["id"]
            await conn.execute(f"DELETE FROM invitefilter WHERE id={inviteid};")
            await conn.commit()
