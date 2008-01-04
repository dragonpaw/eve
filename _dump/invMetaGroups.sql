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
-- Table structure for table `invMetaGroups`
--

DROP TABLE IF EXISTS `invMetaGroups`;
CREATE TABLE `invMetaGroups` (
  `metaGroupID` int(11) NOT NULL default '0',
  `metaGroupName` char(100) default NULL,
  `description` varchar(1000) default NULL,
  `graphicID` int(11) default NULL,
  PRIMARY KEY  (`metaGroupID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `invMetaGroups`
--


/*!40000 ALTER TABLE `invMetaGroups` DISABLE KEYS */;
LOCK TABLES `invMetaGroups` WRITE;
INSERT INTO `invMetaGroups` VALUES (1,'Tech I','',NULL),(2,'Tech II','',NULL),(3,'Storyline','',NULL),(4,'Faction','',NULL),(5,'Officer','',NULL),(6,'Deadspace','Modules found in deadspace.',NULL),(7,'Frigates','',NULL),(8,'Elite Frigates','',NULL),(9,'Commander Frigates','',NULL),(10,'Destroyer','',NULL),(11,'Cruiser','',NULL),(12,'Elite Cruiser','',NULL),(13,'Commander Cruiser','',NULL);
UNLOCK TABLES;
/*!40000 ALTER TABLE `invMetaGroups` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

