# /api/v1/db_setup , /api/v1/ollama_setup , /api/v1/user_setup , /api/v1/indexer , /api/v1/ai_retrieval_query
from fastapi import FastAPI
from pydantic import BaseModel
from python_pipeline.utils.redis.redis_setup import redis_setup, get_indexed_repos,get_redis_setup,setUserIdInEnv,setRepoName,check_existing_repo
from python_pipeline.utils.models_support.ollama_setup import validate_and_save_env_updating_ollama
from python_pipeline.utils.vectorDB.chroma_setup import *
from python_pipeline.agent import invoke_agent 
from python_pipeline.indexer import indexer
from python_pipeline.utils.models_support.ModelDictionary.modelDict import giveModelList

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
    user_id : str
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
    db_flag : bool
    ollama_flag : bool
    modelName : str
    api_key : str

class Retrieval(BaseModel):
    user_id : str
    user_query : str
    repo_url: str
class Indexer(BaseModel):
    user_id : str
    repo_url: str

class GetRedis(BaseModel):
    user_id : str

class IndexedRepoList(BaseModel):
    user_id:str

class RepoIndexed(BaseModel):
    user_id:str
    repo_url:str

@app.post("/api/v1/db_setup_online")
async def wrapper_validate_and_save_env_updating_chroma_online(chromaonline: ChromaOnline):
    validate_and_save_env_updating_chroma_online(chromaonline.CHROMA_TENANT,chromaonline.CHROMA_DATABASE , chromaonline.CHROMA_API_KEY,chromaonline.CHROMA_HOST,chromaonline.user_id)
    return {
        "success": True,
        "message": "ChromaDB cloud setup completed",
        "user_id": chromaonline.user_id
    }

@app.post("/api/v1/db_setup_offline")
async def wrapper_validate_and_save_env_updating_chroma_offline(chromaoffline : ChromaOffline):
    validate_and_save_env_updating_chroma_offline(chromaoffline.db_host,chromaoffline.db_port)
    return {
        "success": True,
        "message": "ChromaDB docker setup completed",
        "user_id": chromaoffline.user_id
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
    redis_setup(usersetup.user_id,usersetup.db_flag,usersetup.api_key,usersetup.modelName,usersetup.ollama_flag)
    return {
        "success": True,
        "message": "User setup completed",
        "user_id": usersetup.user_id
    }

@app.get("/api/v1/user_setup")
async def wrapper_get_redis_setup(user_id:str):
    user_info =  get_redis_setup(user_id)
    return {
        "config":user_info,
        "sources":{
            "user_id": user_id,
        }
    }

@app.post("/api/v1/user_indexed_repos")
async def wrapper_get_indexed_repos(indexrepolist: IndexedRepoList):
    indexed_repos =  get_indexed_repos(indexrepolist.user_id)
    return indexed_repos

@app.post("/api/v1/check_indexed_repos")
async def wrapper_check_existing_repo(checkindexedrepo :RepoIndexed):
    bool_indexed_repo =  check_existing_repo(checkindexedrepo.repo_url,checkindexedrepo.user_id)
    return{
        "exists": bool_indexed_repo,
    }

@app.post("/api/v1/repo_operation/index")
async def wrapper_indexer(indexer_base : Indexer):
    user_id = indexer_base.user_id
    repo_url = indexer_base.repo_url
    indexer(user_id,repo_url)
    return {
        "success": True,
        "message": "Indexing completed",
        "user_id": user_id,
        "repo_url":repo_url
    }


@app.post("/api/v1/repo_operation/retrieve")
async def wrapper_retrieval(retrieval : Retrieval):
    setUserIdInEnv(retrieval.user_id)
    name_collection = setRepoName(retrieval.user_id,retrieval.repo_url) # store in collection_name
    response =  invoke_agent(retrieval.user_query,retrieval.user_id,name_collection)
    setUserIdInEnv("None")
    tmp_var = setRepoName(retrieval.user_id,"None")
    return {
        "answer":response,
        "sources":{
            "success": True,
            "message": "Retrieval completed",
            "user_id": retrieval.user_id,
        }
    }

@app.get("/api/v1/models/getModelNames")
async def wrapper_giveModelList():
    ModelList = giveModelList()
    return {
        "success": True,
        "message": "Retrieval completed",
        "ModelList":ModelList
    }




# if __name__ == "__main__":
