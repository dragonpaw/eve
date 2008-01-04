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
-- Table structure for table `chrSchoolAgents`
--

DROP TABLE IF EXISTS `chrSchoolAgents`;
CREATE TABLE `chrSchoolAgents` (
  `schoolID` int(11) NOT NULL default '0',
  `agentIndex` int(11) NOT NULL default '0',
  `agentID` int(11) NOT NULL default '0',
  PRIMARY KEY  (`schoolID`,`agentIndex`,`agentID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `chrSchoolAgents`
--


/*!40000 ALTER TABLE `chrSchoolAgents` DISABLE KEYS */;
LOCK TABLES `chrSchoolAgents` WRITE;
INSERT INTO `chrSchoolAgents` VALUES (11,1,3018681),(11,2,3018821),(11,3,3018822),(11,4,3018823),(11,5,3018824),(12,1,3018680),(12,2,3018817),(12,3,3018818),(12,4,3018819),(12,5,3018820),(13,1,3018682),(13,2,3018809),(13,3,3018810),(13,4,3018811),(13,5,3018812),(14,1,3018678),(14,2,3018837),(14,3,3018838),(14,4,3018839),(14,5,3018840),(15,1,3018679),(15,2,3018841),(15,3,3018842),(15,4,3018843),(15,5,3018844),(16,1,3018677),(16,2,3018845),(16,3,3018846),(16,4,3018847),(16,5,3018848),(17,1,3018676),(17,2,3018825),(17,3,3018826),(17,4,3018827),(17,5,3018828),(18,1,3018675),(18,2,3018805),(18,3,3018806),(18,4,3018807),(18,5,3018808),(19,1,3018672),(19,2,3018801),(19,3,3018802),(19,4,3018803),(19,5,3018804),(20,1,3018684),(20,2,3018829),(20,3,3018830),(20,4,3018831),(20,5,3018832),(21,1,3018685),(21,2,3018813),(21,3,3018814),(21,4,3018815),(21,5,3018816),(22,1,3018683),(22,2,3018833),(22,3,3018834),(22,4,3018835),(22,5,3018836);
UNLOCK TABLES;
/*!40000 ALTER TABLE `chrSchoolAgents` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

