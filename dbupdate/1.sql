-- V1: Initial commit
-- Create all required tables

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


create table invitefilter
(
	id BIGINT PRIMARY KEY,
	guild_id BIGINT NOT NULL REFERENCES guilds(id),
    invite TEXT,
    alias TEXT
);
