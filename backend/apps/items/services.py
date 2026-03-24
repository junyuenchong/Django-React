import hashlib
from typing import Mapping, Optional, Protocol

from django.conf import settings
from django.db.models import QuerySet

from django.core.cache import cache
from django.http import HttpRequest
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from core.pagination import ItemCursorPagination

from apps.items.models import Item
from apps.items.repositories import ItemRepository
from apps.items.serializers import ItemSerializer

# Key used to store the version of the item list cache
ITEMS_CACHE_VERSION_KEY = "items:items:list_cache_version"

# Protocol for query params; .get and .lists needed
class QueryParamsLike(Protocol):
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]: ...
    def lists(self) -> list[tuple[str, list[str]]]: ...

# Protocol for views that provide serializer context
class SerializerContextView(Protocol):
    def get_serializer_context(self) -> dict[str, object]: ...

# Safely get from cache, never raises, returns None on error
def _cache_get(key: str) -> object | None:
    try:
        return cache.get(key)
    except Exception:
        return None

# Safely set to cache, never raises
def _cache_set(key: str, value: object, ttl_seconds: int | None) -> None:
    try:
        cache.set(key, value, ttl_seconds)
    except Exception:
        pass

# Get the current cache version or set to 1 if missing
def get_items_list_cache_version() -> int:
    version = _cache_get(ITEMS_CACHE_VERSION_KEY)
    if version is None:
        version = 1
        _cache_set(ITEMS_CACHE_VERSION_KEY, version, None)
    if isinstance(version, int):
        return version
    if isinstance(version, str):
        try:
            return int(version)
        except ValueError:
            return 1
    return 1

# Increment the cache version to invalidate list cache
def bump_items_list_cache_version() -> None:
    version = get_items_list_cache_version()
    _cache_set(ITEMS_CACHE_VERSION_KEY, version + 1, None)

# Produce a stable string from query params for hashing
def _normalize_query_params(query_params: QueryParamsLike) -> str:
    parts: list[str] = []
    for key, values in sorted(query_params.lists(), key=lambda x: x[0]):
        parts.append(f"{key}={','.join(sorted(values))}")
    return "&".join(parts)

# Make a cache key for the item list, includes version and query hash
def make_items_list_cache_key(query_params: QueryParamsLike) -> str:
    version = get_items_list_cache_version()
    normalized = _normalize_query_params(query_params)
    digest = hashlib.md5(normalized.encode("utf-8")).hexdigest()  # noqa: S324
    return f"items:items:list:v{version}:{digest}"

# Choose a cache TTL based on query params
def resolve_items_list_cache_ttl_seconds(query_params: QueryParamsLike) -> int:
    default_ttl = int(settings.ITEMS_LIST_CACHE_TTL_SECONDS)
    search_ttl = int(settings.ITEMS_LIST_CACHE_TTL_SEARCH_SECONDS)
    large_page_ttl = int(settings.ITEMS_LIST_CACHE_TTL_LARGE_PAGE_SECONDS)

    q = (query_params.get("q") or "").strip()
    page_size_raw = query_params.get("page_size")

    if q:
        return search_ttl

    try:
        page_size = int(page_size_raw) if page_size_raw else 0
    except (TypeError, ValueError):
        page_size = 0

    if page_size > 10:
        return large_page_ttl

    return default_ttl

# Encapsulates business logic for Item CRUD and list caching
class ItemService:
    def __init__(self, repository: Optional[ItemRepository] = None):
        # Use provided repository or default
        self.repository = repository or ItemRepository()

    # List items with pagination, using cache for performance
    def list_items(
        self,
        *,
        request: HttpRequest,
        queryset: QuerySet[Item],
        view: SerializerContextView,
        pagination_class: type[CursorPagination] = ItemCursorPagination,
    ) -> Response:
        cache_key = make_items_list_cache_key(request.query_params)
        cached = _cache_get(cache_key)
        if cached is not None:
            return Response(cached)

        paginator = pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=view)

        serializer_context = view.get_serializer_context()
        serializer = ItemSerializer(page, many=True, context=serializer_context)
        response = paginator.get_paginated_response(serializer.data)

        ttl_seconds = resolve_items_list_cache_ttl_seconds(request.query_params)
        _cache_set(cache_key, response.data, ttl_seconds)
        return response

    # Create a new item and invalidate cache
    def create_item(self, validated_data: Mapping[str, object]) -> Item:
        instance = self.repository.create_item(validated_data)
        bump_items_list_cache_version()
        return instance

    # Update an item and invalidate cache
    def update_item(self, instance: Item, validated_data: Mapping[str, object]) -> Item:
        instance = self.repository.update_item(instance, validated_data)
        bump_items_list_cache_version()
        return instance

    # Delete an item and invalidate cache
    def delete_item(self, instance: Item) -> None:
        self.repository.delete_item(instance)
        bump_items_list_cache_version()

# Explicitly export these symbols
__all__ = [
    "ItemRepository",
    "ItemService",
    "bump_items_list_cache_version",
    "get_items_list_cache_version",
    "make_items_list_cache_key",
    "resolve_items_list_cache_ttl_seconds",
]
