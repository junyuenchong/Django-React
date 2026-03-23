import pytest
from django.core.cache import cache
from django.http import QueryDict
from rest_framework.test import APIClient
from urllib.parse import urlparse

from apps.items.models import Item
from apps.items.services import get_items_list_cache_version, make_items_list_cache_key


@pytest.mark.integration
@pytest.mark.django_db
def test_crud_and_pagination():
    client = APIClient()

    for i in range(3):
        resp = client.post(
            "/api/items/",
            {"title": f"title-{i}", "description": f"desc-{i}"},
            format="json",
        )
        assert resp.status_code == 201

    resp = client.get("/api/items/?page_size=2")
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 2

    next_url = resp.data["next"]
    assert next_url is not None

    parsed = urlparse(next_url)
    next_path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
    resp2 = client.get(next_path)
    assert resp2.status_code == 200
    assert len(resp2.data["results"]) == 1


@pytest.mark.integration
@pytest.mark.django_db
def test_update_invalidate_list_cache_key():
    client = APIClient()
    cache.clear()

    item = Item.objects.create(title="t1", description="d1")

    params = QueryDict("page_size=10")
    old_key = make_items_list_cache_key(params)

    resp = client.get("/api/items/?page_size=10")
    assert resp.status_code == 200
    assert cache.get(old_key) is not None

    v_before = get_items_list_cache_version()

    resp = client.patch(
        f"/api/items/{item.id}/",
        {"title": "t1-updated", "description": "d1-updated"},
        format="json",
    )
    assert resp.status_code == 200

    v_after = get_items_list_cache_version()
    assert v_after == v_before + 1

    new_key = make_items_list_cache_key(params)
    resp = client.get("/api/items/?page_size=10")
    assert resp.status_code == 200
    assert cache.get(new_key) is not None

