from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os
from python_pipeline.utils.vectorDB.crud_collection import *
from sentence_transformers import SentenceTransformer
from langchain.tools import tool
from pydantic import BaseModel, Field
import redis

load_dotenv()

def load_embedding_model():
    return SentenceTransformer("nomic-ai/CodeRankEmbed",trust_remote_code=True)

def connect_redis_store():
    try:
        redisURI = os.getenv("REDIS_HOST")
        redisPort = os.getenv("REDIS_PORT")
        r = redis.Redis(host=redisURI,port=redisPort,decode_responses=True)
        return r
    except Exception as e:
        raise ValueError(f"Failed to connect to Redis!! \n {e}")

def get_DBflag_collection_name(user_id):
    try:
        r = connect_redis_store()
        exists = r.exists(user_id)
        if exists == 0:
            return None
        return r.hgetall(user_id)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve user's info from redis \n {e}")

def get_user_id():
    try: 
        user_id = os.getenv("user_id")
        return user_id
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve user's info \n {e}")

def get_collection_chroma(db_flag,collection_name):
    try:
        if db_flag == True:
            client = create_connect_collection_localhost()
        else:
            client = create_connect_collection_api()
        collection = client.get_collection(name=collection_name)
        return collection
    except Exception as e:
        print(f"connection to db for retrieval failed!! \n {e}")


def query_to_vectors(user_input):
    embedding_model = load_embedding_model()
    return embedding_model.encode(user_input)


class RetrievalInput(BaseModel):
    user_input: str = Field(
        description=(
            "Natural language query about the repository. "
            "Examples: 'How authentication works', "
            "'Explain footer component', "
            "'Where Redis is used'"
        )
    )

class FilePathInput(BaseModel):
    user_input: str = Field(
        ...,
        description=(
            "Natural language query describing the exact implementation, "
            "logic, function, JSX structure, API usage, or code behavior "
            "to search for inside the target file."
        )
    )

    filepath: str = Field(
        ...,
        description=(
            "Exact repository-relative filepath used to restrict retrieval "
            "to a single source file. "
            "Example: frontend/src/components/Footer.jsx"
        )
    )

@tool(args_schema=RetrievalInput)
def retrieval_general(user_input: str)->dict:
    """
        Performs broad semantic retrieval across ALL repository summary levels.

        Use this tool for:
        - feature understanding
        - debugging workflows
        - implementation tracing
        - execution flow analysis
        - architecture exploration
        - broad repository questions
        - questions spanning multiple architectural layers

        This tool searches:
        - function summaries
        - file summaries
        - module summaries
        - codebase summaries

        Best used when:
        - the correct architectural level is unclear
        - the question spans multiple subsystems
        - the user asks broad implementation questions

        Examples:
        - "How does authentication work?"
        - "Explain signup flow"
        - "How is Redis used?"
        - "How does request processing happen?"
        - "How does the AI pipeline work?"
        - "Explain how retrieval works"
    """
    try:
        user_id = get_user_id()
        user_info = get_DBflag_collection_name(user_id)
        db_flag_string = user_info["db_flag"]
        if db_flag_string == "False":
            db_flag = False
        else:
            db_flag = True
        collection_name = user_info["collection_name"]
        collection = get_collection_chroma(db_flag,collection_name)
        query_vectors = query_to_vectors(user_input)
        result = collection.query(
            query_embeddings = query_vectors,
            n_results=10,
        )
        return result
    except Exception as e:
        print(f"retrieval failed!! \n {e}")

@tool(args_schema=FilePathInput)
def retrieval_raw_code(user_input:str,filepath: str)->dict:
    """
        Retrieves RAW SOURCE CODE chunks from a specific file in the repository.

        This tool performs semantic vector search ONLY inside the provided filepath
        and returns the most relevant raw code chunks matching the query.

        Use this tool for:
        - exact implementation inspection
        - JSX/UI structure analysis
        - counting buttons/elements/components
        - debugging implementation details
        - tracing API calls
        - understanding exact function logic
        - checking imports/hooks/state usage
        - inspecting SQL queries or backend logic
        - locating exact code snippets

        This tool ONLY searches:
        - RAW_CODE chunks
        - inside the specified filepath

        Best used when:
        - the relevant file is already known
        - exact source code is required
        - summaries are insufficient
        - implementation-level answers are needed

        Important:
        - filepath MUST be an exact indexed repository filepath
        - this tool does not search the entire repository
        - this tool retrieves raw implementation chunks, not summaries

        Example queries:
        - "How many buttons are rendered?"
        - "Where is axios called?"
        - "What hooks are used in this component?"
        - "How is JWT validated?"
        - "Find the submit handler"
        - "Where is useEffect used?"
        - "Show the API request logic"

        Example filepath:
        frontend/src/components/Footer.jsx
    """
    try:
        user_id = get_user_id()
        user_info = get_DBflag_collection_name(user_id)
        db_flag_string = user_info["db_flag"]
        if db_flag_string == "False":
            db_flag = False
        else:
            db_flag = True
        collection_name = user_info["collection_name"]
        collection = get_collection_chroma(db_flag,collection_name)
        query_vectors = query_to_vectors(user_input)
        result = collection.query(
            query_embeddings = query_vectors,
            n_results=8,
            where={
                "$and":[
                    {"level":"RAW_CODE"},
                    {"filepath":filepath}
                ]
            }
        )
        return result
    except Exception as e:
        print(f"retrieval failed!! \n {e}")

@tool(args_schema=RetrievalInput)
def retrieval_function(user_input: str)->dict:
    """
        Retrieves FUNCTION-LEVEL implementation details from the repository.

        Use this tool for:
        - function logic understanding
        - utility behavior
        - class method analysis
        - algorithm explanations
        - implementation-specific questions
        - parameter and dependency understanding
        - internal execution logic

        This tool ONLY searches function-level summaries.

        Best used when:
        - the user asks about specific functions
        - low-level implementation details are needed
        - understanding exact execution logic is important

        Examples:
        - "What does validate_token do?"
        - "Where is JWT verified?"
        - "Explain cache manager logic"
        - "Which function calls OpenAI API?"
        - "How is retry logic implemented?"
        - "What handles vector embedding generation?"
    """
    try:
        user_id = get_user_id()
        user_info = get_DBflag_collection_name(user_id)
        db_flag_string = user_info["db_flag"]
        if db_flag_string == "False":
            db_flag = False
        else:
            db_flag = True
        collection_name = user_info["collection_name"]
        collection = get_collection_chroma(db_flag,collection_name)
        query_vectors = query_to_vectors(user_input)
        result = collection.query(
            query_embeddings = query_vectors,
            n_results=8,
            where={"level":"FUNCTION_SUMMARY"}
        )
        return result
    except Exception as e:
        print(f"retrieval failed!! \n {e}")

@tool(args_schema=RetrievalInput)
def retrieval_module(user_input: str)->dict:
    """
        Retrieves MODULE-LEVEL architectural summaries from the repository.

        Use this tool for:
        - subsystem architecture understanding
        - package responsibility analysis
        - service boundary explanations
        - module interaction understanding
        - architectural flow analysis
        - infrastructure/component organization

        This tool ONLY searches module-level summaries.

        Best used when:
        - the user asks about architecture
        - the user asks about packages/subsystems
        - understanding component collaboration is important

        Examples:
        - "Explain backend architecture"
        - "What does the auth module do?"
        - "How does the retrieval subsystem work?"
        - "Explain frontend state management"
        - "What is the role of the vector database module?"
        - "How do backend services interact?"
    """
    try:
        user_id = get_user_id()
        user_info = get_DBflag_collection_name(user_id)
        db_flag_string = user_info["db_flag"]
        if db_flag_string == "False":
            db_flag = False
        else:
            db_flag = True
        collection_name = user_info["collection_name"]
        collection = get_collection_chroma(db_flag,collection_name)
        query_vectors = query_to_vectors(user_input)
        result = collection.query(
            query_embeddings = query_vectors,
            n_results=5,
            where={"level":"MODULE_SUMMARY"}
        )
        return result
    except Exception as e:
        print(f"retrieval failed!! \n {e}")

@tool(args_schema=RetrievalInput)
def retrieval_codebase(user_input: str)->dict:
    """
        Retrieves HIGH-LEVEL codebase architecture and repository summaries.

        Use this tool for:
        - repository onboarding
        - overall system understanding
        - high-level architecture explanations
        - tech stack understanding
        - deployment/system design analysis
        - business/domain understanding

        This tool ONLY searches codebase-level summaries.

        Best used when:
        - the user asks broad repository questions
        - the user wants a system overview
        - onboarding explanations are needed
        - understanding the platform as a whole is important

        Examples:
        - "What does this repository do?"
        - "Explain the overall architecture"
        - "What technologies are used?"
        - "How is the system organized?"
        - "Give me a high-level overview"
        - "What kind of platform is this?"
    """
    try:
        user_id = get_user_id()
        user_info = get_DBflag_collection_name(user_id)
        db_flag_string = user_info["db_flag"]
        if db_flag_string == "False":
            db_flag = False
        else:
            db_flag = True
        collection_name = user_info["collection_name"]
        collection = get_collection_chroma(db_flag,collection_name)
        query_vectors = query_to_vectors(user_input)
        result = collection.query(
            query_embeddings = query_vectors,
            n_results=3,
            where={"level":"CODEBASE_SUMMARY"}
        )
        return result
    except Exception as e:
        print(f"retrieval failed!! \n {e}")


if __name__ == "__main__":
    user_input = "Footer"
    result = retrieval_raw_code(user_input,"frontend/src/components/Footer.jsx")
    for ids, documents, metadatas in zip(result["ids"], result["documents"], result["metadatas"]):
        for id, document, metadata in zip(ids, documents, metadatas):
            print(id, document, metadata)