import asyncio
import sympy as sp
import numpy as np
import json, random
from enum import Enum
from typing import Union
import math, ast, sympy, numpy
from typing import List, Optional
from prompts.statement import ICL_MESSAGE
from prompts.expression import (
QUESTION_ICL_MESSAGES, PARAMETER_ICL_MESSAGES)
from pydantic import BaseModel, field_validator
from concurrent.futures import ThreadPoolExecutor
from prompts import (NUMERICAL_PARAMETER_PROMPT,
NUMERICAL_QUESTION_PROMPT, ParameterGeneratorOutput, STATEMENT_PROMPT,
CodeGeneratorOutput, EXPRESSION_PARAMETER_PROMPT, EXPRESSION_QUESTION_PROMPT,
extract_generator_content, extract_parameter_content, remove_print_statements)
from logic.llm_connector import GroqConfig, LLMConnector, AnthropicConfig, GoogleConfig, MistralConfig, TogetherConfig, OpenAIConfig
from prompts.base import TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE, TOPIC_ONLY_TEMPLATE, PARAMETERS_TEMPLATE, DifficultyLevel, MCQType


class SecurityException(Exception):
    pass

class Option(BaseModel):
    is_correct: bool = False
    input_params: Optional[dict] = None
    output_result: Optional[Union[int, float, str]] = None

    @field_validator('output_result')
    @classmethod
    def format_output_result(cls, value):
        if isinstance(value, float):
            return round(value, 5)
        if isinstance(value, (sympy.Symbol, sympy.Expr)):
            return sympy.latex(value)
        return value

    @field_validator('input_params')
    @classmethod
    def format_input_params(cls, value):
        if value is None:
            return value
        # Convert any SymPy objects in input parameters to strings
        formatted_params = {}
        for k, v in value.items():
            if isinstance(v, (sympy.Symbol, sympy.Expr)):
                formatted_params[k] = sympy.latex(v)
            else:
                formatted_params[k] = v
        return formatted_params

class FinalOutput(BaseModel):
    options:  List[Option]
    question: str
    thoughts: Optional[str] = None
    
    
class MathU:
    """
    A class that generates mathematical questions and evaluates solutions using LLM providers.
    
    This class handles:
    - Generation of mathematical questions and their corresponding code solutions
    - Safe execution of generated code in a restricted environment
    - Parameter generation for multiple choice options
    - Integration with different LLM providers (Anthropic, Google, Together)
    
    The class supports both numerical and expression-based questions, with built-in
    security measures to prevent dangerous code execution.
    """
    def __init__(
        self, 
        max_tokens: int = 3049,
        temperature: float = 0.3,
        code_execution_timeout: int = 5,
        google: GoogleConfig | None = None,
        together: TogetherConfig | None = None,
        anthropic: AnthropicConfig | None = None,
        openai: OpenAIConfig | None = None,
        groq: GroqConfig | None = None,
        mistral: MistralConfig | None = None,
        provider_priority: List[str] = ["anthropic", "google", "together", "openai", "groq", "mistral"]
    ) -> None:
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.llm = LLMConnector(
            google=google,
            together=together,
            anthropic=anthropic,
            openai=openai,
            groq=groq,
            mistral=mistral,
            provider_priority=provider_priority
        )
        self.code_execution_timeout = code_execution_timeout
        
    async def safe_exec(self, code, timeout: int = 5, disallowed_names=None, disallowed_global_vars=None):
        """
        Executes Python code in a restricted environment with security checks and timeout.
        
        Args:
            code (str): Python code to execute
            timeout (int): Maximum execution time in seconds
            disallowed_names (list): Names that cannot be used in the code
            disallowed_global_vars (dict): Global variables to exclude from execution context
            
        Returns:
            dict: Local namespace after execution if successful, None if execution fails
            
        Raises:
            SecurityException: If code contains dangerous operations
            TimeoutError: If code execution exceeds timeout
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

        def execute_code():
            nonlocal disallowed_names, disallowed_global_vars, code
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

        # async def execute_with_timeout():
        #     nonlocal timeout
        #     try:
        #         loop = asyncio.get_event_loop()
        #         with ThreadPoolExecutor() as pool:
        #             result = await asyncio.wait_for(
        #                 loop.run_in_executor(pool, execute_code),
        #                 timeout=timeout
        #             )
        #         return result
        #     except asyncio.TimeoutError:
        #         print(f"Code execution timed out after {timeout} seconds")
        #         return None
        #     except Exception as e:
        #         print(f"Execution error: {str(e)}")
        #         return None
        
        async def execute_with_timeout():
            result = None
            try:
                loop = asyncio.get_event_loop()
                thread_pool = ThreadPoolExecutor(max_workers=1)
                future = loop.run_in_executor(thread_pool, execute_code)
                try:
                    result = await asyncio.wait_for(future, timeout=timeout)
                finally:
                    thread_pool.shutdown(wait=False)
                return result
            except asyncio.TimeoutError:
                print(f"Code execution timed out after {timeout} seconds")
                return None

        return await execute_with_timeout()
        
    async def _generate_numerical_symbolic_problem(
        self, 
        topic: str, 
        chapter_overview: str|None=None, 
        is_numerical: bool=True, 
        difficulty_level: DifficultyLevel=DifficultyLevel.EASY,
        temperature: float = 0.3,
        provider: Optional[str] = None
    ) -> FinalOutput:
        async def _generate_question_and_code() -> CodeGeneratorOutput:
            nonlocal is_numerical
            result_type = "numerical" if is_numerical else "symbolic or expression"
            if chapter_overview is not None:
                messages = [{
                    "role": "user",
                    "content": TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE.format(
                        topic=topic, 
                        result_type=result_type,
                        difficulty_level=difficulty_level,
                        chapter_overview=chapter_overview,
                    )
                }]
            else:
                messages = [{
                    "role": "user",
                    "content": TOPIC_ONLY_TEMPLATE.format(
                        topic=topic, 
                        result_type=result_type,
                        difficulty_level=difficulty_level
                    )
                }]
            return await self.llm.generate(
                provider=provider,
                max_tokens=self.max_tokens,
                temperature=temperature,
                messages=QUESTION_ICL_MESSAGES + messages,
                extractor_function=extract_generator_content,
                system=NUMERICAL_QUESTION_PROMPT if is_numerical else EXPRESSION_QUESTION_PROMPT,
            )
        
        async def _generate_parameters(code: str) -> ParameterGeneratorOutput:
            nonlocal is_numerical
            return await self.llm.generate(
                provider=provider,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system=NUMERICAL_PARAMETER_PROMPT if is_numerical else EXPRESSION_PARAMETER_PROMPT,
                extractor_function=extract_parameter_content,
                messages=PARAMETER_ICL_MESSAGES + [{
                    "role": "user",
                    "content": PARAMETERS_TEMPLATE.format(code=code.replace('actual_params', 'sample_params'))
                }]
            )
            
        code_output = await _generate_question_and_code()
        solve_function_namespace = await self.safe_exec(
            timeout=self.code_execution_timeout,
            code=remove_print_statements(code_output.code),
            disallowed_global_vars=['settings', 'llm'],
            disallowed_names=['os', 'sys', 'eval', 'exec'],
        )
        
        actual_params = solve_function_namespace.get('actual_params')
        solve_function = solve_function_namespace.get('solve_problem')
        
        params_output = await _generate_parameters(code_output.code)
        params_namespace = await self.safe_exec(
            timeout=self.code_execution_timeout,
            code=remove_print_statements(params_output.parameters_code),
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
        
    async def _generate_statement_problem(
        self, 
        topic: str, 
        chapter_overview: str|None=None, 
        difficulty_level: DifficultyLevel=DifficultyLevel.EASY,
        temperature: float = 0.3,
        provider: Optional[str] = None
    ) -> FinalOutput:
        async def _generate_question_and_code() -> CodeGeneratorOutput:
            result_type = "numerical" if random.choice([True, False]) else "symbolic or expression"
            messages = ICL_MESSAGE
            if chapter_overview is not None:
                messages = messages + [{
                    "role": "user",
                    "content": TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE.format(
                        topic=topic, 
                        result_type=result_type,
                        difficulty_level=difficulty_level,
                        chapter_overview=chapter_overview,
                    )
                }]
            else:
                messages = messages + [{
                    "role": "user",
                    "content": TOPIC_ONLY_TEMPLATE.format(
                        topic=topic, 
                        result_type=result_type,
                        difficulty_level=difficulty_level
                    )
                }]
            return await self.llm.generate(
                provider=provider,
                messages=messages,
                system=STATEMENT_PROMPT,
                max_tokens=self.max_tokens,
                temperature=temperature,
                extractor_function=extract_generator_content,
            )
        
        code_output = await _generate_question_and_code()
        solve_function_namespace = await self.safe_exec(
            timeout=self.code_execution_timeout,
            code=remove_print_statements(code_output.code),
            disallowed_global_vars=['settings', 'llm'],
            disallowed_names=['os', 'sys', 'eval', 'exec'],
        )
        
        actual_params = solve_function_namespace.get('actual_params')
        solve_function = solve_function_namespace.get('solve_problem')
        options = []
        if actual_params and 'solve_problem' in solve_function_namespace:
            result, statement, distractors = solve_function(**actual_params)
            options.append(Option(
                is_correct=True,
                output_result=statement, 
                input_params=actual_params  
            ))
            for distractor in distractors:
                options.append(Option(
                    output_result=distractor
                ))
        return FinalOutput(
            options=options,
            question=code_output.question,
            thoughts=code_output.thoughts,
        )
        
    async def generate(
        self, 
        topic: str, 
        sub_topic: str|None=None,
        chapter_overview: str|None=None, 
        mcq_type: MCQType=MCQType.NUMERICAL, 
        temperature: float|None = None,
        difficulty_level: DifficultyLevel|None = None,
        provider: Optional[str] = None
    ) -> FinalOutput:
    
        if temperature is None:
            temperature = self.temperature
        if difficulty_level is None:
            difficulty_level = DifficultyLevel.EASY
        if sub_topic is not None and chapter_overview is not None:
            chapter_overview = chapter_overview + f'\nQuestion must be from the following sub topic: "{sub_topic}".'

        
        if mcq_type == MCQType.STATEMENT:
            output = await self._generate_statement_problem(
                topic=topic, 
                provider=provider,
                temperature=temperature,
                difficulty_level=difficulty_level,
                chapter_overview=chapter_overview, 
            )
            
        if mcq_type == MCQType.NUMERICAL:
            is_numerical = True
        else:
            is_numerical = False
        output = await self._generate_numerical_symbolic_problem(
            topic=topic, 
            provider=provider,
            temperature=temperature,
            is_numerical=is_numerical, 
            difficulty_level=difficulty_level,
            chapter_overview=chapter_overview, 
        )
        all_options = []
        all_options_values = []
        options_map = {option.output_result: option for option in output.options}
        # we need to get the correct option and then the wrong options in a list and we should be able to ensure unique wrong options are there something like list
        for value, option in options_map.items():
            if option.is_correct:
                all_options.append(option)
                all_options_values.append(value)
            elif option.output_result not in all_options_values:
                all_options.append(option)
                all_options_values.append(value)
        output.options = all_options
        return output

