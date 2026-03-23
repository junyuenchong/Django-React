from typing import Optional

from apps.items.models import Item


class ItemRepository:
    def base_queryset(self):
        return Item.objects.all().only(
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
        )

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

