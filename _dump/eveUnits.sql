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
-- Table structure for table `eveUnits`
--

DROP TABLE IF EXISTS `eveUnits`;
CREATE TABLE `eveUnits` (
  `unitID` int(11) NOT NULL default '0',
  `unitName` char(100) default NULL,
  `displayName` char(20) default NULL,
  `description` varchar(1000) default NULL,
  PRIMARY KEY  (`unitID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `eveUnits`
--


/*!40000 ALTER TABLE `eveUnits` DISABLE KEYS */;
LOCK TABLES `eveUnits` WRITE;
INSERT INTO `eveUnits` VALUES (1,'Length','m','Meter'),(2,'Mass','kg','Kilogram'),(3,'Time','sec','Second'),(4,'Electric Current','A','Ampere'),(5,'Temperature','K','Kelvin'),(6,'Amount Of Substance','mol','Mole'),(7,'Luminous Intensity','cd','Candela'),(8,'Area','m2','Square meter'),(9,'Volume','m3','Cubic meter'),(10,'Speed','m/sec','Meter per second'),(11,'Acceleration','m/sec','Meter per second squared'),(12,'Wave Number','m-1','Reciprocal meter'),(13,'Mass Density','kg/m3','Kilogram per cubic meter'),(14,'Specific Volume','m3/kg','Cubic meter per kilogram'),(15,'Current Density','A/m2','Ampere per square meter'),(16,'Magnetic Field Strength','A/m','Ampere per meter'),(17,'Amount-Of-Substance Concentration','mol/m3','Mole per cubic meter'),(18,'Luminance','cd/m2','Candela per square meter'),(19,'Mass Fraction','kg/kg = 1','Kilogram per kilogram, which may be represented by the number 1'),(101,'Milliseconds','ms',''),(102,'Millimeters','mm',''),(103,'MegaPascals','',''),(104,'Multiplier','x','Indicates that the unit is a multiplier.'),(105,'Percentage','%',''),(106,'Teraflops','tf',''),(107,'MegaWatts','MW',''),(108,'Inverse Absolute Percent','%','Used for resistance.\n0.0 = 100% 1.0 = 0%'),(109,'Modifier Percent','%','Used for multipliers displayed as %\n1.1 = +10%\n0.9 = -10%'),(111,'Inversed Modifier Percent','%','Used to modify damage resistance. Damage resistance bonus.\n0.1 = 90%\n0.9 = 10%'),(112,'Radians/Second','rad/sec','Rotation speed.'),(113,'Hitpoints','HP',''),(114,'capacitor units','Energy',''),(115,'groupID','groupID',''),(116,'typeID','typeID',''),(117,'Sizeclass','1=small 2=medium 3=l',''),(118,'Ore units','Ore units',''),(119,'attributeID','attributeID',''),(120,'attributePoints','points',''),(121,'realPercent','%','Used for real percentages, i.e. the number 5 is 5%'),(122,'Fitting slots','',''),(123,'trueTime','sec','Shows seconds directly'),(124,'Modifier Relative Percent','%','Used for relative percentages displayed as %'),(125,'Newton','N',''),(126,'Light Year','ly',''),(127,'Absolute Percent','%','0.0 = 0% 1.0 = 100%'),(128,'Drone bandwidth','Mbit/sec','Mega bits per second');
UNLOCK TABLES;
/*!40000 ALTER TABLE `eveUnits` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

