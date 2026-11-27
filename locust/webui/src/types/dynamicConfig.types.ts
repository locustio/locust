export type JsonValue = string | number | boolean | null | JsonValue[] | JsonObject;
export interface JsonObject {
  [key: string]: JsonValue;
}

// { [user class name]: { [setting]: value } }
export type IDynamicConfig = Record<string, JsonObject>;

export interface IUpdateDynamicConfigResponse {
  success: boolean;
  message: string;
  config?: IDynamicConfig;
}
