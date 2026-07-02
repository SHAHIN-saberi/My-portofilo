export type UIStateStatus =
  | "idle"
  | "loading"
  | "success"
  | "error"
  | "empty"
  | "no_answer"
  | "answered"
  | "unauthorized";

export interface NormalizedError {
  message: string;
  status?: number;
  code?: string;
}

export interface PageState<T> {
  status: UIStateStatus;
  data: T | null;
  error: NormalizedError | null;
}
