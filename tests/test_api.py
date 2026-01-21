from geometrix.api import geom


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
