CREATE TABLE `task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `list_id` int(11) NOT NULL,
  `content` varchar(200) NOT NULL,
  `due_date` datetime DEFAULT NULL,
  `is_completed` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `list_id` (`list_id`)
);