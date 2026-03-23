import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.items.models import Item


@pytest.mark.integration
@pytest.mark.django_db
def test_cache_failure_does_not_break_list(monkeypatch):
    Item.objects.create(title="t1", description="d1")

    def boom(*_args, **_kwargs):
        raise Exception("cache down")

    monkeypatch.setattr(cache, "get", boom)
    monkeypatch.setattr(cache, "set", boom)

    client = APIClient()
    resp = client.get("/api/items/?page_size=2")

    assert resp.status_code == 200
    assert len(resp.data["results"]) == 1

