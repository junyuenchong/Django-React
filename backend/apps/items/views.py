from core.pagination import ItemCursorPagination
from rest_framework import viewsets

from apps.items.http_cache import (
    add_cache_headers,
    build_items_etag,
    build_items_last_modified,
    should_return_not_modified,
)
from apps.items.repositories import ItemRepository
from apps.items.serializers import ItemSerializer
from apps.items.services import ItemService


class ItemViewSet(viewsets.ModelViewSet):
    """
    API controller for Item CRUD.
    """

    serializer_class = ItemSerializer
    pagination_class = ItemCursorPagination

    def _service(self) -> ItemService:
        """Return service instance used by this viewset."""
        return ItemService(repository=ItemRepository())

    def get_queryset(self):
        """Build the base queryset (optionally filtered by `q`)."""
        q = self.request.query_params.get("q")
        return ItemRepository().get_items_queryset(q)

    def list(self, request, *args, **kwargs):
        """List items with cursor pagination, Redis caching, and ETag/304 support."""
        service = self._service()
        queryset = self.get_queryset()
        etag_value = build_items_etag(request)
        last_modified_value = build_items_last_modified(queryset)

        not_modified = should_return_not_modified(
            request,
            queryset,
            etag_value,
            last_modified_value,
        )
        if not_modified is not None:
            return not_modified

        response = service.list_items(
            request=request,
            queryset=queryset,
            view=self,
            pagination_class=self.pagination_class,
        )
        return add_cache_headers(response, etag_value, last_modified_value)

    def perform_create(self, serializer):
        """Create an item and invalidate list cache via service layer."""
        instance = self._service().create_item(serializer.validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        """Update an item and invalidate list cache via service layer."""
        instance = self._service().update_item(
            serializer.instance,
            serializer.validated_data,
        )
        serializer.instance = instance

    def perform_destroy(self, instance):
        """Delete an item and invalidate list cache via service layer."""
        self._service().delete_item(instance)


__all__ = ["ItemViewSet"]

