import pytest
from django.core.cache import cache
from django.conf import settings

from apps.items.services import (
    bump_items_list_cache_version,
    get_items_list_cache_version,
    resolve_items_list_cache_ttl_seconds,
)


@pytest.mark.unit
def test_bump_items_list_cache_version_increments():
    cache.clear()
    v1 = get_items_list_cache_version()
    bump_items_list_cache_version()
    v2 = get_items_list_cache_version()
    assert v2 == v1 + 1


@pytest.mark.unit
def test_ttl_strategy_search_query():
    class Params(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    ttl = resolve_items_list_cache_ttl_seconds(Params({"q": "hello"}))
    assert ttl == settings.ITEMS_LIST_CACHE_TTL_SEARCH_SECONDS

