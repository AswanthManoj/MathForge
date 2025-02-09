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
    'frequencies': [10, 10, 10, 10, 10],  # Uniform distribution
    'assumed_mean': 165,
    'class_size': 10
    # Expected result: ~165.00
}

print(solve_problem(**actual_params))
