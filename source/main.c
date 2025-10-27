#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <concord/discord.h>
#include <concord/log.h>
#include "lifehackd.h"

int main(const int argc, const char **argv) {
    printf("Hello world!\n");

    ccord_global_init();
    struct discord *lifehackd = discord_config_init("config.json");
    // Enable message and guild caching by default
    // More accurate data for guilds
    discord_cache_enable(lifehackd,
                         DISCORD_CACHE_MESSAGES | DISCORD_CACHE_GUILDS);
    // Add needed intents
    discord_add_intents(lifehackd, 
       	DISCORD_GATEWAY_GUILDS |
        DISCORD_GATEWAY_GUILD_MEMBERS |
        DISCORD_GATEWAY_GUILD_BANS |
        DISCORD_GATEWAY_GUILD_MESSAGES |
        DISCORD_GATEWAY_DIRECT_MESSAGES |
        DISCORD_GATEWAY_MESSAGE_CONTENT);
    discord_set_on_ready(lifehackd, &lifehackd_on_ready);
    // discord_set_on_message_create(lifehackd, &lifehackd_on_message);
    lifehackd_init(lifehackd);
    discord_run(lifehackd);

    free(lifehackd);
    return 0;
}
