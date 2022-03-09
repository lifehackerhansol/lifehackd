#
# Copyright (C) 2021-2024 lifehackerhansol
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

from discord.ext import commands
from utils.utils import is_staff, is_guild_owner


class Config(commands.Cog):
    """
    Bot configuration
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check_any(commands.is_owner(), is_staff())
    async def config(self, ctx):
        """Set server configs for the bot"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @config.group()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def modrole(self, ctx):
        """Set moderator roles for this server"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @modrole.command(name='add')
    async def modrole_add(self, ctx, roleid: int):
        """Add moderator roles for this server"""
        for role in ctx.guild.roles:
            if role.id == roleid:
                modrole = await self.bot.db.get_modroles(ctx.guild.id)
                modroleid = []
                for mod in modrole:
                    modroleid.append(mod['id'])
                if roleid in modroleid:
                    return await ctx.send(f"{role.name} is already a moderator role!")
                await self.bot.db.add_modrole(ctx.guild.id, roleid)
                return await ctx.send(f"Success! `{role.name}` is now a moderator role.")
        await ctx.send("Role does not exist. Please try again.")

    @modrole.command(name='remove')
    async def modrole_remove(self, ctx, roleid: int):
        """Remove moderator roles for this server"""
        for role in ctx.guild.roles:
            if role.id == roleid:
                err = await self.bot.db.remove_modrole(ctx.guild.id, roleid)
                if err == 1:
                    return await ctx.send("There are no moderator roles set for this server!")
                if err == 2:
                    return await ctx.send(f"`{role.name}` is not a moderator role!")
                if err == 0:
                    return await ctx.send(f"Success! `{role.name}` is no longer a moderator role.")
        await ctx.send("Role does not exist. Please try again.")

    @config.group()
    async def muterole(self, ctx):
        """Set mute roles for this server"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @muterole.command(name='add')
    async def muterole_add(self, ctx, roleid: int):
        """Add mute role for this server"""
        for role in ctx.guild.roles:
            if role.id == roleid:
                muterole = await self.bot.db.get_muterole(ctx.guild.id)
                if muterole:
                    return await ctx.send("A mute role already exists!")
                await self.bot.db.add_muterole(ctx.guild.id, roleid)
                return await ctx.send(f"Success! `{role.name}` is now a mute role.")
        await ctx.send("Role does not exist. Please try again.")

    @muterole.command(name='remove')
    async def muterole_remove(self, ctx, roleid: int):
        """Remove mute role for this server"""
        for role in ctx.guild.roles:
            if role.id == roleid:
                err = await self.bot.db.remove_muterole(ctx.guild.id, roleid)
                if err == 1:
                    return await ctx.send("There is no mute role set for this server!")
                if err == 2:
                    return await ctx.send(f"`{role.name}` is not a mute role!")
                if err == 0:
                    return await ctx.send(f"Success! `{role.name}` is no longer a mute role.")
        await ctx.send("Role does not exist. Please try again.")

    @config.group()
    async def logchannel(self, ctx):
        """
        Set logging channels for this server
        This is required if you wish to add an invite filter.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @logchannel.command(name='add')
    async def logchannel_add(self, ctx, channelid: int):
        """Set log channel for this server"""
        for channel in ctx.guild.channels:
            if channel.id == channelid:
                logchannel = await self.bot.db.get_logchannel(ctx.guild.id)
                if logchannel:
                    return await ctx.send("A logging channel already exists!")
                await self.bot.db.add_logchannel(ctx.guild.id, channelid)
                return await ctx.send(f"Success! `{channel.name}` is now set as log channel.")
        await ctx.send("Channel does not exist. Please try again.")

    @logchannel.command(name='remove')
    async def logchannel_remove(self, ctx, channelid: int):
        """Remove log channel for this server"""
        for channel in ctx.guild.channels:
            if channel.id == channelid:
                err = await self.bot.db.remove_logchannel(ctx.guild.id, channelid)
                if err == 1:
                    return await ctx.send("There is no logging channel set for this server!")
                if err == 2:
                    return await ctx.send(f"`{channel.name}` is not a logging channel!")
                if err == 0:
                    return await ctx.send(f"Success! `{channel.name}` is no longer a log channel.")
        await ctx.send("Channel does not exist. Please try again.")


async def setup(bot):
    await bot.add_cog(Config(bot))
