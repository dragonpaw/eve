RENAME TABLE agtagents TO ccp_agent,
             agtagenttypes TO ccp_agenttype,
             agtconfig TO ccp_agentconfig,
#             agtofferdetails TO ccp_agentoffer,
#             agtResearchAgents to ccp_agentresearch,
             chrancestries TO ccp_characterancestry,
             chrattributes TO ccp_characterattribute,
             chrbloodlines TO ccp_characterbloodline,
             chrcareers TO ccp_charactercareer,
             chrcareerskills TO ccp_charactercareerskills,
             chrcareerspecialities TO ccp_charactercareerspeciality,
             chrcareerspecialityskills TO ccp_charactercareerspecialityskill,
             chrfactions TO ccp_faction,
             chrraces TO ccp_race,
             chrraceskills TO ccp_raceskill,
             chrschoolagents TO ccp_schoolagent,
             chrschools TO ccp_school,
             crpactivities TO ccp_corporationactivity,
             crpnpccorporationdivisions TO ccp_crpnpccorporationdivisions,
             crpnpccorporationresearchfields TO ccp_crpnpccorporationresearchfields,
             crpnpccorporations TO ccp_corporation,
             crpnpcdivisions TO ccp_corporationdivision,
             dgmattributetypes TO ccp_attribute,
             dgmeffects TO ccp_effect,
             dgmtypeattributes TO ccp_typeattribute,
             dgmtypeeffects TO ccp_typeeffect,
             evegraphics TO ccp_graphic,
             evenames TO ccp_name,
             eveunits TO ccp_unit,
             invblueprinttypes TO ccp_blueprintdetail,
             invcategories TO ccp_category,
             invcontrabandtypes TO ccp_contrabandtype,
             invcontroltowerresourcepurposes TO ccp_stationresourcepurpose,
             invcontroltowerresources TO ccp_stationresource,
             invflags TO ccp_flag,
             invgroups TO ccp_group,
             invmarketgroups TO ccp_marketgroup,
             invmetagroups TO ccp_inventorymetagroup,
             invmetatypes TO ccp_inventorymetatype,
             invtypereactions TO ccp_reaction,
             invtypes TO ccp_item,
             mapcelestialstatistics TO ccp_mapcelestialstatistics,
             mapconstellationjumps TO ccp_constellationjumps,
             mapconstellations TO ccp_constellation,
             mapdenormalize TO ccp_mapdenormalize,
             mapjumps TO ccp_jumps,
             maplandmarks TO ccp_landmarks,
             mapregionjumps TO ccp_regionjumps,
             mapregions TO ccp_region,
             mapsolarsystemjumps TO ccp_solarsystemjumps,
             mapsolarsystems TO ccp_solarsystem,
             mapuniverse TO ccp_mapuniverse,
             ramactivities TO ccp_ramactivity,
             ramassemblylines TO ccp_ramassemblyline,
             ramassemblylinestationcostlogs TO ccp_ramassemblylinestationcostlog,
             ramassemblylinestations TO ccp_ramassemblylinestation,
             ramassemblylinetypedetailpercategory TO ccp_ramassemblylinetypedetailpercategory,
             ramassemblylinetypedetailpergroup TO ccp_ramassemblylinetypedetailpergroup,
             ramassemblylinetypes TO ccp_ramassemblylinetype,
             ramcompletedstatuses TO ccp_ramcompletedstatus,
             raminstallationtypedefaultcontents TO ccp_raminstallationtypedefaultcontent,
             staoperations TO ccp_stationoperation,
             staoperationservices TO ccp_stationoperationservice,
             staservices TO ccp_stationservice,
             stastations TO ccp_station,
             stastationtypes TO ccp_stationtype,
             tl2materialsfortypewithactivity TO ccp_material;

ALTER TABLE `eve`.`ccp_item` DROP COLUMN `slug`;
ALTER TABLE `eve`.`ccp_marketgroup` DROP COLUMN `slug`;
ALTER TABLE `eve`.`ccp_region` DROP COLUMN `slug`;

ALTER TABLE `eve`.`ccp_item` ADD COLUMN `slug` VARCHAR(100) NOT NULL;
ALTER TABLE `eve`.`ccp_marketgroup` ADD COLUMN `slug` VARCHAR(100) NOT NULL;
ALTER TABLE `eve`.`ccp_region` ADD COLUMN `slug` VARCHAR(50) NOT NULL;

ALTER TABLE `eve`.`ccp_item` ADD UNIQUE INDEX `slug`(`slug`);
ALTER TABLE `eve`.`ccp_marketgroup` ADD UNIQUE INDEX `slug`(`slug`);
ALTER TABLE `eve`.`ccp_region` ADD UNIQUE INDEX `slug`(`slug`);

ALTER TABLE `eve`.`ccp_corporation` ADD COLUMN `alliance_id` INT;
ALTER TABLE `eve`.`ccp_corporation` ADD COLUMN `last_updated` DATETIME;
ALTER TABLE `eve`.`ccp_corporation` ADD COLUMN `cached_until` DATETIME;

ALTER TABLE `eve`.`ccp_solarsystem` ADD COLUMN `alliance_old_id` INT;

ALTER TABLE `eve`.`ccp_material` ADD COLUMN `id` INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT,
 ADD PRIMARY KEY (`id`);

ALTER TABLE `eve`.`ccp_reaction` ADD COLUMN `id` INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT,
 ADD PRIMARY KEY (`id`);

ALTER TABLE `eve`.`ccp_stationresource` ADD COLUMN `id` INTEGER UNSIGNED NOT NULL DEFAULT NULL AUTO_INCREMENT,
 ADD PRIMARY KEY (`id`);