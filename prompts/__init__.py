import re
from typing import Optional
from pydantic import BaseModel
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
    Extract content from question generator output including thoughts, 
    question and code block. Supports both XML tags and Markdown headings.
    
    Args:
        text (str): Input text containing XML tags/Markdown headings and code blocks
        
    Returns:
        CodeGeneratorOutput: Object containing thoughts, question and code
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
    Extract content from parameter generator output including thoughts
    and parameter code block. Supports both XML tags and Markdown headings.
    
    Args:
        text (str): Input text containing XML tags/Markdown headings and code blocks
        
    Returns:
        ParameterGeneratorOutput: Object containing thoughts and parameters code
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