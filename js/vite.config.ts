import { defineConfig } from "vite";

import packageJson from "./package.json";

export default defineConfig({
  define: {
    __WIDGET_VERSION__: JSON.stringify(packageJson.version),
  },
  build: {
    lib: {
      entry: "src/widget.ts",
      name: "GeometrixWidget",
      formats: ["iife"],
      fileName: "index",
    },
    outDir: "dist",
  },
});
