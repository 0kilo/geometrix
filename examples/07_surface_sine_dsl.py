# Example: surface defined with the DSL (z = 0.4 sin(u) cos(v)).
# Shows a math-first input style.
from geometrix import geom

# DSL program: define coordinates, surface, and render request.
# Parse the DSL program into a scene.
scene = geom(
    """
coords: u v
X(u,v) = (u, v, 0.4*sin(u)*cos(v))
render: surface X domain u:[-3.14,3.14] v:[-3.14,3.14] res 60 60
"""
)
# Render the scene in the notebook.
scene.show()
