-- MySQL dump 10.10
--
-- Host: localhost    Database: trinity
-- ------------------------------------------------------
-- Server version	5.0.24a-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `crpNPCCorporationResearchFields`
--

DROP TABLE IF EXISTS `crpNPCCorporationResearchFields`;
CREATE TABLE `crpNPCCorporationResearchFields` (
  `skillID` int(11) NOT NULL default '0',
  `corporationID` int(11) NOT NULL default '0',
  `supplierType` int(11) default NULL,
  PRIMARY KEY  (`skillID`,`corporationID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `crpNPCCorporationResearchFields`
--


/*!40000 ALTER TABLE `crpNPCCorporationResearchFields` DISABLE KEYS */;
LOCK TABLES `crpNPCCorporationResearchFields` WRITE;
INSERT INTO `crpNPCCorporationResearchFields` VALUES (11433,1000010,1),(11433,1000057,1),(11433,1000109,1),(11441,1000102,0),(11441,1000109,0),(11442,1000066,0),(11442,1000160,1),(11443,1000019,0),(11443,1000066,1),(11444,1000064,0),(11444,1000066,0),(11444,1000151,0),(11445,1000056,0),(11445,1000057,0),(11445,1000160,0),(11446,1000010,0),(11446,1000020,0),(11447,1000064,0),(11447,1000151,0),(11448,1000010,0),(11448,1000020,1),(11448,1000056,1),(11448,1000101,1),(11448,1000151,1),(11449,1000020,0),(11449,1000056,1),(11449,1000064,1),(11449,1000102,1),(11450,1000101,0),(11450,1000102,0),(11450,1000109,0),(11451,1000056,0),(11451,1000057,0),(11452,1000010,1),(11452,1000057,0),(11452,1000160,1),(11453,1000020,1),(11453,1000056,1),(11453,1000101,0),(11453,1000151,1),(11454,1000010,0),(11454,1000019,0),(11454,1000020,0),(11455,1000019,1),(11455,1000102,0),(11455,1000151,1),(11529,1000066,1),(11529,1000160,0);
UNLOCK TABLES;
/*!40000 ALTER TABLE `crpNPCCorporationResearchFields` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

