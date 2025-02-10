import re
from typing import Optional
from pydantic import BaseModel
from prompts.statement import STATEMENT_PROMPT
from prompts.numerical import (
QUESTION_PROMPT as NUMERICAL_QUESTION_PROMPT, 
PARAMETER_PROMPT as NUMERICAL_PARAMETER_PROMPT)
from prompts.expression import (
QUESTION_PROMPT as EXPRESSION_QUESTION_PROMPT, 
PARAMETER_PROMPT as EXPRESSION_PARAMETER_PROMPT
)


class CodeGeneratorOutput(BaseModel):
    code: str
    thoughts: Optional[str] = None
    question: str
    
class ParameterGeneratorOutput(BaseModel):
    thoughts: Optional[str] = None
    parameters_code: str

def extract_generator_content(text):
    """
    Parses LLM output to extract structured question generation content.
    
    Supports two format types:
    - XML tags (<thoughts>, <question>)
    - Markdown headings (# Thoughts, # Question)
    
    Extracts:
    - Thought process behind question generation
    - The actual question text
    - Python code implementation
    
    Args:
        text (str): Raw LLM output text
        
    Returns:
        CodeGeneratorOutput: Structured output containing thoughts, question and code
    """
    thoughts_match = re.search(r'<thoughts>(.*?)</thoughts>', text, re.DOTALL)
    question_match = re.search(r'<question>(.*?)</question>', text, re.DOTALL)
    if not thoughts_match:
        thoughts_match = re.search(r'#{1,6}\s*Thoughts\s*\n(.*?)(?=\n#{1,6}\s*|$)', text, re.DOTALL)
    if not question_match:
        question_match = re.search(r'#{1,6}\s*Question\s*\n(.*?)(?=\n#{1,6}\s*|$)', text, re.DOTALL)
    
    thoughts = thoughts_match.group(1).strip() if thoughts_match else None
    question = question_match.group(1).strip() if question_match else None
    code_match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL)
    code = code_match.group(1).strip() if code_match else None
    
    return CodeGeneratorOutput(
        code=code,
        thoughts=thoughts,
        question=question,
    )

def extract_parameter_content(text):
    """
    Parses LLM output to extract parameter generation content.
    
    Supports two format types:
    - XML tags (<thoughts>)
    - Markdown headings (# Thoughts)
    
    Extracts:
    - Thought process behind parameter generation
    - Python code for parameter generation
    
    Args:
        text (str): Raw LLM output text
        
    Returns:
        ParameterGeneratorOutput: Structured output containing thoughts and parameter code
    """
    thoughts_match = re.search(r'<thoughts>(.*?)</thoughts>', text, re.DOTALL)
    if not thoughts_match:
        thoughts_match = re.search(r'#{1,6}\s*Thoughts\s*\n(.*?)(?=\n#{1,6}\s*|$)', text, re.DOTALL)
    
    thoughts = thoughts_match.group(1).strip() if thoughts_match else None
    params_match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL)
    params_code = params_match.group(1).strip() if params_match else None
    
    return ParameterGeneratorOutput(
        thoughts=thoughts,
        parameters_code=params_code,
    )

def remove_python_comments(text):
    """
    Removes both single-line and multi-line comments (and associated whitespace) 
    from a string of Python code.
    """
    return re.sub(r'\s*#.*', '', text)

def remove_print_statements(text):
    return re.sub(r'print\s*\([^)]*\)', '', text)