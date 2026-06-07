# /api/v1/db_setup , /api/v1/ollama_setup , /api/v1/user_setup , /api/v1/indexer , /api/v1/ai_retrieval_query
from fastapi import FastAPI
from pydantic import BaseModel
from python_pipeline.utils.redis.redis_setup import redis_setup
from python_pipeline.utils.models_support.ollama_setup import validate_and_save_env_updating_ollama
from python_pipeline.utils.vectorDB.chroma_setup import *
from python_pipeline.agent import invoke_agent 
from python_pipeline.indexer import indexer


app = FastAPI()


#PYDANTIC INPUT BODY PARAMETERS

class ChromaOnline(BaseModel):
    CHROMA_API_KEY : str 
    CHROMA_HOST : str
    CHROMA_TENANT: str 
    CHROMA_DATABASE: str 
    user_id : str


class ChromaOffline(BaseModel):
    db_host : str
    db_port : str

class OllamaSetup(BaseModel):
   user_id : str
   ollama_host : str
   ollama_port : str 
   num_ctx : str 
   num_predict : str 
   temperature : str 
   requests_per_second : str 
   max_bucket_size : str 
   model_name : str 

class UserSetup(BaseModel):
    user_id : str
    db_flag : str
    ollama_flag : str
    repo_url : str
    modelName : str
    api_key : str

class Retrieval(BaseModel):
    user_query : str

@app.post("/api/v1/db_setup_online")
async def wrapper_validate_and_save_env_updating_chroma_online(chromaonline: ChromaOnline):
    await validate_and_save_env_updating_chroma_online(chromaonline["CHROMA_TENANT"],chromaonline["CHROMA_DATABASE"] , chromaonline["CHROMA_API_KEY"],chromaonline["CHROMA_HOST"],chromaonline["user_id"])
    return {
        "success": True,
        "message": "ChromaDB cloud setup completed",
        "user_id": chromaonline["user_id"]
    }

@app.post("/api/v1/db_setup_offline")
async def wrapper_validate_and_save_env_updating_chroma_offline(chromaoffline : ChromaOffline,user_id):
    await validate_and_save_env_updating_chroma_offline(chromaoffline["db_host"],chromaoffline["db_port"])
    return {
        "success": True,
        "message": "ChromaDB docker setup completed",
        "user_id": user_id
    }


@app.post("/api/v1/ollama_setup")
async def wrapper_validate_and_save_env_updating_ollama(ollamasetup : OllamaSetup):
    await validate_and_save_env_updating_ollama(ollamasetup["ollama_host"], ollamasetup["ollama_port"], ollamasetup["model_name"], ollamasetup["num_ctx"], ollamasetup["num_predict"], ollamasetup["temperature"], ollamasetup["requests_per_second"], ollamasetup["max_bucket_size"])
    return {
        "success": True,
        "message": "Ollama setup completed",
        "user_id": ollamasetup["user_id"]
    }




@app.post("/api/v1/user_setup")
async def wrapper_redis_setup(usersetup : UserSetup):
    await redis_setup(usersetup["user_id"],usersetup["db_flag"],usersetup["repo_url"],usersetup["api_key"],usersetup["modelName"],usersetup["ollama_flag"])
    return {
        "success": True,
        "message": "User setup completed",
        "user_id": usersetup["user_id"]
    }


@app.get("/api/v1/indexer")
async def wrapper_indexer(user_id):
    # await indexer(userId)
    print("Hello!!")
    return {
        "success": True,
        "message": "User setup completed",
        "user_id": user_id
    }


@app.get("/api/v1/ai_retrieval_query")
async def wrapper_indexer(retrieval : Retrieval,user_id):
    await invoke_agent(retrieval["user_query"],user_id)
    return {
        "success": True,
        "message": "User setup completed",
        "user_id": user_id
    }

# if __name__ == "__main__":
