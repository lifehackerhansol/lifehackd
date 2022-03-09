#
# Copyright (C) 2023 lifehackerhansol
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import discord
from discord.ext import commands

from utils.utils import is_staff


class Invite(commands.Cog):
    """
    Discord Invites cog.

    This cog manages the invite filter, as well as provide a macro for
    whitelisted invites.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["invf"])
    @commands.check_any(commands.is_owner(), is_staff())
    async def invitefilter(self, ctx):
        """Set server configs for the bot"""
        if not await self.bot.db.get_logchannel(ctx.guild.id):
            return await ctx.send("You must set up a log channel for invite filters.")
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @invitefilter.command(name="add")
    async def invitefilter_add(self, ctx, invite: discord.Invite, alias: str):
        if invite.guild is None or isinstance(invite.guild, discord.Object):
            return await ctx.send("No info from the guild is available(?). Please try again.")
        filters = await self.bot.db.get_invitefilter(ctx.guild.id)
        alias = alias.lower()
        if filters:
            for i in filters:
                if i["invite"] == invite.code:
                    return await ctx.send("This invite already exists in the whitelist!")
                if i["alias"] == alias:
                    return await ctx.send("This alias already exists in the filter!")
        await self.bot.db.add_invitefilter(ctx.guild.id, invite.code, alias)
        await ctx.send("Successfully added invite to whitelist")

    @invitefilter.command(name="delete")
    async def invitefilter_delete(self, ctx, alias: str):
        filters = await self.bot.db.get_invitefilter(ctx.guild.id)
        if not filters:
            return await ctx.send("There are no invites in the whitelist!")
        for i in filters:
            if i["alias"] == alias.lower():
                await self.bot.db.remove_invitefilter(alias)
                return await ctx.send(f"Deleted {i['alias']} from the whitelist.")
        await ctx.send("This invite doesn't exist in the whitelist!")

    @invitefilter.command(name="list")
    async def invitefilter_list(self, ctx):
        filters = await self.bot.db.get_invitefilter(ctx.guild.id)
        if not filters:
            return await ctx.send("There are no invites in the whitelist!")
        embed = discord.Embed()
        embed.add_field(name='Invites', value='\n'.join(f"name: {invite['alias']} code:{invite['invite']}" for invite in filters))
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx, name: str = ""):
        """Post a discord invite to an approved server"""
        filters = await self.bot.db.get_invitefilter(ctx.guild.id)
        if not filters:
            return await ctx.send("There are no approved servers!")
        if not name:
            return await ctx.send(f"Valid server names are: {', '.join(ai['alias'] for ai in filters)}")

        for i in filters:
            if i["alias"] == name:
                return await ctx.send(f"https://discord.gg/{i['invite']}")
        await ctx.send(f"Invalid invite name. Valid server names are: {', '.join(ai['alias'] for ai in filters)}")


async def setup(bot):
    await bot.add_cog(Invite(bot))
