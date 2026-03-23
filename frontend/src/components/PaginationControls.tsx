import React from "react";

export default function PaginationControls(props: {
  nextUrl: string | null;
  previousUrl: string | null;
  loading: boolean;
  onNext: () => void;
  onPrevious: () => void;
}) {
  const { nextUrl, previousUrl, loading, onNext, onPrevious } = props;

  return (
    <div className="flex items-center gap-3 mt-4 justify-end">
      <button
        type="button"
        onClick={onPrevious}
        disabled={!previousUrl || loading}
        className="border border-gray-200 rounded-xl px-3 py-2 hover:bg-gray-50 disabled:opacity-60 text-sm"
      >
        Previous
      </button>
      <div className="flex-1" />
      <button
        type="button"
        onClick={onNext}
        disabled={!nextUrl || loading}
        className="border border-gray-200 rounded-xl px-3 py-2 hover:bg-gray-50 disabled:opacity-60 text-sm"
      >
        Next
      </button>
    </div>
  );
}
