import sympy as sp
from typing import Union

def solve_problem(**params):
    """
    Solves for the ratio of distance covered by train A to total distance.
    
    Args:
        d (Union[float, sp.Symbol]): Total distance between stations
        s (Union[float, sp.Symbol]): Speed of train A
        
    Returns:
        str: LaTeX formatted expression for the ratio
    """
    # Initialize symbolic variables
    d, s = sp.symbols('d s')
    
    # Time taken = d/(4s) hours
    time = d/(4*s)
    
    # Distance covered by train A = speed * time
    distance_A = s * time
    
    # Simplify the ratio of distance_A to total distance d
    ratio = sp.simplify(distance_A/d)
    
    # Convert to LaTeX string
    return sp.latex(ratio)

# Parameters for the main question
actual_params = {
    'd': sp.Symbol('d'),  # Total distance
    's': sp.Symbol('s')   # Speed of train A
}

print(solve_problem(**actual_params))