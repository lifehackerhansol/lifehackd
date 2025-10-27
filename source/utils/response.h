#pragma once

#include <concord/discord.h>

#ifdef __cplusplus
extern "C" {
#endif

void LHD_SendResponseEmbed(struct discord *client, const struct discord_message *event, struct discord_embed *embed);
void LHD_SendResponseText(struct discord *client, const struct discord_message *event, const char* text);

#ifdef __cplusplus
}
#endif
