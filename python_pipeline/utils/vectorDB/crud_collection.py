from dotenv import load_dotenv
import chromadb
from dotenv import load_dotenv
from python_pipeline.utils.load_chunk import chunk_acc_file_type
from python_pipeline.utils.chunk_summary_llm import generate_chunks_summary
from python_pipeline.utils.vectorDB.metadata_creator import *
from python_pipeline.utils.vectorDB.vectorize_llm_output import *
from python_pipeline.utils.file_summary_llm import generate_file_summary
from python_pipeline.utils.module_summary_llm import generate_module_summary
from python_pipeline.utils.codebase_summary_llm import generate_codebase_summary
import json
import os
from uuid import uuid4

from sentence_transformers import SentenceTransformer

load_dotenv()

def create_connect_collection_api(): #change this to get this from redis
    try:
        CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
        CHROMA_TENANT = os.getenv("CHROMA_TENANT")
        CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")

        if not all([CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE]):
            raise ValueError("Missing Chroma environment variables")

    except Exception as e:
        raise RuntimeError(f"Something went wrong while initialization of environment \n Error : {e}")
    try:
        client = chromadb.CloudClient(
                    tenant= os.getenv("CHROMA_TENANT"),
                    database= os.getenv("CHROMA_DATABASE"),
                    api_key= os.getenv("CHROMA_API_KEY")
                )
        print("Connected to ChromaDB Cloud !!")
        return client
    except Exception as e:  
        raise RuntimeError(f"Something went wrong while initialization of environment \n Error : {e}")


def create_connect_collection_localhost(host,port):
    try:
        
        CHROMA_DB_DOCKER_HOST = os.getenv("CHROMA_DB_DOCKER_HOST")
        CHROMA_DB_DOCKER_PORT = os.getenv("CHROMA_DB_DOCKER_PORT")
        client = chromadb.HttpClient(host=host, port=port, ssl=False)
        print(f"Connected to ChromaDB on port {port}!!")
        return client
    except Exception as e:  
        raise RuntimeError(f"Wrong host or port \n Error : {e}")


def add_collection(client,chunks_with_summary,text_chunks,embeddings,ollama_flag,db_flag,name_collection,metadatas):
    try:   
        uuids = [str(uuid4()) for _ in chunks_with_summary]
        collection = client.get_or_create_collection(name=name_collection)
        response = collection.add(
            ids = uuids,
            embeddings = embeddings.tolist(),
            documents = text_chunks,
            metadatas = metadatas,
        )
        print("Source code vectors added to ChromaDB successfully!!")
        return response   
    except Exception as e:  
        raise RuntimeError(f"Failed to create and add vector in DB \n Error : {e}")



# to be implemented later
# def update_collection(
#     filepath: str,
#     filename: str,
#     module_name: str,
#     model_name: str,
#     api_key: str,
#     ollama_flag: bool,
#     embedding_model,
#     tokenizer,
#     db_flag,
#     name_collection,
# ):
#     if ollama_flag == True:
#         chroma_client = create_connect_collection_localhost()
#     else:
#         chroma_client = create_connect_collection_api()
#     collection = chroma_client.get_collection(
#         "source_code_collection"
#     )

#     # ============================================================
#     # STEP 1 — DELETE OLD FUNCTION SUMMARIES
#     # ============================================================

#     existing_function_chunks = collection.get(
#         where={
#             "$and": [
#                 {"level": {"$eq": "FUNCTION_SUMMARY"}},
#                 {"filepath": {"$eq": filepath}},
#                 {"filename": {"$eq": filename}}
#             ]
#         }
#     )

#     if existing_function_chunks["ids"]:

#         collection.delete(
#             ids=existing_function_chunks["ids"]
#         )

#         print(
#             f"Deleted "
#             f"{len(existing_function_chunks['ids'])} "
#             f"function summaries"
#         )

#     # ============================================================
#     # STEP 2 — RECHUNK FILE
#     # ============================================================

#     path = "python_pipeline/input_code"

#     embedding_max_token = int(
#         os.getenv("EMBEDDING_MAX_TOKEN")
#     )

#     chunks_for_embedding = chunk_acc_file_type(
#         path,
#         tokenizer,
#         embedding_max_token
#     )

#     # ============================================================
#     # STEP 3 — GENERATE FUNCTION SUMMARIES
#     # ============================================================

#     chunk_summaries = generate_chunks_summary(
#         chunks_for_embedding,
#         model_name,
#         api_key,
#         ollama_flag
#     )

#     # ============================================================
#     # STEP 4 — VECTORIZE FUNCTION SUMMARIES
#     # ============================================================

#     chunk_documents = [
#         chunk_to_vector_text(chunk)
#         for chunk in chunk_summaries
#     ]

#     chunk_embeddings = embedding_model.encode(
#         chunk_documents,
#         batch_size=8
#     ).tolist()

#     chunk_metadatas = []

#     for chunk in chunk_summaries:

#         metadata = {
#             "level": "FUNCTION_SUMMARY",
#             "filepath": chunk.function_info.filepath,
#             "filename": chunk.function_info.filename,
#             "function_name": chunk.function_info.function_name,
#             "raw": json.dumps(
#                 chunk.model_dump()
#             )
#         }

#         chunk_metadatas.append(metadata)

#     collection.add(
#         ids=[str(uuid4()) for _ in chunk_summaries],
#         embeddings=chunk_embeddings,
#         documents=chunk_documents,
#         metadatas=chunk_metadatas
#     )

#     print(
#         f"Uploaded "
#         f"{len(chunk_summaries)} "
#         f"function summaries"
#     )

#     # ============================================================
#     # STEP 5 — DELETE OLD FILE SUMMARY
#     # ============================================================

#     existing_file_summary = collection.get(
#         where={
#             "$and": [
#                 {"level": {"$eq": "FILE_SUMMARY"}},
#                 {"filepath": {"$eq": filepath}},
#                 {"filename": {"$eq": filename}}
#             ]
#         }
#     )

#     if existing_file_summary["ids"]:

#         collection.delete(
#             ids=existing_file_summary["ids"]
#         )

#         print(
#             f"Deleted old file summary "
#             f"for {filename}"
#         )

#     # ============================================================
#     # STEP 6 — GENERATE FILE SUMMARY
#     # ============================================================

#     file_summary = generate_file_summary(
#         chunk_summaries,
#         model_name,
#         api_key,
#         ollama_flag
#     )

#     file_document = file_to_vector_text(
#         file_summary
#     )

#     file_embedding = embedding_model.encode(
#         [file_document],
#         batch_size=1
#     ).tolist()

#     file_metadata = [{
#         "level": "FILE_SUMMARY",
#         "filepath": file_summary.filepath,
#         "filename": file_summary.filename,
#         "module_name": file_summary.module_name,
#         "raw": json.dumps(
#             file_summary.model_dump()
#         )
#     }]

#     collection.add(
#         ids=[str(uuid4())],
#         embeddings=file_embedding,
#         documents=[file_document],
#         metadatas=file_metadata
#     )

#     print(
#         f"Uploaded file summary "
#         f"for {filename}"
#     )

#     # ============================================================
#     # STEP 7 — FETCH ALL FILE SUMMARIES
#     # INSIDE SAME MODULE
#     # ============================================================

#     module_file_summaries = collection.get(
#         where={
#             "$and": [
#                 {"level": {"$eq": "FILE_SUMMARY"}},
#                 {"module_name": {"$eq": module_name}}
#             ]
#         },
#         include=["metadatas"]
#     )

#     reconstructed_file_summaries = [
#         FileLevelSummary(**json.loads(metadata["raw"]))
#         for metadata in module_file_summaries["metadatas"]
#     ]

#     print(
#         f"Found "
#         f"{len(reconstructed_file_summaries)} "
#         f"file summaries inside module "
#         f"{module_name}"
#     )

#     # ============================================================
#     # STEP 8 — DELETE OLD MODULE SUMMARY
#     # ============================================================

#     existing_module_summary = collection.get(
#         where={
#             "$and": [
#                 {"level": {"$eq": "MODULE_SUMMARY"}},
#                 {"module_name": {"$eq": module_name}}
#             ]
#         }
#     )

#     if existing_module_summary["ids"]:

#         collection.delete(
#             ids=existing_module_summary["ids"]
#         )

#         print(
#             f"Deleted old module summary "
#             f"for {module_name}"
#         )

#     # ============================================================
#     # STEP 9 — GENERATE MODULE SUMMARY
#     # ============================================================

#     module_summary = generate_module_summary(
#         reconstructed_file_summaries,
#         model_name,
#         api_key,
#         ollama_flag
#     )

#     module_document = module_to_vector_text(
#         module_summary
#     )

#     module_embedding = embedding_model.encode(
#         [module_document],
#         batch_size=1
#     ).tolist()

#     module_metadata = [{
#         "level": "MODULE_SUMMARY",
#         "module_name": module_summary.module_name,
#         "filepath": module_summary.filepath,
#         "raw": json.dumps(
#             module_summary.model_dump()
#         )
#     }]

#     collection.add(
#         ids=[str(uuid4())],
#         embeddings=module_embedding,
#         documents=[module_document],
#         metadatas=module_metadata
#     )

#     print(
#         f"Uploaded module summary "
#         f"for {module_name}"
#     )

#     # ============================================================
#     # STEP 10 — DELETE OLD CODEBASE SUMMARY
#     # ============================================================

#     existing_codebase_summary = collection.get(
#         where={
#             "level": {
#                 "$eq": "CODEBASE_SUMMARY"
#             }
#         }
#     )

#     if existing_codebase_summary["ids"]:

#         collection.delete(
#             ids=existing_codebase_summary["ids"]
#         )

#         print(
#             "Deleted old codebase summary"
#         )

#     # ============================================================
#     # STEP 11 — FETCH ALL MODULE SUMMARIES
#     # ============================================================

#     all_module_summaries_response = collection.get(
#         where={
#             "level": {
#                 "$eq": "MODULE_SUMMARY"
#             }
#         },
#         include=["metadatas"]
#     )

#     reconstructed_module_summaries = [

#         ModuleLevelSummary(
#             **json.loads(metadata["raw"])
#         )

#         for metadata
#         in all_module_summaries_response["metadatas"]
#     ]

#     print(
#         f"Found "
#         f"{len(reconstructed_module_summaries)} "
#         f"module summaries"
#     )

#     # ============================================================
#     # STEP 12 — GENERATE CODEBASE SUMMARY
#     # ============================================================

#     codebase_summary = generate_codebase_summary(
#         reconstructed_module_summaries,
#         model_name,
#         api_key,
#         ollama_flag
#     )

#     codebase_document = codebase_to_vector_text(
#         codebase_summary
#     )

#     codebase_embedding = embedding_model.encode(
#         [codebase_document],
#         batch_size=1
#     ).tolist()

#     codebase_metadata = [{
#         "level": "CODEBASE_SUMMARY",
#         "raw": json.dumps(
#             codebase_summary.model_dump()
#         )
#     }]

#     collection.add(
#         ids=[str(uuid4())],
#         embeddings=codebase_embedding,
#         documents=[codebase_document],
#         metadatas=codebase_metadata
#     )

#     print(
#         "Uploaded new codebase summary"
#     )

#     print(
#         f"Update complete for {filename}"
#     )


if __name__ == "__main__":
    chunks_with_summary = [ChunkSummary(function_info=FunctionName(filename='index.js', filepath='python_pipeline/input_code/backend/src/index.js', function_name='anonymous_server_initializer'), parameters=[], return_value='Promise<void>', logic_summary='Initializes the application by connecting to the database, starting the server on a specified port, and setting up Redis connection event listeners.', dependencies=['connectDB', 'app.listen'], side_effects='Starts HTTP server, logs to console, connects to Redis.', error_handling='Logs failure message and throws error if database connection fails.', complexity='critical_path', tags=['server', 'initialization', 'database', 'redis'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='user.model.js', filepath='python_pipeline/input_code/backend/src/model/user.model.js', function_name='anonymous_password_hasher'), parameters=[ParameterInfo(name='next', type='function', description='Mongoose middleware next function')], return_value='void', logic_summary='Mongoose pre-save hook that hashes the user password using bcrypt if it has been modified.', dependencies=['bcrypt.hash'], side_effects='Modifies the password field on the user document.', error_handling='NONE', complexity='core_logic', tags=['mongoose', 'middleware', 'security', 'password'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='user.model.js', filepath='python_pipeline/input_code/backend/src/model/user.model.js', function_name='anonymous_password_validator'), parameters=[ParameterInfo(name='password', type='string', description='The plain text password to verify')], return_value='boolean', logic_summary='Compares a provided plain text password against the stored hashed password.', dependencies=['bcrypt.compare'], side_effects='NONE', error_handling='NONE', complexity='core_logic', tags=['security', 'authentication', 'bcrypt'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='user.model.js', filepath='python_pipeline/input_code/backend/src/model/user.model.js', function_name='anonymous_access_token_generator'), parameters=[], return_value='string', logic_summary='Generates a JWT access token containing user ID, username, and email, signed with a secret and an expiry time.', dependencies=['jwt.sign'], side_effects='NONE', error_handling='NONE', complexity='core_logic', tags=['jwt', 'authentication', 'token'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='user.model.js', filepath='python_pipeline/input_code/backend/src/model/user.model.js', function_name='anonymous_refresh_token_generator'), parameters=[], return_value='string', logic_summary='Generates a JWT refresh token containing only the user ID, signed with a secret and an expiry time.', dependencies=['jwt.sign'], side_effects='NONE', error_handling='NONE', complexity='core_logic', tags=['jwt', 'authentication', 'token'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='testClient.js', filepath='python_pipeline/input_code/backend/src/nlp_model/testClient.js', function_name='analyzeReview'), parameters=[ParameterInfo(name='text', type='string', description='The review text to analyze')], return_value='object', logic_summary='Sends a POST request to the ML API to analyze the sentiment of the provided text.', dependencies=['axios.post'], side_effects='Network request to ML service.', error_handling='NONE', complexity='utility', tags=['nlp', 'api', 'sentiment'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='testClient.js', filepath='python_pipeline/input_code/backend/src/nlp_model/testClient.js', function_name='anonymous_test_runner'), parameters=[], return_value='void', logic_summary='Executes a test call to the analyzeReview function with a sample string and logs the result.', dependencies=['analyzeReview'], side_effects='Logs to console.', error_handling='NONE', complexity='utility', tags=['test', 'nlp'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='model_runner.py', filepath='python_pipeline/input_code/backend/src/nlp_model/model_runner.py', function_name='analyze_text'), parameters=[ParameterInfo(name='text', type='str', description='The input text to classify')], return_value='str', logic_summary='Tokenizes input text, runs it through a pre-trained model, and returns the label corresponding to the highest logit score.', dependencies=['tokenizer', 'model'], side_effects='NONE', error_handling='NONE', complexity='core_logic', tags=['nlp', 'machine_learning', 'classification'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='worker.js', filepath='python_pipeline/input_code/backend/src/nlp_model/worker.js', function_name='anonymous_worker_listener'), parameters=[], return_value='void', logic_summary='Starts the worker server on a specific port and logs the status.', dependencies=['app.listen'], side_effects='Starts server, logs to console.', error_handling='NONE', complexity='utility', tags=['worker', 'server'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='worker.js', filepath='python_pipeline/input_code/backend/src/nlp_model/worker.js', function_name='anonymous_db_error_handler'), parameters=[ParameterInfo(name='error', type='Error', description='The error object')], return_value='void', logic_summary='Logs a database connection failure and re-throws the error.', dependencies=[], side_effects='Logs to console.', error_handling='Throws error.', complexity='utility', tags=['error_handling', 'database'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='worker.js', filepath='python_pipeline/input_code/backend/src/nlp_model/worker.js', function_name='anonymous_job_processor'), parameters=[ParameterInfo(name='job', type='object', description='The job object containing data')], return_value='string', logic_summary="Processes 'analyze-review' jobs by calling the ML API, updating the review sentiment in the database, and updating Redis leaderboards.", dependencies=['axios.post', 'Review.findById', 'connection.zadd', 'connection.zincrby'], side_effects='Updates database, updates Redis.', error_handling='NONE', complexity='critical_path', tags=['worker', 'queue', 'sentiment', 'leaderboard'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='worker.js', filepath='python_pipeline/input_code/backend/src/nlp_model/worker.js', function_name='anonymous_job_completion_logger'), parameters=[ParameterInfo(name='job', type='object', description='The completed job')], return_value='void', logic_summary='Logs the completion of a job.', dependencies=[], side_effects='Logs to console.', error_handling='NONE', complexity='utility', tags=['logging', 'worker'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='worker.js', filepath='python_pipeline/input_code/backend/src/nlp_model/worker.js', function_name='anonymous_job_failure_logger'), parameters=[ParameterInfo(name='job', type='object', description='The failed job'), ParameterInfo(name='err', type='Error', description='The error encountered')], return_value='void', logic_summary='Logs the failure of a job.', dependencies=[], side_effects='Logs to console.', error_handling='NONE', complexity='utility', tags=['logging', 'worker', 'error_handling'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='app.py', filepath='python_pipeline/input_code/backend/src/nlp_model/app.py', function_name='ReviewRequest'), parameters=[], return_value='void', logic_summary='Pydantic model for validating review request input.', dependencies=[], side_effects='NONE', error_handling='NONE', complexity='utility', tags=['pydantic', 'validation'], class_purpose='Data validation schema for review requests', attributes=[ClassAttributes(name='text', type='str', description='The review text')], methods_overview=None, inheritance='BaseModel'), ChunkSummary(function_info=FunctionName(filename='app.py', filepath='python_pipeline/input_code/backend/src/nlp_model/app.py', function_name='analyze_review'), parameters=[ParameterInfo(name='request', type='ReviewRequest', description='The review request object')], return_value='str', logic_summary='Endpoint handler that calls the text analysis function.', dependencies=['analyze_text'], side_effects='NONE', error_handling='NONE', complexity='utility', tags=['api', 'nlp'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='multer.middleware.js', filepath='python_pipeline/input_code/backend/src/middlewares/multer.middleware.js', function_name='anonymous_multer_destination'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='file', type='object', description='File object'), ParameterInfo(name='cb', type='function', description='Callback function')], return_value='void', logic_summary='Sets the destination directory for uploaded files.', dependencies=[], side_effects='NONE', error_handling='NONE', complexity='utility', tags=['multer', 'middleware', 'upload'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='multer.middleware.js', filepath='python_pipeline/input_code/backend/src/middlewares/multer.middleware.js', function_name='anonymous_multer_filename'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='file', type='object', description='File object'), ParameterInfo(name='cb', type='function', description='Callback function')], return_value='void', logic_summary='Sets the filename for uploaded files to their original name.', dependencies=[], side_effects='NONE', error_handling='NONE', complexity='utility', tags=['multer', 'middleware', 'upload'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='auth.middleware.js', filepath='python_pipeline/input_code/backend/src/middlewares/auth.middleware.js', function_name='anonymous_auth_middleware'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object'), ParameterInfo(name='next', type='function', description='Next middleware function')], return_value='void', logic_summary='Authenticates users by verifying the access token from cookies or headers, and attaches the user to the request object.', dependencies=['jwt.verify', 'User.findById', 'ApiError'], side_effects='Modifies req.user.', error_handling='Throws ApiError if token is missing or invalid.', complexity='critical_path', tags=['auth', 'middleware', 'jwt'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='index.js', filepath='python_pipeline/input_code/backend/src/db/index.js', function_name='anonymous_db_connector'), parameters=[], return_value='Promise<void>', logic_summary='Connects to the MongoDB database using environment variables.', dependencies=['mongoose.connect'], side_effects='Connects to database.', error_handling='Logs failure and throws error.', complexity='critical_path', tags=['database', 'mongodb', 'connection'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='leaderboard.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/leaderboard.controller.js', function_name='anonymous_get_top_reviews'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Retrieves the top 10 reviews from the Redis leaderboard and fetches associated review details from the database.', dependencies=['connection.zrevrange', 'Review.findById', 'ApiResponse'], side_effects='NONE', error_handling='Throws ApiError if review not found.', complexity='core_logic', tags=['leaderboard', 'redis', 'reviews'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='leaderboard.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/leaderboard.controller.js', function_name='anonymous_get_review_count'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Returns the total count of reviews from the Redis leaderboard.', dependencies=['connection.zcard', 'ApiResponse'], side_effects='NONE', error_handling='NONE', complexity='utility', tags=['leaderboard', 'redis', 'count'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='leaderboard.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/leaderboard.controller.js', function_name='anonymous_get_top_worst_restaurants'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Fetches the top-rated and worst-rated restaurants from Redis and retrieves their details and a sample review from the database.', dependencies=['connection.zrevrange', 'Restaurant.findById', 'Review.findOne', 'ApiResponse'], side_effects='NONE', error_handling='Throws ApiError if leaderboard is empty.', complexity='core_logic', tags=['leaderboard', 'restaurants', 'analytics'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='user.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/user.controller.js', function_name='anonymous_register_user'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Registers a new user, uploads their profile photo to Cloudinary, and saves the user to the database.', dependencies=['User.findOne', 'uploadOnCloudinary', 'User.create', 'ApiResponse'], side_effects='Creates user in DB, uploads file to Cloudinary.', error_handling='Throws ApiError for validation failures or upload errors.', complexity='critical_path', tags=['user', 'registration', 'cloudinary'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='user.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/user.controller.js', function_name='anonymous_login_user'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Authenticates a user, generates access and refresh tokens, and sets them as secure cookies.', dependencies=['User.findOne', 'isUser.isPasswordCorrect', 'isUser.generateAccessToken', 'isUser.generateRefreshToken', 'ApiResponse'], side_effects='Sets cookies, updates user refresh token in DB.', error_handling='Throws ApiError for invalid credentials.', complexity='critical_path', tags=['user', 'login', 'authentication'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='user.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/user.controller.js', function_name='anonymous_logout_user'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Logs out the user by clearing the refresh token in the database and clearing the authentication cookies.', dependencies=['User.findByIdAndUpdate', 'ApiResponse'], side_effects='Clears cookies, updates DB.', error_handling='NONE', complexity='core_logic', tags=['user', 'logout', 'authentication'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='user.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/user.controller.js', function_name='anonymous_get_user_restaurants'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Retrieves all restaurants owned by a specific user using aggregation.', dependencies=['User.findById', 'Restaurant.aggregate', 'ApiResponse'], side_effects='NONE', error_handling='Throws ApiError if user not found.', complexity='core_logic', tags=['user', 'restaurants', 'aggregation'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='restaurant.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/restaurant.controller.js', function_name='anonymous_register_restaurant'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Registers a new restaurant, uploads the profile photo to Cloudinary, and saves the restaurant to the database.', dependencies=['Restaurant.findOne', 'uploadOnCloudinary', 'Restaurant.create', 'ApiResponse'], side_effects='Creates restaurant in DB, uploads file to Cloudinary.', error_handling='Throws ApiError for validation or upload failures.', complexity='critical_path', tags=['restaurant', 'registration', 'cloudinary'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='restaurant.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/restaurant.controller.js', function_name='anonymous_get_restaurant_owner'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Fetches the owner ID of a specific restaurant.', dependencies=['Restaurant.findById', 'ApiResponse'], side_effects='NONE', error_handling='NONE', complexity='utility', tags=['restaurant', 'owner'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='restaurant.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/restaurant.controller.js', function_name='anonymous_update_restaurant'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Updates restaurant details, including profile photo upload to Cloudinary, ensuring the requester is the owner.', dependencies=['Restaurant.findById', 'uploadOnCloudinary', 'ApiResponse'], side_effects='Updates restaurant in DB, uploads file to Cloudinary.', error_handling='Throws ApiError if restaurant not found or unauthorized.', complexity='core_logic', tags=['restaurant', 'update', 'authorization'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='restaurant.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/restaurant.controller.js', function_name='anonymous_get_restaurant_reviews'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Retrieves all reviews for a restaurant using aggregation, including user details for each review.', dependencies=['Restaurant.aggregate', 'ApiResponse'], side_effects='NONE', error_handling='Throws ApiError if restaurant not found.', complexity='core_logic', tags=['restaurant', 'reviews', 'aggregation'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='review.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/review.controller.js', function_name='anonymous_create_review'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary="Creates a new review, sets its status to 'Pending', and adds it to the analysis queue.", dependencies=['Review.create', 'reviewQueue.add', 'ApiResponse'], side_effects='Creates review in DB, adds job to queue.', error_handling='Throws ApiError for validation failures.', complexity='critical_path', tags=['review', 'queue', 'nlp'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='review.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/review.controller.js', function_name='anonymous_update_review'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary="Updates an existing review, resets its status to 'Pending', and re-adds it to the analysis queue.", dependencies=['Review.findById', 'reviewQueue.add', 'ApiResponse'], side_effects='Updates review in DB, adds job to queue.', error_handling='Throws ApiError for validation or authorization failures.', complexity='core_logic', tags=['review', 'update', 'queue'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='review.controller.js', filepath='python_pipeline/input_code/backend/src/controllers/review.controller.js', function_name='anonymous_delete_review'), parameters=[ParameterInfo(name='req', type='object', description='Request object'), ParameterInfo(name='res', type='object', description='Response object')], return_value='Promise<void>', logic_summary='Deletes a review and removes it from the Redis leaderboards.', dependencies=['Review.findById', 'Review.findByIdAndDelete', 'connection.zrem', 'ApiResponse'], side_effects='Deletes from DB, removes from Redis.', error_handling='Throws ApiError for validation or authorization failures.', complexity='core_logic', tags=['review', 'delete', 'redis'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='ApiResponse.js', filepath='python_pipeline/input_code/backend/src/utils/ApiResponse.js', function_name='ApiResponse'), parameters=[ParameterInfo(name='statusCode', type='number', description='HTTP status code'), ParameterInfo(name='data', type='any', description='Response payload'), ParameterInfo(name='message', type='string', description='Response message')], return_value='void', logic_summary='Standardized API response class.', dependencies=[], side_effects='NONE', error_handling='NONE', complexity='utility', tags=['api', 'response', 'utility'], class_purpose='Standardized API response structure', attributes=[ClassAttributes(name='statusCode', type='number', description='HTTP status code'), ClassAttributes(name='data', type='any', description='Response data'), ClassAttributes(name='message', type='string', description='Response message'), ClassAttributes(name='success', type='boolean', description='Success status')], methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='ApiError.js', filepath='python_pipeline/input_code/backend/src/utils/ApiError.js', function_name='ApiError'), parameters=[ParameterInfo(name='statusCode', type='number', description='HTTP status code'), ParameterInfo(name='message', type='string', description='Error message'), ParameterInfo(name='error', type='array', description='Error details'), ParameterInfo(name='stack', type='string', description='Stack trace')], return_value='void', logic_summary='Standardized API error class extending the base Error class.', dependencies=[], side_effects='NONE', error_handling='NONE', complexity='utility', tags=['api', 'error', 'utility'], class_purpose='Standardized API error handling', attributes=[ClassAttributes(name='statusCode', type='number', description='HTTP status code'), ClassAttributes(name='error', type='array', description='Error details')], methods_overview=None, inheritance='Error'), ChunkSummary(function_info=FunctionName(filename='cloudinary.js', filepath='python_pipeline/input_code/backend/src/utils/cloudinary.js', function_name='anonymous_cloudinary_uploader'), parameters=[ParameterInfo(name='filepath', type='string', description='Path to the local file')], return_value='Promise<object>', logic_summary='Uploads a file to Cloudinary and deletes the local file after the upload attempt.', dependencies=['cloudinary.v2.uploader.upload', 'fs.unlink', 'ApiError'], side_effects='Uploads to Cloudinary, deletes local file.', error_handling='Throws ApiError on failure.', complexity='utility', tags=['cloudinary', 'upload', 'file_system'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None), ChunkSummary(function_info=FunctionName(filename='asyncHandler.js', filepath='python_pipeline/input_code/backend/src/utils/asyncHandler.js', function_name='anonymous_async_handler'), parameters=[ParameterInfo(name='fn', type='function', description='The async controller function')], return_value='function', logic_summary='Higher-order function that wraps async controller functions to handle errors automatically.', dependencies=[], side_effects='NONE', error_handling='Catches errors and sends standardized JSON error response.', complexity='utility', tags=['middleware', 'async', 'error_handling'], class_purpose=None, attributes=None, methods_overview=None, inheritance=None)]
    
    text_chunks = [chunk_to_vector_text(chunk) for chunk in chunks_with_summary]
    embedding_model = SentenceTransformer("nomic-ai/CodeRankEmbed",trust_remote_code=True)
    embeddings_source_code = embedding_model.encode(
                        text_chunks,
                        batch_size=8,        
                        show_progress_bar=True
                    )
    print(f"{len(chunks_with_summary)} chunks, embedding shape {embeddings_source_code.shape}")

    embeddings = embeddings_source_code
    
    ollama_flag = False
    db_flag = False
    name_collection = "test_source_code_collection"
    add_collection(chunks_with_summary,text_chunks,embeddings,metadatas,ollama_flag,db_flag,name_collection)
