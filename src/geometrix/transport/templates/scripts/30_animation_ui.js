function decodeFrame(frame) {
  const out = {};
  for (const [key, spec] of Object.entries(frame)) {
    const ctor = dtypeToCtor[spec.dtype];
    const raw = decode(spec.data);
    out[key] = new ctor(raw);
  }
  return out;
}

function applyFrame(frame) {
  for (const [key, attr] of Object.entries(bufferAttributes)) {
    if (frame[key]) {
      attr.array.set(frame[key]);
      attr.needsUpdate = true;
    }
  }
  valueBindings.forEach((binding) => {
    if (frame[binding.key]) {
      const colors = buildColors(frame[binding.key]);
      binding.geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      binding.geometry.attributes.color.needsUpdate = true;
    }
  });
}
window.geometrixApplyFrame = applyFrame;

if (payload.frames && payload.scene.animation) {
  const frames = payload.frames.map(decodeFrame);
  let frameIndex = 0;
  const fps = payload.scene.animation.fps || 30;
  const loop = payload.scene.animation.loop !== false;
  const timer = setInterval(() => {
    if (!loop && frameIndex >= frames.length) {
      clearInterval(timer);
      return;
    }
    const frame = frames[frameIndex % frames.length];
    applyFrame(frame);
    frameIndex += 1;
  }, 1000 / fps);
}

const axesToggle = document.getElementById("gx-axes");
const gridToggle = document.getElementById("gx-grid");
const gizmoToggle = document.getElementById("gx-gizmo");
const legendToggle = document.getElementById("gx-legend-toggle");
const themeToggle = document.getElementById("gx-theme");
const collapseToggle = document.getElementById("gx-collapse");
const panelBody = document.getElementById("gx-panel-body");
const lightSlider = document.getElementById("gx-light");
const legendPanel = document.getElementById("gx-legend");

const showAxes = payload.scene.axes?.visible ?? true;
const showGrid = payload.scene.grid?.visible ?? true;
const showGizmo = payload.scene.gizmo?.visible ?? true;
const showLegend = payload.scene.legend?.visible ?? false;
const lightingValue = payload.scene.controls?.lighting ?? 1;
const isLightMode = payload.scene.controls?.theme === "light";

axisGroup.visible = showAxes;
gridGroup.visible = showGrid;
gizmoGroup.visible = showGizmo;

axesToggle.checked = showAxes;
gridToggle.checked = showGrid;
gizmoToggle.checked = showGizmo;
legendToggle.checked = showLegend;
lightSlider.value = String(lightingValue);
themeToggle.checked = Boolean(isLightMode);

legendPanel.style.display = showLegend ? "block" : "none";
const legendItems = payload.scene.legend?.items
  ?? payload.scene.objects.map((obj) => obj.name || obj.type);
legendPanel.innerHTML = legendItems
  .map((name) => `<div class="geometrix-legend-item">${name}</div>`)
  .join("");

function updateLighting(value) {
  light.intensity = value * 0.8;
  scene.children.forEach((child) => {
    if (child.isAmbientLight) {
      child.intensity = value * 0.7;
    }
  });
}
updateLighting(lightingValue);
setTheme(themeToggle.checked);

axesToggle.addEventListener("change", (event) => {
  const enabled = event.target.checked;
  axisGroup.visible = enabled;
});
gridToggle.addEventListener("change", (event) => {
  const enabled = event.target.checked;
  gridGroup.visible = enabled;
});
gizmoToggle.addEventListener("change", (event) => {
  gizmoGroup.visible = event.target.checked;
});
legendToggle.addEventListener("change", (event) => {
  legendPanel.style.display = event.target.checked ? "block" : "none";
});
lightSlider.addEventListener("input", (event) => {
  updateLighting(Number(event.target.value));
});
themeToggle.addEventListener("change", (event) => {
  setTheme(event.target.checked);
});
collapseToggle.addEventListener("click", () => {
  const isCollapsed = panel.classList.toggle("geometrix-panel--collapsed");
  collapseToggle.textContent = isCollapsed ? "▸" : "▾";
  panelBody.style.display = isCollapsed ? "none" : "block";
});

function setTheme(isLight) {
  if (isLight) {
    container.classList.add("geometrix-light");
    renderer.setClearColor(0xffffff);
    gridMajorColor = 0x111111;
    gridMinorColor = 0x555555;
    lineMaterials.forEach((material) => {
      material.color.set(0x111111);
    });
    pointMaterials.forEach((material) => {
      material.color.set(0x111111);
    });
  } else {
    container.classList.remove("geometrix-light");
    renderer.setClearColor(0x0b0f1a);
    gridMajorColor = 0x3b4566;
    gridMinorColor = 0x2b324f;
    lineMaterials.forEach((material) => {
      material.color.set(0xffffff);
    });
    pointMaterials.forEach((material) => {
      material.color.set(0xffffff);
    });
  }
  applyGridConfig();
}
