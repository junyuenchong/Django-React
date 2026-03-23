import hashlib
from typing import Any, Mapping, Optional

from django.conf import settings

from django.core.cache import cache
from django.http import HttpRequest
from rest_framework.response import Response

from core.pagination import ItemCursorPagination

from apps.items.repositories import ItemRepository
from apps.items.serializers import ItemSerializer


ITEMS_CACHE_VERSION_KEY = "items:items:list_cache_version"


def get_items_list_cache_version() -> int:
    try:
        version = cache.get(ITEMS_CACHE_VERSION_KEY)
    except Exception:
        # Cache might be down. Fall back to a safe default.
        version = None

    if version is None:
        version = 1
        try:
            cache.set(ITEMS_CACHE_VERSION_KEY, version, None)
        except Exception:
            # Ignore cache write failures.
            pass

    return int(version)


def bump_items_list_cache_version() -> None:
    try:
        version = get_items_list_cache_version()
        cache.set(ITEMS_CACHE_VERSION_KEY, version + 1, None)
    except Exception:
        # Cache might be unavailable. Degrade gracefully.
        pass


def _normalize_query_params(query_params: Any) -> str:
    parts: list[str] = []
    if hasattr(query_params, "lists"):
        for key, values in sorted(query_params.lists(), key=lambda x: x[0]):
            parts.append(f"{key}={','.join(sorted([str(v) for v in values]))}")
    elif isinstance(query_params, Mapping):
        for key, value in sorted(query_params.items(), key=lambda x: x[0]):
            parts.append(f"{key}={value}")
    else:
        parts.append(str(query_params))
    return "&".join(parts)


def make_items_list_cache_key(query_params: Any) -> str:
    version = get_items_list_cache_version()
    normalized = _normalize_query_params(query_params)
    digest = hashlib.md5(normalized.encode("utf-8")).hexdigest()  # noqa: S324
    return f"items:items:list:v{version}:{digest}"


def resolve_items_list_cache_ttl_seconds(query_params: Any) -> int:
    default_ttl = int(settings.ITEMS_LIST_CACHE_TTL_SECONDS)
    search_ttl = int(settings.ITEMS_LIST_CACHE_TTL_SEARCH_SECONDS)
    large_page_ttl = int(settings.ITEMS_LIST_CACHE_TTL_LARGE_PAGE_SECONDS)

    if hasattr(query_params, "get"):
        q = (query_params.get("q") or "").strip()
        page_size_raw = query_params.get("page_size")
    else:
        q = ""
        page_size_raw = None

    if q:
        return search_ttl

    try:
        page_size = int(page_size_raw) if page_size_raw else 0
    except (TypeError, ValueError):
        page_size = 0

    if page_size > 10:
        return large_page_ttl

    return default_ttl


class ItemService:
    def __init__(self, repository: Optional[ItemRepository] = None):
        self.repository = repository or ItemRepository()

    def list_items(
        self,
        *,
        request: HttpRequest,
        queryset,
        view,
        pagination_class=ItemCursorPagination,
    ) -> Response:
        cache_key = make_items_list_cache_key(request.query_params)
        try:
            cached = cache.get(cache_key)
        except Exception:
            cached = None
        if cached is not None:
            return Response(cached)

        paginator = pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=view)

        serializer_context = view.get_serializer_context()
        serializer = ItemSerializer(page, many=True, context=serializer_context)
        response = paginator.get_paginated_response(serializer.data)

        try:
            ttl_seconds = resolve_items_list_cache_ttl_seconds(request.query_params)
            cache.set(cache_key, response.data, ttl_seconds)
        except Exception:
            # Ignore cache write failures.
            pass
        return response

    def create_item(self, validated_data: dict):
        instance = self.repository.create_item(validated_data)
        bump_items_list_cache_version()
        return instance

    def update_item(self, instance, validated_data: dict):
        instance = self.repository.update_item(instance, validated_data)
        bump_items_list_cache_version()
        return instance

    def delete_item(self, instance) -> None:
        self.repository.delete_item(instance)
        bump_items_list_cache_version()


__all__ = [
    "ItemRepository",
    "ItemService",
    "bump_items_list_cache_version",
    "get_items_list_cache_version",
    "make_items_list_cache_key",
    "resolve_items_list_cache_ttl_seconds",
]

