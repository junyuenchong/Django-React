import hashlib
from typing import Optional, Protocol

from django.conf import settings
from django.core.cache import cache


ITEMS_CACHE_VERSION_KEY = "items:items:list_cache_version"


class QueryParamsLike(Protocol):
    """Minimal interface we need from DRF/Django query params."""

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]: ...

    def lists(self) -> list[tuple[str, list[str]]]: ...


def cache_get(key: str) -> object | None:
    """Safe cache read (returns None on any cache failure)."""
    try:
        return cache.get(key)
    except Exception:
        return None


def cache_set(key: str, value: object, ttl_seconds: int | None) -> None:
    """Safe cache write (ignores all cache failures)."""
    try:
        cache.set(key, value, ttl_seconds)
    except Exception:
        pass


def get_items_list_cache_version() -> int:
    """Return list-cache version, defaulting to 1 on miss/failure."""
    version = cache_get(ITEMS_CACHE_VERSION_KEY)
    if version is None:
        cache_set(ITEMS_CACHE_VERSION_KEY, 1, None)
        return 1
    if isinstance(version, int):
        return version
    if isinstance(version, str):
        try:
            return int(version)
        except ValueError:
            return 1
    return 1


def bump_items_list_cache_version() -> None:
    """Increment list-cache version to invalidate all cached list pages."""
    cache_set(ITEMS_CACHE_VERSION_KEY, get_items_list_cache_version() + 1, None)


def _normalize_query_params(query_params: QueryParamsLike) -> str:
    """Convert query params into a stable string for cache key hashing."""
    parts: list[str] = []
    for key, values in sorted(query_params.lists(), key=lambda x: x[0]):
        parts.append(f"{key}={','.join(sorted(values))}")
    return "&".join(parts)


def make_items_list_cache_key(query_params: QueryParamsLike) -> str:
    """Build a versioned cache key for the list endpoint based on query params."""
    version = get_items_list_cache_version()
    normalized = _normalize_query_params(query_params)
    digest = hashlib.md5(normalized.encode("utf-8")).hexdigest()  # noqa: S324
    return f"items:items:list:v{version}:{digest}"


def resolve_items_list_cache_ttl_seconds(query_params: QueryParamsLike) -> int:
    """Select a list-cache TTL using a simple tiered strategy (search/large/default)."""
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


__all__ = [
    "QueryParamsLike",
    "bump_items_list_cache_version",
    "cache_get",
    "cache_set",
    "get_items_list_cache_version",
    "make_items_list_cache_key",
    "resolve_items_list_cache_ttl_seconds",
]

