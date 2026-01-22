import * as THREE from "three";
import { OrbitControls } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/controls/OrbitControls.js";

const payload = __PAYLOAD__;
const container = document.getElementById("geometrix-container");
const panel = document.createElement("div");
panel.className = "geometrix-panel";
panel.innerHTML = `
  <div class="geometrix-panel-header">
    <h4>Scene Controls</h4>
    <button id="gx-collapse" class="geometrix-panel-toggle" aria-label="Toggle panel">▾</button>
  </div>
  <div id="gx-panel-body">
    <label><input type="checkbox" id="gx-axes" checked /> Show axes</label>
    <label><input type="checkbox" id="gx-grid" checked /> Show grid</label>
    <label><input type="checkbox" id="gx-gizmo" checked /> Show gizmo</label>
    <label><input type="checkbox" id="gx-legend-toggle" /> Show legend</label>
    <label><input type="checkbox" id="gx-theme" /> Light mode</label>
    <label>Lighting</label>
    <input type="range" id="gx-light" min="0" max="2" step="0.1" value="1" />
    <div id="gx-location" style="margin-top:6px;color:#9aa7c0;">
      Gizmo: x=0.00 y=0.00 z=0.00
    </div>
    <div id="gx-legend" class="geometrix-legend"></div>
  </div>
`;
container.appendChild(panel);

const dtypeToCtor = {
  float32: Float32Array,
  float64: Float64Array,
  int32: Int32Array,
  uint32: Uint32Array,
  int16: Int16Array,
  uint16: Uint16Array,
  int8: Int8Array,
  uint8: Uint8Array,
};

function decode(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

function buildColors(values) {
  let min = values[0] ?? 0;
  let max = values[0] ?? 1;
  for (let i = 1; i < values.length; i += 1) {
    min = Math.min(min, values[i]);
    max = Math.max(max, values[i]);
  }
  const range = max - min || 1;
  const colors = new Float32Array(values.length * 3);
  for (let i = 0; i < values.length; i += 1) {
    const t = (values[i] - min) / range;
    colors[i * 3] = 0.1 + 0.85 * t;
    colors[i * 3 + 1] = 0.2 + 0.7 * (1 - Math.abs(0.5 - t) * 2);
    colors[i * 3 + 2] = 0.9 - 0.7 * t;
  }
  return colors;
}

function makeLabelSprite(text, color) {
  const size = 64;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, size, size);
  ctx.fillStyle = color;
  ctx.font = "bold 32px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, size / 2, size / 2);
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(0.35, 0.35, 0.35);
  return sprite;
}

const buffers = {};
for (const [key, spec] of Object.entries(payload.buffers)) {
  const ctor = dtypeToCtor[spec.dtype];
  const raw = decode(spec.data);
  buffers[key] = new ctor(raw);
}

const bufferAttributes = {};
const valueBindings = [];
const lineMaterials = [];
const pointMaterials = [];
let gridMajorColor = 0x3b4566;
let gridMinorColor = 0x2b324f;

const scene = new THREE.Scene();
scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const light = new THREE.DirectionalLight(0xffffff, 0.8);
light.position.set(5, 5, 5);
scene.add(light);

const axisGroup = new THREE.Group();
const axisLineMaterialX = new THREE.LineBasicMaterial({ color: 0xff6b6b });
const axisLineMaterialY = new THREE.LineBasicMaterial({ color: 0x6be675 });
const axisLineMaterialZ = new THREE.LineBasicMaterial({ color: 0x7aa2ff });
const axisLabelX = makeLabelSprite("X", "#ff6b6b");
const axisLabelY = makeLabelSprite("Y", "#6be675");
const axisLabelZ = makeLabelSprite("Z", "#7aa2ff");
axisGroup.add(axisLabelX, axisLabelY, axisLabelZ);
scene.add(axisGroup);

const gridGroup = new THREE.Group();
scene.add(gridGroup);
let gridState = { helpers: [], labels: [], ticks: [] };

const gridConfig = {
  center: new THREE.Vector3(0, 0, 0),
  size: new THREE.Vector3(5, 5, 5),
  divisions: new THREE.Vector3(10, 10, 10),
  min: new THREE.Vector3(-2.5, -2.5, -2.5),
  max: new THREE.Vector3(2.5, 2.5, 2.5)
};

function updateGridBoundsFromPositions() {
  let hasBounds = false;
  let minX = 0;
  let maxX = 0;
  let minY = 0;
  let maxY = 0;
  let minZ = 0;
  let maxZ = 0;

  payload.scene.objects.forEach((obj) => {
    const positionKey = obj.buffers?.positions ?? obj.buffers?.vertices;
    if (!positionKey || !buffers[positionKey]) {
      return;
    }
    const positions = buffers[positionKey];
    if (!positions.length) {
      return;
    }
    if (!hasBounds) {
      minX = positions[0];
      maxX = positions[0];
      minY = positions[1];
      maxY = positions[1];
      minZ = positions[2];
      maxZ = positions[2];
      hasBounds = true;
    }
    for (let i = 0; i < positions.length; i += 3) {
      const x = positions[i];
      const y = positions[i + 1];
      const z = positions[i + 2];
      minX = Math.min(minX, x);
      maxX = Math.max(maxX, x);
      minY = Math.min(minY, y);
      maxY = Math.max(maxY, y);
      minZ = Math.min(minZ, z);
      maxZ = Math.max(maxZ, z);
    }
  });

  if (!hasBounds) {
    return;
  }

  let spanX = Math.max(maxX - minX, 1e-3);
  let spanY = Math.max(maxY - minY, 1e-3);
  let spanZ = Math.max(maxZ - minZ, 1e-3);
  const padX = spanX * 0.1;
  const padY = spanY * 0.1;
  const padZ = spanZ * 0.1;
  minX -= padX;
  maxX += padX;
  minY -= padY;
  maxY += padY;
  minZ -= padZ;
  maxZ += padZ;
  spanX = Math.max(maxX - minX, 1e-3);
  spanY = Math.max(maxY - minY, 1e-3);
  spanZ = Math.max(maxZ - minZ, 1e-3);
  gridConfig.center.set((minX + maxX) * 0.5, (minY + maxY) * 0.5, (minZ + maxZ) * 0.5);
  gridConfig.size.set(spanX, spanY, spanZ);
  gridConfig.min.set(minX, minY, minZ);
  gridConfig.max.set(maxX, maxY, maxZ);
  const maxSpan = Math.max(spanX, spanY, spanZ);
  const gizmoScale = Math.min(Math.max(maxSpan * 0.08, 0.25), 1.25);
  gizmoGroup.scale.setScalar(gizmoScale);
  updateAxesFromBounds();
}

let axisLines = [];
function updateAxesFromBounds() {
  axisLines.forEach((line) => {
    line.geometry.dispose();
    axisGroup.remove(line);
  });
  axisLines = [];

  const minX = gridConfig.min.x;
  const maxX = gridConfig.max.x;
  const minY = gridConfig.min.y;
  const maxY = gridConfig.max.y;
  const minZ = gridConfig.min.z;
  const maxZ = gridConfig.max.z;

  const xStart = maxX > 0 ? Math.max(0, minX) : minX;
  const yStart = maxY > 0 ? Math.max(0, minY) : minY;
  const zStart = minZ;
  const xEnd = Math.max(xStart, maxX);
  const yEnd = Math.max(yStart, maxY);
  const zEnd = maxZ;

  const origin = new THREE.Vector3(xStart, yStart, zStart);

  const xLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([
      origin,
      new THREE.Vector3(xEnd, yStart, zStart)
    ]),
    axisLineMaterialX
  );
  const yLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([
      origin,
      new THREE.Vector3(xStart, yEnd, zStart)
    ]),
    axisLineMaterialY
  );
  const zLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([
      origin,
      new THREE.Vector3(xStart, yStart, zEnd)
    ]),
    axisLineMaterialZ
  );
  axisLines.push(xLine, yLine, zLine);
  axisGroup.add(xLine, yLine, zLine);

  axisLabelX.position.set(xEnd, yStart, zStart);
  axisLabelY.position.set(xStart, yEnd, zStart);
  axisLabelZ.position.set(xStart, yStart, zEnd);
}

for (const obj of payload.scene.objects) {
  if (obj.type === "points") {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.BufferAttribute(buffers[obj.buffers.positions], 3)
    );
    bufferAttributes[obj.buffers.positions] = geometry.getAttribute("position");
    const material = new THREE.PointsMaterial({ size: 0.05, color: 0xffffff });
    pointMaterials.push(material);
    const points = new THREE.Points(geometry, material);
    points.userData = { valuesKey: obj.buffers.values };
    scene.add(points);
  } else if (obj.type === "line") {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.BufferAttribute(buffers[obj.buffers.positions], 3)
    );
    bufferAttributes[obj.buffers.positions] = geometry.getAttribute("position");
    const material = new THREE.LineBasicMaterial({ color: 0xffffff });
    lineMaterials.push(material);
    scene.add(new THREE.Line(geometry, material));
  } else if (obj.type === "surface_grid") {
    const geometry = new THREE.BufferGeometry();
    const positions = buffers[obj.buffers.positions];
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    bufferAttributes[obj.buffers.positions] = geometry.getAttribute("position");
    const gridMeta = obj.metadata?.grid;
    if (gridMeta) {
      const divU = Math.max(gridMeta.Nu - 1, 1);
      const divV = Math.max(gridMeta.Nv - 1, 1);
      const divMax = Math.max(divU, divV);
      gridConfig.divisions.set(divU, divV, divMax);
    }
    const grid = obj.metadata?.grid;
    if (!grid) throw new Error("Missing grid metadata");
    const nu = grid.Nu;
    const nv = grid.Nv;
    const indices = [];
    for (let i = 0; i < nu - 1; i += 1) {
      for (let j = 0; j < nv - 1; j += 1) {
        const a = i * nv + j;
        const b = a + 1;
        const c = a + nv;
        const d = c + 1;
        indices.push(a, c, b, b, c, d);
      }
    }
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    const valuesKey = obj.buffers.values;
    let material = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide
    });
    if (valuesKey) {
      const colors = buildColors(buffers[valuesKey]);
      geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      valueBindings.push({ key: valuesKey, geometry });
      material = new THREE.MeshStandardMaterial({
        vertexColors: true,
        side: THREE.DoubleSide
      });
    }
    const mesh = new THREE.Mesh(geometry, material);
    mesh.userData = { valuesKey };
    scene.add(mesh);
  }
}

function applyGridConfig() {
  const { center, size, divisions, min, max } = gridConfig;
  const gridSpace = payload.scene.grid?.space ?? "cartesian";
  gridGroup.clear();
  gridState = buildGrid(gridSpace, center, size, divisions, min, max);
}

function buildGrid(space, center, size, divisions, min, max) {
  const group = new THREE.Group();
  const labels = [];
  const ticks = [];
  const helpers = [];
  const lineMajor = gridMajorColor;
  const lineMinor = gridMinorColor;

  function addLine(points, color = lineMinor) {
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({ color });
    const line = new THREE.Line(geometry, material);
    group.add(line);
    helpers.push(line);
  }

  function addTickLabel(text, position, scale = 0.25) {
    const sprite = makeLabelSprite(text, "#8b95ad");
    sprite.scale.set(scale, scale, scale);
    sprite.position.copy(position);
    group.add(sprite);
    ticks.push(sprite);
  }

  function labelScaleFor(step, span) {
    if (span <= 0) {
      return 0.22;
    }
    const ratio = step / span;
    const scale = 0.3 - ratio * 1.2;
    return Math.max(0.12, Math.min(0.3, scale));
  }

  if (space === "cylindrical") {
    const minX = min.x;
    const maxX = max.x;
    const minY = min.y;
    const maxY = max.y;
    const minZ = min.z;
    const maxZ = max.z;
    const rMax = Math.max(
      Math.hypot(minX, minY),
      Math.hypot(minX, maxY),
      Math.hypot(maxX, minY),
      Math.hypot(maxX, maxY)
    );
    const rMin = 0;
    const rDiv = Math.max(Math.round(divisions.x), 4);
    const phiDiv = Math.max(Math.round(divisions.y), 12);
    const zDiv = Math.max(Math.round(divisions.z), 4);

    for (let zi = 0; zi <= zDiv; zi += 1) {
      const z = minZ + (size.z * zi) / zDiv;
      for (let ri = 1; ri <= rDiv; ri += 1) {
        const r = rMin + ((rMax - rMin) * ri) / rDiv;
        const points = [];
        for (let pi = 0; pi <= phiDiv; pi += 1) {
          const phi = (2 * Math.PI * pi) / phiDiv;
          points.push(new THREE.Vector3(r * Math.cos(phi), r * Math.sin(phi), z));
        }
        const isMajor = ri % Math.max(Math.floor(rDiv / 3), 1) === 0;
        addLine(points, isMajor ? lineMajor : lineMinor);
      }
      for (let pi = 0; pi < phiDiv; pi += 1) {
        const phi = (2 * Math.PI * pi) / phiDiv;
        const points = [];
        for (let ri = 0; ri <= rDiv; ri += 1) {
          const r = rMin + ((rMax - rMin) * ri) / rDiv;
          points.push(new THREE.Vector3(r * Math.cos(phi), r * Math.sin(phi), z));
        }
        addLine(points, lineMinor);
      }
    }

    const zTicks = Math.min(zDiv, 6);
    const zScale = labelScaleFor(size.z / Math.max(zDiv, 1), size.z);
    for (let i = 0; i <= zTicks; i += 1) {
      const z = minZ + (size.z * i) / zTicks;
      addTickLabel(
        z.toFixed(2),
        new THREE.Vector3(rMax * 0.2, -rMax * 1.05, z),
        zScale
      );
    }
    const rTicks = Math.min(rDiv, 6);
    const rScale = labelScaleFor((rMax - rMin) / Math.max(rDiv, 1), rMax - rMin);
    for (let i = 0; i <= rTicks; i += 1) {
      const r = rMin + ((rMax - rMin) * i) / rTicks;
      addTickLabel(
        r.toFixed(2),
        new THREE.Vector3(r, 0, minZ - size.z * 0.05),
        rScale
      );
    }
    const phiTicks = Math.min(phiDiv, 8);
    const phiScale = labelScaleFor((2 * Math.PI) / phiDiv, 2 * Math.PI);
    for (let i = 0; i < phiTicks; i += 1) {
      const phi = (2 * Math.PI * i) / phiTicks;
      addTickLabel(
        phi.toFixed(2),
        new THREE.Vector3(
          rMax * Math.cos(phi),
          rMax * Math.sin(phi),
          minZ - size.z * 0.05
        ),
        phiScale
      );
    }
  } else if (space === "spherical") {
    const minX = min.x;
    const maxX = max.x;
    const minY = min.y;
    const maxY = max.y;
    const minZ = min.z;
    const maxZ = max.z;
    const rMax = Math.max(
      Math.hypot(minX, minY, minZ),
      Math.hypot(minX, minY, maxZ),
      Math.hypot(minX, maxY, minZ),
      Math.hypot(minX, maxY, maxZ),
      Math.hypot(maxX, minY, minZ),
      Math.hypot(maxX, minY, maxZ),
      Math.hypot(maxX, maxY, minZ),
      Math.hypot(maxX, maxY, maxZ)
    );
    const rMin = 0;
    const rDiv = Math.max(Math.round(divisions.x), 4);
    const thetaDiv = Math.max(Math.round(divisions.y), 8);
    const phiDiv = Math.max(Math.round(divisions.z), 12);
    for (let ri = 1; ri <= rDiv; ri += 1) {
      const r = rMin + ((rMax - rMin) * ri) / rDiv;
      for (let ti = 1; ti < thetaDiv; ti += 1) {
        const theta = (Math.PI * ti) / thetaDiv;
        const points = [];
        for (let pi = 0; pi <= phiDiv; pi += 1) {
          const phi = (2 * Math.PI * pi) / phiDiv;
          const x = r * Math.sin(theta) * Math.cos(phi);
          const y = r * Math.sin(theta) * Math.sin(phi);
          const z = r * Math.cos(theta);
          points.push(new THREE.Vector3(x, y, z));
        }
        const isMajor = ri % Math.max(Math.floor(rDiv / 3), 1) === 0;
        addLine(points, isMajor ? lineMajor : lineMinor);
      }
      for (let pi = 0; pi < phiDiv; pi += 1) {
        const phi = (2 * Math.PI * pi) / phiDiv;
        const points = [];
        for (let ti = 0; ti <= thetaDiv; ti += 1) {
          const theta = (Math.PI * ti) / thetaDiv;
          const x = r * Math.sin(theta) * Math.cos(phi);
          const y = r * Math.sin(theta) * Math.sin(phi);
          const z = r * Math.cos(theta);
          points.push(new THREE.Vector3(x, y, z));
        }
        addLine(points, lineMinor);
      }
    }

    const rTicks = Math.min(rDiv, 6);
    const rScale = labelScaleFor((rMax - rMin) / Math.max(rDiv, 1), rMax - rMin);
    for (let i = 0; i <= rTicks; i += 1) {
      const r = rMin + ((rMax - rMin) * i) / rTicks;
      addTickLabel(r.toFixed(2), new THREE.Vector3(r, 0, 0), rScale);
    }
    const thetaTicks = Math.min(thetaDiv, 6);
    const thetaScale = labelScaleFor(Math.PI / thetaDiv, Math.PI);
    for (let i = 1; i < thetaTicks; i += 1) {
      const theta = (Math.PI * i) / thetaTicks;
      const x = rMax * Math.sin(theta);
      const z = rMax * Math.cos(theta);
      addTickLabel(theta.toFixed(2), new THREE.Vector3(x, 0, z), thetaScale);
    }
    const phiTicks = Math.min(phiDiv, 8);
    const phiScale = labelScaleFor((2 * Math.PI) / phiDiv, 2 * Math.PI);
    for (let i = 0; i < phiTicks; i += 1) {
      const phi = (2 * Math.PI * i) / phiTicks;
      addTickLabel(
        phi.toFixed(2),
        new THREE.Vector3(rMax * Math.cos(phi), rMax * Math.sin(phi), 0),
        phiScale
      );
    }
  } else {
    const minX = min.x;
    const maxX = max.x;
    const minY = min.y;
    const maxY = max.y;
    const minZ = min.z;
    const maxZ = max.z;
    const stepX = divisions.x > 0 ? (maxX - minX) / divisions.x : maxX - minX;
    const stepY = divisions.y > 0 ? (maxY - minY) / divisions.y : maxY - minY;
    const stepZ = divisions.z > 0 ? (maxZ - minZ) / divisions.z : maxZ - minZ;
    const strideX = Math.max(Math.floor(divisions.x / 10), 1);
    const strideY = Math.max(Math.floor(divisions.y / 10), 1);
    const strideZ = Math.max(Math.floor(divisions.z / 10), 1);
    const offsetX = (maxX - minX) * 0.04;
    const offsetY = (maxY - minY) * 0.04;
    const offsetZ = (maxZ - minZ) * 0.04;
    const xScale = labelScaleFor(stepX, maxX - minX);
    const yScale = labelScaleFor(stepY, maxY - minY);
    const zScale = labelScaleFor(stepZ, maxZ - minZ);

    const xyZ = minZ;
    for (let yi = 0; yi <= divisions.y; yi += 1) {
      const y = minY + stepY * yi;
      const points = [new THREE.Vector3(minX, y, xyZ), new THREE.Vector3(maxX, y, xyZ)];
      addLine(points, yi % strideY === 0 ? lineMajor : lineMinor);
    }
    for (let xi = 0; xi <= divisions.x; xi += 1) {
      const x = minX + stepX * xi;
      const points = [new THREE.Vector3(x, minY, xyZ), new THREE.Vector3(x, maxY, xyZ)];
      addLine(points, xi % strideX === 0 ? lineMajor : lineMinor);
    }

    const xzY = minY;
    for (let xi = 0; xi <= divisions.x; xi += 1) {
      const x = minX + stepX * xi;
      const points = [new THREE.Vector3(x, xzY, minZ), new THREE.Vector3(x, xzY, maxZ)];
      addLine(points, xi % strideX === 0 ? lineMajor : lineMinor);
    }
    for (let zi = 0; zi <= divisions.z; zi += 1) {
      const z = minZ + stepZ * zi;
      const points = [new THREE.Vector3(minX, xzY, z), new THREE.Vector3(maxX, xzY, z)];
      addLine(points, zi % strideZ === 0 ? lineMajor : lineMinor);
    }

    const yzX = minX;
    for (let yi = 0; yi <= divisions.y; yi += 1) {
      const y = minY + stepY * yi;
      const points = [new THREE.Vector3(yzX, y, minZ), new THREE.Vector3(yzX, y, maxZ)];
      addLine(points, yi % strideY === 0 ? lineMajor : lineMinor);
    }
    for (let zi = 0; zi <= divisions.z; zi += 1) {
      const z = minZ + stepZ * zi;
      const points = [new THREE.Vector3(yzX, minY, z), new THREE.Vector3(yzX, maxY, z)];
      addLine(points, zi % strideZ === 0 ? lineMajor : lineMinor);
    }

    const labelXY = makeLabelSprite("XY", "#9fb3ff");
    const labelXZ = makeLabelSprite("XZ", "#9fb3ff");
    const labelYZ = makeLabelSprite("YZ", "#9fb3ff");
    labelXY.position.set(maxX, maxY, xyZ);
    labelXZ.position.set(maxX, xzY, maxZ);
    labelYZ.position.set(yzX, maxY, maxZ);
    group.add(labelXY, labelXZ, labelYZ);
    labels.push(labelXY, labelXZ, labelYZ);

    for (let i = 0; i <= divisions.x; i += 1) {
      if (i % strideX !== 0) continue;
      const value = minX + stepX * i;
      addTickLabel(
        value.toFixed(2),
        new THREE.Vector3(value, minY - offsetY, minZ - offsetZ),
        xScale
      );
    }
    for (let i = 0; i <= divisions.y; i += 1) {
      if (i % strideY !== 0) continue;
      const value = minY + stepY * i;
      addTickLabel(
        value.toFixed(2),
        new THREE.Vector3(minX - offsetX, value, minZ - offsetZ),
        yScale
      );
    }
    for (let i = 0; i <= divisions.z; i += 1) {
      if (i % strideZ !== 0) continue;
      const value = minZ + stepZ * i;
      addTickLabel(
        value.toFixed(2),
        new THREE.Vector3(maxX + offsetX, minY - offsetY, value),
        zScale
      );
    }
  }

  gridGroup.add(group);
  return { helpers, labels, ticks };
}
