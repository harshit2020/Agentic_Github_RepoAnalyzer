import queue

# global queue for repo url handling
indexing_api_queue = queue.Queue()
for key in ["key1", "key2", "key3", "key4", "key5"]:
    indexing_api_queue.put(key)

def put_api_queue(api_key):
    indexing_api_queue.put(api_key)
def get_api_key():
    return indexing_api_queue.get()

#this is maybe the check-function
def start_analysis_for_repo(github_repo_url):
    # function to get source code from github_repo_url
    api_key = get_api_key()
    
    # response = indexer(source_code,api_key)
    try:
        response = indexer(source_code, api_key)
    finally:
        put_api_queue(api_key)    # ALWAYS return key, success or failure

    # return node_job_completed