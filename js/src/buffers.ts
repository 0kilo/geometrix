import type { BufferMap, BufferSpec, BufferSource } from "./types";

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

function toArrayBuffer(source: BufferSource): ArrayBuffer {
  if (source instanceof ArrayBuffer) {
    return source;
  }
  return source.buffer.slice(source.byteOffset, source.byteOffset + source.byteLength);
}

export function getBuffer(name: string, spec: BufferSpec, buffers: BufferMap): ArrayBufferView {
  const raw = buffers[name];
  if (!raw) {
    throw new Error(`Missing buffer: ${name}`);
  }
  if (ArrayBuffer.isView(raw)) {
    return raw;
  }
  const ctor = DTYPE_TO_ARRAY[spec.dtype];
  if (!ctor) {
    throw new Error(`Unsupported dtype: ${spec.dtype}`);
  }
  return new ctor(toArrayBuffer(raw));
}
