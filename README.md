# lifehackd

life hack daemon. A Discord bot.

## How to use

1. Make a copy of `config.json.example` and name it `config.json`.
1. Set your bot's token ID.
    - You will need to create a bot over at [Discord Developer Portal](https://discord.com/developers/applications).
1. (Optional) Set your command prefix to whatever you like.
1. Install the following for your host:
    - Python 3.9.x (and its respective pip)
1. Run `pip install -r requirements.txt`
1. Run the following command:
    - UNIX-based: `python3 lifehackd.py`
    - Windows: `py lifehackd.py`

### Optional functionality

- Moderation roles can be added per-server. The server owner will have absolute permissions over the bot within the server, regardless of whether a moderator role is set.
    1. Use command `config modrole add <role ID>`.
    1. This role will now have access to moderation commands over the bot. i.e. kick, ban, mute, etc.
- Mute roles can be added per-server. Mute roles will need to be manually configured, however.
    1. Configure @everyone with default settings, and your Mute role with disabled `Send message` permissions.
        - This is the ideal configuration for a mute role: however, configure however you think a mute should be applied.
    1. Use command `config muterole add <role ID>`.
- Automatic roles can be added on join, per-server.
    - Use command `config autorole enable` and `config autorole add <role ID>`.

## License

```
    Copyright (C) 2021-2024 lifehackerhansol

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

## Credits
- Discord.py: This wouldn't exist without it
- [Nintendo Homebrew's Kurisu](https://github.com/nh-server/kurisu): `utils.py` error embeds, `load.py`, `blah.py`, moderation commands
