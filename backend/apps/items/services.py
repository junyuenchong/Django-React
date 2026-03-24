from typing import Mapping, Optional, Protocol

from django.db.models import QuerySet

from django.http import HttpRequest
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from core.pagination import ItemCursorPagination

from apps.items.models import Item
from apps.items.repositories import ItemRepository
from apps.items.serializers import ItemSerializer
from apps.items.helpers.list_cache import (
    QueryParamsLike,
    bump_items_list_cache_version,
    cache_get,
    cache_set,
    make_items_list_cache_key,
    resolve_items_list_cache_ttl_seconds,
)

# Protocol for views that provide serializer context
class SerializerContextView(Protocol):
    def get_serializer_context(self) -> dict[str, object]: ...

# --- Query Service: For Reading/Listing Items ---

class ItemQueryService:
    """Handles list/read queries for items including caching and pagination."""
    def __init__(
        self,
        repository: Optional[ItemRepository] = None,
    ):
        self.repository = repository or ItemRepository()

    def list_items(
        self,
        *,
        request: HttpRequest,
        queryset: QuerySet[Item],
        view: SerializerContextView,
        pagination_class: type[CursorPagination] = ItemCursorPagination,
    ) -> Response:
        cache_key = make_items_list_cache_key(request.query_params)
        cached = cache_get(cache_key)
        if cached is not None:
            return Response(cached)

        paginator = pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=view)

        serializer_context = view.get_serializer_context()
        serializer = ItemSerializer(page, many=True, context=serializer_context)
        response = paginator.get_paginated_response(serializer.data)

        ttl_seconds = resolve_items_list_cache_ttl_seconds(request.query_params)
        cache_set(cache_key, response.data, ttl_seconds)
        return response

# --- Mutation Service: For Creating/Updating/Deleting Items ---

class ItemMutationService:
    """Handles all item mutations (create/update/delete) and cache invalidation."""
    def __init__(
        self,
        repository: Optional[ItemRepository] = None,
    ):
        self.repository = repository or ItemRepository()

    def create_item(self, validated_data: Mapping[str, object]) -> Item:
        instance = self.repository.create_item(validated_data)
        bump_items_list_cache_version()
        return instance

    def update_item(self, instance: Item, validated_data: Mapping[str, object]) -> Item:
        instance = self.repository.update_item(instance, validated_data)
        bump_items_list_cache_version()
        return instance

    def delete_item(self, instance: Item) -> None:
        self.repository.delete_item(instance)
        bump_items_list_cache_version()

# --- Backward Compatibility (Legacy Aggregation Service) ---

class ItemService:
    """
    Backwards compatible interface for code expecting a single ItemService.

    - For queries: uses ItemQueryService.
    - For mutations: uses ItemMutationService.
    """
    def __init__(self, repository: Optional[ItemRepository] = None):
        self.queries = ItemQueryService(repository=repository)
        self.mutations = ItemMutationService(repository=repository)

    def list_items(
        self,
        *,
        request: HttpRequest,
        queryset: QuerySet[Item],
        view: SerializerContextView,
        pagination_class: type[CursorPagination] = ItemCursorPagination,
    ) -> Response:
        return self.queries.list_items(
            request=request,
            queryset=queryset,
            view=view,
            pagination_class=pagination_class,
        )

    def create_item(self, validated_data: Mapping[str, object]) -> Item:
        return self.mutations.create_item(validated_data)

    def update_item(self, instance: Item, validated_data: Mapping[str, object]) -> Item:
        return self.mutations.update_item(instance, validated_data)

    def delete_item(self, instance: Item) -> None:
        return self.mutations.delete_item(instance)

# --- Exports ---

__all__ = [
    "ItemRepository",
    "ItemQueryService",
    "ItemMutationService",
    "ItemService",
    "bump_items_list_cache_version",
    "make_items_list_cache_key",
    "resolve_items_list_cache_ttl_seconds",
]
