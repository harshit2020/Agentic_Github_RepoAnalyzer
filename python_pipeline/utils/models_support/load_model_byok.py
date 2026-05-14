from .ModelDictionary.modelDict import giveModelList
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.rate_limiters import InMemoryRateLimiter

def load_config():
    config= {
                "temperature": 0,
                "timeout": 300,
                "max_retries": 2,
            }
    return config

def load_rate_limiter():
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=1,
        check_every_n_seconds = 0.1,
        max_bucket_size=1
    )
    return rate_limiter

def GeminiModelBuilder(model_name,api_key,rate_limiter,**kwargs):
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            rate_limiter=rate_limiter,
            **kwargs
        )
        return llm
    except Exception as e:
        raise RuntimeError(f"Failed to initialize {model_name}")
    

def OpenAIModelBuilder(model_name,api_key,rate_limiter,**kwargs):
    try:
        llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            rate_limiter=rate_limiter,
            **kwargs
        )
        return llm
    except Exception as e:
        raise RuntimeError(f"Failed to initialize {model_name}")
    

def AnthropicModelBuilder(model_name,api_key,rate_limiter,**kwargs):
    try:
        llm = ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            rate_limiter=rate_limiter,
            **kwargs 
        )
        return llm
    except Exception as e:
        raise RuntimeError(f"Failed to initialize {model_name}")
    


def load_model_byok(model_name,api_key):
    ModelList = giveModelList()
    model_info = ModelList[model_name]
    provider_info = model_info["provider"]

    kwargs = load_config()
    rate_limiter = load_rate_limiter()
    if provider_info == "google":
        llm = GeminiModelBuilder(model_name,api_key,rate_limiter,**kwargs)
        return llm
    elif provider_info == "openai":
        llm = OpenAiModelBuilder(model_name,api_key,rate_limiter,**kwargs)
        return llm
    elif provider_info == "anthropic":
        llm = AnthropicModelBuilder(model_name,api_key,rate_limiter,**kwargs)
        return llm
