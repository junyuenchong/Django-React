import React, { Suspense, lazy } from "react";
import { useItemsCrud } from "./hooks/useItemsCrud";

const ItemForm = lazy(() => import("./components/ItemForm"));
const ItemTable = lazy(() => import("./components/ItemTable"));
const PaginationControls = lazy(() => import("./components/PaginationControls"));

// Main page component that wires UI blocks to CRUD state/actions.
export default function App() {
  const {
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
  } = useItemsCrud(5);

  // Handle form submit for create/update.
  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    await submit();
  }

  // Confirm before deleting an item from the list.
  async function onDelete(id: number) {
    if (!confirm("Are you sure you want to delete this item?")) return;
    await remove(id);
  }

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
            onNext={onNext}
            onPrevious={onPrevious}
          />
        </Suspense>
      </div>
    </div>
  );
}
