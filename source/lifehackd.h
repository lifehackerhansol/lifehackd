#pragma once
#include <stdio.h>

#include <concord/discord.h>

void lifehackd_on_ready(struct discord *client, const struct discord_ready *event);

void lifehackd_init(struct discord *client);
