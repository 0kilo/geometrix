import { DOMWidgetModel, DOMWidgetView } from "@jupyter-widgets/base";

import { decodeBuffers } from "./widget_buffers";
import type { BufferMap, SceneSpec } from "./types";
import { buildViewer, type Viewer } from "./viewer";

export class GeomWidgetModel extends DOMWidgetModel {
  defaults(): Record<string, unknown> {
    return {
      ...super.defaults(),
      _model_name: "GeomWidgetModel",
      _view_name: "GeomWidgetView",
      _model_module: "geometrix-widget",
      _view_module: "geometrix-widget",
      _model_module_version: "0.1.0",
      _view_module_version: "0.1.0",
      scene_spec: {},
      buffers: {},
      height: 420,
    };
  }
}

export class GeomWidgetView extends DOMWidgetView {
  private viewer: Viewer | null = null;

  render(): void {
    const sceneSpec = this.model.get("scene_spec") as SceneSpec;
    const buffers = decodeBuffers(this.model.get("buffers")) as BufferMap;
    const height = this.model.get("height") as number;
    this.el.style.width = "100%";
    this.el.style.height = `${height}px`;
    this.viewer = buildViewer(this.el, sceneSpec, buffers);

    this.listenTo(this.model, "change:scene_spec", this.handleUpdate, this);
    this.listenTo(this.model, "change:buffers", this.handleUpdate, this);
  }

  handleUpdate(): void {
    if (!this.viewer) {
      return;
    }
    const sceneSpec = this.model.get("scene_spec") as SceneSpec;
    const buffers = decodeBuffers(this.model.get("buffers")) as BufferMap;
    this.viewer.updateScene(sceneSpec, buffers);
  }
}
