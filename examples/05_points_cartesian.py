# Example: render point clouds in Cartesian coordinates.
# Use when you have discrete (x, y, z) samples.
import numpy as np

from geometrix import points, show

# Cartesian grid for a point cloud.
# x-axis sampling range.
x = np.linspace(-1.0, 1.0, 20)
# y-axis sampling range.
y = np.linspace(-1.0, 1.0, 20)
# 2D grid of sample points.
xx, yy = np.meshgrid(x, y, indexing="ij")
# Height function sampled on the grid.
zz = np.sin(xx * np.pi) * np.cos(yy * np.pi) * 0.3
# Pack into (x, y, z) points.
positions = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3).astype(np.float32)

# Render the sampled points.
show(points(positions))
