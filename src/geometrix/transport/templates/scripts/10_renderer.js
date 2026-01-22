const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio || 1);
renderer.setClearColor(0x0b0f1a);
container.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(
  45,
  container.clientWidth / container.clientHeight,
  0.01,
  1000
);
camera.position.set(3, 3, 3);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const raycaster = new THREE.Raycaster();
raycaster.params.Points.threshold = 0.05;
const pointer = new THREE.Vector2();
function updateReadout(event) {
  const readout = document.getElementById("gx-readout");
  if (!readout) {
    return;
  }
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(scene.children, true);
  if (!hits.length) {
    readout.textContent = "Hover to inspect";
    return;
  }
  const hit = hits[0];
  const obj = hit.object;
  const geometry = obj.geometry;
  const positionAttr = geometry.getAttribute("position");
  let idx = hit.index ?? 0;
  if (hit.face && hit.face.a !== undefined) {
    idx = hit.face.a;
  }
  const x = (hit.point?.x ?? positionAttr.getX(idx)).toFixed(3);
  const y = (hit.point?.y ?? positionAttr.getY(idx)).toFixed(3);
  const z = (hit.point?.z ?? positionAttr.getZ(idx)).toFixed(3);
  let valueText = "";
  const valuesKey = obj.userData?.valuesKey;
  if (valuesKey && buffers[valuesKey]) {
    const value = buffers[valuesKey][idx];
    valueText = ` | v=${Number(value).toFixed(3)}`;
  }
  readout.textContent = `x=${x}, y=${y}, z=${z}${valueText}`;
}

renderer.domElement.addEventListener("pointermove", updateReadout);
