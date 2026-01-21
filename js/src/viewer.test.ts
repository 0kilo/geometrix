import { describe, expect, it } from "vitest";

import { buildScene } from "./viewer";

const minimalScene = {
  version: "1.0",
  objects: [
    {
      type: "points",
      buffers: { positions: "positions" },
    },
  ],
  buffers: {
    positions: { dtype: "float32", shape: [2, 3] },
  },
};

const buffers = {
  positions: new Float32Array([0, 0, 0, 1, 1, 1]),
};

describe("buildScene", () => {
  it("builds a Three.js scene from a minimal spec", () => {
    const scene = buildScene(minimalScene, buffers);
    expect(scene.children.length).toBeGreaterThan(0);
  });
});
