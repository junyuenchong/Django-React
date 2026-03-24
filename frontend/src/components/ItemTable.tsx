import React from "react";
import type { Item } from "../types/item";

type ItemTableProps = {
  items: Item[];
  loading: boolean;
  onEdit: (item: Item) => void;
  onDelete: (id: number) => void;
};

function ItemTable(props: ItemTableProps) {
  const { items, loading, onEdit, onDelete } = props;
  const sortedItems = React.useMemo(() => [...items].sort((a, b) => a.id - b.id), [items]);

  return (
    <table className="w-full border-collapse">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider border-b border-gray-200">
            ID
          </th>
          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider border-b border-gray-200">
            Title
          </th>
          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider border-b border-gray-200">
            Description
          </th>
          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider border-b border-gray-200">
            Created
          </th>
          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider border-b border-gray-200">
            Actions
          </th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-100">
        {loading ? (
          <tr>
            <td colSpan={5} className="px-4 py-5 text-sm text-gray-600">
              Loading...
            </td>
          </tr>
        ) : items.length === 0 ? (
          <tr>
            <td colSpan={5} className="px-4 py-8 text-sm text-gray-600">
              No data. Create an item above.
            </td>
          </tr>
        ) : (
          sortedItems.map((it) => (
            <tr key={it.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 align-top text-sm text-gray-900">{it.id}</td>
              <td className="px-4 py-3 align-top text-sm text-gray-900 max-w-[220px] break-words">
                {it.title}
              </td>
              <td className="px-4 py-3 align-top text-sm text-gray-900 max-w-[300px] break-words">
                {it.description}
              </td>
              <td className="px-4 py-3 align-top text-sm text-gray-600">{it.created_at}</td>
              <td className="px-4 py-3 align-top">
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(it)}
                    disabled={loading}
                    className="border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-100 disabled:opacity-60 text-sm"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(it.id)}
                    disabled={loading}
                    className="border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-100 disabled:opacity-60 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}

export default React.memo(ItemTable);
