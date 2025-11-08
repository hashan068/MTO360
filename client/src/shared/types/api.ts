export interface PaginatedResponse<T> {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export interface ListParams {
  skip?: number;
  limit?: number;
  search?: string;
  ordering?: string;
  [key: string]: unknown;
}
