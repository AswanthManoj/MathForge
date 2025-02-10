from enum import Enum
from typing import Optional
from pydantic import BaseModel

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    
class MCQType(str, Enum):
    NUMERICAL = 'numerical'
    SYMBOLIC = 'symbolic'
    STATEMENT = 'statement'

class SampleQuestionInput(BaseModel):
    topic: str
    difficulty_level: DifficultyLevel
    chapter_overview: Optional[str] = None
  
class SampleQuestionOutput(BaseModel):
    thoughts: Optional[str] = None
    question: str
    code: str
    
class SampleParameterInput(BaseModel):
    code: str
  
class SampleParameterOutput(BaseModel):
    thoughts: str
    parameters_code: str
    
class Instance(BaseModel):
    input: SampleQuestionInput|SampleParameterInput
    output: SampleQuestionOutput|SampleParameterOutput

class Example(BaseModel):
    question: Instance
    parameter: Instance

TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE = """
# Topic:
{topic}

---
# Overview:
{chapter_overview}

---
Generate questions and code which would result in {result_type} answer results
**Note: Difficulty level of the question should be: {difficulty_level}**
""".strip()


TOPIC_ONLY_TEMPLATE = """
# Topic:
{topic}

---
Generate questions and code which would result in {result_type} answer results
**Note: Difficulty level of the question should be: {difficulty_level}**
""".strip()


PARAMETERS_TEMPLATE = """
Here is `solve_problem` function and a sample parameter inputs:
```python
{code}
```

Now generate different parameter inputs suitable for the `solve_problem` function which would generate distinct answers.
""".strip()

