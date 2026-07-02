export type UIState =
  | "idle"
  | "loading"
  | "success"
  | "error"
  | "empty"
  | "no_answer"
  | "answered"
  | "unauthorized";

export interface SafeAPIResponse<T> {
  data: T;
  meta: Record<string, any>;
  isValid: boolean;
}

export interface SafeError {
  message: string;
  status: number;
  code: string;
  isNormalized: boolean;
  rawError?: unknown;
}

export type ChatStatusType = "answered" | "no_answer" | "error";

export interface SafeChatSource {
  source_type: string;
  source_id: number;
  score: number;
}

export interface ChatStateModel {
  state: ChatStatusType;
  answer: string;
  sources: SafeChatSource[];
  raw: unknown;
  isValid: boolean;
}
