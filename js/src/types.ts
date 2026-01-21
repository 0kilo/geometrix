export type BufferSpec = {
  dtype: string;
  shape: number[];
};

export type ObjectSpec = {
  type: string;
  name?: string | null;
  buffers: Record<string, string>;
  style?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
};

export type SceneSpec = {
  version: string;
  objects: ObjectSpec[];
  buffers: Record<string, BufferSpec>;
  camera?: Record<string, unknown>;
  lights?: Record<string, unknown>[];
  axes?: Record<string, unknown>;
  grid?: Record<string, unknown>;
};

export type BufferSource = ArrayBuffer | ArrayBufferView;
export type BufferMap = Record<string, BufferSource>;
