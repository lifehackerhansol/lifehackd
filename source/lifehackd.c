#include <stdio.h>
#include <string.h>

#include <concord/discord.h>
#include <concord/log.h>

#include <cogs.h>

cog_t * lifehackd_cogs[] = {&extras_cog};

void lifehackd_on_ready(struct discord *client, const struct discord_ready *event) {
    // this function is broken in C++ with concord v2
    log_info("Logged in as %s!", event->user->username);
}

void lifehackd_init(struct discord *client) {
    for (int i=0; i < (sizeof(lifehackd_cogs) / sizeof(lifehackd_cogs[0])); i++) {
        cog_t *cog = lifehackd_cogs[i];
        log_debug("Registering cog %s", cog->name);
        cog->register_cog(client);
    }
}
