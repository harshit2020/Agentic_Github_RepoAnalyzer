from .ModelDictionary.modelDict import giveModelList
from transformers import GPT2TokenizerFast,AutoTokenizer

def GeminiTokenizer():
    tokenizer = AutoTokenizer.from_pretrained("nomic-ai/CodeRankEmbed", trust_remote_code=True)
    return tokenizer

def OpenAITokenizer():
    tokenizer = AutoTokenizer.from_pretrained("DWDMaiMai/tiktoken_cl100k_base")
    return tokenizer


def AnthropicTokenizer():
    tokenizer = GPT2TokenizerFast.from_pretrained('Xenova/claude-tokenizer')
    return tokenizer



def load_tokenizer(model_name):
    ModelList = giveModelList()
    model_info = ModelList[model_name]
    provider_info = model_info["provider"]

    if provider_info == "google":
        tokenizer = GeminiTokenizer()
        return tokenizer
    elif provider_info == "openai":
        tokenizer = OpenAITokenizer()
        return tokenizer
    elif provider_info == "anthropic":
        tokenizer = AnthropicTokenizer()
        return tokenizer