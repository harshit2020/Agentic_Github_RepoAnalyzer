from dotenv import load_dotenv
from uuid import uuid4
import chromadb
import os
from sentence_transformers import SentenceTransformer
from utils.load_chunk import chunk_acc_file_type
from tree_sitter import Parser,Language
import tree_sitter_javascript
import tree_sitter_python
from transformers import AutoTokenizer
from pprint import pprint
from utils.chunk_summary_llm import generate_chunks_summary


#loading some environment
load_dotenv()
try:
    CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
    CHROMA_TENANT = os.getenv("CHROMA_TENANT")
    CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")

    if not all([CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE]):
        raise ValueError("Missing Chroma environment variables")

except Exception as e:
    raise RuntimeError(f"Something went wrong while initialization of environment \n Error : {e}")

# Loading functions
def load_embedding_model():
    return SentenceTransformer("nomic-ai/CodeRankEmbed",trust_remote_code=True)

def load_chroma_client():    
    client = chromadb.CloudClient(
                tenant= os.getenv("CHROMA_TENANT"),
                database= os.getenv("CHROMA_DATABASE"),
                api_key= os.getenv("CHROMA_API_KEY")
            )
    return client

def load_tokenizer():
    return AutoTokenizer.from_pretrained("nomic-ai/CodeRankEmbed", trust_remote_code=True)

#Indexing function
def indexer():
    try:
        path = "./input_code"
        embedding_MAX_TOKEN = 8192

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
        filename_array_for_chunks = [{"filename":chunk["filename"]} for chunk in chunks_for_embedding]
        filepath_array_for_chunks  = [{"filepath":chunk["filepath"]} for chunk in chunks_for_embedding]
        embeddings_source_code = embedding_model.encode(
                        codes,
                        batch_size=8,        
                        show_progress_bar=True
                    )
        print(f"{len(chunks_for_embedding)} chunks, embedding shape {embeddings_source_code.shape}")
       


        # passing the chunks to LLM and adding  file level summary for metadata
        # chunks_with_summary = generate_chunks_summary(chunks_for_embedding,api_key) import this function for generating chunk level summary and pass the chunks with summary to vector db also
        
        # combine the chunk level summary then pass it to llm to generate file level summary and here we can give dependency and call graph
        # call_graph = generate_call_graph()
        # dependency_graph = generate_dep_graph()
        # file_level_summary = generate_file_level(chunks_with_summary,call_graph,dependency_graph)  # After generating file level summary store in mongoDB, again give it to llm with dep and call graph to generate modular level summary 

        #Creating collection and adding vectors
        uuids = [str(uuid4()) for _ in codes]
        metadatas_filename_filepath = {
            "filename":filename_array_for_chunks,
            "filepath":filepath_array_for_chunks
        }
        # try:
        #     name_collection = "source_code_collection"
        #     client = load_chroma_client()
        #     print("Connected to ChromaDB!!")
        #     collection = client.create_collection(name=name_collection)
        #     print(f"Collection {name_collection} created!!")
        #     response = collection.add(
        #         ids = uuids,
        #         embeddings = embeddings_source_code.tolist(),
        #         documents = codes,
        #         metadatas = metadatas_filename_filepath,
        #     )
        #     print("Source code vectors added to ChromaDB successfully!!")

        # except Exception as e:
        #     raise RuntimeError(f"Failed to add documents to ChromaDB: {e}")

        # print(f" Successfully indexed {len(chunks_for_embedding)} documents")
        # return response

    except Exception as e:
        print(f"Indexing failed: {str(e)}")
        return None

if __name__ == "__main__":
    indexer()
