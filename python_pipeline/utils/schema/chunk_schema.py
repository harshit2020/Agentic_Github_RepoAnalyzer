from pydantic import BaseModel,Field
from typing import Optional    

class ParameterInfo(BaseModel):
    name: str = Field(description = "The name of the parameter")
    type: str = Field(description = "The type of the parameter")
    description: str = Field(description = "The description of the parameter")

class ClassAttributes(BaseModel):
    name: str = Field(description = "The name of the class attribute")
    type: str = Field(description = "The type of the class attribute")
    description: str = Field(description = "The usage of the class attribute")
    
class ClassMethods(BaseModel):
    name: str = Field(description = "The name of the class method")
    parameters: list[ParameterInfo] = Field(description = "The parameters of the class method")
    description: str = Field(description = "The description of the method")

    
class FunctionName(BaseModel):
    filename: str = Field(description="The filename this chunk belongs to")
    filepath: str = Field(description="Full relative file path")
    function_name: str = Field(description = "The name of the function")
class ChunkSummary(BaseModel):
    function_info: FunctionName = Field(description = "Metadata about the function")
    parameters: list[ParameterInfo] = Field(description = "The parameters of the function")
    return_value: str = Field(description = "The return value of the function")
    logic_summary: str = Field(description = "The logic of the function")
    dependencies: list[str]  = Field(description = "Other functions and classes  used by the function")    # other functions/classes it uses
    side_effects: str = Field(description = "The side_effects of the function if any or NONE")   # "none" or description
    error_handling: str = Field(description = "The error handled by the function or NONE")   # "none" or what it handles
    complexity: str = Field(description = "The complex of the function is it utility or core_logic or critical_path")  # "utility" / "core_logic" / "critical_path"
    tags: list[str] = Field(description="Keywords a developer would search for to find this code")
    class_purpose: Optional[str] = Field(default=None, description = "If class then what real world concept it represents")
    attributes: Optional[list[ClassAttributes]] = Field(default=None, description = "If class has attributes else NONE")
    methods_overview: Optional[list[ClassMethods]] = Field(default=None, description = "If class has methods else NONE")
    inheritance: Optional[str] = Field(default=None, description="What it extends or None")

class ChunkSummaryList(BaseModel):
    summaries: list[ChunkSummary] = Field(description="List of summaries for each chunk")