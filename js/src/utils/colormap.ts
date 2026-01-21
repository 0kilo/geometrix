import type { ObjectSpec } from "../types";

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function gradient(t: number): [number, number, number] {
  const stops = [
    [0.0, [0.1, 0.2, 0.6]],
    [0.5, [0.3, 0.8, 0.6]],
    [1.0, [0.95, 0.9, 0.2]],
  ] as const;
  for (let i = 0; i < stops.length - 1; i += 1) {
    const [t0, c0] = stops[i];
    const [t1, c1] = stops[i + 1];
    if (t >= t0 && t <= t1) {
      const u = (t - t0) / (t1 - t0);
      return [lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u), lerp(c0[2], c1[2], u)];
    }
  }
  return [0.8, 0.8, 0.8];
}

export function buildColors(values: Float32Array, style?: ObjectSpec["style"]): Float32Array {
  void style;
  let min = values[0] ?? 0;
  let max = values[0] ?? 1;
  for (let i = 1; i < values.length; i += 1) {
    min = Math.min(min, values[i]);
    max = Math.max(max, values[i]);
  }
  const range = max - min || 1;
  const colors = new Float32Array(values.length * 3);
  for (let i = 0; i < values.length; i += 1) {
    const t = clamp01((values[i] - min) / range);
    const [r, g, b] = gradient(t);
    colors[i * 3] = r;
    colors[i * 3 + 1] = g;
    colors[i * 3 + 2] = b;
  }
  return colors;
}
