/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.11-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: wiseekr
-- ------------------------------------------------------
-- Server version	10.11.11-MariaDB-0ubuntu0.24.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `access_points`
--

DROP TABLE IF EXISTS `access_points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `access_points` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bssid` varchar(17) NOT NULL,
  `essid` varchar(64) DEFAULT NULL,
  `counter` int(11) NOT NULL,
  `cracked_password` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_access_points_bssid` (`bssid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access_points`
--

LOCK TABLES `access_points` WRITE;
/*!40000 ALTER TABLE `access_points` DISABLE KEYS */;
/*!40000 ALTER TABLE `access_points` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES
('d4b0b0689f1d');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `followers`
--

DROP TABLE IF EXISTS `followers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `followers` (
  `follower_id` int(11) NOT NULL,
  `followed_id` int(11) NOT NULL,
  KEY `fk_followers_followed_id_users` (`followed_id`),
  KEY `fk_followers_follower_id_users` (`follower_id`),
  CONSTRAINT `fk_followers_followed_id_users` FOREIGN KEY (`followed_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_followers_follower_id_users` FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `followers`
--

LOCK TABLES `followers` WRITE;
/*!40000 ALTER TABLE `followers` DISABLE KEYS */;
INSERT INTO `followers` VALUES
(1,5),
(2,1),
(2,5),
(3,10),
(3,5),
(3,6),
(5,9),
(5,6),
(5,3),
(6,7),
(7,4),
(7,6),
(7,10),
(9,2),
(9,6),
(9,8),
(10,5);
/*!40000 ALTER TABLE `followers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` varchar(280) NOT NULL,
  `timestamp` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_posts_timestamp` (`timestamp`),
  KEY `ix_posts_user_id` (`user_id`),
  CONSTRAINT `fk_posts_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
INSERT INTO `posts` VALUES
(1,'Per consider course same food government. Mouth best certain teacher challenge performance.','2025-04-17 11:39:57',6),
(2,'Decide finish anyone executive peace wind second. Sense democratic center deep technology particularly. Garden us cultural. Use reduce war treat message.','2025-03-23 17:44:15',10),
(3,'Manage police despite source important much. Development health answer fly keep. Huge develop common. Crime able speech.','2025-02-18 16:32:31',10),
(4,'Other avoid no poor wonder that. Media wife blue hour race interesting common. Away off box debate task trouble.','2025-02-16 19:38:05',5),
(5,'Light try usually see. Speak happen similar recently.','2025-03-03 19:50:17',6),
(6,'Plan our local author.','2025-03-17 16:57:20',9),
(7,'Around station yeah. Enjoy full movie meet get they. Tend pressure though his write former growth.','2025-01-16 23:14:57',10),
(8,'Goal job to lawyer term. Friend center response adult sell view blue. Way lose tough option these.','2025-03-04 09:43:40',4),
(9,'Us thank agreement realize develop.','2025-01-04 22:01:29',5),
(10,'Budget center nearly call join place. Program around quite government.','2025-01-19 01:48:38',7),
(11,'Father along stop health against family expert pull. Walk way poor thus benefit fish.','2025-03-07 10:56:32',9),
(12,'Necessary so charge. Wrong detail young behind.','2025-01-22 17:11:23',2),
(13,'Can occur night consider man wear check. Middle national home day.','2025-01-15 09:49:47',9),
(14,'Kid authority appear brother two. Style pattern speech civil act. Television result protect large machine.','2025-03-22 22:11:57',9),
(15,'Message back shake apply ball summer respond. Painting use enough watch right modern.','2025-03-17 23:15:26',2),
(16,'Share since recently. Low identify notice hard member feeling day. Security class including mention perhaps various.','2025-01-22 07:03:57',1),
(17,'Deep spend painting live style. Situation not catch letter black use. Right nice common leave early fire Democrat energy.','2025-03-22 03:40:02',4),
(18,'Stand military wish team speech unit. Local television among rule.','2025-01-09 16:55:56',3),
(19,'Way shake war finish Republican or.','2025-02-25 11:46:14',3),
(20,'Picture different only my. Hard local beautiful since. Green first individual along not.','2025-04-03 22:50:31',10),
(21,'Rate can accept note night. Shake create act author agreement significant themselves include.','2025-03-09 03:52:51',10),
(22,'Suddenly hospital story seem. Onto generation create important hot. Charge difficult also when.','2025-01-13 11:48:11',4),
(23,'Song short apply. Short state day southern guy lose.','2025-03-21 01:53:38',8),
(24,'Six include maybe dark into certainly. Term lot conference American early.','2025-03-25 22:46:44',5),
(25,'Order guy give white wife field.','2025-04-09 05:50:34',6),
(26,'Send last finish occur anyone. Others seem bag major show value decade.','2025-04-19 16:14:16',1),
(27,'Lose detail use concern laugh yet total. Hour care less wish.','2025-01-03 09:46:32',7),
(28,'Rich indicate any. Trip senior outside blood.','2025-01-03 01:02:30',8),
(29,'Do sport choose response remain me knowledge area. Relate read like audience something.','2025-01-11 00:35:33',9),
(30,'Responsibility interesting I person certain whom voice star. Position budget power push. Together team since whether.','2025-01-30 18:35:11',7),
(31,'People put seat five continue agent both list. Body despite improve high.','2025-04-13 18:21:16',8),
(32,'Play letter history. See hold anything maybe. Red add value image.','2025-03-31 14:30:56',2),
(33,'Standard create animal argue reveal entire white. Talk determine image food us page. Machine a organization sell indeed.','2025-02-15 05:15:05',9),
(34,'Compare trip actually actually side American. Student away rich by. Hour scientist task music specific partner herself.','2025-04-13 23:09:08',9),
(35,'Knowledge resource as religious arm right body. Event physical arm week.','2025-02-11 03:44:53',1),
(36,'Case must alone tree such watch. Plant sometimes early.','2025-02-09 20:12:34',2),
(37,'Wait affect military color raise senior agreement mouth.','2025-01-01 02:25:31',1),
(38,'Reach support toward available stage seven mouth. Data already perform. Across development a quickly. Yourself protect over the represent those.','2025-04-04 19:09:14',10),
(39,'Media design exist question shake. Nation thank particular thank account leader rest. Challenge through ten image detail vote.','2025-01-05 09:24:22',4),
(40,'High own not claim garden tough soldier. Last such before reduce produce. Now job court eat around condition land physical.','2025-01-27 15:14:07',8),
(41,'Investment fill save environmental do whom. Nature race series station play bit notice per.','2025-01-01 13:42:00',4),
(42,'Thousand letter record despite may up. With particularly follow better much. Century pick unit before.','2025-01-20 10:39:23',7),
(43,'According financial ask mouth night.','2025-03-06 09:27:12',6),
(44,'Gas moment rich ahead national political. Lay drug blue.','2025-01-29 02:47:57',10),
(45,'Republican plant by to thought. Gas red industry air first.','2025-03-10 18:18:16',6),
(46,'Seem personal half accept ahead call network. Number say ok television so word. Eat explain group save question seem treat.','2025-03-26 22:54:02',9),
(47,'Line kind family Democrat maintain. Factor several doctor white.','2025-02-12 22:06:02',9),
(48,'Street mind option recognize receive question bring. Understand drug management rather catch we.','2025-02-14 06:13:27',3),
(49,'Hair chance subject stand. Notice pay TV service. Method amount defense certainly.','2025-03-13 04:29:25',2),
(50,'Turn any already.','2025-03-08 07:11:39',9),
(51,'Particularly organization night serious. Behavior ever free property drug such computer opportunity.','2025-02-25 01:19:17',4),
(52,'Perhaps speech east car. Ten candidate can contain create story. Four series but.','2025-02-04 14:37:42',3),
(53,'Probably science base poor. Drive bill American heavy floor.','2025-04-08 07:11:45',3),
(54,'School leader article. Scene social camera mention wrong a bank surface. Worker safe her well.','2025-03-31 21:13:07',2),
(55,'Visit television prevent. Citizen senior throughout chance key know.','2025-02-09 09:50:47',9),
(56,'All close produce officer.','2025-01-21 04:54:31',1),
(57,'Project commercial effect southern year since management. Idea throw agent popular citizen letter six hospital.','2025-01-04 06:04:58',7),
(58,'Instead lay much their effort. Charge focus change way area wall food. Better section begin boy pick.','2025-03-01 20:03:26',6),
(59,'Politics its similar challenge economy. Many pull market thought every better.','2025-03-06 13:32:39',8),
(60,'Bag hour toward. Everybody your summer. School forget teacher not factor. Executive guess above letter.','2025-04-08 18:59:22',7),
(61,'There owner leave. Pressure market case someone maintain draw. Door maintain recently month surface. Age coach keep learn million any effort.','2025-03-19 22:19:58',10),
(62,'No father remain art. Know drive authority same box.','2025-01-31 01:38:02',3),
(63,'Teacher mouth part peace expert rule budget quality. Hour anything little lot have since.','2025-03-26 22:42:21',8),
(64,'Minute high open. Audience stock activity result international.','2025-01-27 22:09:51',3),
(65,'Cost while compare use. Soon range what part. Toward without consider sport old key together.','2025-03-13 11:41:31',1),
(66,'Into interview treatment feeling until. Material future peace.','2025-03-24 20:57:43',3),
(67,'Environmental message would people when. Property production nation.','2025-01-11 18:55:49',9),
(68,'Where form fall list laugh tell item. Memory other push.','2025-02-11 01:48:37',5),
(69,'None window thought option. Grow walk PM force something.','2025-04-01 23:10:39',9),
(70,'Interest occur officer campaign like. Threat prevent control want blue strategy.','2025-01-11 07:07:45',3),
(71,'Town realize shake voice. Question administration quality popular voice safe. Opportunity day only push.','2025-01-26 12:14:14',1),
(72,'Interest yard finally page expect all. Item just tax article run teacher several.','2025-04-03 12:33:21',9),
(73,'Month popular size evening democratic build network. Power become media attorney. Only team spring country.','2025-01-27 19:20:33',3),
(74,'Nothing guy religious special. System believe fall single personal.','2025-03-13 12:06:01',4),
(75,'Month those policy yes yet day. Peace get leader hope front system create. Learn cause nearly know compare son maintain.','2025-02-10 21:13:19',7),
(76,'Herself continue guess.','2025-01-02 07:12:22',6),
(77,'Marriage term here occur that agreement.','2025-03-20 12:57:56',5),
(78,'Meet particular only. Shake surface middle eat religious sign. Man consumer the often.','2025-01-04 13:27:37',6),
(79,'Write property this cell begin yourself avoid. Now people gun how fly yard environmental.','2025-02-09 06:57:27',9),
(80,'Offer research community stay animal rather. Various job believe model. Thing morning movie lead debate.','2025-01-28 00:38:38',9),
(81,'Safe sort fight great question simple table get. Watch hour there box doctor some.','2025-04-05 00:30:27',10),
(82,'Pm fly spend reality drive. Building kid again world wind.','2025-01-18 06:59:56',8),
(83,'Worker theory at current single kind. Rest range rather happy street happen project.','2025-04-19 12:36:05',3),
(84,'Art at look discussion want. Life system health role ground however which. Detail ask enter.','2025-01-20 09:32:21',1),
(85,'Minute public life thus only compare. Trouble without can beautiful six face against collection.','2025-02-25 01:59:25',7),
(86,'Production performance that range picture. Finish member risk method.','2025-02-11 12:08:54',10),
(87,'Expert much quickly tell few. Usually particularly prepare.','2025-03-24 14:50:40',2),
(88,'City age chance likely bank minute threat. Including book suddenly deep pull. Individual analysis pull. Democrat rest point seem without job.','2025-02-07 18:35:22',6),
(89,'Want month suddenly few turn science follow. Many claim find rise share investment. Scene place city base.','2025-01-15 07:58:56',8),
(90,'Why line Mrs husband yard break people. Question strategy house traditional. Floor hit very organization discuss pressure person.','2025-01-10 11:09:29',1),
(91,'Both name social air.','2025-02-11 16:12:48',1),
(92,'Military matter alone will glass. History serve eat bank position represent. Street we blood nor attorney.','2025-01-24 19:45:07',5),
(93,'Itself nature product station page. Wish through officer year people blood. Management water many quickly animal she.','2025-02-05 03:24:24',8),
(94,'Do special good several police. Trip both strong stand thought.','2025-02-05 07:19:08',8),
(95,'She blue charge test move rich city. Mission arm certainly than movement natural idea. Movement when performance relationship child.','2025-01-11 19:21:30',6),
(96,'Body and base between. Save argue source mother nation including. With campaign president network ground. Level someone call throw hot them lose.','2025-02-04 14:10:01',9),
(97,'Wear radio voice either purpose too Mr shoulder. Pm military force quite still career. Whole sort year director create.','2025-01-11 08:20:09',8),
(98,'Charge child almost food wear husband article itself. Scientist blood trouble. Idea ask allow increase.','2025-01-15 04:46:54',5),
(99,'Million sometimes stop program accept question. Cell tough simply arm.','2025-03-15 16:00:12',1),
(100,'Record source management today what mention. Last interest tend protect base relationship country.','2025-02-08 17:50:42',2),
(101,'neu','2025-04-21 08:47:50',11),
(102,'hsdhdsh','2025-04-22 15:44:51',11);
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scan_access_points`
--

DROP TABLE IF EXISTS `scan_access_points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `scan_access_points` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scan_id` int(11) NOT NULL,
  `access_point_id` int(11) NOT NULL,
  `first_seen` datetime NOT NULL,
  `last_seen` datetime NOT NULL,
  `channel` int(11) NOT NULL,
  `speed` int(11) NOT NULL,
  `privacy` varchar(64) DEFAULT NULL,
  `cipher` varchar(64) DEFAULT NULL,
  `authentication` varchar(64) DEFAULT NULL,
  `power` int(11) NOT NULL,
  `beacons` int(11) NOT NULL,
  `iv` int(11) NOT NULL,
  `lan_ip` varchar(45) DEFAULT NULL,
  `id_length` int(11) NOT NULL,
  `key` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_scan_access_points_access_point_id_access_points` (`access_point_id`),
  KEY `fk_scan_access_points_scan_id_scans` (`scan_id`),
  CONSTRAINT `fk_scan_access_points_access_point_id_access_points` FOREIGN KEY (`access_point_id`) REFERENCES `access_points` (`id`),
  CONSTRAINT `fk_scan_access_points_scan_id_scans` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scan_access_points`
--

LOCK TABLES `scan_access_points` WRITE;
/*!40000 ALTER TABLE `scan_access_points` DISABLE KEYS */;
/*!40000 ALTER TABLE `scan_access_points` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scan_stations`
--

DROP TABLE IF EXISTS `scan_stations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `scan_stations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scan_id` int(11) NOT NULL,
  `station_id` int(11) NOT NULL,
  `first_seen` datetime NOT NULL,
  `last_seen` datetime NOT NULL,
  `power` int(11) NOT NULL,
  `packets` int(11) NOT NULL,
  `bssid` varchar(17) DEFAULT NULL,
  `probed_essids` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_scan_stations_scan_id_scans` (`scan_id`),
  KEY `fk_scan_stations_station_id_stations` (`station_id`),
  CONSTRAINT `fk_scan_stations_scan_id_scans` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`id`),
  CONSTRAINT `fk_scan_stations_station_id_stations` FOREIGN KEY (`station_id`) REFERENCES `stations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scan_stations`
--

LOCK TABLES `scan_stations` WRITE;
/*!40000 ALTER TABLE `scan_stations` DISABLE KEYS */;
/*!40000 ALTER TABLE `scan_stations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scans`
--

DROP TABLE IF EXISTS `scans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `scans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `description` varchar(256) DEFAULT NULL,
  `filename` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scans`
--

LOCK TABLES `scans` WRITE;
/*!40000 ALTER TABLE `scans` DISABLE KEYS */;
INSERT INTO `scans` VALUES
(5,'2025-04-23 17:37:37','Imported from airodump CSV','airodump-test.csv');
/*!40000 ALTER TABLE `scans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stations`
--

DROP TABLE IF EXISTS `stations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `stations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mac` varchar(17) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_stations_mac` (`mac`)
) ENGINE=InnoDB AUTO_INCREMENT=311 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stations`
--

LOCK TABLES `stations` WRITE;
/*!40000 ALTER TABLE `stations` DISABLE KEYS */;
INSERT INTO `stations` VALUES
(3,'00:25:00:FF:94:73'),
(98,'00:87:01:B7:24:4B'),
(269,'02:1F:8D:64:51:77'),
(52,'02:25:B3:19:39:09'),
(246,'02:34:1A:98:C8:3B'),
(156,'02:83:C9:55:B8:E9'),
(151,'03:D9:9E:0B:5C:3D'),
(123,'05:23:9F:2A:6D:45'),
(265,'06:1D:BE:88:40:3D'),
(249,'06:81:5C:D3:C2:66'),
(87,'06:E1:9A:DE:8D:82'),
(176,'09:3C:25:7C:EF:2C'),
(217,'0A:3B:BF:14:1E:25'),
(242,'0A:72:21:BC:AE:12'),
(276,'0A:B7:E8:97:00:88'),
(297,'0A:B9:EB:69:64:89'),
(132,'0A:C9:DF:5B:6F:CC'),
(222,'0A:FA:6F:42:41:5A'),
(107,'0D:BE:82:EA:92:92'),
(294,'0E:34:B5:6B:97:A1'),
(131,'0E:77:A5:B7:3F:BA'),
(279,'0E:94:90:EA:E7:D8'),
(199,'0E:AD:72:6F:5C:90'),
(154,'10:22:64:A8:DB:0A'),
(51,'10:8E:E0:BB:53:44'),
(275,'12:40:6F:CA:06:7A'),
(66,'12:5E:E8:0A:12:F6'),
(24,'12:71:77:D4:FF:60'),
(59,'12:BD:27:82:CB:EB'),
(92,'12:C0:72:49:89:80'),
(184,'12:C4:1B:F1:77:D4'),
(130,'16:83:E3:39:D4:0C'),
(40,'16:EE:90:62:C0:99'),
(206,'1A:06:E5:5E:11:E0'),
(69,'1A:39:10:9D:78:EA'),
(271,'1E:41:FF:8D:92:17'),
(281,'1E:55:35:E0:43:6D'),
(152,'1E:B3:AC:67:15:31'),
(139,'1E:C4:59:31:FE:AB'),
(209,'1E:C5:77:36:7E:F2'),
(216,'1E:F3:D4:C0:33:EA'),
(101,'1F:BC:E8:7C:23:0B'),
(141,'22:2A:01:54:81:61'),
(293,'22:71:E4:DB:8B:77'),
(230,'22:A4:09:54:6E:BA'),
(194,'22:AF:29:C0:AE:82'),
(166,'22:C1:DF:0F:76:F4'),
(300,'24:41:8C:9E:22:0D'),
(290,'24:41:8C:9E:3F:59'),
(142,'26:15:30:7D:7A:09'),
(49,'26:19:27:B7:00:6F'),
(310,'26:48:D5:95:44:EC'),
(37,'26:5B:EC:AE:B9:CB'),
(189,'26:8B:84:34:30:81'),
(90,'28:08:46:AE:4F:38'),
(100,'28:66:E3:F3:27:61'),
(43,'2A:13:00:00:1E:D2'),
(127,'2A:2A:34:93:DA:0D'),
(133,'2A:5C:FC:94:A8:F0'),
(298,'2A:DF:69:4C:4B:14'),
(182,'2A:F6:28:02:E7:ED'),
(106,'2B:A5:2B:B7:8C:41'),
(117,'2C:2B:B4:FA:E9:1D'),
(190,'32:61:0C:E5:2E:78'),
(215,'32:6A:F1:FF:07:6B'),
(241,'32:7A:01:78:23:26'),
(2,'32:C3:D9:4B:38:18'),
(78,'32:F1:82:04:CB:91'),
(270,'32:F9:C8:0C:B4:6B'),
(105,'33:74:FE:EE:E6:94'),
(214,'36:1A:6C:FD:0C:2A'),
(53,'36:74:92:62:9A:1D'),
(205,'36:87:B3:9C:F4:97'),
(159,'37:B5:EF:DA:74:8B'),
(163,'38:0D:2D:69:9B:6D'),
(161,'39:4E:B7:E6:96:58'),
(234,'3A:37:F4:F2:19:5D'),
(136,'3A:4A:10:CF:BA:E2'),
(286,'3A:DA:D4:7F:2F:24'),
(15,'3C:37:12:2E:34:30'),
(112,'3C:82:9D:B8:86:FC'),
(60,'3C:F0:11:11:F6:BB'),
(210,'3E:3D:27:BB:15:C8'),
(250,'3E:4A:27:16:1F:25'),
(252,'3E:4A:27:58:5D:56'),
(254,'3E:4A:27:69:8B:7B'),
(256,'3E:4A:27:D8:BF:BD'),
(248,'3E:84:C7:9D:23:12'),
(193,'3F:6D:0D:8A:66:4C'),
(306,'40:AA:56:13:21:C3'),
(232,'41:40:35:99:AB:93'),
(192,'42:18:58:3E:71:11'),
(212,'42:AF:8A:F4:78:5C'),
(220,'42:C4:DB:35:3A:C0'),
(111,'43:62:FB:23:9F:18'),
(108,'44:49:CF:E8:E9:AE'),
(50,'46:BF:C8:D6:28:F4'),
(48,'46:BF:C8:F8:7A:1A'),
(183,'46:CE:3F:CC:F2:B9'),
(307,'48:6D:BB:6C:E1:EA'),
(245,'4A:6A:4C:A6:8A:85'),
(35,'4A:80:32:3D:85:93'),
(72,'4A:AE:6D:A0:E3:F8'),
(47,'4B:8A:A0:58:6B:09'),
(134,'4E:35:D6:1E:DE:C2'),
(233,'4E:77:4F:0F:42:4A'),
(94,'4E:CE:56:9C:F5:FA'),
(76,'52:D4:D5:6C:72:64'),
(284,'56:18:F3:29:39:AE'),
(228,'56:20:2F:D2:62:F1'),
(164,'56:33:7E:02:0C:81'),
(174,'56:46:F5:1D:E1:A2'),
(55,'56:51:B8:2A:9E:B2'),
(58,'5A:0C:C4:79:06:EB'),
(22,'5A:12:F9:E4:90:01'),
(128,'5A:2F:06:3C:EC:40'),
(129,'5A:D9:8A:4B:ED:34'),
(304,'5E:C3:98:53:1D:43'),
(103,'5E:EF:06:1E:E9:7D'),
(115,'62:16:CB:22:D3:D8'),
(79,'62:68:39:1C:13:EA'),
(211,'66:3D:93:9F:B2:A7'),
(96,'66:AD:DA:D6:30:17'),
(64,'68:63:59:C4:32:11'),
(126,'6A:22:F3:A4:78:C1'),
(196,'6A:6A:8B:5C:3E:8D'),
(27,'6A:73:0C:DD:3C:31'),
(138,'6A:7E:9B:86:06:AA'),
(25,'6E:05:53:4B:15:25'),
(179,'72:E0:15:17:58:20'),
(302,'74:40:BE:DC:6D:18'),
(12,'74:42:7F:59:E9:2E'),
(7,'74:42:7F:59:ED:B0'),
(14,'74:42:7F:59:ED:B1'),
(247,'76:02:22:8B:AE:43'),
(280,'76:11:79:79:65:C7'),
(56,'76:6C:40:FC:5E:A2'),
(207,'76:C8:C2:16:71:A4'),
(277,'76:CC:D6:56:8B:8D'),
(225,'79:71:62:F7:E2:2C'),
(80,'7A:3B:49:FD:C5:EE'),
(36,'7A:5C:8E:A8:28:AB'),
(201,'7A:5D:93:4C:50:FC'),
(120,'7A:91:4B:98:7B:8C'),
(258,'7A:AF:66:89:5C:83'),
(162,'7A:B3:B3:05:F9:30'),
(240,'7A:E1:C0:22:B6:56'),
(30,'7A:EB:80:74:C9:C2'),
(255,'7E:F1:63:23:8F:CD'),
(65,'7E:F6:A9:8D:6D:F7'),
(305,'82:8F:14:06:A8:00'),
(137,'82:90:FE:A6:3B:38'),
(104,'82:91:7A:95:C8:36'),
(26,'82:92:86:08:7A:A6'),
(167,'83:55:B6:8F:AA:47'),
(54,'86:53:D5:9E:93:31'),
(113,'87:BE:2F:AF:96:18'),
(18,'88:BF:E4:CA:FF:E0'),
(62,'89:E9:68:98:B6:CF'),
(308,'8A:70:7A:FE:6F:3F'),
(81,'8A:BA:4D:9A:CB:21'),
(63,'8A:BF:E4:8C:8B:8E'),
(282,'8A:DD:14:16:70:4F'),
(257,'8A:FD:48:E0:D0:7A'),
(260,'8E:04:D8:93:96:D7'),
(301,'8E:45:6F:67:95:6C'),
(88,'8E:B4:8D:47:89:BB'),
(119,'8E:FD:2F:6E:1F:B5'),
(235,'92:02:63:BE:3E:EB'),
(125,'93:84:5B:0C:94:8F'),
(158,'94:9A:E5:82:0C:7A'),
(46,'96:07:67:59:1F:69'),
(73,'96:3D:1E:25:D3:36'),
(29,'96:97:18:2D:E0:6C'),
(144,'96:D6:A7:4F:37:18'),
(180,'99:57:EC:EA:56:4E'),
(150,'9A:2C:FF:6C:2F:1E'),
(291,'9A:66:C2:90:71:F1'),
(268,'9C:F3:87:B7:92:EE'),
(57,'9E:07:CA:9A:DF:66'),
(226,'9E:6F:AD:66:1A:6D'),
(77,'9E:84:E5:38:57:93'),
(227,'9E:8B:46:76:5C:70'),
(287,'9E:E8:74:AE:FB:C6'),
(175,'9F:40:45:80:B0:ED'),
(171,'9F:52:86:92:3A:BE'),
(11,'A0:D8:07:60:BC:94'),
(4,'A0:D8:07:60:BC:96'),
(165,'A2:9C:0B:B0:40:D3'),
(202,'A2:AF:2D:87:4F:5B'),
(251,'A2:F3:B3:95:05:28'),
(244,'A6:86:09:B7:7B:AB'),
(237,'A6:B3:38:EE:4B:4F'),
(289,'A6:EF:FB:CF:6D:D1'),
(295,'A8:34:6A:AF:73:D4'),
(93,'A9:93:34:B7:2C:FD'),
(153,'AA:39:E5:56:EA:5B'),
(186,'AA:AC:8E:F4:DA:65'),
(266,'AA:C8:B0:6B:F2:DC'),
(67,'AE:8C:B7:45:B3:C9'),
(267,'AE:D6:28:13:69:61'),
(296,'B2:13:BE:87:9C:D6'),
(135,'B2:67:EA:31:5A:56'),
(170,'B2:D7:5F:44:49:8D'),
(261,'B2:F0:19:71:2D:15'),
(157,'B5:C7:28:5F:E6:CA'),
(168,'B6:59:EA:F8:A7:A4'),
(263,'BA:D7:29:D2:DB:0F'),
(71,'BA:E0:17:44:D1:85'),
(172,'BA:E2:F7:DD:4C:F6'),
(45,'BC:F7:3F:05:45:D6'),
(204,'BE:10:B3:DD:D5:AC'),
(85,'BE:A6:EF:A7:8D:EB'),
(122,'C0:AF:83:64:50:A1'),
(238,'C2:1B:65:F8:35:48'),
(239,'C2:53:3A:A0:4D:93'),
(44,'C2:7E:47:7D:65:45'),
(299,'C2:85:39:A4:40:83'),
(149,'C2:A5:17:F5:D2:58'),
(208,'C2:CC:E6:4D:54:22'),
(61,'C2:FF:00:12:1D:91'),
(140,'C6:3A:58:DF:CE:D9'),
(33,'C6:55:D7:5D:EE:B2'),
(32,'C6:6C:CF:D3:EF:0F'),
(70,'C6:9B:5B:8E:2E:F6'),
(169,'C8:30:A8:EA:64:5F'),
(95,'C9:C6:12:EF:B8:56'),
(75,'CA:4B:89:FD:B8:B4'),
(146,'CA:5E:50:EC:B7:20'),
(39,'CA:F3:37:A0:E1:47'),
(118,'CC:02:2E:91:7E:15'),
(6,'CE:50:E3:6C:11:F1'),
(191,'CE:6B:D4:F8:CE:70'),
(20,'CE:87:E9:AB:12:DC'),
(89,'CE:F8:81:6C:4D:F0'),
(143,'D2:34:01:99:7D:D8'),
(173,'D2:67:52:97:03:A2'),
(274,'D2:72:87:50:69:CA'),
(145,'D2:B8:3F:DE:0B:CA'),
(229,'D2:C5:10:9E:90:A7'),
(68,'D3:1A:0E:08:DC:EC'),
(218,'D3:38:BC:12:94:AF'),
(224,'D6:40:D9:AF:12:50'),
(31,'D6:4D:29:99:6E:D7'),
(309,'D6:A1:96:03:82:89'),
(42,'D6:C5:56:7C:A0:AE'),
(177,'D6:C8:08:38:97:19'),
(155,'D6:DE:16:C4:75:06'),
(124,'D8:5A:13:AC:3D:5E'),
(292,'D8:9C:67:75:2C:73'),
(278,'D8:FB:D6:C5:F7:2E'),
(188,'D9:A4:F6:33:8F:CC'),
(223,'DA:2E:87:11:DA:BA'),
(28,'DA:68:1A:5B:66:69'),
(86,'DA:A1:19:2D:96:60'),
(195,'DA:A1:19:41:1B:C6'),
(198,'DA:A1:19:7E:A8:2D'),
(264,'DA:A1:19:82:6F:2B'),
(41,'DA:A1:19:8A:9E:DC'),
(262,'DA:A1:19:D5:AF:68'),
(91,'DA:A1:19:DA:B3:8E'),
(84,'DA:FB:53:2C:5B:FC'),
(10,'DC:15:C8:4A:5A:DB'),
(1,'DC:39:6F:A1:93:07'),
(13,'DC:39:6F:C3:58:4D'),
(187,'DD:5E:8F:8F:0C:64'),
(83,'DE:3A:26:86:51:13'),
(82,'DE:85:E1:53:25:77'),
(283,'DE:8E:98:8D:0D:CF'),
(160,'DE:93:A1:D5:60:D3'),
(178,'DE:C7:47:D0:3C:63'),
(114,'DE:DD:74:AE:B4:F0'),
(9,'E0:28:6D:3B:83:14'),
(221,'E0:AA:96:4E:F3:60'),
(253,'E2:5B:75:C2:19:D4'),
(99,'E2:CD:5C:4F:8C:32'),
(185,'E5:2E:82:36:3B:18'),
(109,'E5:77:64:51:04:3A'),
(288,'E6:03:37:9F:47:86'),
(200,'E6:5F:D8:B9:C4:DF'),
(19,'E6:8A:3D:84:BC:CF'),
(74,'E6:B6:CC:81:6E:DE'),
(121,'E7:41:DD:B8:AE:32'),
(197,'E9:09:E9:F8:1A:8E'),
(21,'EA:49:FD:EB:9E:60'),
(38,'EA:6B:70:A0:04:65'),
(243,'EA:77:5D:CD:9B:E9'),
(219,'EB:30:00:D2:5D:2A'),
(231,'EE:35:56:CA:27:00'),
(23,'EE:46:B8:0D:25:96'),
(97,'EE:68:FB:66:69:3E'),
(116,'F2:15:B8:95:9F:69'),
(303,'F2:77:42:AB:A8:75'),
(181,'F2:84:F8:14:31:B2'),
(203,'F2:F5:AC:39:FE:0F'),
(236,'F4:30:8B:4B:D0:0A'),
(273,'F6:26:29:27:D9:A0'),
(213,'F6:30:ED:99:42:EB'),
(17,'F6:3F:21:CB:B0:F9'),
(5,'F8:0D:60:09:0E:A8'),
(110,'F8:81:8B:5F:4F:95'),
(102,'F9:1C:E1:AC:55:25'),
(147,'FA:50:8E:17:1B:7B'),
(259,'FA:8E:E1:46:90:D1'),
(8,'FA:8F:CA:B1:B1:79'),
(34,'FA:B8:4F:CF:67:F0'),
(285,'FA:DB:DE:E3:CD:EF'),
(148,'FE:95:23:2F:87:97'),
(272,'FE:BC:B4:A3:80:28'),
(16,'Station MAC');
/*!40000 ALTER TABLE `stations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tokens`
--

DROP TABLE IF EXISTS `tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tokens` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `access_token` varchar(64) NOT NULL,
  `access_expiration` datetime NOT NULL,
  `refresh_token` varchar(64) NOT NULL,
  `refresh_expiration` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_tokens_access_token` (`access_token`),
  KEY `ix_tokens_refresh_token` (`refresh_token`),
  KEY `ix_tokens_user_id` (`user_id`),
  CONSTRAINT `fk_tokens_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tokens`
--

LOCK TABLES `tokens` WRITE;
/*!40000 ALTER TABLE `tokens` DISABLE KEYS */;
INSERT INTO `tokens` VALUES
(1,'gqv9_zH8xt4e-ErWwu7gpM1lxztSl879HU8iMv6r1cA','2025-04-21 09:02:47','-puj2qh6YxlTmaZraDYEWt6WmmGuFuayJaO5i0ca_lc','2025-04-28 08:47:47',11),
(4,'W-oc0P7hWO8xhq17DVY-uUkLl8TvY8Vo54ktwlYynA8','2025-04-21 11:52:56','1dvD0fu916JQ0G8TU8MfDUdLBIF9Kmt2kqof154mhUI','2025-04-28 11:37:56',11),
(5,'_0za-CY_CeW8WTW8uEzXgM73jxcCibNSAyPF2Kh_0FE','2025-04-21 11:52:56','aKZHOq9oFJZzH-HwlP14j7BiXcSI5d4WBJ1rTzNpfkk','2025-04-28 11:37:56',11),
(6,'k4J0sjn82JO_xl06710K1t-VJiY1Z2hIpGgSRLQlSCg','2025-04-22 07:43:01','XNMRapefTAf1fCGELEVGGa8psuS_p1Qyc1pUe-DSQaA','2025-04-29 07:28:01',11),
(7,'2HlG-sMNiTZWB2k2VXKITcsvSBwZZr5BexlfU-izPQY','2025-04-22 07:48:31','VstHj0OhxnwJlwtyFDVH2CAxIrN0AMs3TpO_h1eFzt0','2025-04-29 07:33:31',11),
(9,'bFFFszBd691giI9cAgUF5K-AiIxuxOrGW02wAoZ1vsI','2025-04-22 18:43:22','CzuNqo0Vpdea2qWvNsVQOpG21zHFw_j7ey5z9KJsxuk','2025-04-29 18:28:22',11),
(11,'mVU8XbQih3X1xetfMm_-QfIrRlgsdoF4BcMRVHjVuKU','2025-04-22 19:17:23','rGgj9kQ_89urqUw_n88XksgvWQ4gYzMJD5u5OtXsaUU','2025-04-29 19:02:23',11),
(13,'ZVtXHAReNtvnrDoVd6fPT39WjNOljXDMZKikjjc8aFw','2025-04-22 19:32:36','Llbme6d5cUkCrBoUWzOKcWnNFv2XJcMLZUw8gfAn3VY','2025-04-29 19:17:36',11),
(15,'_GRXUdYJmHmw_dBDCnWbcRN0xzYB6IOJAh803qZZtKc','2025-04-22 19:52:17','jOtS6uRNPkWsvwXczyac-2VqN2HGdAjE3rOA-5ppAqc','2025-04-29 19:37:17',11),
(17,'verFZFQlsyzg87olXp7CfBsTDCQIG8CgOZcWqt646cQ','2025-04-22 20:07:39','p3bxf8ozFsHDmAPYQLmJEOldSUx2aI_FFEu5C3rVshs','2025-04-29 19:52:39',11),
(18,'chyijKQRZHlWyeY9sS6KXOm0-JGKaQLk6n0HX9_G2Ns','2025-04-22 20:07:39','F0TMAWubLM1ihSGWNcM12dBe3LJpQYfjLLtG9Bb-4xc','2025-04-29 19:52:39',11),
(19,'I0l4CzULppsoq2HbBPUH67NwtLmVGuzmpPPo47j8GDw','2025-04-23 07:48:01','ZLfW7nybrWmDc5vDkuusAiT1XJ-BXwVUfOYCpkHzxXg','2025-04-23 07:48:01',11),
(20,'2104hv5MWIxkmQWvAdjpTzTMmet6omkqq7y0PNamcOI','2025-04-23 08:02:56','2cK6abE9CojPq3cP5tvxv29xPiybw6H_Y729a0DhKaw','2025-04-30 07:47:56',11),
(21,'FL4ZSFLCOXhhaFhG_s9bKCdndAZsO5Qvxbb7F4K3Xj8','2025-04-23 08:04:19','SvUC3bfJTT27_BZy95J9jbc0zgL6K8ZaHHYGAXAcXes','2025-04-23 08:04:19',11),
(22,'o0nGl4aHMrCTqvdJxcXQhEDYpfuzajFhVw4aYWekgic','2025-04-23 08:19:14','z7qGT7cmcMrU2XSpjxFDSudDis6dJhys_W9z0uP08sk','2025-04-30 08:04:14',11),
(23,'mIxai1zYuvz_3QmNP6zjV7uwDF375QsGUUgaFvnUScA','2025-04-23 08:23:09','BQAwBxPCmEoqplXwxBfUfXQvfvmdInrIA0YceHj18tM','2025-04-23 08:23:09',11),
(24,'9sT8j5dGwFE2jiT7X3-W98242L57nnT_-gjWbwn6bSo','2025-04-23 08:45:06','zUdhQLmbPqV8LOB7SGyPSAMC2-4xA7B-xL-cnA1uRsg','2025-04-23 08:45:06',11),
(25,'HW5jEGZ3Ve2ZSdh-cJkdHgJv_Zsm5BXflxoxkftStWM','2025-04-23 08:38:04','3w0WoRpYSluT-Vrwci-8aktDm6TeuPHDvWDhlSD9XCo','2025-04-30 08:23:04',11),
(26,'Z0EErdjFa2IbxbZwbj209uLLoMAHGnpGs-YEDp6sTBw','2025-04-23 09:00:01','d5a-5KySyDxxiunPzX8VlbXe8Sp9OHfuFzS45rW8BWY','2025-04-30 08:45:01',11),
(27,'uqdmreiy_oOhvW6vLk-AoI21c-4JUiEy7VsvTNe_mnE','2025-04-23 09:00:02','FVrgW9DmCC-SIo3n_UgbUKlXzyy8OiTjD9KzL0tHJ5c','2025-04-30 08:45:02',11),
(28,'ywg2mAvJGFeQVSyyFSWNYd-WGeDTKePVWzAo1L2KWGg','2025-04-23 17:21:40','gbSdowiVSh7UC3umLIfjiKx7AyzDpdQTB0lqaEOGGps','2025-04-23 17:21:40',11),
(29,'IRb9_saWAijT_zQgyl0IKHr2d9woThTgCHTbYuBoaSI','2025-04-23 17:36:35','6ebvaxOtCfVl438xT9vy_lH5BAW8_qGBuVJBxji_jCc','2025-04-30 17:21:35',11),
(30,'IA4CVp-dzdk2tokc5-NL4q1wta_IhfZbZai2F3lPZfA','2025-04-23 18:49:38','EIBy3c5ZYmSF0WdBn-G8t4fXSNZRpcX8Ar6jILzjO_o','2025-04-23 18:49:38',11),
(31,'-X2Nkd8ttsujsEb3xAcmYHOhRTXCw19KWdZQZqK7qGM','2025-04-23 19:04:33','s15Ya0jHqidrobm_w439JHpa7c2BMo6N30rFBRBdfQo','2025-04-30 18:49:33',11),
(32,'cIdwIXRmN6JjEIFWDWieQSAh4b9sjkAqHc8lNgmGCAQ','2025-04-23 19:06:45','t_lPcvkibTSy5QocufWELGRNFgI0kkhPX-rX4MMaHq8','2025-04-23 19:06:45',11),
(33,'EhnM-fvFpCXPyXfH9WYjB4AzQpVKSHBByXlhPudFQCw','2025-04-23 19:21:40','jgoepCbi1me70PBHJWn4n5PIKwUGcS19xwsr4zShhNU','2025-04-30 19:06:40',11),
(34,'cLzNDus1TLYlsRhMpVdVqOjtUR-x8gTE4CQgR5uiwrE','2025-04-23 19:23:30','Vq3rIpKnprJl43LAD-b0wIiMtdHxXlEq-G-0dbbwSUg','2025-04-23 19:23:30',11),
(35,'mOt6bzgL7wULR5SQlqcQasuqtcA2JdQXW5HTLsx5E5I','2025-04-23 19:38:25','BhXU56rkruNmSNQrd50M-Ncj-QG2naut6rRNPxkbGIc','2025-04-30 19:23:25',11),
(36,'_Xq6_JVZAF8KCVKO95zr6tdMk3g7K_j-4S-wykuAN3Q','2025-04-23 19:38:25','3Y_QJK4dINGPZk9lkTnsaXI9dtzpzlGBwMO_C9XVUv8','2025-04-30 19:23:25',11),
(37,'1926MhfKnvPwfLU3NvHrtWAKax9NwrFMRghhJJ1tgSA','2025-04-24 05:58:32','n4GTiVEXwdeCnNE7iWlk3WUhMedrwY-xp31Z21v9hOI','2025-05-01 05:43:32',11);
/*!40000 ALTER TABLE `tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(256) DEFAULT NULL,
  `about_me` varchar(140) DEFAULT NULL,
  `first_seen` datetime NOT NULL,
  `last_seen` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(1,'johnrobles','tiffany96@example.net',NULL,'Off enjoy network.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(2,'berrymichael','ecooper@example.org',NULL,'What like say major gas career job.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(3,'kevinweiss','npadilla@example.org',NULL,'Black stage west decade next special child.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(4,'hurleynathan','davidsilva@example.net',NULL,'Pick skill agreement network.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(5,'donald70','ocampbell@example.com',NULL,'Happy board shoulder professional not cut.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(6,'angelaesparza','beckersandy@example.net',NULL,'Size compare expert similar never system.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(7,'angela81','paul90@example.net',NULL,'Hand drug policy value start green.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(8,'fmoran','perezevan@example.org',NULL,'Establish us interest order.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(9,'gjoyce','thomas67@example.com',NULL,'Night today western rise more.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(10,'scott02','curtisward@example.com',NULL,'Participant what hear.','2025-04-21 08:46:26','2025-04-21 08:46:26'),
(11,'soenke','mantu@gmx.de','scrypt:32768:8:1$B4UnGUQMUWxz5moQ$4fb94a61ca607829de531620e7b6aa65448c60c7fb2a1d440eeb957348e06d20d1cb87daea91724f3bd98dfe706bcb3d632106c75ec0d001c4bd6b928d682920',NULL,'2025-04-21 08:47:39','2025-04-24 05:43:33');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-24  7:47:32
