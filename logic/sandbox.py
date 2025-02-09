import json
import sympy as sp
import numpy as np
from typing import Union
import math, ast, sympy, numpy
from typing import List, Optional
from pydantic import BaseModel, field_validator
from prompts import (NUMERICAL_PARAMETER_PROMPT,
NUMERICAL_QUESTION_PROMPT, ParameterGeneratorOutput,
CodeGeneratorOutput, EXPRESSION_PARAMETER_PROMPT, EXPRESSION_QUESTION_PROMPT,
extract_generator_content, extract_parameter_content, remove_python_comments)
from logic.llm_connector import LLMConnector, AnthropicConfig, GoogleConfig, TogetherConfig
from prompts.base import TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE, TOPIC_ONLY_TEMPLATE, PARAMETERS_TEMPLATE

from prompts.expression import QUESTION_ICL_MESSAGES, PARAMETER_ICL_MESSAGES

class SecurityException(Exception):
    pass

class Option(BaseModel):
    is_correct:    bool = False
    input_params:  dict
    output_result: Optional[int|float|str] = None

    @field_validator('output_result')
    @classmethod
    def round_float_result(cls, value):
        if isinstance(value, float):
            return round(value, 5)
        if isinstance(value, sympy.Expr):
            return sympy.latex(value)
        return value

class FinalOutput(BaseModel):
    options:  List[Option]
    question: str
    thoughts: Optional[str] = None
    
    
class MathU:
    def __init__(
        self, 
        max_tokens: int = 3049,
        temperature: float = 0.3,
        google: GoogleConfig | None = None,
        together: TogetherConfig | None = None,
        anthropic: AnthropicConfig | None = None,
        provider_priority: List[str] = ["anthropic", "google", "together"]
    ) -> None:
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.llm = LLMConnector(
            google=google,
            together=together,
            anthropic=anthropic,
            provider_priority=provider_priority
        )
        
    def safe_exec(self, code, disallowed_names=None, disallowed_global_vars=None):
        """
        Executes code in a restricted environment with security checks.
        
        Args:
            code (str): The code to execute
            disallowed_names (list): Names that cannot be used in the code
            disallowed_global_vars (dict): Global variables to exclude
        
        Returns:
            dict: Updated local namespace after execution, or None on error
        """
        def analyze_ast(node, disallowed_names):
            """
            Recursively analyzes AST nodes to check for disallowed names and dangerous operations.
            """
            if isinstance(node, ast.Name):
                if node.id in disallowed_names:
                    raise SecurityException(f"Use of disallowed name: {node.id}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in disallowed_names:
                        raise SecurityException(f"Import of disallowed module: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in disallowed_names:
                    raise SecurityException(f"Import from disallowed module: {node.module}")
            elif isinstance(node, (ast.Call, ast.Attribute)):
                if isinstance(node, ast.Attribute):
                    if node.attr.startswith('__'):
                        raise SecurityException(f"Access to dunder method not allowed: {node.attr}")
            for child in ast.iter_child_nodes(node):
                analyze_ast(child, disallowed_names)
        try:
            if disallowed_names is None:
                disallowed_names = {
                    'eval', 'exec', 'compile', 'open', 'system', 'os', 
                    'subprocess', 'sys', '__import__'
                }
                
            tree = ast.parse(code)
            analyze_ast(tree, disallowed_names)
            
            local_vars = {}
            globals_copy = globals().copy()
            
            if disallowed_global_vars:
                for name in disallowed_global_vars:
                    globals_copy.pop(name, None)
            
            compiled_code = compile(tree, '<string>', 'exec')
            exec(compiled_code, globals_copy, local_vars)
            
            return local_vars
            
        except SecurityException as e:
            print(f"Security violation: {str(e)}")
            return None
        except Exception as e:
            print(f"Execution error: {str(e)}")
            return None
        
    async def _generate_question_and_code(self, topic: str, chapter_overview: str|None=None, is_numerical: bool=True) -> CodeGeneratorOutput:
        if chapter_overview is not None:
            messages = [{
                "role": "user",
                "content": TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE.format(
                    topic=topic, 
                    chapter_overview=chapter_overview
                )
            }]
        else:
            messages = [{
                "role": "user",
                "content": TOPIC_ONLY_TEMPLATE.format(topic=topic)
            }]
        return await self.llm.generate(
            messages=QUESTION_ICL_MESSAGES + messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=NUMERICAL_QUESTION_PROMPT if is_numerical else EXPRESSION_QUESTION_PROMPT,
            extractor_function=extract_generator_content,
        )
    
    async def _generate_parameters(self, code: str, is_numerical: bool=True) -> ParameterGeneratorOutput:
        # code = remove_python_comments(code)
        return await self.llm.generate(
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=NUMERICAL_PARAMETER_PROMPT if is_numerical else EXPRESSION_PARAMETER_PROMPT,
            extractor_function=extract_parameter_content,
            messages=PARAMETER_ICL_MESSAGES + [{
                "role": "user",
                "content": PARAMETERS_TEMPLATE.format(code=code.replace('actual_params', 'sample_params'))
            }]
        )
        
    async def generate(self, topic: str, chapter_overview: str|None=None, is_numerical: bool=True) -> FinalOutput:
        code_output = await self._generate_question_and_code(topic, chapter_overview, is_numerical)
        solve_function_namespace = self.safe_exec(
            code_output.code,
            disallowed_global_vars=['settings', 'llm'],
            disallowed_names=['os', 'sys', 'eval', 'exec'],
        )
        
        actual_params = solve_function_namespace.get('actual_params')
        solve_function = solve_function_namespace.get('solve_problem')
        
        params_output = await self._generate_parameters(code_output.code, is_numerical)
        params_namespace = self.safe_exec(
            params_output.parameters_code,
            disallowed_global_vars=['settings', 'llm'],
            disallowed_names=['os', 'sys', 'eval', 'exec'],
        )

        param_set_1 = params_namespace.get('param_set_1')
        param_set_2 = params_namespace.get('param_set_2')
        param_set_3 = params_namespace.get('param_set_3')
        param_set_4 = params_namespace.get('param_set_4')
        param_set = [param_set_1, param_set_2, param_set_3, param_set_4]
        
        options = []
        if actual_params and 'solve_problem' in solve_function_namespace:
            result = solve_function(**actual_params)
            options.append(Option(
                is_correct=True,
                output_result=result, 
                input_params=actual_params  
            ))
        
        if param_set and 'solve_problem' in solve_function_namespace:
            for i, params in enumerate(param_set, 1):
                result = solve_function(**params)
                options.append(Option(
                    is_correct=False,
                    input_params=params,
                    output_result=result 
                ))
        return FinalOutput(
            options=options,
            question=code_output.question,
            thoughts=code_output.thoughts,
        )
        

