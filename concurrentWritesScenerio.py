import pymysql
import threading
import time
from datetime import datetime
from config import leader_config, follower_configs

def createTestUser(index):
    timestamp = int(time.time() * 1000)
    return {"username": f"User_{index}", "email": f"user_{index}_{timestamp}@example.com"}

def insertIntoLeader(connection, userData):
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO Users (name, email) VALUES (%s, %s)
            """, (userData['username'], userData['email'])
        )
        connection.commit()

def fetchFromFollower(connection):
    with connection.cursor() as cur:
        cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        cur.execute(
            """
            SELECT user_id, name, email FROM Users ORDER BY user_id
            """
        )
        return cur.fetchall()

def concurrentWriterTask(mainConn, userData, writeSeq, threadLock):
    with threadLock:
        writeTime = datetime.now()
        insertIntoLeader(mainConn, userData)
        print(f"Inserted {userData['username']} into leader at {writeTime} (Sequence: {writeSeq})")

def validateReplicationConsistency():
    mainConn = pymysql.connect(**leader_config)
    replicaConns = [pymysql.connect(**config) for config in follower_configs]

    try:
        threadLock = threading.Lock()
        threadPool = []

        usersToInsert = [createTestUser(idx) for idx in range(1, 11)]

        print("Starting simultaneous writes to leader database...")
        for idx, userData in enumerate(usersToInsert):
            workerThread = threading.Thread(
                target=concurrentWriterTask,
                args=(mainConn, userData, idx + 1, threadLock)
            )
            threadPool.append(workerThread)
            workerThread.start()

        for thread in threadPool:
            thread.join()
        print("Concurrent writes completed.")

        for idx, replicaConn in enumerate(replicaConns):
            print(f"\nFetching data from Replica {idx + 1}...")
            replicationStartTime = datetime.now()

            replicaData = []
            while len(replicaData) < len(usersToInsert):
                replicaData = fetchFromFollower(replicaConn)
                time.sleep(0.01)

            replicationEndTime = datetime.now()
            print(f"Replica {idx + 1} synchronized at {replicationEndTime}")
            print(f"Synchronization delay: {(replicationEndTime - replicationStartTime).total_seconds()} seconds")

            receivedOrder = [record[1] for record in replicaData][-10:]
            expectedOrder = [user['username'] for user in usersToInsert]

            if receivedOrder == expectedOrder:
                print(f"Replica {idx + 1} data is in the correct sequence.")
            else:
                print(f"Replica {idx + 1} data sequence mismatch!")
                print(f"Received sequence: {receivedOrder}")
                print(f"Expected sequence: {expectedOrder}")

    finally:
        mainConn.close()
        for conn in replicaConns:
            conn.close()

validateReplicationConsistency()
