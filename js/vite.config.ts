import { defineConfig } from "vite";

export default defineConfig({
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
