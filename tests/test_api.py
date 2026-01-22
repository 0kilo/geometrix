import numpy as np
import sympy as sp

from geometrix import cylindrical_to_cartesian, lorentz_metric, spherical_to_cartesian
from geometrix.api import geom, line, mesh, points


def test_geom_builds_surface_scene():
    text = """
    coords: u v
    X(u,v) = (u, v, 0)
    render: surface X domain u:[0,1] v:[0,1] res 4 3
    """
    program = geom(text)
    bundle = program.build_scene()
    assert bundle.scene.version == "1.0"
    assert bundle.arrays["positions"].shape == (12, 3)


def test_points_line_mesh_helpers():
    positions = np.zeros((3, 3), dtype=np.float32)
    faces = np.array([[0, 1, 2]], dtype=np.uint32)

    pts = points(positions)
    assert pts.scene.objects[0].type == "points"

    ln = line(positions)
    assert ln.scene.objects[0].type == "line"

    msh = mesh(positions, faces=faces)
    assert msh.scene.objects[0].type == "mesh"


def test_coordinate_helpers():
    r, phi, z = sp.symbols("r phi z")
    x, y, zz = cylindrical_to_cartesian(r, phi, z)
    assert str(x) == str(r * sp.cos(phi))
    assert str(y) == str(r * sp.sin(phi))
    assert zz == z

    r, theta, phi = sp.symbols("r theta phi")
    x, y, zz = spherical_to_cartesian(r, theta, phi)
    assert str(x) == str(r * sp.sin(theta) * sp.cos(phi))
    assert str(y) == str(r * sp.sin(theta) * sp.sin(phi))
    assert str(zz) == str(r * sp.cos(theta))

    metric = lorentz_metric()
    assert metric.shape == (4, 4)
