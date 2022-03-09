#
# Copyright (C) 2020 Nintendo Homebrew
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# .speak from blah.py
# lockdown.py with SQL code stripped
# kickban.py
#

from datetime import datetime
from typing import Optional, Union

import discord
from discord.ext import commands
from discord.utils import format_dt

from utils.modutil import check_if_staff, is_muted, mute_role_exists, mute_member, unmute_member
from utils.utils import is_staff, send_dm_message, parse_time


class Mod(commands.Cog):
    """
    Moderator-only commands.
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @commands.command()
    @is_staff()
    async def speak(self, ctx, channel: discord.TextChannel, *, inp):
        await channel.send(inp, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))

    @commands.command()
    @is_staff()
    async def lockdown(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel. Staff only."""

        if not channels:
            channels.append(ctx.channel)

        for c in channels:

            default_role = ctx.guild.default_role
            overwrites_default = c.overwrites_for(default_role)

            if overwrites_default.send_messages is False or overwrites_default.read_messages is False:
                await ctx.send(f"Nothing would happen from locking {c.mention}")
                continue

            overwrites_default.send_messages = False

            try:
                await c.set_permissions(default_role, overwrite=overwrites_default)
            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue

            await c.send("🔒 Channel locked down. Only staff members may speak. Do not bring the topic to other channels or risk disciplinary actions.")

    @commands.command()
    @is_staff()
    async def unlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Unlock message sending in the channel. Staff only."""

        if not channels:
            channels.append(ctx.channel)

        for c in channels:

            default_role = ctx.guild.default_role
            overwrites_default = c.overwrites_for(default_role)
            overwrites_default.send_messages = None if default_role is ctx.guild.default_role else True

            try:
                await c.set_permissions(default_role, overwrite=overwrites_default)
            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue

            await c.send("🔓 Channel unlocked.")

    @commands.bot_has_permissions(kick_members=True)
    @commands.command(name="kick")
    @is_staff()
    async def kick_member(self, ctx, member: discord.Member, *, reason=""):
        """Kicks a user from the server. Staff only."""
        if await check_if_staff(ctx, member):
            return await ctx.send("You cannot kick another staff member!")
        msg = f"You were kicked from {ctx.guild.name}."
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nYou are able to rejoin the server, but please read the rules in #rules before participating again."
        await send_dm_message(member, msg, ctx)
        try:
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{member} is now gone. 👌")

    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="ban")
    @is_staff()
    async def ban_member(self, ctx, member: Union[discord.Member, discord.User], days: Optional[int] = 0, *, reason=""):
        """Bans a user from the server. OP+ only. Optional: [days] Specify up to 7 days of messages to delete."""
        if member in ctx.guild.members:
            if await check_if_staff(ctx, member):
                return await ctx.send("You cannot ban another staff member!")
        if days > 7:
            days = 7
        elif days < 0:
            days = 0
        if isinstance(member, discord.Member):
            msg = f"You were banned from {ctx.guild.name}."
            if reason != "":
                msg += " The given reason is: " + reason
            msg += "\n\nThis ban does not expire."
            await send_dm_message(member, msg, ctx)
        try:
            await ctx.guild.ban(member, reason=reason, delete_message_days=days)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{member} is now b&. 👍")

    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="unban")
    @is_staff()
    async def unban_member(self, ctx, user: Union[discord.Member, discord.User], *, reason=""):
        """Unbans a user from the server. OP+ only."""
        try:
            await ctx.guild.fetch_ban(user)
        except discord.errors.NotFound:
            return await ctx.send(f"{user} is not banned!")

        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"{user} is now unbanned.")

    @commands.command()
    @is_staff()
    async def warn(self, ctx, member: Union[discord.Member, discord.User], *, reason=""):
        """Warn a user. Staff only."""
        if await check_if_staff(ctx, member):
            return await ctx.send("You cannot warn another staff member!")
        warn_count = len(await self.bot.db.get_warns(member.id, ctx.guild.id))
        if warn_count >= 5:
            await ctx.send("A user can't have more than 5 warns!")
            return
        await self.bot.db.add_warn(member.id, ctx.author.id, ctx.guild.id, reason)
        warn_count += 1
        if isinstance(member, discord.Member):
            msg = f"You were warned on {ctx.guild.name}."
            if reason != "":
                # much \n
                msg += " The given reason is: " + reason
            msg += f"\n\nPlease read the rules. This is warn #{warn_count}."
            if warn_count == 2:
                msg += " __The next warn will automatically kick.__"
            elif warn_count == 3:
                msg += "\n\nYou were kicked because of this warning. You can join again right away. Two more warnings will result in an automatic ban."
            elif warn_count == 4:
                msg += "\n\nYou were kicked because of this warning. This is your final warning. You can join again, but **one more warn will result in a ban**."
            elif warn_count == 5:
                msg += "\n\nYou were automatically banned due to five warnings."
            await send_dm_message(member, msg, ctx)
            if warn_count in {3, 4}:
                try:
                    await member.kick(reason=f"{warn_count} warns.")
                except discord.Forbidden:
                    await ctx.send("I can't kick this user!")
        if warn_count >= 5:  # just in case
            try:
                await ctx.guild.ban(member, reason="5 warns.", delete_message_days=0)
            except discord.Forbidden:
                await ctx.send("I can't ban this user!")
        await ctx.send(f"{member.mention} warned. User has {warn_count} warning(s)")

    @commands.command()
    @is_staff()
    async def delwarn(self, ctx, member: Union[discord.Member, discord.User], idx: int):
        """Remove a specific warn from a user. Staff only."""
        warns = await self.bot.db.get_warns(member.id, ctx.guild.id)
        if not warns:
            return await ctx.send(f"{member.mention} has no warns!")
        warn_count = len(warns)
        if idx > warn_count:
            return await ctx.send(f"Warn index is higher than warn count ({warn_count})!")
        if idx < 1:
            return await ctx.send("Warn index is below 1!")
        await self.bot.db.remove_warn(member.id, ctx.guild.id, idx)
        await ctx.send(f"{member.mention} has a warning removed!")

    @commands.command()
    async def listwarns(self, ctx, member: Union[discord.Member, discord.User] = None):
        """List warns for a user. Only staff can use on members other than oneself."""
        if not member:  # If user is set to None, its a selfcheck
            member = ctx.author
        issuer = ctx.author
        if not await check_if_staff(ctx, ctx.author):
            msg = f"{issuer.mention} Using this command on others is limited to Staff."
            return await ctx.send(msg)
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name=f"Warns for {member}", icon_url=member.display_avatar.url)
        warns = await self.bot.db.get_warns(member.id, ctx.guild.id)
        if warns:
            idx = 0
            for warn in warns:
                idx += 1
                issuer = ctx.guild.get_member(warn['issuer_id'])
                value = ""
                value += f"Issuer: {issuer.name}\n"
                value += f"Reason: {warn['reason']} "
                embed.add_field(name=f"{idx}: {discord.utils.snowflake_time(warn['id']).strftime('%Y-%m-%d %H:%M:%S')}", value=value)
        else:
            embed.description = "There are none!"
            embed.colour = discord.Color.green()
        await ctx.send(embed=embed)

    @is_staff()
    @commands.command(aliases=['timemute'])
    async def timeout(self, ctx: commands.Context, member: discord.Member, length: str, *, reason: Optional[str]):
        """Times out a user. Staff only.\n\nLength format: #d#h#m#s"""
        length = parse_time(length)
        if length is None:
            return
        timeout_expiration = format_dt(datetime.now() + length)
        if not await mute_role_exists(ctx):
            return await ctx.send("Mute role is not set in settings, or role cannot be found! Cannot mute.")
        if await check_if_staff(ctx, member):
            return await ctx.send("You cannot mute another staff member!")
        if length.total_seconds() > 2419200:  # Timeout time can't be more than 28 days
            return await ctx.send("Timeouts can't be longer than 28 days!")
        await unmute_member(ctx, member)  # remove mute role, if exists
        await member.timeout(length, reason=reason)
        msg_user = "You were muted!"
        if reason is not None:
            msg_user += f" The given reason is: {reason}"
        msg_user += f"\nIt will expire in {timeout_expiration}."
        await send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} has been given a timeout. It will expire in {timeout_expiration}.")

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @is_staff()
    async def mute(self, ctx, member: discord.Member, *, reason=""):
        """Mutes a user so they can't speak. Staff only."""
        if not await mute_role_exists(ctx):
            return await ctx.send("Mute role is not set in settings, or role cannot be found! Cannot mute.")
        if await check_if_staff(ctx, member):
            return await ctx.send("You cannot mute another staff member!")
        if await is_muted(ctx, member):
            return await ctx.send("This member is already muted!")
        await mute_member(ctx, member)
        msg_user = "You were muted!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        await send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer speak.")

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @is_staff()
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes a user so they can speak. Staff only."""
        if not await mute_role_exists(ctx):
            return await ctx.send("Mute role is not set in settings, or role cannot be found! Cannot unmute.")
        if not member.is_timed_out() and not await is_muted(ctx, member):
            return await ctx.send("This member is not muted!")
        await unmute_member(ctx, member)
        await ctx.send(f"{member.mention} can now speak again.")


async def setup(bot):
    await bot.add_cog(Mod(bot))
