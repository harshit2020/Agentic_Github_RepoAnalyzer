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


def redis_setup(user_id,db_flag_string,repo_url,api_key,modelName,ollama_flag_string):
    parts = repo_url.rstrip("/").split("/")
    repo_id = parts[-2]
    repo_name = parts[-1]
    env_path = "python_pipeline/.env"
    set_key(env_path,"user_id",user_id)
    try:
        if db_flag_string == False:
            db_flag = "False"
        else:
            db_flag = "True"
        if ollama_flag_string == False:
            ollama_flag = "False"
        else:
            ollama_flag = "True"
        collection_name = f"{repo_id}_{repo_name}"
        r = connect_redis_store()
        r.hset(user_id,
            mapping = {
                "repo_id" : repo_id,
                "repo_name": repo_name,
                "db_flag":db_flag,
                "collection_name":collection_name,
                "thread_id" : "None",
                "api_key" : api_key,
                "model_name" : modelName,
                "ollama_flag" : ollama_flag
            }
        )
        print("Redis data insertion successfull!!")
    except Exception as e:
        print(f"Error occured while setting up the redis credentials!! \n {e}")


if __name__ == "__main__":
    redis_setup("test_mail@gmail.com",False,"https://github.com/SmilingDev/Test2","AIzaSyBH92BNIRgjRIxKKlXxRcU6QsUVfFI9f_0","gemini-3.1-flash-lite",False)