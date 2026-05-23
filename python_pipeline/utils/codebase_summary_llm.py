from langchain_google_genai import ChatGoogleGenerativeAI
import time
from pydantic import BaseModel,Field
from typing import Optional    
from .schema.shared_schema import FileLevelSummaryList
from .schema.chunk_schema import *
from .schema.shared_schema import *
from pprint import pprint
from transformers import AutoTokenizer
from collections import defaultdict
from .models_support.load_model_byok import load_model_byok
from .models_support.max_token_computation  import load_max_token
from langchain_core.rate_limiters import InMemoryRateLimiter
from .models_support.tokenizer_loader import load_tokenizer
from .models_support.load_model_ollama import load_model_ollama


def call_agent(chunks,model_name,api_key,ollama_flag):
    SYSTEM_PROMPT = """
                    You are an expert software architect performing hierarchical codebase-level synthesis.

                    You will receive a PARTIAL set of MODULE-LEVEL summaries belonging to the SAME repository/codebase.

                    IMPORTANT:
                    - The entire repository may not fit into a single request
                    - Module summaries may therefore be processed in MULTIPLE batches
                    - Each request may contain only a subset of all modules in the system

                    Your task is to generate a PARTIAL CODEBASE SUMMARY representing the architectural understanding derivable from ONLY the currently provided module summaries.

                    Your responsibilities:
                    - Infer the high-level purpose of the currently visible system components
                    - Identify architectural patterns and subsystem interactions
                    - Explain execution/data flow across visible modules
                    - Detect shared infrastructure, integrations, and contracts
                    - Compress redundant architectural information
                    - Infer platform capabilities from combined module behavior
                    - Preserve important scalability, security, and operational details
                    - Produce retrieval-friendly architectural synthesis

                    IMPORTANT SYNTHESIS RULES:
                    - Treat all provided module summaries as belonging to the SAME repository
                    - Do NOT summarize modules individually
                    - Merge related workflows into unified architectural understanding
                    - Infer relationships between modules when possible
                    - Focus on system-level behavior rather than implementation details
                    - Do not invent missing modules or integrations
                    - If the repository appears incomplete, summarize only what is observable
                    - Preserve architectural terminology and technical precision

                    OUTPUT REQUIREMENTS:
                    - Return ONLY structured output
                    - Do not include markdown
                    - Do not explain reasoning
                    - Keep summaries dense, technical, and retrieval-friendly
                    - Generate a PARTIAL repository-level understanding from the provided modules only
                    """
    try:
        if ollama_flag == True:
            llm = load_model_ollama(model_name)
        else:
            llm = load_model_byok(model_name,api_key)
        structured_llm = llm.with_structured_output(CodebaseSummary)
        messages = [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            ("human", f"Analyze the given chunks and generate the answer according to the system prompt only {chunks}"),
        ]
        print(f"Successfully imported and structured the model = {model_name} for codebase summary")
        ai_msg = structured_llm.invoke(messages)
        return ai_msg
    
    except Exception as e:
        print(f"Agent for source code analysis failed!! as  {e}")

def generate_codebase_summary(chunks_with_summary, model_name, api_key, ollama_flag):
    MAX_TOKEN_LIMIT = load_max_token(model_name, ollama_flag)
    print(f"MAX_TOKEN_LIMIT = {MAX_TOKEN_LIMIT}")

    tokenizer = load_tokenizer(model_name)
    current_request_chunks_size = 0
    give_chunks = []
    partial_result = None   # carries forward previous codebase summary

    try:
        for chunk in chunks_with_summary:
            str_chunk = str(chunk)
            chunk_tokens = len(tokenizer.encode(str_chunk))
            current_request_chunks_size += chunk_tokens

            if current_request_chunks_size >= MAX_TOKEN_LIMIT:
                partial_result = call_agent(give_chunks, model_name, api_key, ollama_flag)

                if ollama_flag:
                    print("Waiting 10 seconds....")
                    time.sleep(10)
                    print("Done waiting 10 seconds!!")
                else:
                    print("Waiting 60 seconds....")
                    time.sleep(60)
                    print("Done waiting 60 seconds!!")

                # next batch carries forward the partial result
                result_tokens = len(tokenizer.encode(str(partial_result)))
                current_request_chunks_size = result_tokens + chunk_tokens
                give_chunks = [partial_result, chunk]   # partial summary + new chunk
            else:
                give_chunks.append(chunk)

        # final call
        if give_chunks:
            partial_result = call_agent(give_chunks, model_name, api_key, ollama_flag)

        return partial_result   # single CodebaseSummary object

    except Exception as e:
        print(f"Something went wrong while generating codebase summary: {e}")


if __name__ =="__main__":

    chunks_with_summary = [ModuleLevelSummary(filepath='python_pipeline/input_code/backend/src', module_name='backend/src', module_purpose='A full-stack backend system providing user authentication, restaurant management, review processing, and sentiment analysis via an integrated ML pipeline.', architectural_role='core_platform', key_files=['index.js', 'controllers/review.controller.js', 'nlp_model/worker.js', 'model/user.model.js', 'middlewares/auth.middleware.js'], key_symbols=[FunctionReference(symbol_id='python_pipeline/input_code/backend/src/index.js::anonymous_server_initializer', role='Orchestrates database, Redis, and HTTP server startup.'), FunctionReference(symbol_id='python_pipeline/input_code/backend/src/controllers/review.controller.js::anonymous_create_review', role='Entry point for review submission, triggering asynchronous sentiment analysis.'), FunctionReference(symbol_id='python_pipeline/input_code/backend/src/nlp_model/worker.js::anonymous_job_processor', role='Background worker consuming review jobs, performing ML inference, and updating persistent state.'), FunctionReference(symbol_id='python_pipeline/input_code/backend/src/model/user.model.js::anonymous_access_token_generator', role='Handles secure session management via JWT.')], execution_flow='Requests enter via controllers, are validated by middlewares, and interact with MongoDB for persistence. Review submissions trigger an asynchronous flow where a background worker consumes jobs, performs NLP inference via the model_runner, and updates both MongoDB and Redis for real-time analytics.', responsibilities=['User authentication and session management', 'Restaurant CRUD operations', 'Review lifecycle management', 'Asynchronous sentiment analysis processing', 'Real-time leaderboard and analytics generation'], inbound_dependencies=[], outbound_dependencies=[DependencyReference(filepath='python_pipeline/input_code/backend/src/db/index.js', purpose='Provides MongoDB connectivity via Mongoose.'), DependencyReference(filepath='python_pipeline/input_code/backend/src/utils/cloudinary.js', purpose='External media storage integration.')], shared_models_or_contracts=['User schema', 'Review status (Pending/Processed)', 'ApiResponse', 'ApiError'], cross_cutting_concerns=['JWT-based authentication', 'Global error handling via asyncHandler', 'Standardized API responses', 'File upload management via Multer/Cloudinary'], scalability_notes='Uses a background worker pattern for CPU-intensive NLP tasks to prevent blocking the main event loop. Redis is utilized for caching and leaderboard state management to improve read performance.', failure_points=['Database connection failures', 'ML model inference latency', 'Queue processing bottlenecks', 'Cloudinary upload timeouts'], security_model='Implements JWT for stateless authentication, bcrypt for password hashing, and middleware-based route protection.', integration_points=['MongoDB (Persistence)', 'Redis (Caching/Queues/Leaderboards)', 'Cloudinary (Media Storage)', 'ML Model (Sentiment Analysis)'], observability='Uses console logging for job status and error tracking; relies on standardized error classes for API visibility.', business_domain='Restaurant Review and Analytics Platform', tags=['backend', 'nlp', 'mongodb', 'redis', 'authentication', 'micro-service-pattern'], module_complexity='critical_infrastructure')]
    
    api_key = "AIzaSyCCLp1a-C0l4Jh360lzjtM20Vm3AIHtVeE"
    model_name="gemini-3.1-flash-lite-preview"
    # model_name="qwen2.5-coder:7b"
    ollama_flag = False
    ai_msg = generate_codebase_summary(chunks_with_summary,model_name,api_key,ollama_flag)
    print((ai_msg))
    