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

## HTML UI Controls
```python
from dataclasses import replace
import numpy as np
from geometrix.api import SceneBundle, show
from geometrix.scene.build import build_surface_scene

u = np.linspace(0.0, 1.0, 20)
v = np.linspace(0.0, 1.0, 20)
uu, vv = np.meshgrid(u, v, indexing="ij")
positions = np.stack([uu, vv, 0 * uu], axis=-1).reshape(-1, 3).astype(np.float32)

scene = build_surface_scene(positions, (20, 20))
scene = replace(
    scene,
    axes={"visible": True},
    grid={"visible": True},
    controls={"lighting": 1.1},
    legend={"visible": True, "items": ["Surface"]},
    gizmo={"visible": True},
)
show(SceneBundle(scene=scene, arrays={"positions": positions}))
```

## New Capabilities (Tensor Ops + LaTeX Preview)
```python
import sympy as sp
from geometrix.symbolic.ops import auto_from_embedding, gaussian_curvature, laplace_beltrami
from geometrix.transport.latex_viewer import show_latex

u, v = sp.symbols("u v")
X = [sp.sin(u)*sp.cos(v), sp.sin(u)*sp.sin(v), sp.cos(u)]
g = auto_from_embedding(X, [u, v])
K = sp.simplify(gaussian_curvature(g, [u, v]))
show_latex(sp.latex(K))
```

```python
import sympy as sp
from geometrix.symbolic.ops import laplace_beltrami

u, v = sp.symbols("u v")
g = sp.eye(2)
f = u**2 + v**2
lb = sp.simplify(laplace_beltrami(g, [u, v], f))
print(lb)  # 4
```

## Animation (Frame Updates)
```python
import numpy as np
from geometrix.animation import Animation, Frame
from geometrix.api import SceneBundle, show
from geometrix.scene.build import build_surface_scene

positions = np.zeros((100, 3), dtype=np.float32)
scene = build_surface_scene(positions, (10, 10))
frames = [
    Frame(t=0.0, arrays={"positions": positions}),
    Frame(t=1.0, arrays={"positions": positions + 0.2}),
]
show(SceneBundle(scene=scene, arrays={"positions": positions}), animation=Animation(frames, fps=24))
```

## Coordinate Helpers
```python
import numpy as np
from geometrix import cylindrical_to_cartesian, spherical_to_cartesian, lorentz_metric

r, theta, z = np.array([1.0]), np.array([0.5]), np.array([0.0])
xyz = cylindrical_to_cartesian(r, theta, z)
metric = lorentz_metric()
```

## DSL & LaTeX Notes
- Tensor notation is accepted in the DSL using indices (e.g., `g_{ij}`, `Gamma^i_{jk}`).
- LaTeX parsing is allowlisted for common trig/exponential functions, fractions, roots, and Greek symbols; unknown commands are rejected.
- Indices use the symbols `i, j, k, l, m, n, a, b, c, d` by default.

## Colab
`geometrix.show()` uses the HTML renderer and loads Three.js from a CDN.

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
- `js/`: TypeScript frontend sources
- `tests/`: Python tests
- `examples/`: Notebooks
