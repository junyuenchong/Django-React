from typing import Mapping, Optional

from apps.items.models import Item


class ItemRepository:
    """Data-access layer for Item queries and writes."""

    select_related_fields: tuple[str, ...] = ()
    prefetch_related_fields: tuple[str, ...] = ()

    def base_queryset(self):
        """Return a lean queryset used by list/read operations."""
        qs = Item.objects.all().only(
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
        )
        if self.select_related_fields:
            qs = qs.select_related(*self.select_related_fields)
        if self.prefetch_related_fields:
            qs = qs.prefetch_related(*self.prefetch_related_fields)
        return qs

    def get_items_queryset(self, q: Optional[str]):
        """Return list queryset, optionally filtered by title keyword."""
        qs = self.base_queryset()
        if q:
            qs = qs.filter(title__icontains=q)
        return qs.order_by("-id")

    def create_item(self, validated_data: Mapping[str, object]) -> Item:
        """Create one item record."""
        return Item.objects.create(**validated_data)

    def update_item(self, instance: Item, validated_data: Mapping[str, object]) -> Item:
        """Update mutable fields for one item record."""
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete_item(self, instance: Item) -> None:
        """Delete one item record."""
        instance.delete()


__all__ = ["ItemRepository"]

