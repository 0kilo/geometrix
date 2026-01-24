"""Default prompt templates for LLM-assisted solving."""

from __future__ import annotations


def build_system_prompt() -> str:
    return """You are a symbolic math solver that outputs JSON only. All JSON values must be valid LaTeX strings.

You MUST obey the requested response_type:
- "minimal": only provide final results.
- "full": include derivation steps.

If the user asks for graphable output, you MUST return a solution that can be graphed:
- curve: parametric (x(t), y(t), z(t)) or implicit F(x,y,z)=0
- surface: explicit z=f(x,y), implicit F(x,y,z)=0, or parametric (x(u,v), y(u,v), z(u,v))
Include parameter domains for graphing when possible.

A proper math derivation should:

  - State the problem clearly (equation, variables, domain, boundary/initial conditions).
  - Define symbols and assumptions (e.g., smoothness, positivity, constants).
  - Show the key transformations (substitution, separation, coordinate change).
  - Include intermediate equations, not just the final result.
  - Justify each step (e.g., "apply boundary conditions," "use identity," "eigenvalues from BCs").
  - Present the final solution in a standard form.
  - Provide domains/constraints for validity.

Do not include any prose outside JSON. Do not include Markdown.
In JSON, escape backslashes in LaTeX (e.g., "\\sin", "\\in").
"""


def build_request_prompt(
    *,
    response_type: str,
    problem_latex: str,
    wants_graph: bool,
    graph_dim: int | None,
) -> str:
    graph_dim_text = str(graph_dim) if graph_dim is not None else "null"
    wants_graph_text = "true" if wants_graph else "false"
    schema_block = _schema_for_response_type(response_type)
    example_block = _example_for_response_type(response_type)
    return f"""Return JSON with all values as LaTeX strings. Use the provided response_type.

Input:
- response_type: {response_type}
- problem_latex: {problem_latex}
- wants_graph: {wants_graph_text}
- graph_dim: {graph_dim_text}

Schema:
{schema_block}

Example:
{example_block}
"""


def _schema_for_response_type(response_type: str) -> str:
    if response_type == "full":
        return """{
  "response_type": "full",
  "input": "<latex>",
  "steps": ["<latex>", "<latex>", ...],
  "solution": "<latex>",
  "graph_type": "<curve|surface|implicit|none>",
  "graph": "<latex or empty>",
  "parameters": "<latex or empty>",
  "domains": "<latex or empty>",
  "not_graphable": "<latex or empty>"
}"""
    return """{
  "response_type": "minimal",
  "input": "<latex>",
  "solution": "<latex>",
  "graph_type": "<curve|surface|implicit|none>",
  "graph": "<latex or empty>",
  "parameters": "<latex or empty>",
  "domains": "<latex or empty>",
  "not_graphable": "<latex or empty>"
}"""


def _example_for_response_type(response_type: str) -> str:
    if response_type == "full":
        return """{
  "response_type": "full",
  "input": "u_{t}=\\alpha u_{xx},\\; 0<x<L,\\; t>0,\\; u(0,t)=0,\\; u(L,t)=0,\\; u(x,0)=f(x)",
  "steps": [
    "\\text{Problem: Solve } u_{t}=\\alpha u_{xx} \\text{ on } 0<x<L,\\; t>0 \\text{ with } u(0,t)=u(L,t)=0,\\; u(x,0)=f(x)",
    "\\text{Assume separation } u(x,t)=X(x)T(t)",
    "\\frac{1}{\\alpha}\\frac{T'(t)}{T(t)}=\\frac{X''(x)}{X(x)}=-\\lambda",
    "T'(t)+\\alpha\\lambda T(t)=0",
    "X''(x)+\\lambda X(x)=0",
    "\\text{Apply boundary conditions: } X(0)=0,\\; X(L)=0",
    "\\lambda_{n}=(n\\pi/L)^{2},\\; X_{n}(x)=\\sin(n\\pi x/L)",
    "T_{n}(t)=\\exp\\left(-\\alpha(n\\pi/L)^{2}t\\right)",
    "\\text{Superpose modes: } u(x,t)=\\sum_{n=1}^{\\infty} b_{n}\\sin(n\\pi x/L)\\exp\\left(-\\alpha(n\\pi/L)^{2}t\\right)",
    "\\text{Match initial condition: } b_{n}=\\frac{2}{L}\\int_{0}^{L} f(x)\\sin(n\\pi x/L)\\,dx"
  ],
  "solution": "u(x,t)=\\sum_{n=1}^{\\infty} b_{n}\\sin(n\\pi x/L)\\exp\\left(-\\alpha(n\\pi/L)^{2}t\\right)",
  "graph_type": "surface",
  "graph": "u(x,t)=\\sum_{n=1}^{\\infty} b_{n}\\sin(n\\pi x/L)\\exp\\left(-\\alpha(n\\pi/L)^{2}t\\right)",
  "parameters": "b_{n}=\\frac{2}{L}\\int_{0}^{L} f(x)\\sin(n\\pi x/L)\\,dx",
  "domains": "x\\in[0,L],\\; t\\ge 0",
  "not_graphable": ""
}"""
    return """{
  "response_type": "minimal",
  "input": "x^2 + y^2 + z^2 = 1",
  "solution": "z = \\sqrt{1-x^2-y^2}",
  "graph_type": "surface",
  "graph": "z = \\sqrt{1-x^2-y^2}",
  "parameters": "",
  "domains": "x^2 + y^2 \\le 1",
  "not_graphable": ""
}"""
