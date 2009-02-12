
# all of your evolution scripts, mapping the from_version and to_version to a list if sql commands
mysql_evolutions = [
    [('fv1:-745662237','fv1:-1234050589'), # generated 2008-12-12 00:47:46.203000
        "ALTER TABLE `pos_playerstation` ADD COLUMN `owner_id` integer;",
        "CREATE INDEX `pos_playerstation_owner_id` ON `pos_playerstation` (`owner_id`);",
        "ALTER TABLE `pos_playerstation` DROP COLUMN `owner`;",
    ],
    [('fv1:-1234050589','fv1:815928997'), # generated 2008-12-12 00:50:02.421000
        "ALTER TABLE `pos_playerstation` DROP COLUMN `depot_id`;",
    ],
    [('fv1:1143036542','fv1:325662976'), # generated 2008-12-12 01:00:52.546000
        "DROP TABLE `pos_fuelsupply`;",
        "DROP TABLE `pos_fueldepot`;",
    ],
    [('fv1:325662976','fv1:1004061274'), # generated 2008-12-12 01:40:40.515000
        "-- warning: the following may cause data loss",
        "ALTER TABLE `pos_playerstation` DROP COLUMN `is_personal_pos`;",
        "-- end warning",
    ],
    [('fv1:-426538941','fv1:-1195990942'), # generated 2009-02-05 19:46:43.984000
        "ALTER TABLE `pos_playerstation` MODIFY COLUMN `note` varchar(200) NOT NULL;",
        "ALTER TABLE `pos_playerstation` ADD COLUMN `sov_fuel_rate` numeric(6, 4);",
        "UPDATE `pos_playerstation` SET `sov_fuel_rate` = 1 WHERE `sov_fuel_rate` IS NULL;",
        "ALTER TABLE `pos_playerstation` MODIFY COLUMN `sov_fuel_rate` numeric(6, 4) NOT NULL;",
        "ALTER TABLE `pos_playerstation` ADD COLUMN `sov_level` varchar(20);",
        "UPDATE `pos_playerstation` SET `sov_level` = 'None' WHERE `sov_level` IS NULL;",
        "ALTER TABLE `pos_playerstation` MODIFY COLUMN `sov_level` varchar(20) NOT NULL;",
    ],
    [('fv1:-1195990942','fv1:-1288098459'), # generated 2009-02-05 19:58:25.343000
        "ALTER TABLE `pos_fuelsupply` ADD COLUMN `max_consumption` integer;",
        "UPDATE `pos_fuelsupply` SET `max_consumption` = 0 WHERE `max_consumption` IS NULL;",
        "ALTER TABLE `pos_fuelsupply` MODIFY COLUMN `max_consumption` integer NOT NULL;",
        "ALTER TABLE `pos_fuelsupply` ADD COLUMN `purpose` varchar(10);",
        "UPDATE `pos_fuelsupply` SET `purpose` = 'Online' WHERE `purpose` IS NULL;",
        "ALTER TABLE `pos_fuelsupply` MODIFY COLUMN `purpose` varchar(10) NOT NULL;",
    ],
] # don't delete this comment! ## mysql_evolutions_end ##
