from langchain_google_genai import ChatGoogleGenerativeAI
import time
from pydantic import BaseModel,Field
from typing import Optional    
from schema.shared_schema import FileLevelSummaryList
from schema.chunk_schema import *
from schema.shared_schema import *
from pprint import pprint
from transformers import AutoTokenizer
from collections import defaultdict
from models_support.load_model_byok import load_model_byok
from models_support.max_token_computation import load_max_token
from langchain_core.rate_limiters import InMemoryRateLimiter
from models_support.tokenizer_loader import load_tokenizer

def load_tokenizer():
    return AutoTokenizer.from_pretrained("nomic-ai/CodeRankEmbed", trust_remote_code=True)

def call_agent(chunks,model_name,api_key,ollama_flag):
    SYSTEM_PROMPT = """
                        You are an expert software architect and repository analysis system.

                        Your task is to generate a MODULE-LEVEL architectural summary from multiple FILE summaries belonging to the SAME module/package/subsystem.

                        You will receive:
                        1. Module/package metadata
                        2. File-level summaries
                        3. Dependency relationships
                        4. Optional call graph or architecture graph information

                        Your job is to:
                        - Understand the responsibility of the entire module
                        - Infer subsystem architecture
                        - Explain how files collaborate together
                        - Identify the role of the module inside the overall system
                        - Detect major execution flows and integration points
                        - Summarize the business/domain purpose of the module
                        - Preserve important architectural semantics

                        IMPORTANT RULES:

                        - Treat all file summaries as part of ONE logical subsystem/module
                        - Focus on architecture, not implementation details
                        - Do NOT repeat individual function summaries unless critical
                        - Infer module boundaries and responsibilities
                        - Explain how files interact with each other
                        - Identify:
                        - orchestration layers
                        - data flow
                        - service boundaries
                        - shared models/contracts
                        - infrastructure concerns
                        - integrations
                        - state management patterns
                        - security boundaries
                        - async/event processing

                        - Mention important dependencies only if they affect architecture
                        - Compress repetitive implementation details
                        - Prefer subsystem understanding over low-level code explanations
                        - Detect patterns such as:
                        - layered architecture
                        - event-driven design
                        - microservices
                        - repository pattern
                        - middleware pipelines
                        - CQRS
                        - pub/sub
                        - MVC
                        - React component hierarchy

                        - Explain:
                        - what enters the module
                        - what happens internally
                        - what leaves the module

                        - Identify critical files/components/services
                        - Mention scalability/performance concerns if visible
                        - Mention operational concerns like logging, retries, queues, caching if important

                        IMPORTANT:
                        - Keep the summary retrieval-friendly for RAG systems
                        - Prefer concise but semantically dense explanations
                        - Avoid vague wording
                        - Preserve meaningful technical terminology

                        OUTPUT REQUIREMENTS:
                        - Return ONLY structured output
                        - Do not include markdown
                        - Do not explain your reasoning
                        - Keep summaries dense, architectural, and optimized for semantic retrieval

                    """
    try:
        if ollama_flag == True:
            llm = load_model_ollama(model_name,api_key)
        else:
            llm = load_model_byok(model_name,api_key)
        structured_llm = llm.with_structured_output(ChunkSummaryList)
        messages = [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            ("human", f"Analyze the given chunks and generate the answer according to the system prompt only {chunks}"),
        ]
        print(f"Successfully imported and structured the model = {model_name}")
        ai_msg = structured_llm.invoke(messages)
        return ai_msg
    
    except Exception as e:
        print(f"Agent for source code analysis failed!! as  {e}")

def generate_module_summary(chunks_with_summary,model_name,api_key,ollama_flag):
    MAX_TOKEN_LIMIT =  load_max_token(model_name)
    print(f"MAX_TOKEN_LIMIT = {MAX_TOKEN_LIMIT}")
    group_by_module_name = defaultdict(list)
    for chunk in (chunks_with_summary):
        module_name = chunk.module_name
        group_by_module_name[module_name].append(chunk)

    current_request_chunks_size = 0
    give_chunks = []
    ai_msg = []
    try :
        tokenizer = load_tokenizer()
        for module_name,file_chunks in (group_by_module_name.items()):
            str_file_chunks = "".join(map(str,file_chunks))
            current_request_chunks_size += len(tokenizer.encode(str_file_chunks))
            if current_request_chunks_size >= MAX_TOKEN_LIMIT:
                result = call_agent(give_chunks,model_name,api_key,ollama_flag)
                ai_msg.extend(result.summaries)
                print("Waiting 60 seconds....")
                time.sleep(60)
                print("Done waiting 60 seconds!!")
                current_request_chunks_size = len(tokenizer.encode(file_chunks))
                give_chunks = []
            give_chunks.append(file_chunks)

        if give_chunks:
            result = call_agent(give_chunks,model_name,api_key,ollama_flag)
            ai_msg.extend(result.summaries)
        return ai_msg
    except Exception as e:
        print(f"Something went wrong while initiating code analysis via LLM as {e}")


if __name__ =="__main__":
   
    chunks_with_summary = [FileLevelSummary(filename='conditional_calc_agent.py', filepath='../input_code/gen/conditional_calc_agent.py', module_name='gen', file_purpose='Defines a stateful conditional calculation agent workflow using nodes for arithmetic operations and routing.', architecture_role='orchestrator', important_symbols=[FunctionReference(symbol_id='conditional_calc_agent.py::StateAgent', role="TypedDict defining the agent's state structure."), FunctionReference(symbol_id='conditional_calc_agent.py::router', role='Determines the next node in the workflow based on state.')], core_logic_flow='The agent maintains a state of numbers and operations. Nodes (add_node, sub_node) perform calculations, while the router directs the flow, and end_node outputs the final result.', internal_dependencies=[], external_dependencies=[], public_api=['StateAgent', 'add_node', 'sub_node', 'end_node', 'router'], side_effects=['Modifies state object', 'Prints to stdout'], error_handling_strategy='None implemented.', state_management='State is passed through nodes as a TypedDict.', security_considerations=None, performance_notes=None, tags=['state', 'agent', 'workflow'], related_files=[], overall_complexity='feature_logic'), FileLevelSummary(filename='values_processor.py', filepath='../input_code/gen/values_processor.py', module_name='gen', file_purpose='Processes lists of integers using specified mathematical operations.', architecture_role='service', important_symbols=[FunctionReference(symbol_id='values_processor.py::process_values', role='Performs math operations on a list of values.')], core_logic_flow='Accepts an AgentState, performs either addition or multiplication on the values list, and updates the result field.', internal_dependencies=[], external_dependencies=['math'], public_api=['AgentState', 'process_values'], side_effects=['Modifies state object'], error_handling_strategy='None implemented.', state_management='State is passed as a TypedDict.', security_considerations=None, performance_notes=None, tags=['math', 'processing'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='hello_world_agent.py', filepath='../input_code/gen/hello_world_agent.py', module_name='gen', file_purpose='Simple agent for demonstrating state modification.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='hello_world_agent.py::greeter_node', role='Appends text to the state message.')], core_logic_flow='Takes an AgentState and updates the message attribute.', internal_dependencies=[], external_dependencies=[], public_api=['AgentState', 'greeter_node'], side_effects=['Modifies state object'], error_handling_strategy='None implemented.', state_management='State is passed as a TypedDict.', security_considerations=None, performance_notes=None, tags=['greeting', 'agent'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='App.jsx', filepath='../input_code/frontend/src/App.jsx', module_name='frontend', file_purpose='Main entry point for the React application.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='App.jsx::App', role='Root component rendering the main UI.')], core_logic_flow='Initializes local state and renders the main application layout.', internal_dependencies=[], external_dependencies=['react'], public_api=['App'], side_effects=['Updates local state'], error_handling_strategy='None.', state_management='React useState.', security_considerations=None, performance_notes=None, tags=['react', 'ui'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='Layout.jsx', filepath='../input_code/frontend/src/Layout.jsx', module_name='frontend', file_purpose='Defines the global page layout structure.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='Layout.jsx::Layout', role='Wraps content with Header and Footer.')], core_logic_flow='Renders Header, Outlet for nested routes, and Footer.', internal_dependencies=['Header.jsx', 'Footer.jsx'], external_dependencies=['react-router-dom'], public_api=['Layout'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['layout', 'routing'], related_files=['Header.jsx', 'Footer.jsx'], overall_complexity='utility'), FileLevelSummary(filename='SignUp.jsx', filepath='../input_code/frontend/src/pages/SignUp.jsx', module_name='frontend', file_purpose='Handles user registration logic.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='SignUp.jsx::SignUp', role='Registration form component.')], core_logic_flow='Manages form state, validates inputs, uploads profile photo, and submits data to the backend API.', internal_dependencies=[], external_dependencies=['axios', 'react-router-dom'], public_api=['SignUp'], side_effects=['API call', 'Navigation'], error_handling_strategy='Try-catch block for API errors.', state_management='React useState.', security_considerations='Password validation.', performance_notes=None, tags=['auth', 'signup'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='Review.jsx', filepath='../input_code/frontend/src/pages/Review.jsx', module_name='frontend', file_purpose='Displays restaurant reviews and handles review submission.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='Review.jsx::Review', role='Review page component.')], core_logic_flow='Fetches restaurant data on mount, displays reviews, and provides a form to post new reviews.', internal_dependencies=[], external_dependencies=['axios', 'react-router-dom'], public_api=['Review'], side_effects=['API call'], error_handling_strategy='None.', state_management='React useState/useEffect.', security_considerations=None, performance_notes=None, tags=['review', 'ui'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='Dashboard.jsx', filepath='../input_code/frontend/src/pages/Dashboard.jsx', module_name='frontend', file_purpose='Displays restaurant leaderboards.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='Dashboard.jsx::Dashboard', role='Dashboard page component.')], core_logic_flow='Fetches top and worst-rated restaurants from the API and renders them using DashCard components.', internal_dependencies=['DashCard.jsx'], external_dependencies=['axios'], public_api=['Dashboard'], side_effects=['API call'], error_handling_strategy='Try-catch block for API errors.', state_management='React useState/useEffect.', security_considerations=None, performance_notes=None, tags=['dashboard', 'leaderboard'], related_files=['DashCard.jsx'], overall_complexity='core_logic'), FileLevelSummary(filename='Login.jsx', filepath='../input_code/frontend/src/pages/Login.jsx', module_name='frontend', file_purpose='Handles user authentication.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='Login.jsx::Login', role='Login form component.')], core_logic_flow='Manages login form state, calls auth API, updates AuthContext, and redirects to dashboard.', internal_dependencies=['AuthContext.jsx'], external_dependencies=['axios', 'react-router-dom'], public_api=['Login'], side_effects=['API call', 'Cookie management'], error_handling_strategy='Try-catch block for API errors.', state_management='AuthContext, React useState.', security_considerations='Authentication context usage.', performance_notes=None, tags=['auth', 'login'], related_files=['AuthContext.jsx'], overall_complexity='critical_path'), FileLevelSummary(filename='Footer.jsx', filepath='../input_code/frontend/src/components/Footer.jsx', module_name='frontend', file_purpose='Displays site footer.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='Footer.jsx::Footer', role='Footer UI component.')], core_logic_flow='Renders static links.', internal_dependencies=[], external_dependencies=['react-router-dom'], public_api=['Footer'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['footer', 'ui'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='AuthContext.jsx', filepath='../input_code/frontend/src/components/AuthContext.jsx', module_name='frontend', file_purpose='Manages global authentication state.', architecture_role='provider', important_symbols=[FunctionReference(symbol_id='AuthContext.jsx::AuthProvider', role='Context provider for auth state.'), FunctionReference(symbol_id='AuthContext.jsx::anonymous_context_hook', role='Hook to access auth state.')], core_logic_flow='Provides user state and login/logout methods to the component tree.', internal_dependencies=[], external_dependencies=['react'], public_api=['AuthProvider', 'anonymous_context_hook'], side_effects=[], error_handling_strategy='None.', state_management='React Context, useState.', security_considerations='Centralized auth state management.', performance_notes=None, tags=['auth', 'context'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='Header.jsx', filepath='../input_code/frontend/src/components/Header.jsx', module_name='frontend', file_purpose='Displays site navigation and auth status.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='Header.jsx::Header', role='Header UI component.')], core_logic_flow='Uses AuthContext to conditionally render login/logout links.', internal_dependencies=['AuthContext.jsx'], external_dependencies=['react-router-dom'], public_api=['Header'], side_effects=[], error_handling_strategy='None.', state_management='AuthContext.', security_considerations=None, performance_notes=None, tags=['header', 'navigation'], related_files=['AuthContext.jsx'], overall_complexity='utility'), FileLevelSummary(filename='DashCard.jsx', filepath='../input_code/frontend/src/components/DashCard.jsx', module_name='frontend', file_purpose='Displays restaurant summary card.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='DashCard.jsx::DashCard', role='Restaurant card component.')], core_logic_flow='Renders restaurant details and a link to the review page.', internal_dependencies=[], external_dependencies=['react-router-dom'], public_api=['DashCard'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['card', 'ui'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='index.js', filepath='../input_code/backend/src/index.js', module_name='backend', file_purpose='Entry point for the backend server.', architecture_role='orchestrator', important_symbols=[FunctionReference(symbol_id='index.js::anonymous_server_initializer', role='Initializes DB and starts server.')], core_logic_flow='Connects to MongoDB, starts the Express server, and initializes Redis listeners.', internal_dependencies=['db/index.js'], external_dependencies=['express', 'mongoose'], public_api=[], side_effects=['Starts server', 'Connects to DB'], error_handling_strategy='Catch block for DB connection failure.', state_management=None, security_considerations=None, performance_notes=None, tags=['server', 'init'], related_files=['db/index.js'], overall_complexity='critical_path'), FileLevelSummary(filename='user.model.js', filepath='../input_code/backend/src/model/user.model.js', module_name='backend', file_purpose='Defines the User schema and authentication methods.', architecture_role='schema', important_symbols=[FunctionReference(symbol_id='user.model.js::anonymous_password_hasher', role='Middleware to hash passwords.'), FunctionReference(symbol_id='user.model.js::anonymous_password_checker', role='Compares passwords.'), FunctionReference(symbol_id='user.model.js::anonymous_access_token_generator', role='Generates JWT access token.')], core_logic_flow='Provides Mongoose middleware for password hashing and methods for token generation and password verification.', internal_dependencies=[], external_dependencies=['mongoose', 'bcrypt', 'jsonwebtoken'], public_api=['User'], side_effects=['Hashes password'], error_handling_strategy='None.', state_management=None, security_considerations='Password hashing, JWT token generation.', performance_notes=None, tags=['auth', 'model'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='testClient.js', filepath='../input_code/backend/src/nlp_model/testClient.js', module_name='backend', file_purpose='Utility for testing the NLP sentiment analysis API.', architecture_role='client', important_symbols=[FunctionReference(symbol_id='testClient.js::analyzeReview', role='Sends text to ML API.')], core_logic_flow='Sends a sample review to the sentiment analysis endpoint and logs the result.', internal_dependencies=[], external_dependencies=['axios'], public_api=['analyzeReview'], side_effects=['API call'], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['nlp', 'test'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='model_runner.py', filepath='../input_code/backend/src/nlp_model/model_runner.py', module_name='backend', file_purpose='Executes sentiment analysis using a pre-trained model.', architecture_role='service', important_symbols=[FunctionReference(symbol_id='model_runner.py::analyze_text', role='Predicts sentiment from text.')], core_logic_flow='Tokenizes input and runs it through a model to return a sentiment label.', internal_dependencies=[], external_dependencies=[], public_api=['analyze_text'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes='Uses pre-trained model.', tags=['nlp', 'sentiment'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='worker.js', filepath='../input_code/backend/src/nlp_model/worker.js', module_name='backend', file_purpose='Background worker for processing sentiment analysis jobs.', architecture_role='worker', important_symbols=[FunctionReference(symbol_id='worker.js::anonymous_job_processor', role='Processes sentiment analysis jobs.')], core_logic_flow='Listens for jobs, performs sentiment analysis, updates DB, and updates Redis leaderboards.', internal_dependencies=[], external_dependencies=['axios'], public_api=[], side_effects=['DB update', 'Redis update'], error_handling_strategy='Logs and throws errors.', state_management=None, security_considerations=None, performance_notes='Background job processing.', tags=['worker', 'nlp'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='app.py', filepath='../input_code/backend/src/nlp_model/app.py', module_name='backend', file_purpose='API endpoint for sentiment analysis.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='app.py::analyze_review', role='Endpoint handler.')], core_logic_flow='Receives review text, calls analyze_text, and returns sentiment.', internal_dependencies=['model_runner.py'], external_dependencies=['pydantic'], public_api=['analyze_review'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['api', 'nlp'], related_files=['model_runner.py'], overall_complexity='utility'), FileLevelSummary(filename='multer.middleware.js', filepath='../input_code/backend/src/middlewares/multer.middleware.js', module_name='backend', file_purpose='Configures file upload middleware.', architecture_role='middleware', important_symbols=[FunctionReference(symbol_id='multer.middleware.js::anonymous_multer_destination', role='Sets upload destination.')], core_logic_flow='Configures multer storage destination and filename.', internal_dependencies=[], external_dependencies=['multer'], public_api=[], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['middleware', 'upload'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='auth.middleware.js', filepath='../input_code/backend/src/middlewares/auth.middleware.js', module_name='backend', file_purpose='Authenticates requests via JWT.', architecture_role='middleware', important_symbols=[FunctionReference(symbol_id='auth.middleware.js::anonymous_auth_middleware', role='Verifies JWT token.')], core_logic_flow='Extracts token from request, verifies it, and attaches user to request object.', internal_dependencies=['utils/ApiError.js'], external_dependencies=['jsonwebtoken'], public_api=[], side_effects=['Modifies request object'], error_handling_strategy='Throws ApiError if invalid.', state_management=None, security_considerations='JWT verification.', performance_notes=None, tags=['auth', 'middleware'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='index.js', filepath='../input_code/backend/src/db/index.js', module_name='backend', file_purpose='Database connection initialization.', architecture_role='config', important_symbols=[FunctionReference(symbol_id='index.js::anonymous_db_connector', role='Connects to MongoDB.')], core_logic_flow='Uses mongoose to connect to the database URI.', internal_dependencies=[], external_dependencies=['mongoose'], public_api=[], side_effects=['Connects to DB'], error_handling_strategy='Catch block for connection failure.', state_management=None, security_considerations=None, performance_notes=None, tags=['db', 'mongodb'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='leaderboard.controller.js', filepath='../input_code/backend/src/controllers/leaderboard.controller.js', module_name='backend', file_purpose='Handles leaderboard data retrieval.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='leaderboard.controller.js::anonymous_get_top_and_worst_restaurants', role='Fetches leaderboard data.')], core_logic_flow='Queries Redis for leaderboard data and aggregates details from MongoDB.', internal_dependencies=['utils/ApiResponse.js', 'utils/ApiError.js'], external_dependencies=[], public_api=[], side_effects=[], error_handling_strategy='Throws ApiError.', state_management=None, security_considerations=None, performance_notes='Uses Redis for fast leaderboard access.', tags=['leaderboard', 'controller'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='user.controller.js', filepath='../input_code/backend/src/controllers/user.controller.js', module_name='backend', file_purpose='Handles user authentication and profile management.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='user.controller.js::anonymous_register_user', role='Registers user.'), FunctionReference(symbol_id='user.controller.js::anonymous_login_user', role='Authenticates user.')], core_logic_flow='Handles registration (with photo upload), login (with token generation), and logout.', internal_dependencies=['utils/ApiResponse.js', 'utils/ApiError.js', 'utils/cloudinary.js'], external_dependencies=[], public_api=[], side_effects=['DB write', 'Cloudinary upload', 'Cookie management'], error_handling_strategy='Throws ApiError.', state_management=None, security_considerations='Authentication, token management.', performance_notes=None, tags=['user', 'auth'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='restaurant.controller.js', filepath='../input_code/backend/src/controllers/restaurant.controller.js', module_name='backend', file_purpose='Handles restaurant registration and management.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='restaurant.controller.js::anonymous_register_restaurant', role='Registers restaurant.')], core_logic_flow='Handles restaurant creation, updates, and review retrieval.', internal_dependencies=['utils/ApiResponse.js', 'utils/ApiError.js', 'utils/cloudinary.js'], external_dependencies=[], public_api=[], side_effects=['DB write', 'Cloudinary upload'], error_handling_strategy='Throws ApiError.', state_management=None, security_considerations='Ownership validation.', performance_notes=None, tags=['restaurant', 'controller'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='review.controller.js', filepath='../input_code/backend/src/controllers/review.controller.js', module_name='backend', file_purpose='Handles review creation and lifecycle.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='review.controller.js::anonymous_upload_review', role='Creates review.')], core_logic_flow='Creates/updates reviews and queues them for sentiment analysis.', internal_dependencies=['utils/ApiResponse.js', 'utils/ApiError.js'], external_dependencies=[], public_api=[], side_effects=['DB write', 'Queue job'], error_handling_strategy='Throws ApiError.', state_management=None, security_considerations=None, performance_notes='Asynchronous processing via queue.', tags=['review', 'controller'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='ApiResponse.js', filepath='../input_code/backend/src/utils/ApiResponse.js', module_name='backend', file_purpose='Standardized API response structure.', architecture_role='utility', important_symbols=[FunctionReference(symbol_id='ApiResponse.js::ApiResponse', role='Response class.')], core_logic_flow='Encapsulates status code, data, and message.', internal_dependencies=[], external_dependencies=[], public_api=['ApiResponse'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['api', 'response'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='ApiError.js', filepath='../input_code/backend/src/utils/ApiError.js', module_name='backend', file_purpose='Standardized API error structure.', architecture_role='utility', important_symbols=[FunctionReference(symbol_id='ApiError.js::ApiError', role='Error class.')], core_logic_flow='Extends Error to include status code and details.', internal_dependencies=[], external_dependencies=[], public_api=['ApiError'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['api', 'error'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='cloudinary.js', filepath='../input_code/backend/src/utils/cloudinary.js', module_name='backend', file_purpose='Handles file uploads to Cloudinary.', architecture_role='utility', important_symbols=[FunctionReference(symbol_id='cloudinary.js::anonymous_upload_to_cloudinary', role='Uploads file.')], core_logic_flow='Uploads local file to Cloudinary and deletes the local copy.', internal_dependencies=['ApiError.js'], external_dependencies=['cloudinary', 'fs'], public_api=[], side_effects=['Cloudinary upload', 'Local file deletion'], error_handling_strategy='Throws ApiError.', state_management=None, security_considerations=None, performance_notes=None, tags=['cloudinary', 'upload'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='asyncHandler.js', filepath='../input_code/backend/src/utils/asyncHandler.js', module_name='backend', file_purpose='Higher-order function for async error handling.', architecture_role='middleware', important_symbols=[FunctionReference(symbol_id='asyncHandler.js::anonymous_async_handler', role='Wraps async functions.')], core_logic_flow='Wraps controller functions to catch and handle errors automatically.', internal_dependencies=[], external_dependencies=[], public_api=[], side_effects=[], error_handling_strategy='Catches errors and sends response.', state_management=None, security_considerations=None, performance_notes=None, tags=['async', 'middleware'], related_files=[], overall_complexity='utility')]
    api_key = "AIzaSyAXR6i-o-9uHdOSxo1HCKzGhpaDxO51lQ8"
    model_name="gemini-3.1-flash-lite-preview"
    ollama_flag = False
    ai_msg = generate_module_summary(chunks_with_summary,model_name,api_key,ollama_flag)
    print(ai_msg)
    