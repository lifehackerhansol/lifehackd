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
# about command and membercount command from Jenkins.py
#

from typing import Optional
import urllib

import aiohttp
from discord.ext import commands


class Jenkins(commands.Cog):
    """
    Jenkins commands
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # Jenkins needs to actually be set up in config
        if not self.bot.config["JENKINS_URL"] or not self.bot.config["JENKINS_USER"]:
            raise commands.CheckFailure()
        # Bot owner has ultimate perms
        if await self.bot.is_owner(ctx.author):
            return True
        # Some users in specified guild with specified role has perms
        if self.bot.config['GUILD'] and self.bot.config["JENKINS_DISCORD_ROLE"]:
            guild = self.bot.get_guild(self.bot.config['GUILD'])
            if guild:
                member = guild.get_member(ctx.author.id)
                if member and any(role.id == self.bot.config["JENKINS_DISCORD_ROLE"] for role in member.roles):
                    return True
        raise commands.CheckFailure()

    @commands.command()
    async def build(self, ctx, device: str, branch: str, release_type: str, manifest: Optional[str] = ""):
        """
        Start a LineageOS build.
        Usage: `build <device> <branch> <release_type> [manifest (if not hosted on hudson)]`
        Example: build joan lineage-21.0 testing
        """
        async with ctx.typing():
            local_manifest_url = urllib.parse.quote_plus(manifest if manifest else f"https://raw.githubusercontent.com/lifehacker-101/hudson/main/manifests/{branch}/devices/{device}.xml")
            build_trigger_url = f"{self.bot.config['JENKINS_URL']}/job/lineageos/job/{branch}/buildWithParameters?JENKINS_DEVICE={device}&JENKINS_LOCAL_MANIFEST={local_manifest_url}{f'&JENKINS_RELEASE_TYPE={release_type}' if release_type != 'testing' else ''}"

            build_post = await self.bot.session.post(build_trigger_url, auth=aiohttp.BasicAuth(self.bot.config["JENKINS_USER"], self.bot.config["JENKINS_LINEAGE_TOKEN"]))

            # Jenkins returns 201 when a job is successfully created
            if build_post.status == 201:
                await ctx.send(f"Build for {device} on branch {branch} started.")
            else:
                await ctx.send(f"Failed to trigger a build with error {build_post.status}.")


async def setup(bot):
    await bot.add_cog(Jenkins(bot))
