-- V2: Pre-move to MySQL
-- Add a db_info table, replacement for user_version

create table db_info
(
	id BIGINT PRIMARY KEY
);

insert into db_info (id) values(2);
