const gizmoGroup = new THREE.Group();
const gizmoBall = new THREE.Mesh(
  new THREE.SphereGeometry(0.12, 16, 16),
  new THREE.MeshStandardMaterial({ color: 0xffc857 })
);
gizmoGroup.add(gizmoBall);
const gizmoAxes = new THREE.Group();
gizmoGroup.add(gizmoAxes);

function buildArrow(axis, color) {
  const group = new THREE.Group();
  const shaft = new THREE.Mesh(
    new THREE.CylinderGeometry(0.02, 0.02, 0.6, 12),
    new THREE.MeshStandardMaterial({ color })
  );
  shaft.position.y = 0.3;
  const tip = new THREE.Mesh(
    new THREE.ConeGeometry(0.06, 0.2, 12),
    new THREE.MeshStandardMaterial({ color })
  );
  tip.position.y = 0.7;
  const hit = new THREE.Mesh(
    new THREE.SphereGeometry(0.12, 12, 12),
    new THREE.MeshBasicMaterial({ opacity: 0, transparent: true })
  );
  hit.position.y = 0.7;
  group.add(shaft, tip);
  group.add(hit);
  if (axis === "x") {
    group.rotation.z = -Math.PI / 2;
    group.userData = { axis: new THREE.Vector3(1, 0, 0) };
  } else if (axis === "y") {
    group.userData = { axis: new THREE.Vector3(0, 1, 0) };
  } else {
    group.rotation.x = Math.PI / 2;
    group.userData = { axis: new THREE.Vector3(0, 0, 1) };
  }
  tip.userData = group.userData;
  hit.userData = group.userData;
  return group;
}

const arrowX = buildArrow("x", 0xff6b6b);
const arrowY = buildArrow("y", 0x6be675);
const arrowZ = buildArrow("z", 0x7aa2ff);
gizmoAxes.add(arrowX, arrowY, arrowZ);
const gizmoLabelX = makeLabelSprite("X", "#ff6b6b");
gizmoLabelX.position.set(0.9, 0, 0);
const gizmoLabelY = makeLabelSprite("Y", "#6be675");
gizmoLabelY.position.set(0, 0.9, 0);
const gizmoLabelZ = makeLabelSprite("Z", "#7aa2ff");
gizmoLabelZ.position.set(0, 0, 0.9);
gizmoGroup.add(gizmoLabelX, gizmoLabelY, gizmoLabelZ);
scene.add(gizmoGroup);
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const gizmoLight = new THREE.DirectionalLight(0xffffff, 0.6);
gizmoLight.position.set(3, 3, 3);
scene.add(gizmoLight);

updateGridBoundsFromPositions();
applyGridConfig();

const gizmoRaycaster = new THREE.Raycaster();
const gizmoPointer = new THREE.Vector2();
let gizmoDragging = false;
let gizmoAxis = null;
let lastPointer = null;
const locationReadout = document.getElementById("gx-location");

function updateGizmoReadout() {
  const { x, y, z } = gizmoGroup.position;
  locationReadout.textContent =
    `Gizmo: x=${x.toFixed(2)} y=${y.toFixed(2)} z=${z.toFixed(2)}`;
}
updateGizmoReadout();

function pickGizmoAxis(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  gizmoPointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  gizmoPointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  gizmoRaycaster.setFromCamera(gizmoPointer, camera);
  const hits = gizmoRaycaster.intersectObjects(gizmoAxes.children, true);
  if (!hits.length) {
    return null;
  }
  let node = hits[0].object;
  while (node && !node.userData?.axis) {
    node = node.parent;
  }
  return node?.userData?.axis || null;
}

function axisScreenDirection(axis) {
  const from = gizmoGroup.position.clone();
  const to = from.clone().add(axis.clone().multiplyScalar(1));
  const fromNdc = from.project(camera);
  const toNdc = to.project(camera);
  const dir = new THREE.Vector2(
    toNdc.x - fromNdc.x,
    toNdc.y - fromNdc.y
  ).normalize();
  return dir;
}

renderer.domElement.addEventListener("pointerdown", (event) => {
  if (!gizmoGroup.visible) {
    return;
  }
  const axis = pickGizmoAxis(event);
  if (!axis) {
    return;
  }
  gizmoDragging = true;
  gizmoAxis = axis;
  lastPointer = { x: event.clientX, y: event.clientY };
  controls.enabled = false;
});

window.addEventListener("pointerup", () => {
  gizmoDragging = false;
  gizmoAxis = null;
  lastPointer = null;
  controls.enabled = true;
});

window.addEventListener("pointermove", (event) => {
  if (!gizmoDragging || !gizmoAxis || !lastPointer) {
    return;
  }
  const deltaX = event.clientX - lastPointer.x;
  const deltaY = event.clientY - lastPointer.y;
  lastPointer = { x: event.clientX, y: event.clientY };
  const axisDir = axisScreenDirection(gizmoAxis);
  const delta = (deltaX * axisDir.x + -deltaY * axisDir.y) * 0.005;
  const move = gizmoAxis.clone().multiplyScalar(delta);
  gizmoGroup.position.add(move);
  updateGizmoReadout();
});

function animate() {
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();
