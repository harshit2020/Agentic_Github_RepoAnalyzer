from langchain_ollama import ChatOllama
from langchain_core.rate_limiters import InMemoryRateLimiter
from dotenv import load_dotenv
import os

load_dotenv()

def load_model_ollama(model_name):
    host= os.getenv("OLLAMA_HOST","http://localhost")
    port= os.getenv("OLLAMA_PORT","11434")
    model_name= os.getenv("OLLAMA_MODEL","qwen2.5-coder:7b")
    num_ctx= int(os.getenv("OLLAMA_NUM_CTX","32000"))
    num_predict= int(os.getenv("OLLAMA_NUM_PREDICT", "8000"))
    temperature= float(os.getenv("OLLAMA_TEMPERATURE","0"))
    rps= float(os.getenv("OLLAMA_RPS","1.0"))
    max_bucket_size= int(os.getenv("OLLAMA_MAX_BUCKET_SIZE","1"))


    rate_limiter = InMemoryRateLimiter(
        requests_per_second=rps,
        check_every_n_seconds=0.1,
        max_bucket_size=max_bucket_size
    )

    llm = ChatOllama(
        model=model_name,
        temperature=temperature,
        base_url=f"{host}:{port}",
        num_ctx=num_ctx,
        num_predict=num_predict,
        rate_limiter=rate_limiter
    )
    return llm

if __name__ == "__main__":
    llm = load_model_ollama("qwen2.5-coder:1.5b")
    print(llm.invoke("Hi how are you"))