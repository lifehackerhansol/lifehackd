#include <concord/discord.h>

void LHD_SendResponseEmbed(struct discord *client, const struct discord_message *event, struct discord_embed *embed) {
    struct discord_create_message params = {
        .embeds = &(struct discord_embeds) {
            .size = 1,
            .array = embed,
        }
    };
    discord_create_message(client, event->channel_id, &params, NULL);
}

void LHD_SendResponseText(struct discord *client, const struct discord_message *event, const char* text)
{
    struct discord_create_message params = {
        .content = text
    };
    discord_create_message(client, event->channel_id, &params, NULL);
}