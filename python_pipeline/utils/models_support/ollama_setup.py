from dotenv import set_key
from langchain_ollama import ChatOllama
from langchain_core.rate_limiters import InMemoryRateLimiter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_DICT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ModelDictionary", "modelDict.py"
)

def get_all_models() -> dict:
    from ModelDictionary.modelDict import giveModelList
    return giveModelList()

def get_ollama_models() -> dict:
    all_models = get_all_models()
    return {k: v for k, v in all_models.items() if v["provider"] == "ollama"}

def get_cloud_models() -> dict:
    all_models = get_all_models()
    return {k: v for k, v in all_models.items() if v["provider"] != "ollama"}

#This is the function when someone calls a ollama saved button
def validate_and_save_env_updating_ollama_(
    host: str, port: str, model_name: str,
    num_ctx: int = 32000, num_predict: int = 8000, temperature: float = 0,
    requests_per_second: float = 1.0, max_bucket_size: int = 1
):
    try:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=requests_per_second,
            check_every_n_seconds=0.1,
            max_bucket_size=max_bucket_size
        )
        test_llm = ChatOllama(
            model=model_name,
            base_url=f"{host}:{port}",
            num_ctx=num_ctx,
            num_predict=num_predict,
            temperature=temperature,
            rate_limiter=rate_limiter
        )
        test_llm.invoke("say hi in one word")

    except ConnectionError:
        raise ValueError(f"Cannot connect to Ollama at {host}:{port} — is Ollama running?")
    except Exception as e:
        if "model not found" in str(e).lower():
            raise ValueError(f"Model '{model_name}' not found — run: ollama pull {model_name}")
        raise ValueError(f"Model validation failed: {e}")

    _add_to_model_list(model_name, num_ctx, num_predict)

    env_path = "python_pipeline/.env"
    set_key(env_path, "OLLAMA_HOST",host)
    set_key(env_path, "OLLAMA_PORT",port)
    set_key(env_path, "OLLAMA_MODEL",model_name)
    set_key(env_path, "OLLAMA_NUM_CTX",str(num_ctx))
    set_key(env_path, "OLLAMA_NUM_PREDICT", str(num_predict))
    set_key(env_path, "OLLAMA_TEMPERATURE", str(temperature))
    set_key(env_path, "OLLAMA_RPS", str(requests_per_second))
    set_key(env_path, "OLLAMA_MAX_BUCKET_SIZE", str(max_bucket_size))

    print("Ollama config saved and validated ✅")


def _add_to_model_list(model_name: str, num_ctx: int, num_predict: int):
    new_entry = f"""
        "{model_name}": {{
            "provider": "ollama",
            "context_window": {num_ctx},
            "max_output_tokens": {num_predict},
            "supports_reasoning": False,
            "supports_structured_output": True,
            "supports_tools": False,
        }},"""

    with open(MODEL_DICT_PATH, "r") as f:
        content = f.read()

    if f'"{model_name}"' in content:
        print(f"Model {model_name} already in list, updating...")
        content = _remove_model_entry(content, model_name)

    insert_point = content.rfind("    }")
    content = content[:insert_point] + new_entry + "\n" + content[insert_point:]

    with open(MODEL_DICT_PATH, "w") as f:
        f.write(content)

    print(f"Model {model_name} added to ModelList ✅")


def remove_from_model_list(model_name: str):
    # check provider first — only ollama models can be removed
    all_models = get_all_models()

    if model_name not in all_models:
        print(f"Model {model_name} not found")
        return

    if all_models[model_name]["provider"] != "ollama":
        raise ValueError(f"Cannot delete '{model_name}' — only Ollama models can be removed")

    with open(MODEL_DICT_PATH, "r") as f:
        content = f.read()

    if f'"{model_name}"' not in content:
        print(f"Model {model_name} not found in file")
        return

    content = _remove_model_entry(content, model_name)

    with open(MODEL_DICT_PATH, "w") as f:
        f.write(content)

    print(f"Model {model_name} removed from ModelList ✅")


def _remove_model_entry(content: str, model_name: str) -> str:
    lines = content.split("\n")
    result = []
    skip = False
    brace_count = 0

    for line in lines:
        if f'"{model_name}"' in line and "provider" not in line:
            skip = True
            brace_count = 0

        if skip:
            brace_count += line.count("{") - line.count("}")
            if brace_count <= 0 and "}" in line:
                skip = False
            continue

        result.append(line)

    return "\n".join(result)


if __name__ == "__main__":
    print("Ollama models:", get_ollama_models())
    print("Cloud models:", get_cloud_models())
    validate_and_save_env_updating_ollama_("http://localhost", "11434", "qwen2.5-coder:7b")
