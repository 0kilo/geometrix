import * as THREE from "three";

import { getBuffer } from "../buffers";
import type { BufferMap, ObjectSpec, SceneSpec } from "../types";
import { buildColors } from "../utils/colormap";

export function buildMesh(obj: ObjectSpec, scene: SceneSpec, buffers: BufferMap): THREE.Mesh {
  const verticesKey = obj.buffers.vertices ?? obj.buffers.positions;
  if (!verticesKey) {
    throw new Error("Mesh object missing vertices buffer");
  }
  const vertexSpec = scene.buffers[verticesKey];
  const vertexData = getBuffer(verticesKey, vertexSpec, buffers) as Float32Array;

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(vertexData, 3));

  const facesKey = obj.buffers.faces;
  if (facesKey) {
    const faceSpec = scene.buffers[facesKey];
    const faceData = getBuffer(facesKey, faceSpec, buffers) as Uint32Array;
    geometry.setIndex(new THREE.BufferAttribute(faceData, 1));
  }
  geometry.computeVertexNormals();

  const valuesKey = obj.buffers.values;
  if (valuesKey) {
    const valuesSpec = scene.buffers[valuesKey];
    const values = getBuffer(valuesKey, valuesSpec, buffers) as Float32Array;
    const colors = buildColors(values, obj.style);
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  }

  const material = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    side: THREE.DoubleSide,
    vertexColors: Boolean(valuesKey),
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.userData = { spec: obj };
  return mesh;
}
