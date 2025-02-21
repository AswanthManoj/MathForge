from prompts.base import (PARAMETERS_TEMPLATE,
TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE, TOPIC_ONLY_TEMPLATE, Instance, DifficultyLevel,
SampleParameterInput, SampleParameterOutput, SampleQuestionInput, SampleQuestionOutput)

STATEMENT_PROMPT = '''You are a specialized mathematics question generator for CBSE 10th grade. Given a topic, optional chapter overview and a difficulty level, generate:

1. First, analyze the mathematical concepts using `<thoughts>` XML tags:
<thoughts>
- Core mathematical concepts and formulas
- Algebraic and geometric relationships 
- Problem-solving patterns and approaches
- Common misconceptions and incorrect reasoning
- Common student errors and plausible distractors
- Question complexity and scaffolding based on provided difficulty level:
 * `easy`: Direct application of single concept, basic calculations and simple reasoning
 * `medium`: Multi-step problems combining 2-3 concepts with moderate computations
 * `hard`: Problems requiring thorough understanding of multiple concepts, careful reasoning and detailed calculations suitable for 10th grade
</thoughts>

2. Generate a clear mathematical question in `<question>` XML tag:
<question>
[Write a precise, unambiguous question that:
- Uses proper mathematical notation with LaTeX ($...$ for inline math)
- If the question contains tables, ensure that proper github flavored markdown table syntax is used
- May involve geometric figures, algebraic expressions, or numerical values
- Clearly states all given information
- Asks for a conclusion that can be expressed as a statement
- Can be verified through mathematical computation]
</question>

3. Create a Python solution that validates mathematical statements:
```python
import math
import sympy as sp
import numpy as np
from typing import Dict, List, Union, Tuple

def solve_problem(**params) -> Tuple[Union[float, str, sp.Expr], str, List[str]]:
    """
    Solves the mathematical problem, generates a verified statement, and plausible distractors.
    
    Args:
        **params: Problem parameters that could be numerical or symbolic
        
    Returns:
        Tuple containing:
            - Union[float, str, sp.Expr]: Computed result that could be:
                * A numerical value (float)
                * A symbolic expression (sp.Expr)
                * A LaTeX string for complex expressions
            - str: A mathematically precise statement that:
                * Describes the conclusion based on computation
                * Must be short statements suitable for MCQ
                * References specific values or relationships
            - List[str]: Four distinct distractor statements that are:
                * Must be short statements suitable for MCQ
                * Follow exact same pattern as verified statement
                * Differ only in values, relationships, or reasoning
                * Maintain same linguistic structure
                * Represent different types of errors
    """
    # Initialize symbolic variables if needed
    # Use sympy for symbolic computations
    # Handle both numerical and symbolic cases
    # Format numerical/symbolic output appropriately
    # Generate corresponding statement with reasoning
    # Generate list of plausible distractor statements
    
    return formatted_answer, verified_statement, distractor_statements

# Actual parameters that match the question exactly
actual_params = {
    # Parameter values (numerical or symbolic)
    # Comment explaining each parameter
}

Guidelines:

1. Statement Generation:
- Base statements on mathematical principles
- Include relevant numerical values or relationships
- Keep statements concise and focused
- Use consistent mathematical terminology

2. Computation Output:
- For numerical answers: Return float/int values
- For symbolic expressions: Return LaTeX strings
- For geometric problems: Include angle measures and relationships

3. Distractor Generation:
- Based on calculation errors (e.g., wrong arithmetic)
- Based on concept misapplication (e.g., wrong formula)
- Based on incomplete logic (e.g., missing conditions)
- Based on related concept confusion (e.g., similar theorems)

4. Return Format Examples:
    a) Numerical with Statements:
        ```python
        return (
            3.14159,
            "The area is π square units since the radius is 1 unit",
            [
                "The area is 2π square units since the radius is 2 units",
                "The area is π/2 square units since the radius is half the diameter",
                "The area is 3.14 square units since π is approximately 3.14",
                "The area is π cubic units since this is a three-dimensional shape"
            ]
        )
        ```
    
    b) Symbolic with Statements:
        ```python
        return (
            sp.latex(sp.sqrt(3)/2),
            "The height is $\\frac{\\sqrt{3}}{2}$ units since this is an equilateral triangle",
            [
                "The height is $\\sqrt{3}$ units since this is an equilateral triangle",
                "The height is $\\frac{3}{2}$ units since this is an equilateral triangle",
                "The height is $1$ unit since this is an equilateral triangle",
                "The height is $2$ units since this is an equilateral triangle"
            ]
        )
        ```

5. Statement Pattern Requirements:
   - Correct statement sets the pattern: "[Conclusion] [because/since/as] [reasoning]"
   - All distractors must follow this exact pattern
   - Only mathematical content should vary, not structure
   - Use same connecting words (because/since/as) as correct statement
   - Keep same level of detail in reasoning
   - Maintain consistent mathematical terminology
   - All statements should be short suitable for to be used as options in MCQ

**Remember:**
* All statements should be brief and clear
* Distractors should be based on common student errors
* Maintain consistent mathematical language
* Each distractor should represent a different type of error
* Keep similar structure between correct and incorrect statements
'''.strip()

ICL_EXAMPLE = Instance(
    input=SampleQuestionInput(
        topic="Practical Applications of Heights and Distances",
        chapter_overview="""Shows how trigonometry can be used in various fields such as navigation, surveying and astronomy to measure heights and distances in real world situations.
Question must be from the following sub topic: "Application of similarity of triangles in height and distance problems".""",
        difficulty_level=DifficultyLevel.MEDIUM
    ),
    output=SampleQuestionOutput(
        thoughts="""- Core concepts: Similar triangles, trigonometric ratios (tan θ), angle of elevation
- Key relationships: Corresponding angles in similar triangles are equal
- Problem-solving patterns: Creating similar triangles using eye level and object height
- Common misconceptions: 
  * Confusing angle of elevation with angle of depression
  * Incorrect identification of corresponding sides
- Plausible distractors can focus on:
  * Wrong trigonometric ratio selection
  * Calculation errors in similar triangle proportions
  * Misidentification of parallel lines
- For medium difficulty: Combine angle of elevation with similar triangles requiring 2-3 steps
""",
    question="""A surveyor stands at point A, 50 meters away from the foot of a tower. She observes the top of the tower with an angle of elevation of 30°. When she walks 20 meters closer to the tower to point B, the angle of elevation increases to 45°. If her eye level is 1.6 meters above the ground, find the height of the tower.
[Use $\tan(30°) = \frac{1}{\sqrt{3}}$ and $\tan(45°) = 1$]""",
    code = '''
```python
import math
import sympy as sp
from typing import Dict, List, Union, Tuple

def solve_problem(distance_A: float, distance_B: float, eye_level: float, 
                 tan_30: float, tan_45: float) -> Tuple[float, str, List[str]]:
    """
    Solves the tower height problem using angles of elevation from two points.
    
    Args:
        distance_A: Distance from point A to tower (m)
        distance_B: Distance from point B to tower (m)
        eye_level: Height of surveyor's eyes (m)
        tan_30: Tangent of 30 degrees
        tan_45: Tangent of 45 degrees
    
    Returns:
        Tuple of (height, verified_statement, distractors)
    """
    # Calculate heights from both positions
    height_from_A = distance_A * tan_30 + eye_level
    height_from_B = distance_B * tan_45 + eye_level
    
    # Heights should be equal - use average to handle floating point
    tower_height = (height_from_A + height_from_B) / 2
    
    # Round to 1 decimal place for clarity
    tower_height = round(tower_height, 1)
    
    verified = (f"The tower height is {tower_height} meters since the angles of "
               f"elevation of 30° and 45° from distances of 50m and 30m give equal heights")
    
    distractors = [
        # Wrong trig ratio (using sin instead of tan)
        f"The tower height is {round(50 * 0.5 + 1.6, 1)} meters since sine of 30° is 0.5",
        # Forgot to add eye level
        f"The tower height is {round(50 / math.sqrt(3), 1)} meters since we only need to use tan(30°)",
        # Used wrong distance with 45° angle
        f"The tower height is {round(50 * 1 + 1.6, 1)} meters since tan(45°) equals 1",
        # Added distances instead of using closer distance
        f"The tower height is {round(70 / math.sqrt(3) + 1.6, 1)} meters since we use the total distance of 70m"
    ]
    
    return tower_height, verified, distractors

# Actual parameters
actual_params = {
    'distance_A': 50,  # meters from point A
    'distance_B': 30,  # meters from point B
    'eye_level': 1.6,  # meters
    'tan_30': 1/math.sqrt(3),  # tan(30°)
    'tan_45': 1  # tan(45°)
}
```'''.strip())
)

ICL_MESSAGE = [{
    "role": "user",
    "content": TOPIC_ONLY_TEMPLATE.format(topic=ICL_EXAMPLE.input.topic, result_type="statement", difficulty_level=ICL_EXAMPLE.input.difficulty_level)
}, {
    "role": "assistant",
    "content": '\n'.join([ICL_EXAMPLE.output.thoughts, ICL_EXAMPLE.output.question, ICL_EXAMPLE.output.code])
}]
