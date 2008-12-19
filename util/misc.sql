
ALTER TABLE `eve`.`ccp_item` DROP COLUMN `slug`;
ALTER TABLE `eve`.`ccp_marketgroup` DROP COLUMN `slug`;
ALTER TABLE `eve`.`ccp_region` DROP COLUMN `slug`;

ALTER TABLE `eve`.`ccp_item` ADD COLUMN `slug` VARCHAR(100) NOT NULL;
ALTER TABLE `eve`.`ccp_marketgroup` ADD COLUMN `slug` VARCHAR(100) NOT NULL;
ALTER TABLE `eve`.`ccp_region` ADD COLUMN `slug` VARCHAR(50) NOT NULL;

ALTER TABLE `eve`.`ccp_item` ADD UNIQUE INDEX `slug`(`slug`);
ALTER TABLE `eve`.`ccp_marketgroup` ADD UNIQUE INDEX `slug`(`slug`);
ALTER TABLE `eve`.`ccp_region` ADD UNIQUE INDEX `slug`(`slug`);

ALTER TABLE `ccp_corporation`
    ADD COLUMN `alliance_id` `alliance_id` INT(11) NULL DEFAULT NULL,
    ADD COLUMN `last_updated` `last_updated` DATETIME NULL DEFAULT NULL,
    ADD COLUMN `cached_until` `cached_until` DATETIME NULL DEFAULT NULL;

ALTER TABLE `eve`.`ccp_solarsystem`
    ADD COLUMN `alliance_id` INTEGER,
    ADD COLUMN `alliance_old_id` INTEGER,
    ADD COLUMN `sovereigntyLevel` INTEGER,
    ADD COLUMN `sovereigntyDate` DATE;

ALTER TABLE `eve`.`ccp_constellation`
    ADD COLUMN `sovereigntyDateTime` DATETIME,
    ADD COLUMN `graceDateTime` DATETIME,
    ADD COLUMN `alliance_id` INTEGER;

ALTER TABLE `eve`.`ccp_station`
    ADD COLUMN `capitalStation`,
    ADD COLUMN `ownershipDateTime` DATETIME,
    ADD COLUMN `upgradeLevel` INTEGER,
    ADD COLUMN `customServiceMask` INTEGER;

ALTER TABLE `eve`.`ccp_material` ADD COLUMN `id` INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT,
 ADD UNIQUE INDEX (`id`);;

ALTER TABLE `eve`.`ccp_reaction` ADD COLUMN `id` INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT,
 ADD UNIQUE INDEX (`id`);

ALTER TABLE `eve`.`ccp_stationresource` ADD COLUMN `id` INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT,
 ADD UNIQUE INDEX (`id`);

ALTER TABLE `eve`.`ccp_item` CHANGE COLUMN `typeName` `name`;
