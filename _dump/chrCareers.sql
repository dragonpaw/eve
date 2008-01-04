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
-- Table structure for table `chrCareers`
--

DROP TABLE IF EXISTS `chrCareers`;
CREATE TABLE `chrCareers` (
  `raceID` int(11) NOT NULL default '0',
  `careerID` int(11) NOT NULL default '0',
  `careerName` char(100) default NULL,
  `description` varchar(2000) default NULL,
  `shortDescription` varchar(500) default NULL,
  `graphicID` int(11) default NULL,
  `schoolID` int(11) default NULL,
  PRIMARY KEY  (`raceID`,`careerID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `chrCareers`
--


/*!40000 ALTER TABLE `chrCareers` DISABLE KEYS */;
LOCK TABLES `chrCareers` WRITE;
INSERT INTO `chrCareers` VALUES (1,11,'Military','A career in the military means learning what you need to know about how to dispose of enemy vessels as fast and securely as possible, without them disposing of you. Military academies educate enlist cadets thoroughly in combat related skills.','Focuses mainly on combat training.',3178,17),(1,14,'Business','Business is all about dealing with people, solving problems or finding compromises in quarrels and servicing trade routes. And of course, all in the name of financial success. Business careers can be roughly divided into two categories. One revolves entirely around buying and selling, dealing with business contacts and playing the market with the sole purpose of maximizing the profit margin. The other catergory is all about preparing the pilot to lead a group or a crowd of people, form and run a corporation and to supply leadership.','Focuses mainly on practical studies.',3175,18),(1,17,'Industry','A carrier in industry is a career that spells not only wealth for those that choose to follow that path, but it also opens the door to potential popularity. In the war torn reaches of space, everyone loves a provider. Serious industrialists need to learn how to harvest precious ore, refine it and either produce something from it or haul it around and sell where prices are high. Eventually, a successful industrialist often ends up with a lot of cash on his hands to spend on some other line of work.','Focuses mainly on technical studies.',3172,19),(2,21,'Military','A career in the military means learning what you need to know about how to dispose of enemy vessels as fast and securely as possible, without them disposing of you. Military academies educate enlist cadets thoroughly in combat related skills.','An up-and-coming military training institution.',3178,14),(2,24,'Business','Business is all about dealing with people, solving problems or finding compromises in quarrels and servicing trade routes. And of course, all in the name of financial success. Business careers can be roughly divided into two categories. One revolves entirely around buying and selling, dealing with business contacts and playing the market with the sole purpose of maximizing the profit margin. The other catergory is all about preparing the pilot to lead a group or a crowd of people, form and run a corporation and to supply leadership.','Founded to help gifted children reach their potential.',3175,16),(2,27,'Industry','A carrier in industry is a career that spells not only wealth for those that choose to follow that path, but it also opens the door to potential popularity. In the war torn reaches of space, everyone loves a provider. Serious industrialists need to learn how to harvest precious ore, refine it and either produce something from it or haul it around and sell where prices are high. Eventually, a successful industrialist often ends up with a lot of cash on his hands to spend on some other line of work.','A forward-thinking house of higher learning.',3172,15),(4,41,'Military','A career in the military means learning what you need to know about how to dispose of enemy vessels as fast and securely as possible, without them disposing of you. Military academies educate enlist cadets thoroughly in combat related skills.','The Empire\'s breeding grounds for military might.',3178,11),(4,44,'Business','Business is all about dealing with people, solving problems or finding compromises in quarrels and servicing trade routes. And of course, all in the name of financial success. Business careers can be roughly divided into two categories. One revolves entirely around buying and selling, dealing with business contacts and playing the market with the sole purpose of maximizing the profit margin. The other catergory is all about preparing the pilot to lead a group or a crowd of people, form and run a corporation and to supply leadership.','A bastion of liberalism and free thought.',3175,12),(4,47,'Industry','A carrier in industry is a career that spells not only wealth for those that choose to follow that path, but it also opens the door to potential popularity. In the war torn reaches of space, everyone loves a provider. Serious industrialists need to learn how to harvest precious ore, refine it and either produce something from it or haul it around and sell where prices are high. Eventually, a successful industrialist often ends up with a lot of cash on his hands to spend on some other line of work.','One of the most venerable educational facilities in the universe.',3172,13),(8,81,'Military','A career in the military means learning what you need to know how about to dispose of enemy vessels as fast and securely as possible, without them disposing of you. Military academies educate enlist cadets thoroughly in combat related skills.','An extremely strict but effective military academy.',3178,20),(8,84,'Business','Business is all about dealing with people, solving problems or finding compromises in quarrels and servicing trade routes. And of course, all in the name of financial success. Business careers can be roughly divided into two categories. One revolves entirely around buying and selling, dealing with business contacts and playing the market with the sole purpose of maximizing the profit margin. The other catergory is all about preparing the pilot to lead a group or a crowd of people, form and run a corporation and to supply leadership.','The largest school in the universe.',3175,21),(8,87,'Industry','A carrier in industry is a career that spells not only wealth for those that choose to follow that path, but it also opens the door to potential popularity. In the war torn reaches of space, everyone loves a provider. Serious industrialists need to learn how to harvest precious ore, refine it and either produce something from it or haul it around and sell where prices are high. Eventually, a successful industrialist often ends up with a lot of cash on his hands to spend on some other line of work.','One of the very best technical schools in the universe.',3172,22),(16,161,'Business','','',3175,23),(16,164,'Industry','','',3172,24),(16,167,'Military','','',3178,25);
UNLOCK TABLES;
/*!40000 ALTER TABLE `chrCareers` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

