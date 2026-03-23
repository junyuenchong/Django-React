from typing import Optional

from apps.items.models import Item


class ItemRepository:
    select_related_fields: tuple[str, ...] = ()
    prefetch_related_fields: tuple[str, ...] = ()

    def base_queryset(self):
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
        qs = self.base_queryset()
        if q:
            qs = qs.filter(title__icontains=q)
        return qs.order_by("-id")

    def create_item(self, validated_data: dict) -> Item:
        return Item.objects.create(**validated_data)

    def update_item(self, instance: Item, validated_data: dict) -> Item:
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete_item(self, instance: Item) -> None:
        instance.delete()


__all__ = ["ItemRepository"]

