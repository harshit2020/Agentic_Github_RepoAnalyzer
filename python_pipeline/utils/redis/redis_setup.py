import redis
from dotenv import load_dotenv,set_key
import os

load_dotenv()
def connect_redis_store():
    try:
        redisURI = os.getenv("REDIS_HOST")
        redisPort = os.getenv("REDIS_PORT")
        r = redis.Redis(host=redisURI,port=redisPort,decode_responses=True)
        return r
    except Exception as e:
        raise ValueError(f"Failed to connect to Redis!! \n {e}")


def redis_setup(user_id,db_flag_string,repo_id,repo_name):
    env_path = "python_pipeline/.env"
    set_key(env_path,"user_id",user_id)
    try:
        if db_flag_string == False:
            db_flag = "False"
        else:
            db_flag = "True"
        collection_name = f"{repo_id}_{repo_name}"
        r = connect_redis_store()
        r.hset(user_id,
            mapping = {
                "db_flag":db_flag,
                "collection_name":collection_name,
                "thread_id" : "None"
            }
        )
        print("Redis data insertion successfull!!")
    except Exception as e:
        print(f"Error occured while setting up the redis credentials!! \n {e}")


if __name__ == "__main__":
    redis_setup("test_mail@gmail.com",False,"SmilingDev","Test1")