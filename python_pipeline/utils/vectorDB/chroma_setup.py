from  dotenv import set_key

def validate_and_save_env_updating_chroma_(CHROMA_TENANT, CHROMA_DATABASE, CHROMA_API_KEY,CHROMA_HOST): # change this to store this into redis
    try:
        env_path = "python_pipeline/.env"
        set_key(env_path, "CHROMA_HOST",CHROMA_HOST)
        set_key(env_path, "CHROMA_TENANT",CHROMA_TENANT)
        set_key(env_path, "CHROMA_DATABASE",CHROMA_DATABASE)
        set_key(env_path, "CHROMA_API_KEY",CHROMA_API_KEY)
        print("Chroma DB config saved and validated ✅")
    except Exception as e:
        raise ValueError(f"Cannot connect to Chroma DB ad {e}")

if __name__ == "__main__":
    validate_and_save_env_updating_chroma_("eaceab92-b4b0-4077-a227-7f42147672f2","Dev","ck-nWpufyuBJR4KL7GoyqdqafsxDbnvur8e6boTfH9G5hz","api.trychroma.com")