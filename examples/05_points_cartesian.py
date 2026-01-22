import numpy as np

from geometrix import points, show

x = np.linspace(-1.0, 1.0, 20)
y = np.linspace(-1.0, 1.0, 20)
xx, yy = np.meshgrid(x, y, indexing="ij")
zz = np.sin(xx * np.pi) * np.cos(yy * np.pi) * 0.3
positions = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3).astype(np.float32)

show(points(positions))
