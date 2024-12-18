-- Enable Replication on Replica Server in Configration File
-- [mysqld]
-- server-id=2  
-- relay-log=relay-log

-- Restart the MySQL server to apply changes.

-- Connect the Replica to the Master
              -- From the note
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='MASTER-IP',
  SOURCE_USER='berkay_repl',
  SOURCE_PASSWORD='berkay',
  SOURCE_LOG_FILE='mysql-bin.000001',
  SOURCE_LOG_POS=0;

-- Start the Slave Process
START REPLICA;

-- Verify the Replica Status
SHOW REPLICA STATUS\G;
