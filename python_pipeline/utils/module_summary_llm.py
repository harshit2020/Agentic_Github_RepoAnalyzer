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
from .models_support.max_token_computation import load_max_token
from langchain_core.rate_limiters import InMemoryRateLimiter
from .models_support.tokenizer_loader import load_tokenizer
from .models_support.load_model_ollama import load_model_ollama

def load_tokenizer():
    return AutoTokenizer.from_pretrained("nomic-ai/CodeRankEmbed", trust_remote_code=True)

def call_agent(chunks,model_name,api_key,ollama_flag):
    SYSTEM_PROMPT = """
                    You are an expert software architect and repository analysis system.

                    Your task is to generate MODULE-LEVEL architectural summaries from FILE-LEVEL summaries.

                    The input MAY contain file summaries from MULTIPLE modules/packages/subsystems.

                    You will receive:
                    1. File-level summaries
                    2. Architectural metadata
                    3. Dependency relationships
                    4. Optional call graph or architecture graph information

                    Your responsibilities are to:
                    - Detect architectural module boundaries
                    - Group related files into the correct logical subsystem
                    - Generate ONE module summary per architectural module
                    - Infer subsystem responsibilities and collaboration patterns
                    - Explain how files interact together inside each module
                    - Understand the role of each module inside the overall system

                    IMPORTANT GROUPING RULES:

                    - The input may contain files from MULTIPLE unrelated modules
                    - NEVER merge unrelated architectural subsystems together
                    - Files contain:
                        - root_module
                        - optional architectural_submodule
                    - Use these fields as strong architectural grouping hints
                    - Multiple module summaries may be produced in a single run
                    - A module represents an architectural subsystem, NOT merely a folder
                    - Group files based on shared responsibilities, execution flow,
                    integrations, and architectural collaboration patterns

                    A valid module may represent:
                    - backend API system
                    - frontend UI layer
                    - authentication subsystem
                    - NLP processing pipeline
                    - analytics engine
                    - queue worker system
                    - infrastructure/runtime layer
                    - caching layer
                    - AI orchestration pipeline
                    - repository abstraction layer
                    - shared contracts/model layer

                    MODULE ANALYSIS OBJECTIVES:

                    For EACH detected module:

                    - Understand the responsibility of the subsystem
                    - Infer architectural structure and collaboration patterns
                    - Explain major execution/data/control flow
                    - Identify critical files/components/services
                    - Detect orchestration layers
                    - Detect infrastructure concerns
                    - Detect integration points
                    - Detect state management patterns
                    - Detect async/event-driven behavior
                    - Detect security boundaries
                    - Detect scalability concerns
                    - Detect operational concerns

                    IMPORTANT:

                    - Focus on architecture, NOT low-level implementation details
                    - Do NOT repeat individual function summaries unless critical
                    - Compress repetitive implementation details
                    - Preserve important architectural semantics
                    - Preserve meaningful technical terminology
                    - Prefer subsystem understanding over code explanation
                    - Mention important dependencies only if architecturally relevant

                    PATTERN DETECTION:

                    Detect and explain architectural patterns such as:
                    - layered architecture
                    - event-driven systems
                    - microservices
                    - MVC
                    - repository pattern
                    - middleware pipelines
                    - CQRS
                    - pub/sub
                    - worker queues
                    - React component hierarchy
                    - service orchestration
                    - async pipelines
                    - distributed processing
                    - caching systems

                    EXECUTION FLOW REQUIREMENTS:

                    Explain:
                    - what enters the module
                    - what happens internally
                    - what leaves the module
                    - how the module interacts with other subsystems

                    SCALABILITY + OPERATIONS:

                    Mention important operational concerns if visible:
                    - caching
                    - retries
                    - queues
                    - workers
                    - batching
                    - horizontal scaling
                    - async processing
                    - rate limiting
                    - observability
                    - monitoring
                    - logging
                    - fault tolerance

                    OUTPUT REQUIREMENTS:

                    - Return ONLY structured output
                    - Do not include markdown
                    - Do not explain reasoning
                    - Generate ONE summary per detected module
                    - Keep summaries concise but semantically dense
                    - Optimize summaries for semantic retrieval in RAG systems
                    - Avoid vague wording
                    """
    try:
        if ollama_flag == True:
            llm = load_model_ollama(model_name)
        else:
            llm = load_model_byok(model_name,api_key)
        structured_llm = llm.with_structured_output(ModuleLevelSummaryList)
        messages = [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            ("human", f"Analyze the given chunks and generate the answer according to the system prompt only {chunks}"),
        ]
        print(f"Successfully imported and structured the model = {model_name} for module summary")
        ai_msg = structured_llm.invoke(messages)
        return ai_msg
    
    except Exception as e:
        print(f"Agent for source code analysis failed!! as  {e}")

def generate_module_summary(chunks_with_summary,model_name,api_key,ollama_flag):
    MAX_TOKEN_LIMIT =  load_max_token(model_name,ollama_flag)
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
                if ollama_flag == False:
                    print("Waiting 60 seconds....")
                    time.sleep(60)
                    print("Done waiting 60 seconds!!")
                else:
                    print("Waiting 10 seconds....")
                    time.sleep(10)
                    print("Done waiting 10 seconds!!")
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

    chunks_with_summary = [FileLevelSummary(filename='conditional_calc_agent.py', filepath='../input_code/gen/conditional_calc_agent.py', module_name='agents', file_purpose='Implements a state-based conditional calculation agent workflow.', architecture_role='orchestrator', important_symbols=[FunctionReference(symbol_id='../input_code/gen/conditional_calc_agent.py::StateAgent', role='TypedDict defining the agent state structure.'), FunctionReference(symbol_id='../input_code/gen/conditional_calc_agent.py::router', role='Determines the next node in the calculation workflow.')], core_logic_flow='The agent maintains a state of numbers and operations. The router directs the flow to add_node or sub_node based on state, which perform calculations and update the state, eventually ending at end_node.', internal_dependencies=[], external_dependencies=[], public_api=['StateAgent', 'add_node', 'sub_node', 'end_node', 'router'], side_effects=['Prints state to console', 'Modifies state object'], error_handling_strategy='None implemented.', state_management=None, security_considerations=None, performance_notes=None, tags=['agent', 'workflow', 'calculation'], related_files=[], overall_complexity='feature_logic'), FileLevelSummary(filename='values_processor.py', filepath='../input_code/gen/values_processor.py', module_name='agents', file_purpose='Processes lists of integers based on a specified operation.', architecture_role='service', important_symbols=[FunctionReference(symbol_id='../input_code/gen/values_processor.py::process_values', role='Performs math operations on a list of values.')], core_logic_flow='Accepts an AgentState containing a list of values and an operation, performs the operation, and updates the result field.', internal_dependencies=[], external_dependencies=[], public_api=['AgentState', 'process_values'], side_effects=['Modifies state object'], error_handling_strategy='None implemented.', state_management=None, security_considerations=None, performance_notes=None, tags=['agent', 'math', 'processing'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='hello_world_agent.py', filepath='../input_code/gen/hello_world_agent.py', module_name='agents', file_purpose='Simple greeting agent demonstration.', architecture_role='utility', important_symbols=[FunctionReference(symbol_id='../input_code/gen/hello_world_agent.py::greeter_node', role='Appends a message to the agent state.')], core_logic_flow='Updates the message field in the AgentState.', internal_dependencies=[], external_dependencies=[], public_api=['AgentState', 'greeter_node'], side_effects=['Modifies state object'], error_handling_strategy='None implemented.', state_management=None, security_considerations=None, performance_notes=None, tags=['agent', 'greeting'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='App.jsx', filepath='../input_code/frontend/src/App.jsx', module_name='frontend', file_purpose='Main entry point for the React application.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/App.jsx::App', role='Root component rendering the application UI.')], core_logic_flow='Initializes local state and renders the main application layout.', internal_dependencies=[], external_dependencies=['react'], public_api=['App'], side_effects=['Updates local state'], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['react', 'ui'], related_files=['Layout.jsx'], overall_complexity='utility'), FileLevelSummary(filename='Layout.jsx', filepath='../input_code/frontend/src/Layout.jsx', module_name='frontend', file_purpose='Defines the global application layout.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/Layout.jsx::Layout', role='Wraps application content with Header and Footer.')], core_logic_flow='Renders Header, Outlet (for nested routes), and Footer.', internal_dependencies=['Header.jsx', 'Footer.jsx'], external_dependencies=['react-router-dom'], public_api=['Layout'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['layout', 'ui'], related_files=['App.jsx'], overall_complexity='utility'), FileLevelSummary(filename='SignUp.jsx', filepath='../input_code/frontend/src/pages/SignUp.jsx', module_name='frontend/pages', file_purpose='Handles user registration logic.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/pages/SignUp.jsx::SignUp', role='Registration form component.')], core_logic_flow='Manages form state, validates inputs, uploads profile photo, and submits registration data to the backend.', internal_dependencies=[], external_dependencies=['axios', 'react-router-dom'], public_api=['SignUp'], side_effects=['API calls', 'Navigation'], error_handling_strategy='Validates passwords and handles API error responses.', state_management=None, security_considerations=None, performance_notes=None, tags=['auth', 'form'], related_files=['Login.jsx'], overall_complexity='critical_path'), FileLevelSummary(filename='Review.jsx', filepath='../input_code/frontend/src/pages/Review.jsx', module_name='frontend/pages', file_purpose='Displays restaurant reviews and handles review submission.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/pages/Review.jsx::Review', role='Review page component.')], core_logic_flow='Fetches restaurant data on mount and provides a form for user reviews.', internal_dependencies=[], external_dependencies=['axios', 'react-router-dom'], public_api=['Review'], side_effects=['API data fetching'], error_handling_strategy='Handles loading states.', state_management=None, security_considerations=None, performance_notes=None, tags=['review', 'ui'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='Dashboard.jsx', filepath='../input_code/frontend/src/pages/Dashboard.jsx', module_name='frontend/pages', file_purpose='Displays restaurant leaderboards.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/pages/Dashboard.jsx::Dashboard', role='Dashboard page component.')], core_logic_flow='Fetches leaderboard data from the backend and renders DashCard components.', internal_dependencies=['DashCard.jsx'], external_dependencies=['axios'], public_api=['Dashboard'], side_effects=['API data fetching'], error_handling_strategy='Logs errors to console.', state_management=None, security_considerations=None, performance_notes=None, tags=['dashboard', 'leaderboard'], related_files=['DashCard.jsx'], overall_complexity='core_logic'), FileLevelSummary(filename='Login.jsx', filepath='../input_code/frontend/src/pages/Login.jsx', module_name='frontend/pages', file_purpose='Handles user authentication.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/pages/Login.jsx::Login', role='Login form component.')], core_logic_flow='Manages login form state, authenticates via AuthContext, and redirects on success.', internal_dependencies=['AuthContext.jsx'], external_dependencies=['axios', 'react-router-dom'], public_api=['Login'], side_effects=['Authentication state update', 'Navigation'], error_handling_strategy='Displays error messages for invalid credentials.', state_management=None, security_considerations=None, performance_notes=None, tags=['auth', 'login'], related_files=['SignUp.jsx', 'AuthContext.jsx'], overall_complexity='critical_path'), FileLevelSummary(filename='Footer.jsx', filepath='../input_code/frontend/src/components/Footer.jsx', module_name='frontend/components', file_purpose='Application footer component.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/components/Footer.jsx::Footer', role='Footer UI component.')], core_logic_flow='Renders static links.', internal_dependencies=[], external_dependencies=['react-router-dom'], public_api=['Footer'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['ui', 'footer'], related_files=['Layout.jsx'], overall_complexity='utility'), FileLevelSummary(filename='AuthContext.jsx', filepath='../input_code/frontend/src/components/AuthContext.jsx', module_name='frontend/components', file_purpose='Manages global authentication state.', architecture_role='provider', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/components/AuthContext.jsx::AuthProvider', role='Context provider for auth state.'), FunctionReference(symbol_id='../input_code/frontend/src/components/AuthContext.jsx::anonymous_auth_hook', role='Hook to access auth state.')], core_logic_flow='Provides user state and auth methods (login/logout) to the component tree.', internal_dependencies=[], external_dependencies=['react'], public_api=['AuthProvider', 'anonymous_auth_hook'], side_effects=['State management'], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['auth', 'context'], related_files=['Login.jsx', 'Header.jsx'], overall_complexity='core_logic'), FileLevelSummary(filename='Header.jsx', filepath='../input_code/frontend/src/components/Header.jsx', module_name='frontend/components', file_purpose='Application header with navigation.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/components/Header.jsx::Header', role='Header UI component.')], core_logic_flow='Conditionally renders navigation links based on authentication status.', internal_dependencies=['AuthContext.jsx'], external_dependencies=['react-router-dom'], public_api=['Header'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['ui', 'navigation'], related_files=['Layout.jsx'], overall_complexity='utility'), FileLevelSummary(filename='DashCard.jsx', filepath='../input_code/frontend/src/components/DashCard.jsx', module_name='frontend/components', file_purpose='Displays restaurant summary card.', architecture_role='component', important_symbols=[FunctionReference(symbol_id='../input_code/frontend/src/components/DashCard.jsx::DashCard', role='Restaurant card component.')], core_logic_flow='Renders restaurant details and a link to the restaurant page.', internal_dependencies=[], external_dependencies=['react-router-dom'], public_api=['DashCard'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['ui', 'card'], related_files=['Dashboard.jsx'], overall_complexity='utility'), FileLevelSummary(filename='index.js', filepath='../input_code/backend/src/index.js', module_name='backend', file_purpose='Application entry point and server initialization.', architecture_role='orchestrator', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/index.js::anonymous_server_initializer', role='Initializes DB and starts server.')], core_logic_flow='Connects to MongoDB, initializes Redis listeners, and starts the Express server.', internal_dependencies=['db/index.js'], external_dependencies=['mongoose'], public_api=[], side_effects=['Database connection', 'Server startup'], error_handling_strategy='Throws error if DB connection fails.', state_management=None, security_considerations=None, performance_notes=None, tags=['server', 'init'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='user.model.js', filepath='../input_code/backend/src/model/user.model.js', module_name='backend/model', file_purpose='Defines User schema and authentication logic.', architecture_role='schema', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/model/user.model.js::anonymous_password_hasher', role='Middleware to hash passwords.'), FunctionReference(symbol_id='../input_code/backend/src/model/user.model.js::anonymous_password_validator', role='Validates user password.')], core_logic_flow='Uses Mongoose middleware to hash passwords before saving and provides methods for token generation and password validation.', internal_dependencies=[], external_dependencies=['bcrypt', 'jsonwebtoken'], public_api=['User'], side_effects=['Password hashing'], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['auth', 'model'], related_files=['user.controller.js'], overall_complexity='core_logic'), FileLevelSummary(filename='testClient.js', filepath='../input_code/backend/src/nlp_model/testClient.js', module_name='backend/nlp', file_purpose='Utility for testing sentiment analysis API.', architecture_role='client', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/nlp_model/testClient.js::analyzeReview', role='Client for sentiment analysis API.')], core_logic_flow='Sends text to the ML API and returns the result.', internal_dependencies=[], external_dependencies=['axios'], public_api=['analyzeReview'], side_effects=['API call'], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['nlp', 'test'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='model_runner.py', filepath='../input_code/backend/src/nlp_model/model_runner.py', module_name='backend/nlp', file_purpose='Core sentiment analysis logic.', architecture_role='service', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/nlp_model/model_runner.py::analyze_text', role='Performs sentiment analysis on text.')], core_logic_flow='Tokenizes input and runs it through a pre-trained model to return a sentiment label.', internal_dependencies=[], external_dependencies=[], public_api=['analyze_text'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['nlp', 'model'], related_files=['app.py'], overall_complexity='core_logic'), FileLevelSummary(filename='worker.js', filepath='../input_code/backend/src/nlp_model/worker.js', module_name='backend/nlp', file_purpose='Background worker for processing sentiment analysis jobs.', architecture_role='worker', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/nlp_model/worker.js::anonymous_job_processor', role='Processes sentiment analysis jobs.')], core_logic_flow='Consumes jobs from a queue, performs sentiment analysis, updates the database, and updates Redis leaderboards.', internal_dependencies=[], external_dependencies=['axios', 'bull'], public_api=[], side_effects=['Database update', 'Redis update'], error_handling_strategy='Logs job failures.', state_management=None, security_considerations=None, performance_notes=None, tags=['worker', 'nlp'], related_files=['review.controller.js'], overall_complexity='critical_path'), FileLevelSummary(filename='app.py', filepath='../input_code/backend/src/nlp_model/app.py', module_name='backend/nlp', file_purpose='API endpoint for sentiment analysis.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/nlp_model/app.py::analyze_review', role='Endpoint handler for sentiment analysis.')], core_logic_flow='Receives review text and calls the model_runner to analyze sentiment.', internal_dependencies=['model_runner.py'], external_dependencies=['pydantic'], public_api=['analyze_review'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['api', 'nlp'], related_files=['model_runner.py'], overall_complexity='core_logic'), FileLevelSummary(filename='multer.middleware.js', filepath='../input_code/backend/src/middlewares/multer.middleware.js', module_name='backend/middlewares', file_purpose='Configures file upload handling.', architecture_role='middleware', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/middlewares/multer.middleware.js::anonymous_multer_destination', role='Sets upload destination.')], core_logic_flow='Configures multer storage settings for file uploads.', internal_dependencies=[], external_dependencies=['multer'], public_api=[], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['middleware', 'upload'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='auth.middleware.js', filepath='../input_code/backend/src/middlewares/auth.middleware.js', module_name='backend/middlewares', file_purpose='Authenticates API requests.', architecture_role='middleware', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/middlewares/auth.middleware.js::anonymous_auth_middleware', role='Verifies JWT tokens.')], core_logic_flow='Extracts token from request, verifies it, and attaches user to request object.', internal_dependencies=['utils/ApiError.js'], external_dependencies=['jsonwebtoken'], public_api=['anonymous_auth_middleware'], side_effects=['Modifies request object'], error_handling_strategy='Throws ApiError on invalid/missing token.', state_management=None, security_considerations=None, performance_notes=None, tags=['auth', 'security'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='index.js', filepath='../input_code/backend/src/db/index.js', module_name='backend/db', file_purpose='Database connection initialization.', architecture_role='config', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/db/index.js::anonymous_db_connector', role='Connects to MongoDB.')], core_logic_flow='Uses Mongoose to connect to the database URI.', internal_dependencies=[], external_dependencies=['mongoose'], public_api=[], side_effects=['Database connection'], error_handling_strategy='Throws error on connection failure.', state_management=None, security_considerations=None, performance_notes=None, tags=['db', 'mongodb'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='leaderboard.controller.js', filepath='../input_code/backend/src/controllers/leaderboard.controller.js', module_name='backend/controllers', file_purpose='Handles leaderboard data retrieval.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/controllers/leaderboard.controller.js::anonymous_get_top_and_worst_restaurants', role='Fetches leaderboard data.')], core_logic_flow='Queries Redis for leaderboard rankings and fetches details from MongoDB.', internal_dependencies=['utils/ApiResponse.js', 'utils/ApiError.js'], external_dependencies=[], public_api=[], side_effects=[], error_handling_strategy='Throws ApiError if data is missing.', state_management=None, security_considerations=None, performance_notes=None, tags=['leaderboard', 'controller'], related_files=[], overall_complexity='critical_path'), FileLevelSummary(filename='user.controller.js', filepath='../input_code/backend/src/controllers/user.controller.js', module_name='backend/controllers', file_purpose='Handles user authentication and profile management.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/controllers/user.controller.js::anonymous_register_user', role='Registers new user.'), FunctionReference(symbol_id='../input_code/backend/src/controllers/user.controller.js::anonymous_login_user', role='Authenticates user.')], core_logic_flow='Handles registration (with photo upload), login (token generation), and logout.', internal_dependencies=['utils/ApiResponse.js', 'utils/ApiError.js', 'utils/cloudinary.js'], external_dependencies=[], public_api=[], side_effects=['Database writes', 'Cloudinary upload'], error_handling_strategy='Throws ApiError for validation/auth failures.', state_management=None, security_considerations=None, performance_notes=None, tags=['user', 'auth'], related_files=['user.model.js'], overall_complexity='critical_path'), FileLevelSummary(filename='restaurant.controller.js', filepath='../input_code/backend/src/controllers/restaurant.controller.js', module_name='backend/controllers', file_purpose='Handles restaurant management.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/controllers/restaurant.controller.js::anonymous_register_restaurant', role='Registers new restaurant.')], core_logic_flow='Handles restaurant registration, updates, and review retrieval.', internal_dependencies=['utils/ApiResponse.js', 'utils/ApiError.js', 'utils/cloudinary.js'], external_dependencies=[], public_api=[], side_effects=['Database writes', 'Cloudinary upload'], error_handling_strategy='Throws ApiError for validation/auth failures.', state_management=None, security_considerations=None, performance_notes=None, tags=['restaurant', 'controller'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='review.controller.js', filepath='../input_code/backend/src/controllers/review.controller.js', module_name='backend/controllers', file_purpose='Handles review lifecycle and analysis queuing.', architecture_role='controller', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/controllers/review.controller.js::anonymous_upload_review', role='Creates review and queues analysis.')], core_logic_flow='Creates/updates reviews and adds them to a background queue for sentiment analysis.', internal_dependencies=['utils/ApiResponse.js', 'utils/ApiError.js'], external_dependencies=[], public_api=[], side_effects=['Database writes', 'Queue job creation'], error_handling_strategy='Throws ApiError for validation failures.', state_management=None, security_considerations=None, performance_notes=None, tags=['review', 'queue'], related_files=['worker.js'], overall_complexity='critical_path'), FileLevelSummary(filename='ApiResponse.js', filepath='../input_code/backend/src/utils/ApiResponse.js', module_name='backend/utils', file_purpose='Standardized API response structure.', architecture_role='utility', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/utils/ApiResponse.js::ApiResponse', role='Response class.')], core_logic_flow='Encapsulates status code, data, and message.', internal_dependencies=[], external_dependencies=[], public_api=['ApiResponse'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['api', 'utils'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='ApiError.js', filepath='../input_code/backend/src/utils/ApiError.js', module_name='backend/utils', file_purpose='Standardized API error structure.', architecture_role='utility', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/utils/ApiError.js::ApiError', role='Error class.')], core_logic_flow='Extends Error to include status code and error details.', internal_dependencies=[], external_dependencies=[], public_api=['ApiError'], side_effects=[], error_handling_strategy='None.', state_management=None, security_considerations=None, performance_notes=None, tags=['api', 'utils'], related_files=[], overall_complexity='utility'), FileLevelSummary(filename='cloudinary.js', filepath='../input_code/backend/src/utils/cloudinary.js', module_name='backend/utils', file_purpose='Handles file uploads to Cloudinary.', architecture_role='utility', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/utils/cloudinary.js::anonymous_cloudinary_uploader', role='Uploads file to Cloudinary.')], core_logic_flow='Uploads local file to Cloudinary and deletes the local copy.', internal_dependencies=['ApiError.js'], external_dependencies=['cloudinary', 'fs'], public_api=['anonymous_cloudinary_uploader'], side_effects=['File system operations', 'Network call'], error_handling_strategy='Throws ApiError on failure.', state_management=None, security_considerations=None, performance_notes=None, tags=['cloudinary', 'upload'], related_files=[], overall_complexity='core_logic'), FileLevelSummary(filename='asyncHandler.js', filepath='../input_code/backend/src/utils/asyncHandler.js', module_name='backend/utils', file_purpose='Higher-order function for async error handling.', architecture_role='middleware', important_symbols=[FunctionReference(symbol_id='../input_code/backend/src/utils/asyncHandler.js::anonymous_async_handler', role='Wraps async functions.')], core_logic_flow='Wraps controller functions to catch and handle errors automatically.', internal_dependencies=[], external_dependencies=[], public_api=['anonymous_async_handler'], side_effects=[], error_handling_strategy='Catches errors and sends standardized response.', state_management=None, security_considerations=None, performance_notes=None, tags=['async', 'middleware'], related_files=[], overall_complexity='utility')]
    
    print(len(chunks_with_summary))
    api_key = "AIzaSyCCLp1a-C0l4Jh360lzjtM20Vm3AIHtVeE"
    model_name="gemini-3.1-flash-lite-preview"
    # model_name="qwen2.5-coder:7b"
    ollama_flag = False
    ai_msg = generate_module_summary(chunks_with_summary,model_name,api_key,ollama_flag)
    
    print(len(ai_msg))
    