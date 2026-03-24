import random
from typing import Iterable

from apps.items.models import Item


def _sample_titles() -> list[str]:
    """Return a reusable list of deterministic demo title prefixes."""
    return [
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "iota",
        "kappa",
    ]


def seed_items(*, count: int = 20, clear: bool = False, seed: int = 42) -> int:
    """
    Seed demo data for Item CRUD.

    Parameters:
    - count: number of items to insert
    - clear: if True, delete existing items first
    - seed: deterministic random seed
    """
    if count <= 0:
        return 0

    if clear:
        Item.objects.all().delete()

    rng = random.Random(seed)
    titles = _sample_titles()

    to_create: list[Item] = []
    for i in range(count):
        title = titles[i % len(titles)] + f"-{rng.randint(1000, 9999)}"
        description = f"seeded description {i + 1}"
        to_create.append(Item(title=title, description=description))

    Item.objects.bulk_create(to_create)
    return count


def iter_item_ids() -> Iterable[int]:
    """Yield item IDs in descending order (newest first)."""
    return Item.objects.order_by("-id").values_list("id", flat=True)

