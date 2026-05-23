

# def load_max_token(model_name,ollama_flag):
#     ModelList = giveModelList()
#     model = ModelList[model_name]
#     context_window = model["context_window"]
#     max_output_tokens = model["max_output_tokens"]
#     reserved_system_tokens = 8_000
#     safety_margin = 10_000
#     system_prompt = 2_000
#     if ollama_flag == True:
#         reserved_system_tokens = 2_000
#         safety_margin = 2_000
#     usable_input_limit = (
#         context_window
#         - max_output_tokens
#         - reserved_system_tokens
#         - safety_margin
#         - system_prompt
#     )   
#     return usable_input_limit

def load_max_token(model_name,ollama_flag):
    ModelList = giveModelList()
    model = ModelList[model_name]
    max_output_tokens = model["max_output_tokens"]
    safety_margin = 2000
    usable_input_limit = (max_output_tokens - safety_margin)   
    return usable_input_limit

if __name__ == "__main__":
    from ModelDictionary.modelDict import giveModelList

    print(load_max_token("gpt-4.1",False))

else:
    from .ModelDictionary.modelDict import giveModelList