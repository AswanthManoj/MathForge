import sympy as sp
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_validator

    
class MCQType(str, Enum):
    NUMERICAL = 'numerical'
    SYMBOLIC = 'symbolic'
    STATEMENT = 'statement'


class SolverOutput(BaseModel):
    code: Optional[str] = None
    thoughts: Optional[str] = None
    

class ParameterGeneratorOutput(BaseModel):
    thoughts: Optional[str] = None
    parameters_code: str



class LLMMessage(BaseModel):
    role:              str = "assistant"
    content:           str
    content_delta:     Optional[str] = None
    response_finished: bool = False
    
class LLMProviderConfig(BaseModel):
    model:   str
    api_key: str
    
class AnthropicConfig(LLMProviderConfig):
    pass

class GoogleConfig(LLMProviderConfig):
    pass

class TogetherConfig(LLMProviderConfig):
    pass

class OpenAIConfig(LLMProviderConfig):
    pass

class GroqConfig(LLMProviderConfig):
    pass

class MistralConfig(LLMProviderConfig):
    pass




class SecurityException(Exception):
    pass

class Option(BaseModel):
    is_correct: bool = False
    output_result: Optional[int|float|str|tuple|list] = None

    @field_validator('output_result')
    @classmethod
    def format_output_result(cls, value):
        if isinstance(value, float):
            return round(value, 5)
        if isinstance(value, (sp.Symbol, sp.Expr)):
            return sp.latex(value)
        return value

class FinalOutput(BaseModel):
    question: str
    options:  List[Option]
    correct_answer: int|float|str
    thoughts: Optional[str] = None
