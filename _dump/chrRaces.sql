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
-- Table structure for table `chrRaces`
--

DROP TABLE IF EXISTS `chrRaces`;
CREATE TABLE `chrRaces` (
  `raceID` int(11) NOT NULL default '0',
  `raceName` char(100) default NULL,
  `description` varchar(1000) default NULL,
  `skillTypeID1` int(11) default NULL,
  `typeID` int(11) default NULL,
  `typeQuantity` int(11) default NULL,
  `graphicID` int(11) default NULL,
  `shortDescription` varchar(500) default NULL,
  PRIMARY KEY  (`raceID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `chrRaces`
--


/*!40000 ALTER TABLE `chrRaces` DISABLE KEYS */;
LOCK TABLES `chrRaces` WRITE;
INSERT INTO `chrRaces` VALUES (1,'Caldari','Ruled by a handful of mega corporations, the Caldari State is the epitome of civil duty and efficiency, where ruthless capitalism leaves no room for human rights or feelings. They are brutally efficient fighters, giving their opponents no chance of retaliation. Through grit and superior technology, the State fought the much larger Gallente Federation to a standstill.',3330,215,100,1439,'The Caldari State is the epitome of civil duty and ruthless militaristic efficiency.'),(2,'Minmatar','Enslaved by the Amarr Empire for centuries, the Minmatar Republic now revels in its relatively newfound freedom, fighting for its claim as a major power. Steeped in a deep-rooted tribal society, the Matari display vehement attachment to their kindred. They will never forget their lost brothers and sisters, still enslaved by the Amarr Empire.',3329,178,100,1440,'Formerly enslaved by the Amarr, the Minmatar are a nation of tough, no-nonsense tribalists.'),(4,'Amarr','Amarr is a vast and ancient empire, with the Amarr Emperor sitting at the head of a feudal society. It is rich in history and traditions, with a caste system that is cruel to those on the bottom, but kind to those at the top. Centuries ago, during a time known as the Reclaiming, the Amarr Empire enslaved several nations, including the Minmatars, but has calmed down in recent times.',3331,NULL,NULL,1442,'Amarr is a vast and ancient empire, solely devoted to God and Emperor.'),(8,'Gallente','The Gallente Federation is the only true democracy in the universe at present, and its inhabitants regard themselves as champions of freedom and liberty. Their human touch makes them excellent traders and media moguls. Forged in fire in a war against the Caldari State, the Federation still depends on its mighty drone fleets to defend its beliefs against encroaching anarchy.',3328,215,100,1441,'Championing freedom and liberty across the universe, the Gallente Federation is the only true democracy currently in existence.'),(16,'Jove','The most mysterious and elusive of all the universe\'s peoples, the Jovians number only a fraction of any of their neighbors, but their technological superiority makes them powerful beyond all proportion.',NULL,NULL,NULL,NULL,''),(32,'Pirate','',NULL,NULL,NULL,NULL,'');
UNLOCK TABLES;
/*!40000 ALTER TABLE `chrRaces` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

