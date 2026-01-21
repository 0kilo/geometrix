import type { BufferMap } from "./types";

const DTYPE_TO_ARRAY: Record<string, new (buffer: ArrayBuffer) => ArrayBufferView> = {
  float32: Float32Array,
  float64: Float64Array,
  int32: Int32Array,
  uint32: Uint32Array,
  int16: Int16Array,
  uint16: Uint16Array,
  int8: Int8Array,
  uint8: Uint8Array,
};

function decodeBase64(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

export function decodeBuffers(payload: Record<string, unknown>): BufferMap {
  const buffers: BufferMap = {};
  Object.entries(payload ?? {}).forEach(([key, entry]) => {
    const spec = entry as { dtype: string; data: string };
    const ctor = DTYPE_TO_ARRAY[spec.dtype];
    if (!ctor) {
      throw new Error(`Unsupported dtype: ${spec.dtype}`);
    }
    const buffer = decodeBase64(spec.data);
    buffers[key] = new ctor(buffer);
  });
  return buffers;
}
