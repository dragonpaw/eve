
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
    [('fv1:9041061595866408371','fv1:-2582557340894518261'), # generated 2010-01-03 10:42:23.456639
        "UPDATE `trade_marketindexvalue` SET `buy_qty` = 0 WHERE `buy_qty` IS NULL;",
        "ALTER TABLE `trade_marketindexvalue` MODIFY COLUMN `buy_qty` numeric(15, 0) NOT NULL;",
        "UPDATE `trade_marketindexvalue` SET `sell_qty` = 0 WHERE `sell_qty` IS NULL;",
        "ALTER TABLE `trade_marketindexvalue` MODIFY COLUMN `sell_qty` numeric(15, 0) NOT NULL;",
    ],
    [('fv1:-7568494508689043539','fv1:-4886211896034941373'), # generated 2010-01-04 01:53:50.453829
        "UPDATE `trade_blueprintowned` SET `cost_per_run` = 0 WHERE `cost_per_run` IS NULL;",
        "ALTER TABLE `trade_blueprintowned` MODIFY COLUMN `cost_per_run` numeric(15, 2) NOT NULL;",
    ],
    [('fv1:-4886211896034941373','fv1:-7014047568890444953'), # generated 2010-01-12 06:03:34.028231
        "UPDATE `trade_journalentry` SET `transaction_id` = 0 WHERE `transaction_id` IS NULL;",
        "ALTER TABLE `trade_journalentry` MODIFY COLUMN `transaction_id` numeric(20, 0) NOT NULL;",
        "UPDATE `trade_transaction` SET `transaction_id` = 0 WHERE `transaction_id` IS NULL;",
        "ALTER TABLE `trade_transaction` MODIFY COLUMN `transaction_id` numeric(20, 0) NOT NULL;",
    ],
    [('fv1:2108721505323759407','fv1:8359134830156444955'), # generated 2010-01-12 06:25:36.389923
        "UPDATE `trade_journalentry` SET `transaction_id` = 0 WHERE `transaction_id` IS NULL;",
        "ALTER TABLE `trade_journalentry` MODIFY COLUMN `transaction_id` numeric(20, 0) NOT NULL;",
        "UPDATE `trade_transaction` SET `transaction_id` = 0 WHERE `transaction_id` IS NULL;",
        "ALTER TABLE `trade_transaction` MODIFY COLUMN `transaction_id` numeric(20, 0) NOT NULL;",
    ],
] # don't delete this comment! ## mysql_evolutions_end ##
