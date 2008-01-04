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
-- Table structure for table `chrSchools`
--

DROP TABLE IF EXISTS `chrSchools`;
CREATE TABLE `chrSchools` (
  `raceID` int(11) default NULL,
  `schoolID` int(11) NOT NULL default '0',
  `schoolName` char(100) default NULL,
  `description` varchar(1000) default NULL,
  `graphicID` int(11) default NULL,
  `corporationID` int(11) default NULL,
  `agentID` int(11) default NULL,
  `newAgentID` int(11) default NULL,
  `careerID` int(11) default NULL,
  PRIMARY KEY  (`schoolID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `chrSchools`
--


/*!40000 ALTER TABLE `chrSchools` DISABLE KEYS */;
LOCK TABLES `chrSchools` WRITE;
INSERT INTO `chrSchools` VALUES (4,11,'Imperial Academy','The Imperial Academy (from which all Amarr enlists graduate) is rooted in tradition and generally considered sub-par to the more modern military institutes found in the other empires. However, it is the only one of its kind within the Amarr Empire, thus serving a vital function.',1447,1000166,3010801,3018681,41),(4,12,'Hedion University','Hedion University (graduating the best Business students in the Empire) is located in the Hedion system - the first solar system colonized by the Amarrians after their own. The university was founded by spirited and liberal scholars, free from the scrutinizing eye of the Emperor and his theologians.',1448,1000165,3010791,3018680,44),(4,13,'Royal Amarr Institute','One of the oldest educational facilities in the universe (the breeding grounds for future Amarrian industrialists), the Royal Amarr Institute dates from an era when the Amarrians were still confined to their continent on Amarr Prime, before the Empire and the Great Reclaiming.',1449,1000077,3013332,3018682,47),(2,14,'Republic Military School','The Republic Military School (from which all Minmatar enlists graduate) was for a long time the bastard child of the Minmatar education system - it existed because it was perceived as needed, but it had no support; most military personnel were Gallente trained.  In recent years, however, as the Republic tries to ascertain its total independence, efforts are being made to transform the RMS into a top-notch military school.',1450,1000170,3010841,3018678,21),(2,15,'Republic University','The Republic University (from where future Minmatar industrialists graduate) was founded by Minmatar emigrates as a show of support for the fledgling republic shortly after its inception. The school is modeled after the University of Caille and based on the Gallentean education system.',1451,1000171,3010851,3018679,27),(2,16,'Pator Tech School','Pator Tech School (from where Minmatar business people are commonly educated) was founded on the principle of helping gifted Minmatar children be better qualified for high-level positions; something the Republic was in dire need of when assembling a new government and administration virtually from scratch. This principle has held intact to this day, even if the foundations of the Republic were firmly set a long time ago.',1458,1000172,3010861,3018677,24),(1,17,'State War Academy','The State War Academy  (from which all Caldari enlists graduate)  was founded shortly after the Caldari State came into being, while the war with the Gallente Federation was still in full swing. Due to this, the academy has always had a very combat oriented slant, as opposed to the broader scope of ship handling.',1452,1000167,3010811,3018676,11),(1,18,'Science and Trade Institute','Like all Caldari schools, the Science & Trade Institute (from which all Caldari Business Students graduate) has a very formal curriculum that focuses primarily on the practical side of education. This results in a very dull and tedious learning process, but one that is remarkably efficient.',1453,1000045,3012249,3018675,14),(1,19,'School of Applied Knowledge','The School of Applied Knowledge (from where future Caldari industrialists graduate) focuses mainly on technical studies and is considered the best school for aspiring engineers. The school collaborates with many leading Caldari corporations, an arrangement which benefits the school, the companies and not the least the students.',1455,1000044,3012239,3018672,17),(8,20,'Federal Navy Academy','The Federation Navy (where all Gallente cadets are enlisted) has recently begun upholding extremely strict standards of professionalism for its cadets. The result of these standards, draconian even for a military school, is a leaner, meaner academy with much stricter entry requirements than before and more effective tutoring.',1454,1000168,3010821,3018684,81),(8,21,'University of Caille','The largest school in the universe at almost half a million students, the University of Caille has long acted as a melting pot for cultures and ideas from all over. As befits its status, it offers a wide range of studies, but is best known for its extensive anthropology department.',1456,1000115,3009793,3018685,84),(8,22,'Center for Advanced Studies','Originally conceived as a think-tank for researchers at Chemal Tech, the Center for Advanced Studies (the breeding grounds for future Gallente industrialists) evolved into an independent educational facility that today is considered one of the very best technical schools in the universe.',1457,1000169,3010831,3018683,87),(16,23,'Society of Conscious Thought','The Society of Conscious Thought was founded some 300 years ago. Since then it has seen many guises, including spiritual healing-house and political power-block. Today, it is one of the finest and most respected educational facilities in the world of EVE. As it is only loosely connected to the Jove state the Society admits non-Jovian students. For them, being admitted to a Society school is a great honor and an almost certain ticket to a prestigious position later in life.',NULL,1000131,3010177,NULL,161),(16,24,'Material Institute','The Jovians, with all their power and resources, are not always very pragmatic. The Material Institute was founded precisely to combat this. Most Jovians are already well schooled in the technical aspects, but they need some tutoring on the practical application for use in industry and manufacturing.',NULL,1000177,3010484,NULL,164),(16,25,'Academy of Aggressive Behaviour','Most Jovians have had their aggressive instincts curbed or even removed through genetic engineering. The Academy for Aggressive Behaviour, responsible for training space cadets, uses the latest in gene therapies to re-introuduce the base instincts to their students to ensure the animalistic nature of humans, so important for fighting, is alive and fresh in them.',NULL,1000178,3010447,NULL,167);
UNLOCK TABLES;
/*!40000 ALTER TABLE `chrSchools` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

