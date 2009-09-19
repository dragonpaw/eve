
# all of your evolution scripts, mapping the from_version and to_version to a list if sql commands
mysql_evolutions = [
    [('fv1:7600293746071432459','fv1:-3926359637847260771'), # generated 2009-09-09 01:40:14.893391
        "CREATE TABLE `trade_journalentrytype` (\n    `id` integer NOT NULL PRIMARY KEY,\n    `name` varchar(100) NOT NULL,\n    `is_boring` bool NOT NULL\n)\n;",
        "CREATE TABLE `trade_journalentry` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `transaction_id` integer NOT NULL,\n    `character_id` integer NOT NULL,\n    `type_id` integer NOT NULL,\n    `client` varchar(100) NOT NULL,\n    `time` datetime NOT NULL,\n    `price` numeric(20, 2) NOT NULL,\n    `reason` varchar(200) NOT NULL\n)\n;",
        "CREATE TABLE `trade_transaction` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `transaction_id` integer NOT NULL,\n    `character_id` integer NOT NULL,\n    `item_id` integer NOT NULL,\n    `sold` bool NOT NULL,\n    `price` double precision NOT NULL,\n    `quantity` integer NOT NULL,\n    `station_id` integer NOT NULL,\n    `region_id` integer NOT NULL,\n    `time` datetime NOT NULL,\n    `client` varchar(100) NOT NULL\n)\n;",
        "CREATE TABLE `trade_marketindex` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `name` varchar(200) NOT NULL,\n    `url` varchar(200) NOT NULL,\n    `note` varchar(200) NOT NULL,\n    `user_id` integer,\n    `priority` integer NOT NULL\n)\n;",
        "CREATE TABLE `trade_marketindexvalue` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `item_id` integer NOT NULL,\n    `index_id` integer NOT NULL,\n    `date` date NOT NULL,\n    `buy` double precision NOT NULL,\n    `sell` double precision NOT NULL,\n    `buy_qty` integer NOT NULL,\n    `sell_qty` integer NOT NULL\n)\n;",
        "CREATE TABLE `trade_blueprintowned` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `user_id` integer NOT NULL,\n    `blueprint_id` integer NOT NULL,\n    `pe` integer NOT NULL,\n    `me` integer NOT NULL,\n    `original` bool NOT NULL,\n    `cost_per_run` double precision NOT NULL\n)\n;",
    ],
    [('fv1:-2098354881473224911','fv1:2364860626862231440'), # generated 2009-09-19 05:59:46.943025
        "UPDATE `trade_blueprintowned` SET `cost_per_run` = 0 WHERE `cost_per_run` IS NULL;",
        "ALTER TABLE `trade_blueprintowned` MODIFY COLUMN `cost_per_run` double precision NOT NULL;",
    ],
] # don't delete this comment! ## mysql_evolutions_end ##
