import * as THREE from "three";

import { getBuffer } from "../buffers";
import type { BufferMap, ObjectSpec, SceneSpec } from "../types";
import { buildColors } from "../utils/colormap";

export function buildPoints(obj: ObjectSpec, scene: SceneSpec, buffers: BufferMap): THREE.Points {
  const positionsKey = obj.buffers.positions;
  if (!positionsKey) {
    throw new Error("Points object missing positions buffer");
  }
  const positionSpec = scene.buffers[positionsKey];
  const positionData = getBuffer(positionsKey, positionSpec, buffers) as Float32Array;

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positionData, 3));

  const valuesKey = obj.buffers.values;
  if (valuesKey) {
    const valuesSpec = scene.buffers[valuesKey];
    const values = getBuffer(valuesKey, valuesSpec, buffers) as Float32Array;
    const colors = buildColors(values, obj.style);
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  }

  const material = new THREE.PointsMaterial({
    size: 0.05,
    color: 0xffffff,
    vertexColors: Boolean(valuesKey),
  });

  const points = new THREE.Points(geometry, material);
  points.userData = { spec: obj };
  return points;
}
