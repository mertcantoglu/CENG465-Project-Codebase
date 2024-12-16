-- Enable Binary Logging for Replication in Configration File
-- [mysqld]
-- server-id=1
-- log-bin=mysql-bin

-- Restart the MySQL server to apply changes.

-- Create a User and Grant priviliges for Replication
CREATE USER 'berkay_repl'@'%' IDENTIFIED BY 'berkay';
GRANT REPLICATION SLAVE ON *.* TO 'berkay_repl'@'%';

CREATE USER 'mertcan_repl'@'%' IDENTIFIED BY 'mertcan';
GRANT REPLICATION SLAVE ON *.* TO 'mertcan_repl'@'%';
FLUSH PRIVILEGES;

-- LOCK TABLES
FLUSH TABLES WITH READ LOCK;
-- Check the Master Status
SHOW MASTER STATUS;
UNLOCK TABLES;

-- Note down the 'File' and 'Position' values for replica configuration.

-- Create a Sample Database and Table
CREATE DATABASE test;
USE test;

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(100) NOT NULL,             
    email VARCHAR(100) UNIQUE NOT NULL,     
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
                    ON UPDATE CURRENT_TIMESTAMP 
);
ALTER TABLE Users ADD COLUMN version INT DEFAULT 0;

-- Insert Sample Data
INSERT INTO Users (name, email) VALUES ('Mertcan', 'mertcan@mail.com');