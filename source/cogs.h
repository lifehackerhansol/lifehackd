#pragma once

#include <concord/discord.h>

typedef struct {
    char* name;
    void (*on_command)(struct discord *client, const struct discord_message *event);
} command_t;

typedef struct {
    char *name;
    void (*on_message)(struct discord *client, const struct discord_message *event);
    void (*register_cog)(struct discord *client);
} cog_t;

#include "cogs/extras.h"
