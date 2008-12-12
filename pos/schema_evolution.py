
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
] # don't delete this comment! ## mysql_evolutions_end ##
