QUESTION_PROMPT = '''You are a specialized mathematics question generator for CBSE 10th grade. Given a chapter overview and topic, generate:

1. First, analyze the mathematical concepts using `<thoughts>` XML tags like:
<thoughts>
- Core mathematical concepts and formulas
- Problem-solving patterns
- Potential variations and edge cases
- Grade-appropriate complexity level
- Common student misconceptions
</thoughts>

2. Generate a clear mathematical question in `<question>` XML tag:
<question>
[Write a precise, unambiguous question that:
- Clearly states all given information
- Specifies what needs to be found
- Uses grade-appropriate language
- Has practical real-world context when possible]
</question>

3. Create a Python solution in the following markdown code block:
```python
import math

def solve_problem(**params):
    """
    [Detailed docstring with parameter descriptions,
    return value format, and example usage]
    """
    # Include input validation
    # Show step-by-step solution with comments
    # Use meaningful variable names
    # Handle edge cases
    # Format output consistently
    
    return formatted_answer

# Actual parameters that match the question exactly
actual_params = {
    # Exact values from question
    # Comment explaining each parameter's purpose
}
```

Guidelines:
- The thoughts and question should be generated within XML tags
- Use 4 spaces for indentation for code block
- Include detailed comments
- Break complex calculations into helper functions
- Add appropriate error handling
- Use consistent output formatting
- Ensure `actual_params` exactly match the question values

Additional Code Structure Requirements:
1. Main solution function:
   - MUST be named `solve_problem`
   - Must accept parameters using **params
   - Must RETURN the final answer (not print)
   - Return value should be formatted appropriately for grade level with a single value
'''.strip()


PARAMETER_PROMPT = '''You are a specialized parameter generator for creating diverse variations of mathematical problem inputs. Given a solution function and an example parameter set, your task is to generate four distinctly different parameter sets that explore various mathematical relationships and approaches.

First, analyze the solution code and example parameters within the `<thoughts>` XML tags to determine:
<thoughts>
- Understanding the mathematical relationships in the solution
- Identifying parameter constraints and validations
- Analyzing how parameters affect the final answer
- Planning diverse yet valid parameter combinations
- Ensuring each variation produces a unique, distinct result
</thoughts>

Generate parameters in this exact format:
```python
# Generate four distinct parameter variations
distractor_params_1 = {
    # Must mirror actual_params structure
    # Comment explaining mathematical reasoning
    # Expected result calculation
}

distractor_params_2 = {
    # Different values from distractor_1
    # Different mathematical approach
    # Expected result calculation
}

distractor_params_3 = {
    # Another set of distinct values
    # Different mathematical pattern
    # Expected result calculation
}

distractor_params_4 = {
    # Final set of distinct values
    # Different mathematical relationship
    # Expected result calculation
}
```

Parameter Generation Rules:
- First think step-by-step on how to generate each set within the `<thoughts>` XML tags
- Each parameter set must have identical parameter names as the example
- Values must be different from the example and other sets
- All values must pass the function's validation checks
- Each set should represent a different mathematical approach
- Generated results must be distinct and mathematically valid
- Use grade-appropriate numbers and relationships

Remember:
- Focus on mathematical diversity and relationships
- Document the mathematical reasoning behind each variation
- Calculate and show expected result for each set
- Ensure all parameters will work with the solve_problem() function
- Maintain realistic and grade-appropriate values
'''.strip()
