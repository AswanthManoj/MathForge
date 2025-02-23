import re
import ast
import math
import asyncio
import sympy as sp
import numpy as np
from typing import Optional, List, Tuple
from src.schema import SecurityException
from src.schema import SolverOutput, QuestionBank
from concurrent.futures import ThreadPoolExecutor

def convert_decimals_to_fraction(text):
    pattern = r'(-?\d*\.\d{6,})(?![a-zA-Z+\-*/^])'
    def replace_with_fraction(match):
        decimal = match.group(1)
        fraction = sp.Rational(str(decimal))
        return f"{fraction.numerator}/{fraction.denominator}"
    return re.sub(pattern, replace_with_fraction, text)

def format_result(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return str(round(value, 5) if isinstance(value, float) else value)
    if isinstance(value, (sp.Expr, sp.Symbol, sp.Matrix)):
        return sp.latex(value)
    
    # Handle sets - use curly braces
    if isinstance(value, set):
        formatted_items = [format_result(item) for item in value]
        return "\\{" + ", ".join(formatted_items) + "\\}"
        
    # Handle tuples - use parentheses (common for coordinates, ordered pairs)
    if isinstance(value, tuple):
        formatted_items = [format_result(item) for item in value]
        return "(" + ", ".join(formatted_items) + ")"
    
    if isinstance(value, list):
        formatted_items = [format_result(item) for item in value]
        return "[" + ", ".join(formatted_items) + "]"
    return str(value)

def remove_python_comments(text):
    return re.sub(r'\s*#.*', '', text)

def remove_print_statements(text):
    return re.sub(r'print\s*\([^)]*\)', '', text)

def extract_xml_content(text: str, tag: str) -> Optional[str]:
    """Extract content between XML tags, excluding the tags themselves."""
    pattern = fr'(?s)<{tag}>(.*?)</{tag}>'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None

def extract_iter_xml(text: str, tag: str) -> List[str]:
    output = []
    pattern = fr'<{tag}>(.*?)</{tag}>'
    for match in re.finditer(pattern, text, re.DOTALL):
        txt = match.group(1).strip()
        output.append(txt)
    return output

def extract_code_snippet(text: str, itered: bool=False, requires: list|None=None):
    if itered:
        code_blocks = re.finditer(r'```python\s*(.*?)\s*```', text, re.DOTALL)
        code = None
        for match in code_blocks:
            code = match.group(1).strip()
            if isinstance(requires, list):
                if all(tag in code for tag in requires):
                    return code
        return code
    code_match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL)
    return code_match.group(1).strip() if code_match else None

def extract_from_solver(text: str) -> SolverOutput:
    thoughts = extract_xml_content(text, 'thoughts')
    code = extract_code_snippet(text, itered=True)
    return SolverOutput(code=code, thoughts=thoughts)

def extract_from_verifier(text: str) -> Tuple[bool, SolverOutput]:
    thoughts = extract_xml_content(text, 'thoughts')
    need_update = ast.literal_eval(str(extract_xml_content(text, 'need_update')))
    code = extract_code_snippet(text, itered=True, requires=['solve_problem', 'actual_params'])
    return need_update, SolverOutput(code=code, thoughts=thoughts)

def extract_distractors(text: str) -> List[str]:
    return extract_iter_xml(text, 'option')

def extract_question(text: str) -> QuestionBank:
    thoughts = extract_xml_content(text, 'thoughts')
    questions_xml = extract_xml_content(text, 'questions')
    if questions_xml is not None:
        questions = extract_iter_xml(questions_xml, 'li')
    else:
        questions = extract_iter_xml(text, 'li')
    return QuestionBank(
        thoughts=thoughts, 
        questions=questions
    )

async def safe_exec(code, timeout: int = 5, disallowed_names=None, disallowed_global_vars=None):
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

