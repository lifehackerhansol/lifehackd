#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <string>

#include <concord/discord.h>
#include <concord/log.h>

#include <cogs.h>
#include <utils/response.h>

static void extras_lifehackd(struct discord *client, const struct discord_message *event) {
    struct discord_embed embed = {
        .title = "lifehackd",
        .description = "lifehacker 101 Discord bot",
        .url = "https://github.com/lifehackerhansol/lifehackd",
    };
    discord_embed_set_thumbnail(&embed, "https://avatars.githubusercontent.com/u/105009381", NULL, 0, 0);
    LHD_SendResponseEmbed(client, event, &embed);
}

static void extras_membercount(struct discord *client, const struct discord_message *event) {
    const struct discord_guild * guild = discord_cache_get_guild(client, event->guild_id);
    std::string response;
    response += guild->name + std::string(" has ") + std::to_string(guild->member_count) + " members!";
    LHD_SendResponseText(client, event, response.c_str());
    discord_unclaim(client, guild);
}

static void register_cog(struct discord *client) {
    discord_set_on_command(client, "lifehackd", &extras_lifehackd);
    discord_set_on_command(client, "membercount", &extras_membercount);
}

cog_t extras_cog = {.name = "Extras", .register_cog = &register_cog};
