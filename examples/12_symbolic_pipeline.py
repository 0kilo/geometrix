# Example: symbolic parsing, simplification, and solving.
# Demonstrates the LaTeX-first symbolic pipeline.
import sympy as sp

from geometrix import canonicalize, latex, latex_equation, simplify, solve

# Symbols used in the algebraic system.
x, y = sp.symbols("x y")

# Parse a LaTeX expression and normalize it.
expr = latex("x^2 - 1")
print("canonical:", canonicalize(expr))
print("simplify:", simplify(expr, mode="factor"))

# Solve a simple linear system.
solutions = solve([x + y - 1, x - y - 1], [x, y], dict=True)
print("solutions:", solutions)

# Parse a LaTeX equation into SymPy.
(eq,) = [latex_equation("x = 2")]
print("equation:", eq)
