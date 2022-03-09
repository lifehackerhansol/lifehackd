#
# Copyright 2021 Nintendo Homebrew
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
# about command and membercount command from extras.py
#

from typing import Union

import discord
from discord.ext import commands
from discord.utils import format_dt


class Extras(commands.Cog):
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def lifehackd(self, ctx):
        """Information on the bot lifehackd"""
        embed = discord.Embed(title="lifehackd")
        embed.set_author(name="lifehackerhansol")
        embed.url = "https://github.com/lifehackerhansol/lifehackd"
        embed.set_thumbnail(url="https://archives.bulbagarden.net/media/upload/thumb/0/04/707lifehackd.png/240px-707lifehackd.png")
        embed.description = "ROM hacking Discord server bot"
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def membercount(self, ctx):
        """Prints the member count of the server."""
        await ctx.send(f"{ctx.guild.name} has {ctx.guild.member_count:,} members!")

    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx, user: Union[discord.Member, discord.User] = None):
        """Shows information from a user."""
        if user is None:
            user = ctx.author

        embed = discord.Embed()
        embed.description = (
            f"**User:** {user.mention}\n"
            f"**User's ID:** {user.id}\n"
            f"**Created on:** {format_dt(user.created_at)} ({format_dt(user.created_at, style='R')})\n"
            f"**Default Profile Picture:** {user.default_avatar}\n"
        )

        if isinstance(user, discord.Member):
            member_type = "member"
            embed.description += (
                f"**Join date:** {format_dt(user.joined_at)} ({format_dt(user.joined_at, style='R')})\n"
                f"**Current Status:** {user.status}\n"
                f"**User Activity:** {user.activity}\n"
                f"**Current Display Name:** {user.display_name}\n"
                f"**Nitro Boost Info:** {f'Boosting since {format_dt(user.premium_since)}' if user.premium_since else 'Not a booster'}\n"
                f"**Current Top Role:** {user.top_role}\n"
                f"**Color:** {user.color}\n"
                f"**Profile Picture:** [link]({user.avatar})"
            )
            if user.guild_avatar:
                embed.description += f"\n**Guild Profile Picture:** [link]({user.guild_avatar})"
        else:
            member_type = "user"
            try:
                ban = await ctx.guild.fetch_ban(user)
                embed.description += f"\n**Banned**, reason: {ban.reason}"
            except discord.NotFound:
                pass

        member_type = member_type if not user.bot else "bot"
        embed.title = f"**Userinfo for {member_type} {user}**"
        embed.set_thumbnail(url=user.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Extras(bot))
