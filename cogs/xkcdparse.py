#
# Copyright (C) 2021 Nintendo Homebrew
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

import xkcd

from discord.ext import commands


class xkcdparse(commands.Cog):
    """
    xkcd parser.
    """
    def __init__(self, bot):
        self.bot = bot

    word_responses = {
        "pointers": 138,
        "sudo": 149,
        "sandwich": 149,
        "compiling": 303,
        "code compiling": 303,
        "bobby tables": 327,
        "little bobby tables": 327,
        "duty calls": 386,
        "security": 538,
        "standards": 927,
        "password": 936,
        "denvercoder9": 979,
        "workflow": 1172,
        "free speech": 1357,
        "screenshot": 1373,
        "tasks": 1425,
        "real programmers": 378
    }

    @commands.hybrid_command()
    async def xkcd(self, ctx, *, comic):
        """Show xkcd comic by number. Use "latest" to show latest comic, or "random" to show random comic."""
        comic = comic.lower()
        if comic == "latest":
            await ctx.send(f"https://xkcd.com/{xkcd.getLatestComic().number}/")
        elif comic == "random":
            await ctx.send(f"https://xkcd.com/{xkcd.getRandomComic().number}/")
        elif comic.isdecimal():
            await ctx.send(f"https://xkcd.com/{xkcd.getComic(comic).number}/")
        elif comic in self.word_responses:
            await ctx.send(f"https://xkcd.com/{xkcd.getComic(self.word_responses[comic]).number}/")
        else:
            await ctx.send("I can't find that one!")


async def setup(bot):
    await bot.add_cog(xkcdparse(bot))
