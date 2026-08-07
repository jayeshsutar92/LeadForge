export interface ApiError {
  detail: string | Array<{ loc: (string | number)[]; msg: string; type: string }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
