/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.5.2-MariaDB, for osx10.19 (arm64)
--
-- Host: localhost    Database: forum_system
-- ------------------------------------------------------
-- Server version	11.5.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES
(1,'Bachelor Tea','All the juicy details about roses, romance, and rejections. Who is here for the right reasons and who is just chasing clout?',0,0,'2024-11-07 16:20:26',1),
(2,'Big Brother S1','What happens in the house, does NOT stay in the house! From secret alliances to midnight drama, get all the tea here.',0,1,'2024-11-07 16:20:26',1),
(3,'Love Island Gossip','Steamy couples, dramatic recouplings, and villa drama. The hottest gossip from paradise!',1,0,'2024-11-07 16:20:26',1),
(4,'Survivor Spills','Alliances, betrayals, and hidden immunity idols. Who is really playing who?',0,0,'2024-11-07 16:20:26',1),
(5,'Masked Singer Reveals','Guess who is behind the mask! Exclusive hints and backstage drama from our anonymous sources.',0,0,'2024-11-07 16:20:26',1),
(6,'Dancing With Stars Drama','Behind the scenes drama, romantic rumors, and judge controversies. Every step holds a story!',1,0,'2024-11-07 16:20:26',1),
(7,'Hells Kitchen Heat','What really happens in Chef Ramsays kitchen? The burns are not just from the stove!',0,0,'2024-11-07 16:20:26',1),
(8,'Kardashian Kronicals','Keeping up with all the drama, scandals, and family feuds. Nothing stays hidden in this family!',0,0,'2024-11-07 16:20:26',1);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `category_accesses`
--

LOCK TABLES `category_accesses` WRITE;
/*!40000 ALTER TABLE `category_accesses` DISABLE KEYS */;
INSERT INTO `category_accesses` VALUES
(1,6,1),
(2,3,1),
(4,6,0),
(5,3,1),
(7,3,0),
(8,6,1),
(9,3,0),
(10,6,0);
/*!40000 ALTER TABLE `category_accesses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `conversations`
--

LOCK TABLES `conversations` WRITE;
/*!40000 ALTER TABLE `conversations` DISABLE KEYS */;
INSERT INTO `conversations` VALUES
(1,1,3),
(2,1,5),
(3,1,7),
(4,1,9),
(5,1,11);
/*!40000 ALTER TABLE `conversations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES
(28,'Hey admin! I heard theres some major tea in the Love Island category. Can I get access? Promise to keep the gossip flowing!','2023-09-15 14:23:11',3,1,1),
(29,'Hi there! Sure, I can help with that. Do you want read-only access or would you like to contribute tea as well?','2023-09-15 14:30:22',1,3,1),
(30,'Id love to contribute! I have some insider info from my cousin who works on the show!','2023-09-15 14:32:45',3,1,1),
(31,'Perfect! Ive given you full access to the Love Island category. Spill that tea!','2023-09-15 14:35:12',1,3,1),
(32,'Thank you so much! The tea is already brewing!','2023-09-15 14:36:01',3,1,1),
(33,'Hi admin! Could you help me change my profile picture? The current one isnt giving witch vibes','2023-10-01 09:15:33',5,1,2),
(34,'Of course! Would you like the girl.png or boy.png avatar?','2023-10-01 09:20:45',1,5,2),
(35,'girl.png please! Gotta keep my mystical aesthetic','2023-10-01 09:22:17',5,1,2),
(36,'All done! Your new profile picture is serving pure witch realness!','2023-10-01 09:25:03',1,5,2),
(37,'Perfect! Now I can serve my tea in style!','2023-10-01 09:26:11',5,1,2),
(38,'Hey! Why was my Big Brother topic locked? The tea was just getting good!','2023-10-15 16:45:22',7,1,3),
(39,'Hi! The topic was getting a bit too spicy with personal information. We need to keep some things under wraps!','2023-10-15 16:50:33',1,7,3),
(40,'Can we at least keep the existing tea visible? Its already out there!','2023-10-15 16:52:47',7,1,3),
(41,'Yes, existing comments will stay. Just no new tea in that topic! Start a fresh one if you have more gossip!','2023-10-15 16:55:15',1,7,3),
(42,'Thanks for explaining! New topic coming soon with fresh tea!','2023-10-15 16:56:02',7,1,3),
(43,'Admin! I need access to Dancing With Stars category ASAP! Got major choreo drama to share!','2023-11-01 20:10:15',9,1,4),
(44,'Hello detective! Read-only or full tea-spilling privileges?','2023-11-01 20:15:33',1,9,4),
(45,'Full access please! This tea is too hot to just read!','2023-11-01 20:17:42',9,1,4),
(46,'Done! Your detective skills are now unleashed on the dance floor!','2023-11-01 20:20:05',1,9,4),
(47,'Time to expose those dance floor secrets!','2023-11-01 20:21:33',9,1,4),
(48,'Why were my comments deleted? I was just sharing the truth!','2023-11-15 13:30:27',11,1,5),
(49,'Hi! Remember our rules - we keep it juicy but not personal! Some of your tea was a bit too identifying','2023-11-15 13:35:44',1,11,5),
(50,'But everyone wants to know the real story!','2023-11-15 13:37:12',11,1,5),
(51,'I get it, but we need to protect our sources! Keep the tea flowing but keep it classy! Next time will be a timeout!','2023-11-15 13:40:33',1,11,5),
(52,'Fine... Ill water down my tea next time','2023-11-15 13:41:55',11,1,5);
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `replies`
--

LOCK TABLES `replies` WRITE;
/*!40000 ALTER TABLE `replies` DISABLE KEYS */;
INSERT INTO `replies` VALUES
(1,'I was working as a PA that night! The champagne thing is just the tip of the iceberg. Two of the contestants almost got into a physical fight over someone who was already eliminated!',1,'2020-06-16 02:15:33',1,5),
(2,'My cousin works in production and showed me some footage. The eliminated contestant was actually hiding in the bushes trying to sneak back into the mansion that night!',0,'2020-06-17 13:20:45',1,8),
(3,'The ex already recorded an interview spilling everything! They have screenshots of texts from just days before filming started. This tea is scalding hot!',1,'2021-03-01 09:45:22',2,3),
(4,'I went to college with the ex and this story checks out. There are pictures of them ring shopping just 3 months ago. The producers definitely knew and cast them anyway for drama!',0,'2021-03-02 16:30:11',2,7),
(5,'One of the houseguests in the alliance slipped up yesterday during the live feeds. They accidentally used their secret signal during dinner and everyone noticed! Production cut the feeds immediately.',1,'2022-07-20 01:25:17',3,4),
(6,'My friend is on the camera crew and said theres way more footage they havent shown yet. The alliance has a whole secret code using the kitchen appliances to communicate!',0,'2022-07-21 19:40:55',3,9),
(7,'The messages were actually meant for another contestant\"s family! They were trying to get information about strategy from the outside. Security had to change all their protocols!',1,'2023-01-06 22:15:40',4,2),
(8,'I decoded some of the messages from the live feeds. They were using song lyrics to pass coded information. So clever but so against the rules!',0,'2023-01-07 11:35:28',4,6),
(9,'I was delivering food to Casa Amor that night! The new bombshell and islander were in the kitchen at 3AM \"making snacks\" but there was definitely more than cooking going on!',0,'2020-08-13 04:20:15',5,11),
(10,'Just got word from my bestie who works in editing - theres a whole compilation of their secret meetings that will air next week. Their partner in the main villa is going to be devastated!',1,'2020-08-14 15:55:33',5,7),
(11,'I used to bartend at the club where they had their big fight! The tea is that they were both dating this person AT THE SAME TIME without knowing. The producers struck gold with this casting!',0,'2021-07-23 21:10:42',6,10),
(12,'Found their old Instagram posts - they were literally at the same party last New Years Eve! There\"s no way they didnt know each other. This whole \"first meeting\" scene was totally fake!',1,'2021-07-24 13:25:18',6,4),
(13,'The sleeping contestant just posted cryptic tweets about \"karma coming soon\" - they definitely know about the idol now! Tribal council is going to be insane!',0,'2022-12-01 18:30:27',7,5),
(14,'My sister works in post-production and says the footage of the idol find is wild. They had to use five different camera angles to capture how close they were to getting caught!',1,'2022-12-02 09:15:44',7,3),
(15,'The rescued contestant finally spoke out! They said the show edited out two other major medical incidents that happened the same day. The conditions were way worse than they showed!',0,'2023-03-18 12:40:33',8,8),
(16,'One of the crew members who helped posted TikToks about it! They got deleted super fast but I screen-recorded everything. The real story is way more intense than what aired!',1,'2023-03-19 16:50:21',8,2),
(17,'Just compared the Unicorn\"s voice to recent award show speeches - its definitely that singer who just went into acting! Their schedule mysteriously cleared for all filming dates!',0,'2020-12-26 20:15:38',9,6),
(18,'My friend does costume fittings for the show and confirmed the celeb had their own security team and made everyone sign extra NDAs. This is definitely an A-lister!',1,'2020-12-27 11:45:59',9,9),
(19,'I have a friend in the audience that day! They said security collected every single phone and smartwatch before letting people in after the incident. The panic was real!',1,'2021-09-04 14:20:17',10,5),
(20,'Word is that three different costume designers quit after this happened! The celeb threatened to sue if any photos leaked. Production is still in damage control mode!',0,'2021-09-05 19:35:42',10,11),
(21,'Overheard them arguing in the parking lot after rehearsal! The celeb keeps showing up late and the dancer is furious about wasting practice time. They had to be separated by security!',1,'2022-04-02 10:25:18',11,8),
(22,'The dancer\"s spouse just unfollowed the celeb on Instagram! This feud is spreading beyond the dance floor. Even other contestants are picking sides!',0,'2022-04-03 15:40:33',11,2),
(23,'I work in sound and heard the whole argument during the break! One judge accused another of taking bribes to give better scores. The producers are trying to keep this quiet!',1,'2023-05-30 09:15:27',12,7),
(24,'Check the scoring patterns - one couple consistently gets extra points despite obvious mistakes. The other judges are finally standing up against this favoritism!',0,'2023-05-31 20:30:44',12,10),
(25,'The saboteur got caught on the night vision cameras! They\"ve been tampering with more than just salt - multiple dishes were deliberately overcooked or seasoned wrong!',1,'2020-11-01 23:45:18',13,4),
(26,'I heard from craft services that Chef Ramsay already knows who it is! He\"s waiting for the perfect moment to expose them during service. The drama is going to be epic!',0,'2020-11-02 16:20:33',13,9),
(27,'The contestant who walked out finally spoke to my friend at TMZ! The allergy incident wasnt an accident - someone deliberately contaminated their food!',1,'2021-12-13 14:55:22',14,6),
(28,'There\"s unaired footage of Gordon defending the contestant to production! He was furious about the safety protocols being ignored. This could turn into a huge lawsuit!',0,'2021-12-14 11:30:47',14,3),
(29,'Just saw the trademark applications! One sister is literally copying the others entire product line but with a slightly different name. Their mom is trying to mediate but its getting ugly!',1,'2022-02-15 17:25:38',15,7),
(30,'My friend works at their headquarters and said they had a screaming match in the conference room! Security had to be called because samples were being thrown across the room!',0,'2022-02-16 13:40:19',15,5),
(31,'I was doing catering at the party! One sister accused the other of stealing her suppliers. The footage exists because three different people were livestreaming when it happened!',0,'2023-11-02 21:15:33',16,4),
(32,'Their PR teams are in crisis mode trying to contain this! I heard the footage shows one sister throwing a drink at the others new product displays. Kris is threatening to sue anyone who leaks it!',1,'2023-11-03 12:45:27',16,8);
/*!40000 ALTER TABLE `replies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `topics`
--

LOCK TABLES `topics` WRITE;
/*!40000 ALTER TABLE `topics` DISABLE KEYS */;
INSERT INTO `topics` VALUES
(1,'Midnight Pool Party Drama','The producers didnt show us everything from that wild pool party! Three contestants were caught sneaking champagne after hours. Sources say there was a secret midnight rendezvous that production had to break up. The camera crew is sitting on MAJOR tea!',0,'2020-06-15 23:45:12',1,4,1),
(2,'Contestant Past Revealed','Looks like our frontrunner wasnt so honest about their dating history! Multiple sources confirmed they were engaged just months before filming. Their ex is ready to spill all the details. The bachelor/ette is apparently devastated after finding out!',0,'2021-02-28 14:30:45',1,7,3),
(3,'Kitchen Alliance Exposed','Late night footage reveals a secret alliance formed in the kitchen during midnight snacks. Five houseguests have been plotting while everyone sleeps! They even created a secret hand signal to communicate during nominations. The other houseguests are completely clueless!',1,'2022-07-19 02:15:33',2,5,5),
(4,'Diary Room Confessions','A production insider spilled that one contestant has been trying to send secret messages during diary room sessions. They\"ve been speaking in code to communicate with the outside world. Big Brother had to issue multiple warnings!',0,'2023-01-05 19:20:18',2,9,8),
(5,'Casa Amor Couple Scandal','One of the strongest couples might not survive Casa Amor! Sources say one islander got very cozy under the covers with a new bombshell. Multiple contestants witnessed some suspicious late-night movements. The main villa is about to explode with this revelation!',0,'2020-08-12 03:45:22',3,2,10),
(6,'Pre-Show Relationship Drama','Two islanders knew each other before entering the villa! They apparently dated the same person back home and have major beef. Production is sitting on this drama bomb waiting for the perfect moment to expose everything!',0,'2021-07-22 16:55:39',3,5,12),
(7,'Hidden Immunity Secret','A player found the immunity idol but theres a twist! They actually discovered it while another contestant was sleeping right next to it. The footage of them sneaking it out under everyones noses is incredible. This will change everything when it comes out at tribal!',1,'2022-11-30 21:10:45',4,8,14),
(8,'Medical Emergency Truth','The real story behind that medical evacuation is way more dramatic than what was shown. It actually involved three other contestants who helped but got edited out. The crew had to break multiple production protocols during the rescue!',0,'2023-03-17 08:25:11',4,3,15),
(9,'Celebrity Identity Leak','The Unicorn costume is hiding a MAJOR A-list celebrity! Multiple crew members confirmed its someone who recently won both an Oscar and Grammy. The judges are going to be shocked when this mask comes off!',0,'2020-12-25 22:30:15',5,10,17),
(10,'Costume Malfunction Drama','During rehearsals, one of the masks partially fell off exposing the celebrity! The entire crew had to sign additional NDAs. The wardrobe team spent an entire night rebuilding the costume before the live show!',0,'2021-09-03 11:40:33',5,6,19),
(11,'Partnership Tension Exposed','One of the professional dancers is demanding a new celebrity partner! Multiple sources confirmed heated arguments during rehearsals. The tension is so bad that they barely speak outside of required dance practice. Production is considering the switch!',0,'2022-04-01 17:15:28',6,4,22),
(12,'Judge Score Controversy','Inside sources reveal major disagreements between judges over scoring! One judge threatened to quit after a heated argument about favoritism. The producers had to intervene during a commercial break to calm things down!',0,'2023-05-29 13:50:42',6,7,24),
(13,'Blue Team Sabotage','A contestant was caught deliberately sabotaging their teams dishes! Late night footage shows them adding extra salt when no one was watching. Chef Ramsay suspects something but doesnt have proof yet. The team is falling apart with paranoia!',0,'2020-10-31 20:20:20',7,2,26),
(14,'Mystery Walk Out','The real reason for that dramatic walk out wasnt shown on TV! It involved a secret food allergy violation and multiple safety protocols being broken. Gordon was actually defending the contestant in the unaired footage!',0,'2021-12-12 12:12:12',7,11,27),
(15,'Secret Business Deal','One of the sisters is secretly planning to launch a competing business to another family members brand! Multiple employees confirmed seeing confidential documents. This could start the biggest family feud we\"ve ever seen!',0,'2022-02-14 04:44:44',8,5,29),
(16,'Holiday Party Showdown','The annual holiday party ended in tears and drama! Two sisters had a massive fight over their competing brands. Sources say phones were recording everything and the footage might leak. Kris is trying to contain the situation!',0,'2023-11-01 15:35:25',8,8,31);
/*!40000 ALTER TABLE `topics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(1,'admin','Admin','Admin','admin@gmail.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',1,'2024-11-07 16:20:26','/static/images/girl.png'),
(2,'rumyana','Rumyana','Tale','rumyana@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/girl.png'),
(3,'tea_spiller','Tea','Spiller','tea_spiller@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/girl.png'),
(4,'gossip_queen','Gossip','Queen','gossip_queen@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/girl.png'),
(5,'secret_keeper','Secret','Keeper','secret_keeper@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/boy.png'),
(6,'drama_llama','Drama','Llama','drama_llama@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/girl.png'),
(7,'whisper_witch','Whisper','Witch','whisper_witch@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/girl.png'),
(8,'tell_tale_tiger','Tell','Tiger','tell_tale_tiger@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/boy.png'),
(9,'rumor_has_it','Rumor','Hasit','rumor_has_it@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/girl.png'),
(10,'chatter_box','Chatter','Box','chatter_box@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/boy.png'),
(11,'scandal_sleuth','Scandal','Sleuth','scandal_sleuth@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/girl.png'),
(12,'tattle_tale','Tattle','Tale','tattle_tale@email.com','$2b$12$ianKte2e7TmDP7sKH/.Q/uisT9QTrCLEza4fyAG8vAng6T9yY.rd2',0,'2024-11-07 16:20:26','/static/images/boy.png');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `votes`
--

LOCK TABLES `votes` WRITE;
/*!40000 ALTER TABLE `votes` DISABLE KEYS */;
INSERT INTO `votes` VALUES
(1,1,1,3),
(2,1,1,4),
(3,1,1,7),
(4,1,1,8),
(5,1,1,9),
(6,0,1,2),
(7,1,2,5),
(8,1,2,8),
(9,0,2,3),
(10,0,2,6),
(11,1,3,2),
(12,1,3,4),
(13,1,3,7),
(14,1,3,9),
(15,1,3,11),
(16,0,4,1),
(17,0,4,5),
(18,0,4,8),
(19,1,5,2),
(20,1,5,4),
(21,1,5,6),
(22,1,5,9),
(23,1,5,10),
(24,1,5,12),
(25,1,6,3),
(26,1,6,7),
(27,1,6,8),
(28,0,6,5),
(29,1,7,1),
(30,1,7,4),
(31,1,7,6),
(32,1,7,9),
(33,0,8,2),
(34,0,8,5),
(35,0,8,7),
(36,1,9,2),
(37,1,9,4),
(38,0,9,6),
(39,0,9,8),
(40,0,9,10),
(41,1,10,1),
(42,1,10,3),
(43,1,10,5),
(44,1,10,7),
(45,1,10,9),
(46,1,11,2),
(47,1,11,4),
(48,1,11,8),
(49,0,11,6),
(50,1,12,3),
(51,1,12,5),
(52,1,12,7),
(53,0,12,9),
(54,1,13,1),
(55,1,13,3),
(56,1,13,5),
(57,1,13,7),
(58,1,13,9),
(59,1,13,11),
(60,1,14,2),
(61,1,14,4),
(62,1,14,6),
(63,1,14,8),
(64,1,14,10),
(65,1,15,1),
(66,1,15,3),
(67,1,15,5),
(68,0,15,7),
(69,1,16,2),
(70,1,16,4),
(71,1,16,6),
(72,1,16,8),
(73,1,17,3),
(74,1,17,5),
(75,1,17,7),
(76,1,17,9),
(77,0,17,11),
(78,1,18,2),
(79,1,18,4),
(80,1,18,6),
(81,0,18,8),
(82,1,19,1),
(83,1,19,5),
(84,1,19,9),
(85,0,19,7),
(86,1,20,3),
(87,1,20,6),
(88,1,20,8),
(89,0,20,4),
(90,1,21,2),
(91,1,21,5),
(92,1,21,8),
(93,1,21,10),
(94,1,21,12),
(95,0,22,3),
(96,0,22,6),
(97,0,22,9),
(98,1,23,1),
(99,1,23,4),
(100,1,23,7),
(101,1,23,10),
(102,1,24,2),
(103,1,24,5),
(104,1,24,8),
(105,1,24,11),
(106,1,25,3),
(107,1,25,6),
(108,1,25,9),
(109,1,25,11),
(110,1,26,2),
(111,1,26,5),
(112,1,26,7),
(113,1,26,10),
(114,1,27,1),
(115,1,27,4),
(116,1,27,8),
(117,0,27,6),
(118,1,28,3),
(119,1,28,7),
(120,1,28,9),
(121,0,28,5),
(122,1,29,2),
(123,1,29,4),
(124,1,29,6),
(125,1,29,8),
(126,1,29,10),
(127,1,29,12),
(128,1,30,1),
(129,1,30,3),
(130,1,30,5),
(131,1,30,7),
(132,1,30,9),
(133,1,30,11),
(134,1,31,2),
(135,1,31,4),
(136,1,31,6),
(137,1,31,8),
(138,1,31,10),
(139,1,32,1),
(140,1,32,3),
(141,1,32,5),
(142,1,32,7),
(143,1,32,9);
/*!40000 ALTER TABLE `votes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2024-11-07 16:59:47
