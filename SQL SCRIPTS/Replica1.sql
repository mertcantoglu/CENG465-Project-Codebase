-- Enable Replication on Replica Server in Configration File
-- [mysqld]
-- server-id=2  
-- relay-log=relay-log

-- Restart the MySQL server to apply changes.

-- Connect the Replica to the Master
CHANGE MASTER TO
    MASTER_HOST='MASTER-IP',
    MASTER_USER='berkay_repl',
    MASTER_PASSWORD='berkay',
    MASTER_LOG_FILE='mysql-bin.000001',  -- From the note
    MASTER_LOG_POS=0;                  -- From the note

-- Start the Slave Process
START REPLICA;

-- Verify the Replica Status
SHOW REPLICA STATUS\G;
