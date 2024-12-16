import pymysql
import time
from datetime import datetime
from config import leader_config, follower_configs

testUser = {"name": "Test User", "email": f"test_user_{int(time.time())}@example.com"}

def writeToLeader(connection, user, version):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Users (name, email, version) VALUES (%s, %s, %s)
        """, (user['name'], user['email'], version))
        connection.commit()

def updateVersionOnLeader(connection, email, version):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE Users SET version = %s WHERE email = %s
        """, (version, email))
        connection.commit()

def readFromFollower(connection, email):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT version FROM Users WHERE email = %s
        """, (email,))
        result = cursor.fetchone()
        return result[0] if result else None

def testMonotonicReads():
    leaderConn = pymysql.connect(**leader_config)
    followerConns = [pymysql.connect(**config) for config in follower_configs]
    
    for conn in followerConns:
        with conn.cursor() as cursor:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    try:
        print("Writing initial data to leader...")
        writeToLeader(leaderConn, testUser, version=1)
        print(f"Initial data written to leader at {datetime.now()}")

        lastReadVersions = [0] * len(followerConns)
        for version in range(2, 6):
            print(f"\nUpdating version to {version} on leader...")
            updateVersionOnLeader(leaderConn, testUser['email'], version)
            print(f"Updated to version {version} on leader at {datetime.now()}")

            for i, followerConn in enumerate(followerConns):
                currentVersion = readFromFollower(followerConn, testUser['email'])
                readTime = datetime.now()
                print(f"Follower {i+1} read version {currentVersion} at {readTime}")

                if currentVersion <= lastReadVersions[i]:
                    print(f"Monotonicity violation: Follower {i+1} read version {currentVersion} after {lastReadVersions[i]} at {readTime}")
                else:
                    lastReadVersions[i] = currentVersion
                    print(f"Monotonic read preserved for Follower {i+1}: {currentVersion}")

                time.sleep(0.01)

    finally:
        leaderConn.close()
        for conn in followerConns:
            conn.close()

testMonotonicReads()
