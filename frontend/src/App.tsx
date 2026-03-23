import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import React, { Suspense, lazy, useEffect, useState } from "react";
import { createItem, deleteItem, fetchFromUrl, listItemsCursor, updateItem } from "./api/itemsApi";
import type { CursorPaginatedResponse, Item } from "./types/item";

type Draft = { title: string; description: string };

const ItemForm = lazy(() => import("./components/ItemForm"));
const ItemTable = lazy(() => import("./components/ItemTable"));
const PaginationControls = lazy(() => import("./components/PaginationControls"));

export default function App() {
  const [pageSize] = useState(5);
  const [q, setQ] = useState("");
  const [debouncedQ, setDebouncedQ] = useState("");
  const [pageUrl, setPageUrl] = useState<string | null>(null);

  const [actionError, setActionError] = useState<string | null>(null);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [draft, setDraft] = useState<Draft>({ title: "", description: "" });
  const queryClient = useQueryClient();

  // Debounce search to avoid flooding the API on every keystroke.
  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedQ(q);
      setPageUrl(null);
    }, 250);
    return () => clearTimeout(t);
  }, [q]);

  const listQuery = useQuery<CursorPaginatedResponse<Item>>({
    queryKey: ["items", debouncedQ, pageUrl, pageSize],
    queryFn: () => {
      if (pageUrl) {
        return fetchFromUrl<CursorPaginatedResponse<Item>>(pageUrl);
      }
      return listItemsCursor({ pageSize, q: debouncedQ || undefined });
    },
  });

  const createMutation = useMutation({
    mutationFn: createItem,
    onSuccess: async () => {
      setPageUrl(null);
      await queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Draft }) => updateItem(id, payload),
    onSuccess: async () => {
      setPageUrl(null);
      await queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteItem,
    onSuccess: async () => {
      setPageUrl(null);
      await queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
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
  }

  async function onDelete(id: number) {
    if (!confirm("Are you sure you want to delete this item?")) return;
    setActionError(null);
    try {
      await deleteMutation.mutateAsync(id);
      setEditingId(null);
      setDraft({ title: "", description: "" });
    } catch (e) {
      setActionError(e instanceof Error ? e.message : String(e));
    }
  }

  function startEdit(item: Item) {
    setEditingId(item.id);
    setDraft({ title: item.title, description: item.description });
  }

  const items = listQuery.data?.results ?? [];
  const nextUrl = listQuery.data?.next ?? null;
  const previousUrl = listQuery.data?.previous ?? null;
  const queryError = listQuery.error instanceof Error ? listQuery.error.message : null;
  const error = actionError ?? queryError;
  const loading =
    listQuery.isFetching ||
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-5xl p-4 sm:p-6">
        <header className="bg-white shadow-sm border border-gray-100 rounded-2xl p-5 mb-5">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h2 className="text-2xl font-semibold">React + Django CRUD</h2>
              <p className="text-sm text-gray-600 mt-1">
                Cursor pagination + Redis cache invalidation demo.
              </p>
            </div>
            <div className="text-sm text-gray-600">
              Showing <span className="font-semibold">{items.length}</span> items
            </div>
          </div>
        </header>

        <section className="mb-5">
          <div className="bg-white shadow-sm border border-gray-100 rounded-2xl p-4 sm:p-5">
            <label className="flex flex-col sm:flex-row sm:items-center gap-2">
              <span className="font-medium text-gray-700">Search by title</span>
              <input
                className="border border-gray-200 rounded-xl px-3 py-2 w-full sm:w-96"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="e.g. hello"
              />
            </label>
          </div>
        </section>

        <section className="mb-5">
          <div className="bg-white shadow-sm border border-gray-100 rounded-2xl p-4 sm:p-5">
            <Suspense fallback={<div className="text-sm text-gray-500">Loading form...</div>}>
              <ItemForm
                loading={loading}
                editingId={editingId}
                draft={draft}
                onDraftChange={setDraft}
                onSubmit={onSubmit}
                onReset={() => {
                  setEditingId(null);
                  setDraft({ title: "", description: "" });
                }}
              />
            </Suspense>
          </div>
        </section>

        {error ? (
          <div className="mb-5 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-800 whitespace-pre-wrap">
            {error}
          </div>
        ) : null}

        <section className="mb-5">
          <div className="bg-white shadow-sm border border-gray-100 rounded-2xl p-0 overflow-hidden">
            <Suspense fallback={<div className="p-4 text-sm text-gray-500">Loading table...</div>}>
              <ItemTable items={items} loading={loading} onEdit={startEdit} onDelete={onDelete} />
            </Suspense>
          </div>
        </section>

        <Suspense fallback={<div className="text-sm text-gray-500">Loading pagination...</div>}>
          <PaginationControls
            nextUrl={nextUrl}
            previousUrl={previousUrl}
            loading={loading}
            onNext={() => {
              if (nextUrl) setPageUrl(nextUrl);
            }}
            onPrevious={() => {
              if (previousUrl) setPageUrl(previousUrl);
            }}
          />
        </Suspense>
      </div>
    </div>
  );
}
