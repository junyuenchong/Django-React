import type { CursorPaginatedResponse, Item } from "../types/item";

const API_BASE = (globalThis as any).__VITE_API_URL__ || "http://localhost:8000";

// Typed error that carries an optional HTTP status code.
export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function toQueryString(params: Record<string, string | number | undefined>) {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === "") continue;
    usp.set(k, String(v));
  }
  const qs = usp.toString();
  return qs ? `?${qs}` : "";
}

async function apiJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`Request failed: ${res.status} ${res.statusText}. ${text}`.trim(), res.status);
  }
  // DELETE endpoints commonly return 204/205 with no response body.
  if (res.status === 204 || res.status === 205) {
    return undefined as T;
  }
  // Be defensive: empty or non-JSON payloads should produce a clear error.
  try {
    return (await res.json()) as T;
  } catch {
    throw new ApiError(`Invalid JSON response from ${url}.`);
  }
}

// List items using DRF cursor pagination (supports `q`, `page_size`, and `cursor`).
export async function listItemsCursor(params: {
  pageSize: number;
  q?: string;
  cursor?: string;
}): Promise<CursorPaginatedResponse<Item>> {
  const url = `${API_BASE}/api/items/${toQueryString({
    page_size: params.pageSize,
    q: params.q,
    cursor: params.cursor,
  })}`;
  return apiJson<CursorPaginatedResponse<Item>>(url);
}

// Fetch a paginated response using a `next`/`previous` URL returned by the API.
export async function fetchFromUrl<T>(url: string): Promise<T> {
  return apiJson<T>(url);
}

// Create a new item.
export async function createItem(payload: { title: string; description: string }): Promise<Item> {
  return apiJson<Item>(`${API_BASE}/api/items/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// Update an existing item.
export async function updateItem(
  id: number,
  payload: { title: string; description: string },
): Promise<Item> {
  return apiJson<Item>(`${API_BASE}/api/items/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

// Delete an item by id.
export async function deleteItem(id: number): Promise<void> {
  await apiJson<void>(`${API_BASE}/api/items/${id}/`, { method: "DELETE" });
}
