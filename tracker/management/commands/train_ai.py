from django.core.management.base import BaseCommand

from ai_engine.classifier import classify_category
from ai_engine.train import train_and_save
from tracker.models import Transaction


class Command(BaseCommand):
    help = "Train the AI category and bank-identity models and reclassify transactions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-reclassify",
            action="store_true",
            help="Skip reclassifying existing transactions in the database.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Training AI models on expanded realistic financial dataset...")
        metrics = train_and_save()
        self.stdout.write(self.style.SUCCESS(f"Models trained successfully: {metrics}"))

        if not options.get("no_reclassify"):
            self.stdout.write("Reclassifying existing database transactions with updated AI model...")
            # Clean up zero-amount balance artifact rows
            noise_txns = Transaction.objects.filter(
                debit=0,
                credit=0,
                description__icontains="bualllance",
            )
            deleted_count, _ = noise_txns.delete()
            if deleted_count > 0:
                self.stdout.write(f"Removed {deleted_count} non-transaction balance artifact row(s).")

            txns = Transaction.objects.all()
            updated = []
            for t in txns:
                new_cat, new_conf = classify_category(t.description)
                old_cat, old_conf = t.category, t.confidence
                t.category = new_cat
                t.confidence = new_conf
                updated.append(t)
                self.stdout.write(
                    f"  #{t.id}: '{t.description[:35]}' [{old_cat} -> {new_cat}] (conf: {new_conf:.2f})"
                )

            if updated:
                Transaction.objects.bulk_update(updated, ["category", "confidence"])
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully reclassified {len(updated)} transaction(s)!")
                )
