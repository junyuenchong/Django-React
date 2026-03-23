import pytest
from django.core.cache import cache

from apps.items.services import bump_items_list_cache_version, get_items_list_cache_version


@pytest.mark.unit
def test_bump_items_list_cache_version_increments():
    cache.clear()
    v1 = get_items_list_cache_version()
    bump_items_list_cache_version()
    v2 = get_items_list_cache_version()
    assert v2 == v1 + 1

