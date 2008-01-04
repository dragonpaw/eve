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
-- Table structure for table `crpNPCDivisions`
--

DROP TABLE IF EXISTS `crpNPCDivisions`;
CREATE TABLE `crpNPCDivisions` (
  `divisionID` int(11) NOT NULL default '0',
  `divisionName` char(100) default NULL,
  `description` varchar(1000) default NULL,
  `leaderType` char(100) default NULL,
  PRIMARY KEY  (`divisionID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `crpNPCDivisions`
--


/*!40000 ALTER TABLE `crpNPCDivisions` DISABLE KEYS */;
LOCK TABLES `crpNPCDivisions` WRITE;
INSERT INTO `crpNPCDivisions` VALUES (1,'Accounting','','CFO'),(2,'Administration','','CFO'),(3,'Advisory','','Chief Advisor'),(4,'Archives','','Chief Archivist'),(5,'Astrosurveying','','Survey Manager'),(6,'Command','','COO'),(7,'Distribution','','Distribution Manager'),(8,'Financial','','CFO'),(9,'Intelligence','','Chief Operative'),(10,'Internal Security','','Commander'),(11,'Legal','','Principal Clerk'),(12,'Manufacturing','','Assembly Manager'),(13,'Marketing','','Market Manager'),(14,'Mining','','Mining Coordinator'),(15,'Personnel','','Chief of Staff'),(16,'Production','','Production Manager'),(17,'Public Relations','','Chief Coordinator'),(18,'R&D','','Chief Researcher'),(19,'Security','','Commander'),(20,'Storage','','Storage Facilitator'),(21,'Surveillance','','Chief Scout');
UNLOCK TABLES;
/*!40000 ALTER TABLE `crpNPCDivisions` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

