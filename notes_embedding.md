# Notes: Embedding Mapping Paper

## Goals
- Explain why metrics alone are insufficient to determine a visible grid in 3D.
- Define charts, embeddings, and induced metrics.
- Show how Geometrix uses embeddings to map grids.
- Provide DSL and Python usage patterns.

## Key Points
- A Riemannian metric defines inner products on tangent spaces; it does not fix an embedding.
- An embedding X(u,v) into R^3 induces a metric g = J^T J.
- Grid lines are parameter lines of the chart mapped through X.
- For curved surfaces, using X for grid mapping ensures visual fidelity.

## Examples to include
- Sphere embedding
- Torus embedding (optional)
- Surface with computed curvature; grid follows geometry
