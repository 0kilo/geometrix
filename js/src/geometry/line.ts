import * as THREE from "three";

import { getBuffer } from "../buffers";
import type { BufferMap, ObjectSpec, SceneSpec } from "../types";
import { buildColors } from "../utils/colormap";

export function buildLine(obj: ObjectSpec, scene: SceneSpec, buffers: BufferMap): THREE.Line {
  const positionsKey = obj.buffers.positions;
  if (!positionsKey) {
    throw new Error("Line object missing positions buffer");
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

  const material = new THREE.LineBasicMaterial({
    color: 0xffffff,
    linewidth: 1,
    vertexColors: Boolean(valuesKey),
  });

  const line = new THREE.Line(geometry, material);
  line.userData = { spec: obj };
  return line;
}
