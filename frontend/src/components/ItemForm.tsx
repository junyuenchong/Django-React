import React from "react";

type Draft = { title: string; description: string };

type ItemFormProps = {
  loading: boolean;
  editingId: number | null;
  draft: Draft;
  onDraftChange: (next: Draft) => void;
  onSubmit: (e: React.FormEvent) => void;
  onReset: () => void;
};

function ItemForm(props: ItemFormProps) {
  const { loading, editingId, draft, onDraftChange, onSubmit, onReset } = props;

  return (
    <form onSubmit={onSubmit}>
      <div className="flex flex-col gap-4 md:flex-row">
        <label className="flex flex-col gap-1 md:w-80">
          <span>Title:</span>
          <input
            className="border border-gray-200 rounded-xl px-3 py-2 bg-white"
            value={draft.title}
            onChange={(e) => onDraftChange({ ...draft, title: e.target.value })}
            placeholder="title"
          />
        </label>

        <label className="flex flex-col gap-1 flex-1">
          <span>Description:</span>
          <textarea
            className="border border-gray-200 rounded-xl px-3 py-2 min-h-[90px] bg-white"
            value={draft.description}
            onChange={(e) => onDraftChange({ ...draft, description: e.target.value })}
            placeholder="description"
          />
        </label>
      </div>

      <div className="flex gap-3 mt-4">
        <button
          className="bg-blue-600 border border-blue-600 text-white rounded px-3 py-2 hover:bg-blue-700 disabled:opacity-60"
          type="submit"
          disabled={loading}
        >
          {editingId == null ? "Create" : "Save"}
        </button>

        <button
          className="border border-gray-200 rounded-xl px-3 py-2 hover:bg-gray-50 disabled:opacity-60"
          type="button"
          onClick={onReset}
          disabled={loading}
        >
          Reset
        </button>
      </div>
    </form>
  );
}

export default React.memo(ItemForm);
