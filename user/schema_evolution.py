
# all of your evolution scripts, mapping the from_version and to_version to a list if sql commands
mysql_evolutions = [
    [('fv1:-930638415213035279','fv1:-8552158230827939040'), # generated 2009-09-09 01:40:09.269261
        "CREATE TABLE `user_userprofile` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `user_id` integer NOT NULL UNIQUE,\n    `pos_days` integer NOT NULL,\n    `pos_shipping_cost` numeric(10, 2) NOT NULL,\n    `lost_password_key` varchar(50) NOT NULL,\n    `lost_password_time` datetime\n)\n;",
        "CREATE TABLE `user_account` (\n    `id` integer NOT NULL PRIMARY KEY,\n    `user_id` integer NOT NULL,\n    `api_key` varchar(200) NOT NULL,\n    `last_refreshed` datetime,\n    `refresh_messages` longtext NOT NULL\n)\n;",
        "CREATE TABLE `user_character` (\n    `id` integer NOT NULL PRIMARY KEY,\n    `account_id` integer NOT NULL,\n    `name` varchar(100) NOT NULL,\n    `isk` double precision,\n    `training_completion` datetime,\n    `training_level` integer,\n    `training_skill_id` integer,\n    `is_director` bool NOT NULL,\n    `is_pos_monkey` bool NOT NULL,\n    `corporation_id` integer NOT NULL,\n    `user_id` integer NOT NULL,\n    `last_refreshed` datetime NOT NULL,\n    `cached_until` datetime NOT NULL,\n    `refresh_messages` longtext NOT NULL\n)\n;",
        "CREATE TABLE `user_skilllevel` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `character_id` integer NOT NULL,\n    `skill_id` integer NOT NULL,\n    `level` integer NOT NULL,\n    `points` integer NOT NULL\n)\n;",
    ],
    [('fv1:-8553226820598921118','fv1:-4810847124748903936'), # generated 2009-09-19 05:59:53.267385
        "UPDATE `user_account` SET `refresh_messages` = '' WHERE `refresh_messages` IS NULL;",
        "ALTER TABLE `user_account` MODIFY COLUMN `refresh_messages` longtext NOT NULL;",
    ],
    [('fv1:-4234292800486184428','fv1:-776422834835482277'), # generated 2010-01-02 22:13:11.229075
        "CREATE TABLE `user_skillintraining` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `character_id` integer NOT NULL,\n    `skill_id` smallint NOT NULL,\n    `level` integer NOT NULL,\n    `order` integer NOT NULL,\n    `finish_time` datetime NOT NULL\n)\n;",
        "-- warning: the following may cause data loss",
        "ALTER TABLE `user_character` DROP COLUMN `training_skill_id`;",
        "ALTER TABLE `user_character` DROP COLUMN `training_completion`;",
        "ALTER TABLE `user_character` DROP COLUMN `training_level`;",
        "-- end warning",
    ],
    [('fv1:-3316076659933319594','fv1:4939214094813406265'), # generated 2010-01-03 01:21:22.760078
        "ALTER TABLE `user_skillintraining` MODIFY COLUMN `finish_time` datetime NULL;",
    ],
    [('fv1:-776422834835482277','fv1:674206596723670124'), # generated 2010-01-03 10:42:34.286478
        "ALTER TABLE `user_skillintraining` MODIFY COLUMN `finish_time` datetime NULL;",
    ],
] # don't delete this comment! ## mysql_evolutions_end ##
