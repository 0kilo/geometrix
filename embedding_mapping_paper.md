# Embedding-Based Grid Mapping for Curved Geometry in Geometrix

## Abstract
Geometrix renders differential geometry in notebook environments by sampling charts and mapping them into 3D space. This paper explains why the metric tensor alone is not enough to draw a visual grid, and why embedding-based mapping is the most faithful and practical approach. We define charts, embeddings, and induced metrics, then show how to use embedding mappings in Geometrix with clear DSL and Python examples. The goal is to provide a rigorous foundation that still matches how users build geometry and inspect tensor quantities in practice.

## 1. Motivation: What a Metric Does (and Does Not) Determine
A Riemannian (or pseudo-Riemannian) metric g_ij defines inner products on tangent spaces. It encodes lengths, angles, and curvature. However, the metric does not uniquely determine a 3D shape or a visual embedding. Many distinct surfaces (or even non-embeddable metrics) can share equivalent local metric properties. Therefore, a plotting system needs more than the metric to render a grid: it needs a mapping from parameters to 3D coordinates.

In practice, users work with charts (u, v, ...) and a parametric embedding X(u, v). The embedding provides an explicit way to place points in R^3, and it induces a metric via:

- J = dX/du (Jacobian)
- g = J^T J (first fundamental form)

Geometrix follows this approach: for any surface or chart, the grid is generated in parameter space and mapped through the embedding to produce geometry and gridlines.

## 2. Core Concepts

### 2.1 Charts (Coordinate Systems)
A chart is a local coordinate system (u, v, ...) that parameterizes a manifold. Charts are how we specify domains, sampling resolution, and tensor component expressions.

### 2.2 Embedding
An embedding is a smooth map X(u, v) into R^3. It is the most concrete way to generate geometry for visualization. In Geometrix, a surface is a 3-vector expression:

X(u, v) = (x(u, v), y(u, v), z(u, v))

### 2.3 Induced Metric
Given X, the induced metric is:

g_ij = <dX/du_i, dX/du_j>

This metric is what you use to compute Christoffels, curvature, and differential operators. The grid lines you see are the images of the parameter lines under X.

## 3. Why Embedding-Based Grids Are the Right Default

1. **Visual fidelity**: Grid lines reflect the actual surface shape.
2. **Consistency**: The same embedding used for geometry also defines the grid and the metric.
3. **Compatibility**: Works across cartesian, cylindrical, spherical, and custom charts.
4. **Extensibility**: Custom embeddings support arbitrary coordinate systems and metrics.

If you only provide g_ij without X, Geometrix cannot uniquely reconstruct a 3D grid. For that case, Geometrix can only draw a chart-space grid (a conceptual grid), or it requires a user-supplied embedding.

## 4. Practical Usage in Geometrix

### 4.1 DSL Example: Sphere Embedding
```text
coords: u v
X(u,v) = (sin(u)*cos(v), sin(u)*sin(v), cos(u))
g_{ij} = auto_from_embedding(X)
render: surface X domain u:[0,3.1416] v:[0,6.2832] res 50 80
grid.space: spherical
grid.mapping: X
```

- `grid.mapping: X` tells Geometrix to generate the grid in (u, v) and map it using X.
- `grid.space` sets the grid style (cartesian/cylindrical/spherical) for ticks and parameter interpretation.

### 4.2 Python Example: Embedding with Tensor Ops
```python
import sympy as sp
from geometrix.symbolic.ops import auto_from_embedding, gaussian_curvature

u, v = sp.symbols("u v")
X = [sp.sin(u)*sp.cos(v), sp.sin(u)*sp.sin(v), sp.cos(u)]

g = auto_from_embedding(X, [u, v])
K = sp.simplify(gaussian_curvature(g, [u, v]))
```

The same X should be used for grid mapping. This keeps geometry, grid, and tensor results aligned.

### 4.3 Cylindrical Chart Example
```text
coords: r phi
X(r,phi) = (r*cos(phi), r*sin(phi), 0)
render: surface X domain r:[0,1] phi:[0,6.2832] res 40 80
grid.space: cylindrical
grid.mapping: X
```

## 5. Recommended Workflow for Curved Metrics

1. Define chart coordinates (u, v, ...).
2. Define an embedding X(u, v) into R^3.
3. Derive g_ij via `auto_from_embedding(X)` or define it explicitly.
4. Use X as `grid.mapping` so the grid follows the surface.
5. Compute tensor quantities (Christoffel, Riemann, Ricci, curvature) on the same chart.

This workflow ensures all computations and visual cues are consistent.

## 6. Limitations and Extensions

- **Non-embeddable metrics**: Some metrics cannot be globally embedded in R^3. Geometrix will require either a local embedding or a lower-dimensional visualization.
- **Higher dimensions**: For 4D spacetimes, you must choose a 3D slice (e.g., t = const) for visualization; the grid mapping can be the slice embedding.
- **Metric-only inputs**: Without X, grid lines default to chart space, which is informative but not geometrically unique.

Future extensions may include numerical embedding reconstruction for metric-only inputs, but that is ill-posed without additional constraints.

## 7. Summary
Embedding-based grid mapping is the most reliable way to visualize curved geometry. The metric tensor defines distances and curvature, but it does not uniquely determine a 3D grid. By using an explicit embedding X and mapping grid lines through it, Geometrix produces faithful grids, aligns tensor computations with the rendered surface, and supports familiar coordinate presets. For differential geometry workflows, this approach provides the right balance of mathematical rigor and practical usability.
