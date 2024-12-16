import pymysql
from config import leader_config, follower_configs

def test_connection(config):
    try:
        connection = pymysql.connect(**config)
        connection.close()
        print(f"Connection successful to {config['host']}.")
    except Exception as e:
        print(f"Connection failed to {config['host']}.")
        
def main():
    configs = [leader_config] + follower_configs
    for config in configs:
        test_connection(config)


if __name__ == "__main__":
    main()
