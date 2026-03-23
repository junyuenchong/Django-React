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

    def get_queryset(self):
        q = self.request.query_params.get("q")
        return ItemRepository().get_items_queryset(q)

    def list(self, request, *args, **kwargs):
        service = ItemService(repository=ItemRepository())
        queryset = self.get_queryset()
        etag_value = build_items_etag(request)
        last_modified_value = build_items_last_modified(queryset)

        not_modified = should_return_not_modified(request, queryset, etag_value, last_modified_value)
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
        instance = ItemService(repository=ItemRepository()).create_item(serializer.validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        instance = ItemService(repository=ItemRepository()).update_item(serializer.instance, serializer.validated_data)
        serializer.instance = instance

    def perform_destroy(self, instance):
        ItemService(repository=ItemRepository()).delete_item(instance)


__all__ = ["ItemViewSet"]

