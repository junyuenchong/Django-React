from rest_framework.pagination import CursorPagination


class ItemCursorPagination(CursorPagination):
    # Cursor-based pagination is stable for growing datasets and avoids
    # expensive offset scans.
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    # Use a unique, monotonic field for deterministic cursor ordering.
    ordering = "-id"


__all__ = ["ItemCursorPagination"]

