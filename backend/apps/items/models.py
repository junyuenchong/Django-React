from django.db import models


class Item(models.Model):
    """Simple item entity used by the CRUD demo."""

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at", "id"], name="items_item_created_at_id_idx"),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

