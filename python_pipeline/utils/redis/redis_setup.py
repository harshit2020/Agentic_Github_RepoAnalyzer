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


def redis_setup(user_id,db_flag_string,api_key,modelName,ollama_flag_string):
    try:
        if db_flag_string == False:
            db_flag = "False"
        else:
            db_flag = "True"
        if ollama_flag_string == False:
            ollama_flag = "False"
        else:
            ollama_flag = "True"
        r = connect_redis_store()
        r.hset(user_id,
            mapping = {
                "repo_id" : "None",
                "repo_name": "None",
                "db_flag":db_flag,
                "collection_name":"None",
                "thread_id" : "None",
                "api_key" : api_key,
                "model_name" : modelName,
                "ollama_flag" : ollama_flag
            }
        )
        print("Redis data insertion successfull!!")
    except Exception as e:
        raise ValueError(f"Error occured while setting up the redis credentials!! \n {e}")



def get_redis_setup(user_id):
    try:
        r = connect_redis_store()
        user_info = r.hgetall(user_id)
        user_info["modelName"] = user_info.pop("model_name")
        if user_info["db_flag"] == "True":
            user_info["db_flag"] = True # dont judge its just frontend issue
        else:
            user_info["db_flag"] = False
        if user_info["ollama_flag"] == "True":
            user_info["ollama_flag"] = True
        else:
            user_info["ollama_flag"] = False
        print(user_info)
        return user_info
    except Exception as e:
        raise ValueError(f"Error occured while getting user_setup (REDIS) \n {e}")

def get_indexed_repos(user_id):
    try:
        r = connect_redis_store()
        user_indexed_repos = r.hkeys(f"user{user_id}:indexed_repos")
        return user_indexed_repos
    except Exception as e:
        raise ValueError(f"Error occured while getting indexed repos \n {e}")

def check_existing_repo(repo_url,user_id):
    try:
        r = connect_redis_store()
        user_indexed_repos = r.hkeys(f"user{user_id}:indexed_repos")
        parts = repo_url.rstrip("/").split("/")
        repo_id = parts[-2]
        repo_name = parts[-1]
        name_collection = f"{repo_id}_{repo_name}"
        if name_collection in user_indexed_repos:
            return True
        else:
            return False
    except Exception as e:
        raise ValueError(f"Error occured while getting indexed repos \n {e}")

def setUserIdInEnv(user_id):
    
    try:
        env_path = "python_pipeline/.env"
        set_key(env_path,"user_id",user_id)
    except Exception as e:
        raise ValueError(f"Error occured while setting user_id for retrieval \n {e}")

def setRepoName(user_id,repo_url):
    try:
        r = connect_redis_store()
        name_collection = "None"
        if repo_url != "None":
            parts = repo_url.rstrip("/").split("/")
            repo_id = parts[-2]
            repo_name = parts[-1]
            name_collection = f"{repo_id}_{repo_name}"
        r.hset(user_id,
                mapping = {
                    "collection_name":name_collection
                })
        print(r.hgetall(user_id))
        return name_collection
    except Exception as e:
        raise ValueError(f"Error occured while setting repo_name \n {e}")

if __name__ == "__main__":
    redis_setup("test_mail@gmail.com",False,"AIzaSyBH92BNIRgjRIxKKlXxRcU6QsUVfFI9f_0","gemini-3.1-flash-lite",False)
    setUserIdInEnv("test_mail@gmail.com")
    setRepoName("test_mail@gmail.com","https://github.com/SmilingDev/Test1")
    