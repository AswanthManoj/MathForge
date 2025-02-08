import math, ast
from pydantic import BaseModel
from typing import List, Optional
from prompt import (ParameterGeneratorOutput,  
extract_generator_content, extract_parameter_content,
PARAMETER_GENERATOR, CODE_GENERATOR, CodeGeneratorOutput)
from llm_connector import LLMConnector, AnthropicConfig, GoogleConfig, TogetherConfig


class SecurityException(Exception):
    pass

class Option(BaseModel):
    is_correct:    bool = False
    input_params:  dict
    output_result: Optional[int|float|str] = None

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
        
    async def _generate_question_and_code(self, topic: str, chapter_overview: str|None=None) -> CodeGeneratorOutput:
        if chapter_overview is not None:
            messages = [{
                "role": "user",
                "content": f"# Topic:\n{topic}\n\n---\n# Chapter Oerview:\n{chapter_overview}"
            }]
        else:
            messages = [{
                "role": "user",
                "content": f"# Topic:\n{topic}"
            }]
        return await self.llm.generate(
            messages=messages,
            system=CODE_GENERATOR,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            extractor_function=extract_generator_content,
        )
    
    async def _generate_parameters(self, actual_params: dict, code: str) -> ParameterGeneratorOutput:
        return await self.llm.generate(
            system=PARAMETER_GENERATOR,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            extractor_function=extract_parameter_content,
            messages=[{
                "role": "user",
                "content": f"Here is the code: \n```python\n{code}\n```\n\nHere is sample input for the `solve_problem` function: \n```python\n{actual_params}\n```""".strip()
            }], 
    ) 
        
    async def generate(self, topic: str, chapter_overview: str|None=None) -> FinalOutput:
        code_output = await self._generate_question_and_code(topic, chapter_overview)
        solve_function_namespace = self.safe_exec(
            code_output.code,
            disallowed_global_vars=['settings', 'llm'],
            disallowed_names=['os', 'sys', 'eval', 'exec'],
        )
        
        actual_params = solve_function_namespace.get('actual_params')
        solve_function = solve_function_namespace.get('solve_problem')
        
        params_output = await self._generate_parameters(actual_params, code_output.code)
        params_namespace = self.safe_exec(
            params_output.parameters_code,
            disallowed_global_vars=['settings', 'llm'],
            disallowed_names=['os', 'sys', 'eval', 'exec'],
        )

        distractor_params_1 = params_namespace.get('distractor_params_1')
        distractor_params_2 = params_namespace.get('distractor_params_2')
        distractor_params_3 = params_namespace.get('distractor_params_3')
        distractor_params_4 = params_namespace.get('distractor_params_4')
        distractor_params = [distractor_params_1, distractor_params_2, distractor_params_3, distractor_params_4]
        
        options = []
        if actual_params and 'solve_problem' in solve_function_namespace:
            result = solve_function(**actual_params)
            options.append(Option(
                is_correct=True,
                output_result=result, 
                input_params=actual_params  
            ))
        
        if distractor_params and 'solve_problem' in solve_function_namespace:
            for i, params in enumerate(distractor_params, 1):
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
        

