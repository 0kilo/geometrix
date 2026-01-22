from geometrix import geom

scene = geom(
    """
coords: u v
X(u,v) = (u, v, 0.4*sin(u)*cos(v))
render: surface X domain u:[-3.14,3.14] v:[-3.14,3.14] res 60 60
"""
)
scene.show()
