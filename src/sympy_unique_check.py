# from sympy.parsing.latex import parse_latex
# from sympy import simplify

# latex_expr1 = "$\\frac{2}{4}$"
# latex_expr2 = "$\\frac{1}{2}$"

# # Parse LaTeX expressions into SymPy expressions
# expr1 = parse_latex(latex_expr1)
# expr2 = parse_latex(latex_expr2)

# # Simplify the SymPy expressions
# simplified_expr1 = simplify(expr1)
# simplified_expr2 = simplify(expr2)

# # Check for mathematical equivalence
# if simplified_expr1 == simplified_expr2:
#     print(f"'{latex_expr1}' and '{latex_expr2}' are mathematically equivalent.")
# else:
#     print(f"'{latex_expr1}' and '{latex_expr2}' are NOT mathematically equivalent.")

# # You can also directly compare without explicit simplification in some cases,
# # but simplification is generally a good practice for robust equivalence checking.
# # if expr1 == expr2: # This might work for simple cases but not always reliably.
# #     print("Direct comparison: Expressions are equivalent (possibly without full simplification).")
# # else:
# #     print("Direct comparison: Expressions are NOT equivalent (or not recognized as such without simplification).")