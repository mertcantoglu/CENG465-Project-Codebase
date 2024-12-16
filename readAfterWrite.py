import pymysql
import time
from datetime import datetime
from config import leader_config, follower_configs

test_user = {"name": "Test User", "email": f"test_user_{int(time.time())}@example.com"}

def leaderWrite(connection, user):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Users (name, email) VALUES (%s, %s)
        """, (user['name'], user['email']))
        connection.commit()

def followerRead(connection, email):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, name, email, last_updated FROM Users WHERE email = %s
        """, (email,))
        result = cursor.fetchone()
        return result

def testConsistency():
    masterConnection = pymysql.connect(**leader_config)
    replicaConnection = [pymysql.connect(**config) for config in follower_configs]
    
    for connection in replicaConnection:
        with connection.cursor() as cursor:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
    
    print("Writing to master...")
    leaderWrite(masterConnection, test_user)
    writeTime = datetime.now()
    print(f"Data written to master at {writeTime}")

    print("Reading from replicas...")
    recordedConvergeTime = None
    start = time.time()
    
    while True:
        consistent = True
        for i, followerConn in enumerate(replicaConnection):
            result = followerRead(followerConn, test_user['email'])
            if result is None:
                print(f"Replica {i+1} not consistent at {datetime.now()}")
                consistent = False
            else:
                print(f"Replica {i+1} consistent at {datetime.now()} - Record: {result}")
        
        if consistent:
            recordedConvergeTime = datetime.now()
            print(f"All replicas consistent at {recordedConvergeTime}")
            break
        
        time.sleep(0.0001)
        if time.time() - start > 60:
            print("Timed out. Not all replicas reached consistency.")
            break
    
    masterConnection.close()
    for connection in replicaConnection:
        connection.close()
    
    if recordedConvergeTime:
        print(f"Eventual consistency at {recordedConvergeTime - writeTime}")
    else:
        print("Eventual consistency not achieved.")

testConsistency()
