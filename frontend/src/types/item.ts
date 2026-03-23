export type Item = {
  id: number;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
};

export type CursorPaginatedResponse<T> = {
  next: string | null;
  previous: string | null;
  results: T[];
};
