
def giveModelList():
    ModelList = {
        "gpt-4.1": {
            "provider": "openai",
            "tokenizer": "cl100k_base",
            "context_window": 1_000_000,
            "max_output_tokens": 32_768,
            "supports_reasoning": True,
            "supports_structured_output": True,
            "supports_tools": True,
        },

        "gpt-4.1-mini": {
            "provider": "openai",
            "tokenizer": "cl100k_base",
            "context_window": 1_000_000,
            "max_output_tokens": 32_768,
            "supports_reasoning": True,
            "supports_structured_output": True,
            "supports_tools": True,
        },

        "gpt-4o": {
            "provider": "openai",
            "tokenizer": "o200k_base",
            "context_window": 128_000,
            "max_output_tokens": 16_384,
            "supports_reasoning": False,
            "supports_structured_output": True,
            "supports_tools": True,
        },

        "claude-sonnet-4-6": {
            "provider": "anthropic",
            "tokenizer": "claude_tokenizer",
            "context_window": 1_000_000,
            "max_output_tokens": 64_000,
            "supports_reasoning": True,
            "supports_structured_output": True,
            "supports_tools": True,
        },

        "claude-opus-4-6": {
            "provider": "anthropic",
            "tokenizer": "claude_tokenizer",
            "context_window": 1_000_000,
            "max_output_tokens": 64_000,
            "supports_reasoning": True,
            "supports_structured_output": True,
            "supports_tools": True,
        },

        "claude-haiku": {
            "provider": "anthropic",
            "tokenizer": "claude_tokenizer",
            "context_window": 200_000,
            "max_output_tokens": 8_192,
            "supports_reasoning": False,
            "supports_structured_output": True,
            "supports_tools": True,
        },

        "gemini-2.5-pro": {
            "provider": "google",
            "tokenizer": "gemini_tokenizer",
            "context_window": 1_000_000,
            "max_output_tokens": 65_536,
            "supports_reasoning": True,
            "supports_structured_output": True,
            "supports_tools": True,
        },

        "gemini-2.5-flash": {
            "provider": "google",
            "tokenizer": "gemini_tokenizer",
            "context_window": 1_000_000,
            "max_output_tokens": 65_536,
            "supports_reasoning": True,
            "supports_structured_output": True,
            "supports_tools": True,
        },

        "gemini-2.5-flash-lite": {
            "provider": "google",
            "tokenizer": "gemini_tokenizer",
            "context_window": 1_000_000,
            "max_output_tokens": 32_768,
            "supports_reasoning": False,
            "supports_structured_output": True,
            "supports_tools": False,
        },

        "gemini-3.1-flash-lite": {
            "provider": "google",
            "tokenizer": "gemini_tokenizer",
            "context_window": 1_000_000,
            "max_output_tokens": 32_768,
            "supports_reasoning": False,
            "supports_structured_output": True,
            "supports_tools": False,
        },
        "qwen2.5-coder:1.5b": {
            "provider": "ollama",
            "context_window": 32000,
            "max_output_tokens": 8000,
            "supports_reasoning": False,
            "supports_structured_output": True,
            "supports_tools": False,
        },

        "qwen2.5-coder:7b": {
            "provider": "ollama",
            "context_window": 32000,
            "max_output_tokens": 8000,
            "supports_reasoning": False,
            "supports_structured_output": True,
            "supports_tools": False,
        },
    }
        
    return ModelList
