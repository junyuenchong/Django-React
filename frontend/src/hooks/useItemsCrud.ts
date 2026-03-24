import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  createItem,
  deleteItem,
  fetchFromUrl,
  listItemsCursor,
  updateItem,
} from "../api/itemsApi";
import type { CursorPaginatedResponse, Item } from "../types/item";

export type Draft = { title: string; description: string };

// Centralize item list fetching, pagination, and CRUD mutations.
export function useItemsCrud(pageSize = 5) {
  const [q, setQ] = useState("");
  const [debouncedQ, setDebouncedQ] = useState("");
  const [pageUrl, setPageUrl] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [draft, setDraft] = useState<Draft>({ title: "", description: "" });

  const queryClient = useQueryClient();

  // Retry only transient server-side failures.
  const shouldRetryRequest = useCallback((failureCount: number, error: unknown) => {
    if (!(error instanceof ApiError) || !error.status) return false;
    return error.status >= 500 && failureCount < 2;
  }, []);

  // Debounce search input to avoid frequent API calls.
  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedQ(q);
      setPageUrl(null);
    }, 250);
    return () => clearTimeout(t);
  }, [q]);

  // Load first page or a cursor URL, while keeping previous data during transitions.
  const listQuery = useQuery<CursorPaginatedResponse<Item>>({
    queryKey: ["items", debouncedQ, pageUrl, pageSize],
    placeholderData: keepPreviousData,
    retry: shouldRetryRequest,
    queryFn: () =>
      pageUrl
        ? fetchFromUrl<CursorPaginatedResponse<Item>>(pageUrl)
        : listItemsCursor({ pageSize, q: debouncedQ || undefined }),
  });

  // Create item and refresh list cache.
  const createMutation = useMutation({
    mutationFn: createItem,
    retry: shouldRetryRequest,
    onSuccess: async () => {
      setPageUrl(null);
      await queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  // Update item and refresh list cache.
  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Draft }) => updateItem(id, payload),
    retry: shouldRetryRequest,
    onSuccess: async () => {
      setPageUrl(null);
      await queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  // Delete item and refresh list cache.
  const deleteMutation = useMutation({
    mutationFn: deleteItem,
    retry: shouldRetryRequest,
    onSuccess: async () => {
      setPageUrl(null);
      await queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  const nextUrl = listQuery.data?.next ?? null;
  const previousUrl = listQuery.data?.previous ?? null;
  const items = listQuery.data?.results ?? [];

  // Prefetch next page so pagination feels instant.
  useEffect(() => {
    if (!nextUrl) return;
    void queryClient.prefetchQuery({
      queryKey: ["items", debouncedQ, nextUrl, pageSize],
      queryFn: () => fetchFromUrl<CursorPaginatedResponse<Item>>(nextUrl),
      staleTime: 30_000,
    });
  }, [debouncedQ, nextUrl, pageSize, queryClient]);

  const loading =
    listQuery.isFetching ||
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending;

  const queryError = listQuery.error instanceof Error ? listQuery.error.message : null;
  const error = actionError ?? queryError;

  // Submit create/update based on current edit mode.
  const submit = useCallback(async () => {
    setActionError(null);
    if (!draft.title.trim()) {
      setActionError("Title cannot be empty.");
      return;
    }

    try {
      if (editingId == null) {
        await createMutation.mutateAsync(draft);
      } else {
        await updateMutation.mutateAsync({ id: editingId, payload: draft });
      }
      setEditingId(null);
      setDraft({ title: "", description: "" });
    } catch (e) {
      setActionError(e instanceof Error ? e.message : String(e));
    }
  }, [createMutation, draft, editingId, updateMutation]);

  // Delete one item and reset editing state.
  const remove = useCallback(async (id: number) => {
    setActionError(null);
    try {
      await deleteMutation.mutateAsync(id);
      setEditingId(null);
      setDraft({ title: "", description: "" });
    } catch (e) {
      setActionError(e instanceof Error ? e.message : String(e));
    }
  }, [deleteMutation]);

  // Fill form with selected item for editing.
  const startEdit = useCallback((item: Item) => {
    setEditingId(item.id);
    setDraft({ title: item.title, description: item.description });
  }, []);

  const onNext = useCallback(() => {
    if (nextUrl) setPageUrl(nextUrl);
  }, [nextUrl]);

  const onPrevious = useCallback(() => {
    if (previousUrl) setPageUrl(previousUrl);
  }, [previousUrl]);

  return {
    q,
    setQ,
    items,
    loading,
    error,
    draft,
    setDraft,
    editingId,
    setEditingId,
    nextUrl,
    previousUrl,
    onNext,
    onPrevious,
    submit,
    remove,
    startEdit,
  };
}

