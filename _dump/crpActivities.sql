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
-- Table structure for table `crpActivities`
--

DROP TABLE IF EXISTS `crpActivities`;
CREATE TABLE `crpActivities` (
  `activityID` int(11) NOT NULL default '0',
  `activityName` char(100) default NULL,
  `description` varchar(1000) default NULL,
  PRIMARY KEY  (`activityID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `crpActivities`
--


/*!40000 ALTER TABLE `crpActivities` DISABLE KEYS */;
LOCK TABLES `crpActivities` WRITE;
INSERT INTO `crpActivities` VALUES (1,'Agriculture',''),(2,'Construction',''),(3,'Mining',''),(4,'Chemical',''),(5,'Military',''),(6,'Biotech',''),(7,'Hi-Tech',''),(8,'Entertainment',''),(9,'Shipyard',''),(10,'Warehouse',''),(11,'Retail',''),(12,'Trading',''),(13,'Bureaucratic',''),(14,'Political',''),(15,'Legal',''),(16,'Security',''),(17,'Financial',''),(18,'Education',''),(19,'Manufacture',''),(20,'Disputed','');
UNLOCK TABLES;
/*!40000 ALTER TABLE `crpActivities` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

