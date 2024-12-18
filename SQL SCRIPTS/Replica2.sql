-- Enable Replication on Replica Server in Configration File
-- [mysqld]
-- server-id=3
-- relay-log=relay-log

-- Restart the MySQL server to apply changes.

-- Connect the Replica to the Master
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='MASTER-IP',
  SOURCE_USER='mertcan_repl',
  SOURCE_PASSWORD='mertcan',
  SOURCE_LOG_FILE='mysql-bin.000001',
  SOURCE_LOG_POS=0;
                 

-- Start the Slave Process
START REPLICA;

-- Verify the Replica Status
SHOW REPLICA STATUS\G;
