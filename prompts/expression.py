from prompts.base import (PARAMETERS_TEMPLATE,
TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE, TOPIC_ONLY_TEMPLATE, Instance, DifficultyLevel,
SampleParameterInput, SampleParameterOutput, SampleQuestionInput, SampleQuestionOutput)


QUESTION_PROMPT = '''You are a specialized mathematics question generator for CBSE 10th grade. Given a topic, optional chapter overview and a difficulty level, generate:

1. First, analyze the mathematical concepts using `<thoughts>` XML tags:
<thoughts>
- Core mathematical concepts and formulas
- Algebraic and geometric relationships
- Problem-solving patterns and approaches
- Possible symbolic and expression solutions
- Common student misconceptions
- Question complexity and scaffolding based on provided difficulty level:
 * `easy`: Direct application of single concept, basic calculations and simple reasoning
 * `medium`: Multi-step problems combining 2-3 concepts with moderate computations
 * `hard`: Problems requiring thorough understanding of multiple concepts, careful reasoning and detailed calculations suitable for 10th grade
</thoughts>

2. Generate a clear mathematical question in `<question>` XML tag using LaTeX notation where needed:
<question>
[Write a precise, unambiguous question that:
- Uses proper mathematical notation with LaTeX ($...$ for inline math)
- May involve geometric figures, algebraic expressions, or numerical values
- Clearly states all given information
- Specifies what needs to be found]
</question>

3. Create a Python solution that can handle symbolic and numerical computations:
```python
import math
import sympy as sp
import numpy as np
from typing import Dict, List, Union

def solve_problem(**params):
    """
    Solves the mathematical problem, handling both symbolic and numerical cases.
    
    Args:
        **params: Problem parameters that could be numerical or symbolic
        
    Returns:
        Union[float, str, sp.Expr]: Solution that could be:
            - A numerical value (float)
            - A symbolic expression (sp.Expr) (preffered)
            - A LaTeX string for complex expressions (preffered)
    """
    # Initialize symbolic variables if needed
    # Use sympy for symbolic computations
    # Handle both numerical and symbolic cases
    # Format output appropriately (LaTeX strings when needed)
    
    return formatted_answer

# Actual parameters that match the question exactly
actual_params = {
    # Parameter values (numerical or symbolic)
    # Comment explaining each parameter
}
```

Guidelines:
- Use sympy for symbolic computations
- Format expressions in LaTeX when returning symbolic answers
- Handle both numerical and symbolic inputs
- Include comprehensive input validation
- Break complex calculations into helper functions
- Return either numerical values or LaTeX strings

Answer Format Requirements:
1. For numerical answers:
    - Return float or int values directly
2. For symbolic expressions:
    - Return LaTeX strings with proper formatting
    - Use $...$ notation for inline math
3. For geometric problems:
    - Consider using sympy.geometry for calculations
    - Return angles in degrees when appropriate

Common Return Types:
1. Numerical: `return 0.5`
2. Fraction: `return sp.latex(sp.Rational(1, 2))`
3. Symbolic: `return sp.latex(sp.sqrt(3)/2)`
4. Trigonometric: `return sp.latex(sp.cos(sp.pi/3))`
'''.strip()

PARAMETER_PROMPT = """You are a specialized parameter generator for creating variations of mathematical problems that may involve symbolic expressions. Given a solution function and example parameters, generate four distinctly different parameter sets.

First, analyze the solution approach:
<thoughts>
- Identify if the problem is numerical, symbolic, or mixed
- Understand the mathematical relationships
- Consider valid parameter ranges and constraints
- Plan variations that test different cases
- Ensure generated expressions are grade-appropriate
</thoughts>

Generate parameters in this format:
```python
# Four distinct parameter variations that work with the solution
param_set_1 = {
    # Parameters that produce a different valid answer
    # May include symbolic or numerical values
    # Comment explaining mathematical significance
}

param_set_2 = {
    # Another set of parameters
    # Different mathematical approach
    # May use different symbolic forms
}

param_set_3 = {
    # Third variation
    # Different mathematical pattern
    # Consider alternative representations
}

param_set_4 = {
    # Final variation
    # Different mathematical relationship
    # May mix symbolic and numerical values
}
```

Parameter Generation Rules:
- Parameters can be numerical or symbolic expressions
- Each set should produce mathematically distinct results
- Consider both exact and approximate forms
- Use appropriate trigonometric values (π/6, π/4, π/3, etc.)
- Include common mathematical constants when relevant
- Ensure expressions are in simplified form
- Use grade-appropriate values and relationships

Remember:
- Generate both numerical and symbolic variations when appropriate
- Document the expected result for each parameter set
- Ensure all parameters work with the solve_problem() function
- Keep expressions and calculations at 10th-grade level
- Consider multiple representations of the same value
""".strip()


QUESTION_ICL_EXAMPLE_1 = Instance(
    input=SampleQuestionInput(
        difficulty_level=DifficultyLevel.HARD,
        topic="Word Problems on Time, Speed and Distance using Quadratic Equations with expression as a solution"
    ),
    output=SampleQuestionOutput(
        thoughts='''
<thoughts>
- Need a quadratic equation that emerges naturally from the problem
- Should involve more than one unknown variable
- Include speed ratios that lead to algebraic expressions
- Solution should require step-by-step algebraic manipulation
- Include relative speed concepts
- Make it contextually relevant to real-world scenarios
</thoughts>''',
    question='''
<question>
A car and a bike start moving from the same point in the same direction. The car's speed is thrice the bike's speed. If the car overtakes the bike after $t$ hours and is $36$ km ahead of the bike at that time, express the bike's speed in terms of $t$.
</question>
    ''',
    code='''
```python
import math
import sympy as sp
import numpy as np
from typing import Dict, List, Union

def solve_problem(**params):
    """
    Solves for the bike's speed in terms of time t.
    
    Args:
        t (sp.Symbol): Time taken for car to overtake bike
        distance_gap (float): Distance between vehicles when car overtakes bike
        speed_ratio (float): Ratio of car's speed to bike's speed
        
    Returns:
        str: LaTeX formatted expression for bike's speed
    """
    # Initialize symbolic variable
    t = params['t']
    distance_gap = params['distance_gap']
    speed_ratio = params['speed_ratio']
    
    # Let bike's speed be x km/hr
    x = sp.Symbol('x')
    
    # Distance covered by bike = x * t
    # Distance covered by car = 3x * t
    # Difference in distance = 36
    # (3x * t) - (x * t) = 36
    
    # Form equation: 2x * t = 36
    equation = sp.Eq((speed_ratio * x * t) - (x * t), distance_gap)
    
    # Solve for x
    bike_speed = sp.solve(equation, x)[0]
    
    # Simplify the expression
    bike_speed = sp.simplify(bike_speed)
    
    return sp.latex(bike_speed)

# Parameters for the main question
actual_params = {
    't': sp.Symbol('t'),
    'distance_gap': 36,
    'speed_ratio': 3
}
```
'''
    )
)

PARAMETER_ICL_EXAMPLE_1 = Instance(
    input=SampleParameterInput(
        code='''
```python
import math
import sympy as sp
import numpy as np
from typing import Dict, List, Union

def solve_problem(**params):
    """
    Solves for the bike's speed in terms of time t.
    
    Args:
        t (sp.Symbol): Time taken for car to overtake bike
        distance_gap (float): Distance between vehicles when car overtakes bike
        speed_ratio (float): Ratio of car's speed to bike's speed
        
    Returns:
        str: LaTeX formatted expression for bike's speed
    """
    # Initialize symbolic variable
    t = params['t']
    distance_gap = params['distance_gap']
    speed_ratio = params['speed_ratio']
    
    # Let bike's speed be x km/hr
    x = sp.Symbol('x')
    
    # Distance covered by bike = x * t
    # Distance covered by car = 3x * t
    # Difference in distance = 36
    # (3x * t) - (x * t) = 36
    
    # Form equation: 2x * t = 36
    equation = sp.Eq((speed_ratio * x * t) - (x * t), distance_gap)
    
    # Solve for x
    bike_speed = sp.solve(equation, x)[0]
    
    # Simplify the expression
    bike_speed = sp.simplify(bike_speed)
    
    return sp.latex(bike_speed)

# Parameters for the main question
sample_params = {
    't': sp.Symbol('t'),
    'distance_gap': 36,
    'speed_ratio': 3
}
```
'''
    ),
    output=SampleParameterOutput(
        thoughts='''
<thoughts>
For generating parameter variations, let's think strategically:

1. Mathematical Pattern Analysis:
- Each parameter set needs to yield a different symbolic expression
- The formula structure is `distance_gap / (t * (speed_ratio - 1))`
- Need to vary both distance_gap and speed_ratio to get distinct results
- Keep 't' as the symbolic variable in all cases

2. Value Selection Strategy:
- Base case gives 18/t (36/(2*t) where 2 comes from 3-1)
- Can modify either numerator or denominator for distinct results
- Distance gaps: using 36, 48 affects numerator directly
- Speed ratios: using 2,3,4,5 affects denominator via (ratio-1)

3. Result Distinctness:
- Result 1: 24/t (from 48 gap, ratio 3)
- Result 2: 12/t (from 36 gap, ratio 4)
- Result 3: 9/t (from 36 gap, ratio 5)
- Result 4: 36/t (from 36 gap, ratio 2)
- Verified all results are mathematically different

4. Educational Value:
- Parameters showcase different ways same answer form can arise
- Numbers chosen are manageable for mental math
- Ratios are reasonable in real-world context
</thoughts>
''',
    parameters_code='''
```python
# Generate different variations of parameters
param_set_1 = {
    't': sp.Symbol('t'),
    'distance_gap': 48,
    'speed_ratio': 3
    # Expected result: 24/t
}

param_set_2 = {
    't': sp.Symbol('t'),
    'distance_gap': 36,
    'speed_ratio': 4
    # Expected result: 12/t
}

param_set_3 = {
    't': sp.Symbol('t'),
    'distance_gap': 36,
    'speed_ratio': 5
    # Expected result: 9/t
}

param_set_4 = {
    't': sp.Symbol('t'),
    'distance_gap': 36,
    'speed_ratio': 2
    # Expected result: 36/t
}
```
'''
    )
)


QUESTION_ICL_EXAMPLE_2 = Instance(
    input=SampleQuestionInput(
        difficulty_level=DifficultyLevel.MEDIUM,
        topic="Simplifying Trigonometric Expressions",
        chapter_overview="Teaches advanced techniques for reducing complex trigonometric expressions using known identities and algebra."
    ),
    output=SampleQuestionOutput(
        thoughts='''
<thoughts>
1. Core Concepts to Test:
- Application of multiple trigonometric identities
- Strategic simplification steps
- Pattern recognition in expressions
- Understanding of Pythagorean identities
- Relationship between reciprocal functions

2. Design Considerations:
- Need an expression complex enough to require multiple steps
- Should involve at least 2-3 different trig functions
- Expression should simplify elegantly
- Must be verifiable through systematic computation
- Should test both algebraic and trigonometric skills

3. Educational Value:
- Tests understanding of fundamental identities
- Requires strategic thinking in simplification
- Builds problem-solving confidence
- Demonstrates practical application of identities
</thoughts>''',
    question='''
<question>
If $\theta$ is an acute angle, simplify the expression:
$\frac{\sin^2 \theta \cos \theta + \cos^3 \theta}{\sin^2 \theta + \cos^2 \theta}$
to its simplest form.
</question>
''',
    code='''
```python
import math
import sympy as sp
import numpy as np
from typing import Dict, List, Union

def solve_problem(**params):
    """
    Simplifies a trigonometric expression using given angle value or symbolically.
    
    Args:
        theta (Union[float, sp.Symbol]): Angle in radians
        evaluate (bool): Whether to evaluate numerically or keep symbolic
        
    Returns:
        str: LaTeX formatted simplified expression
    """
    # Initialize symbolic variable
    theta = params['theta']
    evaluate = params.get('evaluate', False)
    
    # Create the expression
    sin_theta = sp.sin(theta)
    cos_theta = sp.cos(theta)
    
    # Build numerator and denominator
    numerator = sin_theta**2 * cos_theta + cos_theta**3
    denominator = sin_theta**2 + cos_theta**2
    
    # Form the expression
    expression = numerator/denominator
    
    # Simplify using trigonometric identities
    # sin²θ + cos²θ = 1
    denominator = 1  # Using the identity
    
    # Factor out cos θ from numerator
    # cos θ(sin²θ + cos²θ)
    simplified = cos_theta * (sin_theta**2 + cos_theta**2)
    simplified = sp.simplify(simplified)
    
    if evaluate and not isinstance(theta, sp.Symbol):
        return sp.latex(simplified.evalf())
    return sp.latex(simplified)

# Parameters for the main question
actual_params = {
    'theta': sp.Symbol('theta'),
    'evaluate': False
}
```
'''
    )
)

PARAMETER_ICL_EXAMPLE_2 = Instance(
    input=SampleParameterInput(
        code='''
```python
import math
import sympy as sp
import numpy as np
from typing import Dict, List, Union

def solve_problem(**params):
    """
    Simplifies a trigonometric expression using given angle value or symbolically.
    
    Args:
        theta (Union[float, sp.Symbol]): Angle in radians
        evaluate (bool): Whether to evaluate numerically or keep symbolic
        
    Returns:
        str: LaTeX formatted simplified expression
    """
    # Initialize symbolic variable
    theta = params['theta']
    evaluate = params.get('evaluate', False)
    
    # Create the expression
    sin_theta = sp.sin(theta)
    cos_theta = sp.cos(theta)
    
    # Build numerator and denominator
    numerator = sin_theta**2 * cos_theta + cos_theta**3
    denominator = sin_theta**2 + cos_theta**2
    
    # Form the expression
    expression = numerator/denominator
    
    # Simplify using trigonometric identities
    # sin²θ + cos²θ = 1
    denominator = 1  # Using the identity
    
    # Factor out cos θ from numerator
    # cos θ(sin²θ + cos²θ)
    simplified = cos_theta * (sin_theta**2 + cos_theta**2)
    simplified = sp.simplify(simplified)
    
    if evaluate and not isinstance(theta, sp.Symbol):
        return sp.latex(simplified.evalf())
    return sp.latex(simplified)

# Parameters for the main question
sample_params = {
    'theta': sp.Symbol('theta'),
    'evaluate': False
}
```
'''
    ),
    output=SampleParameterOutput(
        thoughts='''
<thoughts>
1. Parameter Strategy:
- Need angles that give distinct symbolic results
- Should consider special angles (π/6, π/4, π/3)
- Must verify results remain distinct
- Include both symbolic and numeric cases
- Consider angles from different quadrants

2. Result Analysis:
- Main answer simplifies to cos θ
- Need values that give distinctly different results
- Each result should be in reduced form
- Must avoid duplicate values
- Consider both exact and decimal forms

3. Variation Approach:
- Use different special angles
- Mix symbolic and numeric inputs
- Ensure results are mathematically distinguishable
- Keep expressions grade-appropriate
</thoughts>
''',
    parameters_code='''
```python
# Generate different variations of parameters
param_set_1 = {
    'theta': sp.pi/6,  # 30 degrees
    'evaluate': True
    # Expected result: cos(π/6) = √3/2
}

param_set_2 = {
    'theta': sp.pi/4,  # 45 degrees
    'evaluate': True
    # Expected result: cos(π/4) = 1/√2
}

param_set_3 = {
    'theta': sp.pi/3,  # 60 degrees
    'evaluate': True
    # Expected result: cos(π/3) = 1/2
}

param_set_4 = {
    'theta': sp.pi/2,  # 90 degrees
    'evaluate': True
    # Expected result: cos(π/2) = 0
}
```
'''
    )
)


QUESTION_ICL_EXAMPLE_3 = Instance(
    input=SampleQuestionInput(
        difficulty_level=DifficultyLevel.EASY,
        topic="Calculating Mean (Assumed Mean Method)",
        chapter_overview="Teaches how to use the assumed mean method to simplify the calculation of the mean, especially with large data sets."
    ),
    output=SampleQuestionOutput(
        thoughts='''
<thoughts>
1. Core Statistical Concepts:
- Understanding of assumed mean method
- Deviation calculation from assumed mean
- Class intervals and frequency
- Property that shifting data preserves mean differences
- Weighted arithmetic calculations

2. Problem Design Strategy:
- Need grouped data with frequencies
- Values should be large enough to demonstrate method's utility
- Class intervals should be uniform
- Data should be realistic and contextual
- Final calculation should validate method's efficiency

3. Pedagogical Elements:
- Tests understanding of procedure
- Demonstrates computational advantage
- Reinforces frequency concepts
- Connects to real-world data
- Shows error checking methods
</thoughts>''',
    question='''
<question>
The following data shows the daily sales (in hundreds of rupees) of a shop for 50 days:

| Sales (in hundreds) | Number of Days |
|-------------------|----------------|
| 140-150          | 5              |
| 150-160          | 12             |
| 160-170          | 18             |
| 170-180          | 10             |
| 180-190          | 5              |

Using assumed mean method with assumed mean of 165, find the actual mean daily sales.
</question>
    ''',
    code='''
```python
import math
import sympy as sp
import numpy as np
from typing import Dict, List, Union

def solve_problem(**params):
    """
    Calculates mean using assumed mean method for grouped data.
    
    Args:
        class_intervals (List[List[float]]): List of class interval bounds
        frequencies (List[int]): List of frequencies
        assumed_mean (float): The assumed mean value
        class_size (float): Size of each class interval
        
    Returns:
        str: LaTeX formatted actual mean value
    """
    class_intervals = params['class_intervals']
    frequencies = params['frequencies']
    assumed_mean = params['assumed_mean']
    class_size = params['class_size']
    
    # Calculate class marks
    class_marks = [(interval[0] + interval[1])/2 for interval in class_intervals]
    
    # Calculate deviations from assumed mean
    deviations = [(mark - assumed_mean)/class_size for mark in class_marks]
    
    # Calculate frequency * deviation
    fd = [f * d for f, d in zip(frequencies, deviations)]
    
    # Sum of frequencies
    N = sum(frequencies)
    
    # Sum of frequency * deviation
    sum_fd = sum(fd)
    
    # Calculate correction factor
    correction = sum_fd/N * class_size
    
    # Calculate actual mean
    actual_mean = assumed_mean + correction
    
    # Format for display
    if isinstance(actual_mean, sp.Expr):
        return sp.latex(actual_mean)
    return f"{actual_mean:.2f}"

# Parameters for the main question
actual_params = {
    'class_intervals': [[140, 150], [150, 160], [160, 170], 
                       [170, 180], [180, 190]],
    'frequencies': [5, 12, 18, 10, 5],
    'assumed_mean': 165,
    'class_size': 10
}
```
'''
    )
)

PARAMETER_ICL_EXAMPLE_3 = Instance(
    input=SampleParameterInput(
        code='''
```python
import math
import sympy as sp
import numpy as np
from typing import Dict, List, Union

def solve_problem(**params):
    """
    Calculates mean using assumed mean method for grouped data.
    
    Args:
        class_intervals (List[List[float]]): List of class interval bounds
        frequencies (List[int]): List of frequencies
        assumed_mean (float): The assumed mean value
        class_size (float): Size of each class interval
        
    Returns:
        str: LaTeX formatted actual mean value
    """
    class_intervals = params['class_intervals']
    frequencies = params['frequencies']
    assumed_mean = params['assumed_mean']
    class_size = params['class_size']
    
    # Calculate class marks
    class_marks = [(interval[0] + interval[1])/2 for interval in class_intervals]
    
    # Calculate deviations from assumed mean
    deviations = [(mark - assumed_mean)/class_size for mark in class_marks]
    
    # Calculate frequency * deviation
    fd = [f * d for f, d in zip(frequencies, deviations)]
    
    # Sum of frequencies
    N = sum(frequencies)
    
    # Sum of frequency * deviation
    sum_fd = sum(fd)
    
    # Calculate correction factor
    correction = sum_fd/N * class_size
    
    # Calculate actual mean
    actual_mean = assumed_mean + correction
    
    # Format for display
    if isinstance(actual_mean, sp.Expr):
        return sp.latex(actual_mean)
    return f"{actual_mean:.2f}"

# Parameters for the main question
sample_params = {
    'class_intervals': [[140, 150], [150, 160], [160, 170], 
                       [170, 180], [180, 190]],
    'frequencies': [5, 12, 18, 10, 5],
    'assumed_mean': 165,
    'class_size': 10
}
```
'''
    ),
    output=SampleParameterOutput(
        thoughts='''
<thoughts>
1. Parameter Variation Strategy:
- Need different class intervals but same structure
- Maintain realistic sales data contexts
- Vary frequencies while keeping total constant
- Choose different assumed means
- Ensure distinct final answers
- Keep computations manageable

2. Data Distribution Considerations:
- Mix of symmetric and skewed distributions
- Different central tendencies
- Realistic frequency patterns
- Various spread patterns
- Maintain data integrity

3. Result Distinctness:
- Each parameter set should yield different mean
- Results should be distinguishable
- Maintain reasonable value ranges
- Avoid very close results
- Keep numbers practical
</thoughts>
''',
    parameters_code='''
```python
# Generate different variations of parameters
param_set_1 = {
    'class_intervals': [[140, 150], [150, 160], [160, 170], 
                       [170, 180], [180, 190]],
    'frequencies': [8, 15, 12, 10, 5],  # More left-skewed
    'assumed_mean': 165,
    'class_size': 10
    # Expected result: ~162.80
}

param_set_2 = {
    'class_intervals': [[140, 150], [150, 160], [160, 170], 
                       [170, 180], [180, 190]],
    'frequencies': [5, 10, 15, 12, 8],  # More right-skewed
    'assumed_mean': 165,
    'class_size': 10
    # Expected result: ~166.60
}

param_set_3 = {
    'class_intervals': [[140, 150], [150, 160], [160, 170], 
                       [170, 180], [180, 190]],
    'frequencies': [6, 14, 20, 8, 2],  # Peaked distribution
    'assumed_mean': 165,
    'class_size': 10
    # Expected result: ~162.20
}

param_set_4 = {
    'class_intervals': [[140, 150], [150, 160], [160, 170], 
                       [170, 180], [180, 190]],
    'frequencies': [10, 10, 10, 10, 10],  # Uniform distribution
    'assumed_mean': 165,
    'class_size': 10
    # Expected result: ~165.00
}
```
'''
    )
)


QUESTION_ICL_MESSAGES = [{
    "role": "user",
    "content": TOPIC_ONLY_TEMPLATE.format(topic=QUESTION_ICL_EXAMPLE_1.input.topic, result_type="symbolic or expression", difficulty_level=QUESTION_ICL_EXAMPLE_1.input.difficulty_level)
}, {
    "role": "assistant",
    "content": '\n'.join([QUESTION_ICL_EXAMPLE_1.output.thoughts, QUESTION_ICL_EXAMPLE_1.output.question, QUESTION_ICL_EXAMPLE_1.output.code])
}, {
    "role": "user",
    "content": TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE.format(topic=QUESTION_ICL_EXAMPLE_2.input.topic, chapter_overview=QUESTION_ICL_EXAMPLE_2.input.chapter_overview, result_type="symbolic or expression", difficulty_level=QUESTION_ICL_EXAMPLE_2.input.difficulty_level)
}, {
    "role": "assistant",
    "content": '\n'.join([QUESTION_ICL_EXAMPLE_2.output.thoughts, QUESTION_ICL_EXAMPLE_2.output.question, QUESTION_ICL_EXAMPLE_2.output.code])
}, {
    "role": "user",
    "content": TOPIC_AND_CHAPTER_OVERVIEW_TEMPLATE.format(topic=QUESTION_ICL_EXAMPLE_3.input.topic, chapter_overview=QUESTION_ICL_EXAMPLE_3.input.chapter_overview, result_type="symbolic or expression", difficulty_level=QUESTION_ICL_EXAMPLE_3.input.difficulty_level)
}, {
    "role": "assistant",
    "content": '\n'.join([QUESTION_ICL_EXAMPLE_3.output.thoughts, QUESTION_ICL_EXAMPLE_3.output.question, QUESTION_ICL_EXAMPLE_3.output.code])
}]


PARAMETER_ICL_MESSAGES = [{
    "role": "user",
    "content": PARAMETERS_TEMPLATE.format(code=PARAMETER_ICL_EXAMPLE_1.input.code)
}, {
    "role": "assistant",
    "content": '\n'.join([PARAMETER_ICL_EXAMPLE_1.output.thoughts, PARAMETER_ICL_EXAMPLE_1.output.parameters_code])
}, {
    "role": "user",
    "content": PARAMETERS_TEMPLATE.format(code=PARAMETER_ICL_EXAMPLE_2.input.code)
}, {
    "role": "assistant",
    "content": '\n'.join([PARAMETER_ICL_EXAMPLE_2.output.thoughts, PARAMETER_ICL_EXAMPLE_2.output.parameters_code])
}, {
    "role": "user",
    "content": PARAMETERS_TEMPLATE.format(code=PARAMETER_ICL_EXAMPLE_3.input.code)
}, {
    "role": "assistant",
    "content": '\n'.join([PARAMETER_ICL_EXAMPLE_3.output.thoughts, PARAMETER_ICL_EXAMPLE_3.output.parameters_code])
}]
