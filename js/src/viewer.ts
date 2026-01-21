import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import { buildLine, buildMesh, buildPoints, buildSurfaceGrid } from "./geometry";
import type { BufferMap, ObjectSpec, SceneSpec } from "./types";

export type ViewerOptions = {
  onHover?: (object: ObjectSpec | null) => void;
  background?: number;
};

export type Viewer = {
  dispose: () => void;
  updateScene: (scene: SceneSpec, buffers: BufferMap) => void;
};

function buildObject(obj: ObjectSpec, scene: SceneSpec, buffers: BufferMap): THREE.Object3D {
  switch (obj.type) {
    case "points":
      return buildPoints(obj, scene, buffers);
    case "line":
      return buildLine(obj, scene, buffers);
    case "surface_grid":
      return buildSurfaceGrid(obj, scene, buffers);
    case "mesh":
      return buildMesh(obj, scene, buffers);
    default:
      throw new Error(`Unsupported object type: ${obj.type}`);
  }
}

export function buildScene(sceneSpec: SceneSpec, buffers: BufferMap): THREE.Scene {
  const scene = new THREE.Scene();
  scene.userData = { sceneSpec };

  const ambient = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambient);
  const directional = new THREE.DirectionalLight(0xffffff, 0.8);
  directional.position.set(5, 5, 5);
  scene.add(directional);

  sceneSpec.objects.forEach((obj) => {
    const node = buildObject(obj, sceneSpec, buffers);
    scene.add(node);
  });

  return scene;
}

export function buildViewer(
  container: HTMLElement,
  sceneSpec: SceneSpec,
  buffers: BufferMap,
  options: ViewerOptions = {},
): Viewer {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setClearColor(options.background ?? 0x0b0f1a);
  container.appendChild(renderer.domElement);

  const scene = buildScene(sceneSpec, buffers);

  const camera = new THREE.PerspectiveCamera(
    45,
    container.clientWidth / container.clientHeight,
    0.01,
    1000,
  );
  camera.position.set(3, 3, 3);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let hovered: THREE.Object3D | null = null;

  function onPointerMove(event: PointerEvent): void {
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObjects(scene.children, true);
    const hit = hits[0]?.object ?? null;
    if (hit !== hovered) {
      hovered = hit;
      const spec = hit?.userData?.spec ?? null;
      options.onHover?.(spec ?? null);
    }
  }

  renderer.domElement.addEventListener("pointermove", onPointerMove);

  let running = true;
  function animate(): void {
    if (!running) {
      return;
    }
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }
  animate();

  function updateScene(nextScene: SceneSpec, nextBuffers: BufferMap): void {
    scene.clear();
    const newScene = buildScene(nextScene, nextBuffers);
    newScene.children.forEach((child) => scene.add(child));
  }

  function dispose(): void {
    running = false;
    renderer.domElement.removeEventListener("pointermove", onPointerMove);
    renderer.dispose();
    controls.dispose();
    scene.clear();
    container.removeChild(renderer.domElement);
  }

  return { dispose, updateScene };
}
