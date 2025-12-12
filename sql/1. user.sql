CREATE DATABASE flaskfinal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE flaskfinal;

CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);