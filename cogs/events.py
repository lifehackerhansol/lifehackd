#
# Copyright (C) 2022 lifehackerhansol
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

import re

import discord
from discord.ext import commands

from utils.modutil import check_if_staff


class Events(commands.Cog):
    """
    Handles server events
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ctx = await self.bot.get_context(message)
        # message deletion only available if you enable logs
        if not await self.bot.db.get_logchannel(ctx.guild.id):
            return
        if message.author.id == self.bot.user.id:
            return
        if await check_if_staff(ctx, message.author):
            return

        # Now for the actual checking
        res = re.findall(r'(?:discordapp\.com/invite|discord\.gg|discord\.com/invite)/([\w]+)', message.content)
        if res:
            await message.delete()
            logchannel_id = await self.bot.db.get_logchannel(message.guild.id)
            logchannel = message.guild.get_channel(logchannel_id)
            log_msg = f"{message.author.mention} tried to send an invite:\n"
            log_msg = f"{log_msg}----------------\n"
            log_msg = f"{log_msg}{message.content}"
            await logchannel.send(log_msg)


async def setup(bot):
    await bot.add_cog(Events(bot))
