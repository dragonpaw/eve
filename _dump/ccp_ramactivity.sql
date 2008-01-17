-- MySQL dump 10.11
--
-- Host: localhost    Database: ash_eve
-- ------------------------------------------------------
-- Server version       5.0.45-community

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
-- Table structure for table `ccp_ramactivity`
--

DROP TABLE IF EXISTS `ccp_ramactivity`;
CREATE TABLE `ccp_ramactivity` (
  `activityid` int(11) NOT NULL,
  `activityname` varchar(300) NOT NULL,
  PRIMARY KEY  (`activityid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

--
-- Dumping data for table `ccp_ramactivity`
--

LOCK TABLES `ccp_ramactivity` WRITE;
/*!40000 ALTER TABLE `ccp_ramactivity` DISABLE KEYS */;
INSERT INTO `ccp_ramactivity` VALUES (0,'None'),(1,'Manufacturing'),(2,'Research Technology'),(3,'Research Time Production'),(4,'Research Mineral Production'),(5,'Copying'),(6,'Duplicating - Not in game'),(7,'Reverse Engineering - Not in game'),(8,'Inventing'),(50,'Refining');
/*!40000 ALTER TABLE `ccp_ramactivity` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2008-01-17  0:31:38