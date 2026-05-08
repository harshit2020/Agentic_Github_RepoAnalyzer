from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from langchain_chroma import Chroma
from dotenv import load_dotenv

def retrieval(user_input):
    try:
        load_dotenv()
        CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
        CHROMA_TENANT = os.getenv("CHROMA_TENANT")
        CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
        try:
            hf = HuggingFaceEmbeddings(
                model_name = "BAAI/bge-base-en-v1.5",
                model_kwargs = {"device":"cpu"},
                encode_kwargs = {"normalize_embeddings":True}
            )
        except Exception as e:
            print("Embedding model initialization failed!!")

        try:
            client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT,
                database=CHROMA_DATABASE,
            )
        except Exception as e:
            print("cloud chromadb initialization failed!!")

        try:
            vector_store = Chroma(
                client = client,
                collection_name = "source_code_vectors",
                embedding_function = hf
            )
        except Exception as e:
            print("vector store loading failed!!")
        
        response = vector_store.similarity_search_by_vector(
            embedding = hf.embed_query(user_input),
            k=1
        )
        for docs in response:
            print(f"*{docs.page_content} [{docs.metadata}]")
        
    except Exception as e:
        print("retrieval failed!!")

if __name__ = "__main__":
    retrieval("Hello! my name is Maniac , can you explain me the code")