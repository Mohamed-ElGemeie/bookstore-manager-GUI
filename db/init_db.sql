CREATE DATABASE  IF NOT EXISTS `db_bookstore` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `db_bookstore`;
-- MySQL dump 10.13  Distrib 8.0.29, for Win64 (x86_64)
--
-- Host: localhost    Database: db_bookstore
-- ------------------------------------------------------
-- Server version	8.0.29

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `instore`
--

DROP TABLE IF EXISTS `instore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `instore` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tran_id` int DEFAULT NULL,
  `table_num` int NOT NULL,
  `end_time` datetime NOT NULL,
  `wifi` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tran_id` (`tran_id`),
  CONSTRAINT `instore_ibfk_1` FOREIGN KEY (`tran_id`) REFERENCES `transactions` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instore`
--

LOCK TABLES `instore` WRITE;
/*!40000 ALTER TABLE `instore` DISABLE KEYS */;
/*!40000 ALTER TABLE `instore` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `price` int NOT NULL,
  `price_ta` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item`
--

LOCK TABLES `item` WRITE;
/*!40000 ALTER TABLE `item` DISABLE KEYS */;
INSERT INTO `item` VALUES (1,'bondok/hazelnut coffe',23,18),(2,'pepsi',12,5),(3,'cappuccino',25,20),(4,'dodo',30,25),(5,'dbs latte',30,25),(7,'espresso{s}',18,13),(8,'espresso{d}',23,18),(9,'florida',30,25),(10,'flavor',5,5),(11,'frappuccino caramel',27,22),(12,'french coffe',20,15),(13,'guafa/peer fresh',23,18),(14,'hot chocolate',20,15),(15,'hot cider',20,15),(16,'icecream chocolate',20,15),(17,'icercream',25,20),(18,'ice latte',27,22),(19,'ice coffe',27,22),(20,'lemon/lemon-mint',20,15),(21,'latte',25,20),(22,'manga fresh',25,20),(23,'milk strawberry',27,22),(24,'milk guafa/peer',25,20),(25,'milk banana',25,20),(26,'mojito',20,13),(27,'mochaccino',27,22),(28,'mars frappe',27,22),(29,'milkshake chocolate',27,22),(30,'milkshake strawberry',27,22),(31,'milkshake vanilla',27,22),(32,'milkshake manga',27,22),(33,'milkshake caramel',27,22),(34,'micato',25,20),(35,'mocha',25,20),(36,'nescafe',20,15),(37,'oreo icecream',25,20),(38,'power',30,25),(39,'pineapple/ananas',25,20),(40,'redbull',35,30),(41,'strawberry fresh',25,20),(42,'sauce',5,5),(43,'sahlab/middle eastern milk pudding',25,20),(44,'tete',30,25),(45,'turky/turkish coffe',15,10),(46,'tea/chay/shay',8,5),(47,'tea/chay/shay milk',12,12),(48,'water/maya',5,5),(49,'yansoon/anise',8,5),(50,'zabado{no fruit}',20,15),(51,'zabado{fruit}',25,20),(52,'seven up 7up',12,5),(53,'schweppes orange',12,5),(54,'schweppes peach 5o5',12,5),(55,'schweppes pomegrante raman',12,5),(56,'schweppes lemon',12,5),(57,'schweppes pinapple anannas',12,5),(58,'fanta rasberry tot',12,5),(59,'fanta apple tofa7',12,5),(60,'fanta orange',12,5);
/*!40000 ALTER TABLE `item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_group`
--

DROP TABLE IF EXISTS `order_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_id` int DEFAULT NULL,
  `tran_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tran_id` (`tran_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `order_group_ibfk_1` FOREIGN KEY (`tran_id`) REFERENCES `transactions` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_group_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_group`
--

LOCK TABLES `order_group` WRITE;
/*!40000 ALTER TABLE `order_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `print_stock`
--

DROP TABLE IF EXISTS `print_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `print_stock` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `price` float NOT NULL,
  `amount` int NOT NULL,
  `tran_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tran_id` (`tran_id`),
  CONSTRAINT `print_stock_ibfk_1` FOREIGN KEY (`tran_id`) REFERENCES `transactions` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `print_stock`
--

LOCK TABLES `print_stock` WRITE;
/*!40000 ALTER TABLE `print_stock` DISABLE KEYS */;
/*!40000 ALTER TABLE `print_stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `start_time` datetime NOT NULL,
  `type` varchar(21) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-06-19 12:44:41
