from django.core.management.base import BaseCommand

from apps.items.seeder.items import seed_items


class Command(BaseCommand):
    help = "Seed demo data for Item CRUD"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20, help="Number of items to create")
        parser.add_argument("--clear", action="store_true", help="Delete existing items before seeding")
        parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]
        seed = options["seed"]

        created = seed_items(count=count, clear=clear, seed=seed)
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} items."))

