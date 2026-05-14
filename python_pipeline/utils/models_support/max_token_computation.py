from .ModelDictionary.modelDict import giveModelList


def load_max_token(model_name):
    ModelList = giveModelList()
    model = ModelList[model_name]
    context_window = model["context_window"]
    max_output_tokens = model["max_output_tokens"]
    reserved_system_tokens = 8_000
    safety_margin = 10_000
    system_prompt = 2_000
    usable_input_limit = (
        context_window
        - max_output_tokens
        - reserved_system_tokens
        - safety_margin
        - system_prompt
    )   
    return usable_input_limit