-- Copyright (c) 2009 www.cryer.co.uk
-- Script is free to use provided this copyright header is included.
drop procedure if exists AddColumnUnlessExists;
delimiter '//'

create procedure AddColumnUnlessExists(
	IN dbName tinytext,
	IN tableName tinytext,
	IN fieldName tinytext,
	IN fieldDef text)
begin
	IF NOT EXISTS (
		SELECT * FROM information_schema.COLUMNS
		WHERE column_name=fieldName
		and table_name=tableName
		and table_schema=dbName
		)
	THEN
		set @ddl=CONCAT('ALTER TABLE ',dbName,'.',tableName,
			' ADD COLUMN ',fieldName,' ',fieldDef);
		prepare stmt from @ddl;
		execute stmt;
	END IF;
end;
//

delimiter ';'

-- call AddColumnUnlessExists('GIS', 'boundaries', 'fillColour', 'int unsigned not null default 1');

call AddColumnUnlessExists('eve', 'invTypes', 'slug', 'VARCHAR(50) NOT NULL');
call AddColumnUnlessExists('eve', 'invMarketGroups', 'slug', 'VARCHAR(50) NOT NULL');
call AddColumnUnlessExists('eve', 'invGroups', 'slug', 'VARCHAR(50) NOT NULL');
call AddColumnUnlessExists('eve', 'mapRegions', 'slug', 'VARCHAR(50) NOT NULL');

-- Only call these AFTER you slugify the objects.
-- ALTER TABLE `eve`.`invTypes` ADD UNIQUE INDEX `slug`(`slug`);
-- ALTER TABLE `eve`.`invMarketGroups` ADD UNIQUE INDEX `slug`(`slug`);
-- ALTER TABLE `eve`.`invGroups` ADD UNIQUE INDEX `slug`(`slug`);
-- ALTER TABLE `eve`.`mapRegions` ADD UNIQUE INDEX `slug`(`slug`);
-- ALTER TABLE `eve`.`ccp_alliance` ADD UNIQUE INDEX `slug`(`slug`);

call AddColumnUnlessExists('eve', 'crpNPCCorporations', 'alliance_id', 'INT(11) NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'crpNPCCorporations', 'last_updated', 'DATETIME NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'crpNPCCorporations', 'cached_until', 'DATETIME NULL DEFAULT NULL');

call AddColumnUnlessExists('eve', 'mapSolarSystems', 'alliance_id', 'INTEGER NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'mapSolarSystems', 'alliance_old_id', 'INTEGER NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'mapSolarSystems', 'sovereigntyLevel', 'INTEGER NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'mapSolarSystems', 'sovereigntyDate', 'DATETIME NULL DEFAULT NULL');

call AddColumnUnlessExists('eve', 'mapConstellations', 'sovereigntyDateTime', 'DATETIME NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'mapConstellations', 'graceDateTime', 'DATETIME NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'mapConstellations', 'alliance_id', 'INTEGER NULL DEFAULT NULL');

call AddColumnUnlessExists('eve', 'staStations', 'capitalStation', 'INTEGER NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'staStations', 'ownershipDateTime', 'DATETIME NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'staStations', 'upgradeLevel', 'INTEGER NULL DEFAULT NULL');
call AddColumnUnlessExists('eve', 'staStations', 'customServiceMask', 'INTEGER NULL DEFAULT NULL');

call AddColumnUnlessExists('eve', 'typeActivityMaterials', 'id', 'INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT UNIQUE');

call AddColumnUnlessExists('eve', 'invTypeReactions', 'id', 'INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT UNIQUE');

call AddColumnUnlessExists('eve', 'invControlTowerResources', 'id', 'INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT UNIQUE');

ALTER TABLE `eve`.`dgmTypeAttributes` ADD COLUMN `id` int  NOT NULL AUTO_INCREMENT AFTER `valueFloat`,
 DROP PRIMARY KEY,
 ADD PRIMARY KEY (`id`);
