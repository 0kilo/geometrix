# Geometrix

LaTeX-first differential geometry renderer for Jupyter/Colab. Author geometry in a small DSL (or Python), compile to numeric buffers, and render with a Three.js viewer.

## Quickstart (Notebook)
```python
from geometrix import geom

scene = geom("""
coords: u v
X(u,v) = (u, v, 0)
render: surface X domain u:[0,1] v:[0,1] res 30 30
""")
scene.show()
```

## Colab
```python
from google.colab import output
output.enable_custom_widget_manager()
```
If widget support is unavailable, `geometrix.show()` falls back to an HTML renderer that loads Three.js from a CDN. Use the widget explicitly with `use_widget=True`.

## Development
```bash
# Python
python -m pytest

# JS
cd js
npm install
npm run build
```

## Project Layout
- `src/geometrix/`: Python package (parsing, sampling, scene, transport)
- `js/`: TypeScript widget frontend
- `tests/`: Python tests
- `examples/`: Notebooks
