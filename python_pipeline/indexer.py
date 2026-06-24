from dotenv import load_dotenv
from uuid import uuid4
import chromadb
import os
from sentence_transformers import SentenceTransformer
from python_pipeline.utils.load_chunk import chunk_acc_file_type
from tree_sitter import Parser,Language
import tree_sitter_javascript
import tree_sitter_python
from transformers import AutoTokenizer
from pprint import pprint
from python_pipeline.utils.chunk_summary_llm import generate_chunks_summary
from python_pipeline.utils.file_summary_llm import generate_file_summary
from python_pipeline.utils.module_summary_llm import generate_module_summary
from python_pipeline.utils.codebase_summary_llm import generate_codebase_summary
from python_pipeline.utils.vectorDB.vectorize_llm_output import chunk_to_vector_text,file_to_vector_text,module_to_vector_text,codebase_to_vector_text
from python_pipeline.utils.vectorDB.crud_collection import *
from python_pipeline.utils.vectorDB.metadata_creator import *
from python_pipeline.agent import get_user_info,store_thread_id
from python_pipeline.utils.repo_clone.git_clone_repo import clone_repo
from python_pipeline.utils.repo_clone.delete_repo import delete_repo

#loading some environment
load_dotenv()



# Loading functions
def load_embedding_model():
    return SentenceTransformer("nomic-ai/CodeRankEmbed",trust_remote_code=True)

def load_tokenizer():
    return AutoTokenizer.from_pretrained("nomic-ai/CodeRankEmbed", trust_remote_code=True)

def embed_list_str(stringg_listt):
    embedding_model = load_embedding_model()
    
    batch_size = 8
    while batch_size >= 1:
        try:
            embeddings_source_code = embedding_model.encode(
                stringg_listt,
                batch_size=batch_size,
                show_progress_bar=True
            )
            break

        except Exception:
            batch_size //= 2
    
    print(f"{len(embeddings_source_code)} chunks, embedding shape {embeddings_source_code.shape}")
    return embeddings_source_code

#Indexing function
def indexer(user_id,repo_url):
    
    try:
        del_path = clone_repo(repo_url)
        path = "python_pipeline/input_code"

        exists = get_user_info(user_id)
        ollama_flag_string = exists["ollama_flag"]
        if ollama_flag_string == "True":
            ollama_flag = True
        else:
            ollama_flag = False       
        model_name = exists["model_name"]
        api_key = exists["api_key"]
        db_flag = exists["db_flag"]
        parts = repo_url.rstrip("/").split("/")
        repo_id = parts[-2]
        repo_name = parts[-1]
        name_collection = f"{repo_id}_{repo_name}"
        if db_flag == True:
            client = create_connect_collection_localhost()
        else:
            client = create_connect_collection_api(user_id)

        embedding_MAX_TOKEN = int(os.getenv("embedding_MAX_TOKEN"))
        print(f"embedding_MAX_TOKEN = {embedding_MAX_TOKEN}")
        tokenizer = load_tokenizer()
        embedding_model = load_embedding_model()

        chunks_for_embedding = chunk_acc_file_type(path,tokenizer,embedding_MAX_TOKEN)
        print("Chunking Completed!!")
        if not chunks_for_embedding:
            print(f"No chunks found in {path}")
            return [], []
        
        codes = []
        for chunk in chunks_for_embedding:
            codes.append(chunk["code"])
        embeddings_source_code = embedding_model.encode(
                        codes,
                        batch_size=8,        
                        show_progress_bar=True
                    )
        print(f"{len(chunks_for_embedding)} chunks, dense vectors created!!")
        
        metadata_codes = [{"filepath" : chunk["filepath"],"level":"RAW_CODE"} for chunk in chunks_for_embedding]
        add_collection(client,chunks_for_embedding,codes,embeddings_source_code,ollama_flag,db_flag,name_collection,metadata_codes)
        # passing the chunks to LLM and adding  file level summary for metadata
        chunks_with_summary = generate_chunks_summary(chunks_for_embedding,model_name,api_key,ollama_flag)
        print("Chunks Summary generated successfully!!\n\n")
        text_chunks_with_summary = [chunk_to_vector_text(chunk) for chunk in chunks_with_summary]
        embeddings_chunks_with_summary = embed_list_str(text_chunks_with_summary)
        metadatas_chunks_with_summary = metadata_chunk_level(chunks_with_summary)
        add_collection(client,chunks_with_summary,text_chunks_with_summary,embeddings_chunks_with_summary,ollama_flag,db_flag,name_collection,metadatas_chunks_with_summary)
       
        # combine the chunk level summary then pass it to llm to generate file level summary and here we can give dependency and call graph
        # call_graph = generate_call_graph()
        # dependency_graph = generate_dep_graph()

        # After generating file level summary store in mongoDB, again give it to llm with dep and call graph to generate modular level summary 
        file_level_summary = generate_file_summary(chunks_with_summary,model_name,api_key,ollama_flag)
        print("File Summary generated successfully!!")
        text_file_level_summary = [file_to_vector_text(chunk) for chunk in file_level_summary]
        embeddings_file_level_summary = embed_list_str(text_file_level_summary)
        metadatas_file_level_summary = metadata_file_level(file_level_summary)
        add_collection(client,file_level_summary,text_file_level_summary,embeddings_file_level_summary,ollama_flag,db_flag,name_collection,metadatas_file_level_summary)
      


        module_level_summary = generate_module_summary(file_level_summary,model_name,api_key,ollama_flag)
        print("Module Summary generated successfully!!")
        text_module_level_summary= [module_to_vector_text(chunk) for chunk in module_level_summary]
        embeddings_module_level_summary = embed_list_str(text_module_level_summary)
        metadatas_module_level_summary = metadata_module_level(module_level_summary)
        add_collection(client,module_level_summary,text_module_level_summary,embeddings_module_level_summary,ollama_flag,db_flag,name_collection,metadatas_module_level_summary)
       

        codebase_summary = generate_codebase_summary(module_level_summary,model_name,api_key,ollama_flag)
        print("CodebaseSummary Summary generated successfully!!")
        text_codebase_summary= codebase_to_vector_text(codebase_summary)
        embeddings_codebase_summary = embed_list_str(text_codebase_summary)
        metadatas_codebase_summary = metadata_codebase_level(repo_id,repo_name,codebase_summary)
        add_collection(client,[codebase_summary],text_codebase_summary,embeddings_codebase_summary,ollama_flag,db_flag,name_collection,metadatas_codebase_summary)
        store_thread_id(user_id,"",name_collection)
        print("Indexing Completed Successfully!!")
        delete_repo(del_path)
    except Exception as e:
        raise ValueError(f"Indexing failed: {str(e)}")

if __name__ == "__main__":
    user_id = "test_mail@gmail.com"
    indexer(user_id)


