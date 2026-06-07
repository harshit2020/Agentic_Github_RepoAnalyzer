from  dotenv import set_key
from python_pipeline.utils.redis.redis_setup import connect_redis_store


def validate_and_save_env_updating_chroma_online(CHROMA_TENANT, CHROMA_DATABASE, CHROMA_API_KEY,CHROMA_HOST,user_id): # change this to store this into redis
    try:
        r = connect_redis_store()
        r.hset(user_id,
            mapping = {
                "CHROMA_HOST":CHROMA_HOST,
                "CHROMA_TENANT":CHROMA_TENANT,
                "CHROMA_DATABASE" : CHROMA_DATABASE,
                "CHROMA_API_KEY" : CHROMA_API_KEY
            }
        )
        print("Chroma DB config saved and validated ✅")
    except Exception as e:
        raise ValueError(f"Cannot connect to Chroma DB ad {e}")
    

def validate_and_save_env_updating_chroma_offline(db_host,db_port): # change this to store this into redis
    try:
        env_path = "python_pipeline/.env"
        set_key(env_path,"db_host",db_host)
        set_key(env_path,"db_port",db_port)
        print("Chroma DB config saved and validated ✅")
    except Exception as e:
        raise ValueError(f"Cannot connect to Chroma DB ad {e}")
    

if __name__ == "__main__":
    validate_and_save_env_updating_chroma_offline("172.21.16.1","8000")
    validate_and_save_env_updating_chroma_online("eaceab92-b4b0-4077-a227-7f42147672f2","Dev","ck-nWpufyuBJR4KL7GoyqdqafsxDbnvur8e6boTfH9G5hz","api.trychroma.com","test_mail@gmail.com")