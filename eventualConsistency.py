import pymysql
import time
from datetime import datetime
from config import leader_config, follower_configs

test_user = {"name": "Test User", "email": f"test_user_{int(time.time())}@example.com"}

def writeToLeader(connection, user):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Users (name, email) VALUES (%s, %s)
        """, (user['name'], user['email']))
        connection.commit()

def readFromFollower(connection, email):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, name, email, last_updated FROM Users WHERE email = %s
        """, (email,))
        result = cursor.fetchone()
        return result

def testEventualConsistency():
    leaderConn = pymysql.connect(**leader_config)
    followerConns = [pymysql.connect(**config) for config in follower_configs]
    
    for conn in followerConns:
        with conn.cursor() as cursor:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
    
    print("Writing to leader...")
    writeToLeader(leaderConn, test_user)
    writeTime = datetime.now()
    print(f"Data written to leader at {writeTime}")

    print("Reading from followers...")
    convergenceTime = None
    startTime = time.time()
    
    while True:
        allConsistent = True
        for i, followerConn in enumerate(followerConns):
            result = readFromFollower(followerConn, test_user['email'])
            if result is None:
                print(f"Follower {i+1} not consistent at {datetime.now()}")
                allConsistent = False
            else:
                print(f"Follower {i+1} consistent at {datetime.now()} - Record: {result}")
        
        if allConsistent:
            convergenceTime = datetime.now()
            print(f"All followers consistent at {convergenceTime}")
            break
        
        time.sleep(0.0001)
        if time.time() - startTime > 60:
            print("Test timed out. Not all followers reached consistency.")
            break
    
    leaderConn.close()
    for conn in followerConns:
        conn.close()
    
    if convergenceTime:
        print(f"Eventual consistency at {convergenceTime - writeTime}")
    else:
        print("Eventual consistency not achieved.")

testEventualConsistency()
