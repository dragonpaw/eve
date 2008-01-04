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
-- Table structure for table `staServices`
--

DROP TABLE IF EXISTS `staServices`;
CREATE TABLE `staServices` (
  `serviceID` int(11) NOT NULL default '0',
  `serviceName` char(100) default NULL,
  `description` varchar(1000) default NULL,
  PRIMARY KEY  (`serviceID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `staServices`
--


/*!40000 ALTER TABLE `staServices` DISABLE KEYS */;
LOCK TABLES `staServices` WRITE;
INSERT INTO `staServices` VALUES (1,'Bounty Missions',''),(2,'Assassination Missions',''),(4,'Courier Missions',''),(8,'Interbus',''),(16,'Reprocessing Plant',''),(32,'Refinery',''),(64,'Market',''),(128,'Black Market',''),(256,'Stock Exchange',''),(512,'Cloning',''),(1024,'Surgery',''),(2048,'DNA Therapy',''),(4096,'Repair Facilities',''),(8192,'Factory',''),(16384,'Laboratory',''),(32768,'Gambling',''),(65536,'Fitting',''),(131072,'Paintshop',''),(262144,'News',''),(524288,'Storage',''),(1048576,'Insurance','Used to buy insurance for ships.'),(2097152,'Docking',''),(4194304,'Office Rental',''),(8388608,'Jump Clone Facility',''),(16777216,'Loyalty Point Store','');
UNLOCK TABLES;
/*!40000 ALTER TABLE `staServices` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

