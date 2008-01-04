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
-- Table structure for table `invCategories`
--

DROP TABLE IF EXISTS `invCategories`;
CREATE TABLE `invCategories` (
  `categoryID` int(11) NOT NULL default '0',
  `categoryName` char(100) default NULL,
  `description` varchar(3000) default NULL,
  `graphicID` int(11) default NULL,
  `published` int(11) default NULL,
  PRIMARY KEY  (`categoryID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `invCategories`
--


/*!40000 ALTER TABLE `invCategories` DISABLE KEYS */;
LOCK TABLES `invCategories` WRITE;
INSERT INTO `invCategories` VALUES (0,'#System','',NULL,0),(1,'Owner','',1,0),(2,'Celestial','',6,1),(3,'Station','',17,0),(4,'Material','',399,1),(5,'Accessories','',33,0),(6,'Ship','',38,1),(7,'Module','',67,1),(8,'Charge','',171,1),(9,'Blueprint','',194,1),(10,'Trading','',195,0),(11,'Entity','',NULL,0),(14,'Bonus','Character creation bonuses.  Like innate skills but genetic rather than learned.',0,0),(16,'Skill','Where all the skills go under.',33,1),(17,'Commodity','',0,1),(18,'Drone','Player owned and controlled drones.',0,1),(20,'Implant','Implant',0,1),(22,'Deployable','',0,1),(23,'Structure','Player owned structure related objects',0,1),(24,'Reaction','',0,1),(25,'Asteroid','',NULL,1);
UNLOCK TABLES;
/*!40000 ALTER TABLE `invCategories` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

