from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

    
class MCQType(str, Enum):
    NUMERICAL = 'numerical'
    SYMBOLIC = 'symbolic'
    STATEMENT = 'statement'

class DifficultyLevel(str, Enum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'

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

class QuestionBank(BaseModel):
    thoughts: str
    questions: List[str] = []

class Question(BaseModel):
    numerical: List[str] = []
    symbolic: List[str] = []
    statement: List[str] = []

class MultiLevelQuestionBank(BaseModel):
    easy_questions: Question = Question()
    medium_questions: Question = Question()
    hard_questions: Question = Question()

class Option(BaseModel):
    is_correct: bool = False
    output_result: Optional[int|float|str] = None

class FinalOutput(BaseModel):
    question: str
    options:  List[Option]
    correct_answer: int|float|str
    thoughts: Optional[str] = None
