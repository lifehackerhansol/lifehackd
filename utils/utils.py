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
# send_dm_message, command_signature, error embeds taken from Kurisu, http://www.apache.org/licenses/LICENSE-2.0
#

import datetime
import re
import traceback
from inspect import cleandoc

import discord
from discord.ext import commands


async def send_dm_message(member: discord.Member, message: str, ctx: commands.Context = None, **kwargs) -> bool:
    """A helper function for sending a message to a member's DMs.

    Returns a boolean indicating success of the DM
    and notifies of the failure if ctx is supplied."""
    try:
        await member.send(message, **kwargs)
        return True
    except (discord.HTTPException, discord.Forbidden, discord.NotFound, AttributeError):
        if ctx:
            await ctx.send(f"Failed to send DM message to {member.mention}")
        return False


def command_signature(command, *, prefix=".") -> str:
    """Helper function for a command signature

    Parameters
    -----------
    command: :class:`discord.ext.commands.Command`
        The command to generate a signature for
    prefix: str
        The prefix to include in the signature"""
    signature = f"{discord.utils.escape_markdown(prefix)}{command.qualified_name} {command.signature}"
    return signature


def create_error_embed(ctx, exc) -> discord.Embed:
    embed = discord.Embed(title=f"Unexpected exception in command {ctx.command}", color=0xe50730)
    trace = "".join(traceback.format_exception(type(exc), value=exc, tb=exc.__traceback__))
    embed.description = f'```py\n{trace}```'
    embed.add_field(name="Exception Type", value=exc.__class__.__name__)
    embed.add_field(name="Information", value=f"channel: {ctx.channel.mention if isinstance(ctx.channel, discord.TextChannel) else 'Direct Message'}\ncommand: {ctx.command}\nmessage: {ctx.message.content}\nauthor: {ctx.author.mention}", inline=False)
    return embed


def is_guild_owner():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        if ctx.author == ctx.guild.owner:
            return True
        return False
    return commands.check(predicate)


def is_staff():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        if ctx.author == ctx.guild.owner:
            return True
        else:
            modroles = await ctx.bot.db.get_modroles(ctx.guild.id)
            modroleid = []
            for role in modroles:
                modroleid.append(role['id'])
            for role in ctx.author.roles:
                if role.id in modroleid:
                    return True
        return False
    return commands.check(predicate)


def parse_time(time_str):
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return datetime.timedelta(**time_params)


def simple_embed(text="", title="", color=discord.Color.default()) -> discord.Embed:
    embed = discord.Embed(title=title, color=color)
    embed.description = cleandoc(text)
    return embed
