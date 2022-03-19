CREATE TABLE `bans` (
  `days` bigint(24) NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `ban_date` bigint(24) NOT NULL,
  `user_id` bigint(24) NOT NULL,
  `access_key` varchar(24) NOT NULL
);


CREATE TABLE `guild_settings` (
  `access_key` varchar(24) NOT NULL,
  `guild_id` varchar(24) NOT NULL
);