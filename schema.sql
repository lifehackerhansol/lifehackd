--
-- Copyright (C) 2022-2023 lifehackerhansol
--
-- SPDX-License-Identifier: AGPL-3.0-or-later
--
-- This is the bot databse schema.
-- Do not actually apply this schema, just running
-- the bot will use migrations in `dbupdate` folder
-- to apply this schema.
--
drop table if exists guilds;
drop table if exists modroles;
drop table if exists warns;


create table guilds
(
	id BIGINT PRIMARY KEY,
	mute_id BIGINT,
	logchannel_id BIGINT
);


create table modroles
(
	id BIGINT PRIMARY KEY,
	guild_id BIGINT NOT NULL REFERENCES guilds(id)
);


create table warns
(
	id BIGINT PRIMARY KEY,
	user_id BIGINT NOT NULL,
	issuer_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL REFERENCES guilds(id),
	reason TEXT
);

create table invitewhitelist
(
	id BIGINT PRIMARY KEY,
	guild_id BIGINT NOT NULL REFERENCES guilds(id),
    invite TEXT
);
