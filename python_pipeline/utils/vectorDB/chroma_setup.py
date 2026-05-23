from  dotenv import set_key

def validate_and_save_env_updating_chroma_(CHROMA_TENANT, CHROMA_DATABASE, CHROMA_API_KEY,CHROMA_HOST):
    try:
        env_path = ".env"
        set_key(env_path, "CHROMA_HOST",CHROMA_HOST)
        set_key(env_path, "CHROMA_TENANT",CHROMA_TENANT)
        set_key(env_path, "CHROMA_DATABASE",CHROMA_DATABASE)
        set_key(env_path, "CHROMA_API_KEY",CHROMA_API_KEY)
        print("Chroma DB config saved and validated ✅")
    except Exception as e:
        raise ValueError(f"Cannot connect to Chroma DB — Please check the configs again.")