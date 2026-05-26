import queue


#this is maybe the check-function
def start_analysis_for_repo(github_repo_url,model_name,ollama_flag,api_key):
    try:
        # parts = github_repo_url.rstrip("/").split("/")
        # owner = parts[-2]
        # repo = parts[-1]
        # function to get source code from github_repo_url and store it in path "python_pipeline/input_code/owner_repo"
        # create folder name as owner_repo to store the souce code individually
        
        # chroma setup if online
        # set ollama if required
        # redis setup
    
        response = indexer(source_code, api_key)
    
        #after indexing the code we ll delete it from the server i.e. delete folder owner_repo
        
    except Exception as e:
        print(f"LLM Pipeline failed \n Error : {e}")

    # return node_job_completed

