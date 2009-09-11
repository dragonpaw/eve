
# all of your evolution scripts, mapping the from_version and to_version to a list if sql commands
mysql_evolutions = [
    [('fv1:-2891577100790052762','fv1:3805638760169930366'), # generated 2009-09-09 01:39:37.597325
        "CREATE TABLE `mining_miningop` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `datetime` datetime NOT NULL,\n    `description` varchar(200) NOT NULL,\n    `created_by_id` integer NOT NULL,\n    `hours` double precision NOT NULL\n)\n;",
        "CREATE TABLE `mining_mineronop` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `op_id` integer NOT NULL,\n    `name` varchar(100) NOT NULL,\n    `multiplier` double precision NOT NULL,\n    `start_time` datetime NOT NULL,\n    `end_time` datetime NOT NULL\n)\n;",
        "CREATE TABLE `mining_miningopmineral` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `op_id` integer NOT NULL,\n    `type_id` integer NOT NULL,\n    `quantity` integer NOT NULL\n)\n;",
    ],
] # don't delete this comment! ## mysql_evolutions_end ##
