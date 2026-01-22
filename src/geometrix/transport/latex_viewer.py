"""LaTeX preview utilities for notebooks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LatexPreview:
    html: str


def latex_html(latex: str, inline: bool = True) -> LatexPreview:
    wrapper = "$" if inline else "$$"
    html = f"""
<div class=\"geometrix-latex\">{wrapper}{latex}{wrapper}</div>
<script>
if (!window.MathJax) {{
  const script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
  script.async = true;
  document.head.appendChild(script);
}}
</script>
"""
    return LatexPreview(html=html)


def show_latex(latex: str, inline: bool = True) -> None:
    preview = latex_html(latex, inline=inline)
    try:
        from IPython.display import HTML, display
    except ImportError as exc:
        raise RuntimeError("IPython is required to render LaTeX") from exc
    display(HTML(preview.html))
