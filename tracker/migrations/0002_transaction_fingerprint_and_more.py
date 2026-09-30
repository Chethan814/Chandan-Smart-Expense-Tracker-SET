import hashlib
from django.conf import settings
from django.db import migrations, models


def populate_fingerprints(apps, schema_editor):
    Transaction = apps.get_model('tracker', 'Transaction')
    seen = set()
    to_delete = []
    to_update = []
    for txn in Transaction.objects.all():
        raw = f"{txn.account_id}|{txn.txn_date}|{(txn.description or '').strip().lower()}|{txn.debit}|{txn.credit}"
        fp = hashlib.sha256(raw.encode()).hexdigest()
        key = (txn.user_id, fp)
        if key in seen:
            to_delete.append(txn.id)
        else:
            seen.add(key)
            txn.fingerprint = fp
            to_update.append(txn)

    if to_delete:
        Transaction.objects.filter(id__in=to_delete).delete()
    if to_update:
        Transaction.objects.bulk_update(to_update, ['fingerprint'], batch_size=500)


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='fingerprint',
            field=models.CharField(db_index=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='uploadbatch',
            name='duplicates_skipped',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(populate_fingerprints, reverse_code=migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='transaction',
            unique_together={('user', 'fingerprint')},
        ),
    ]

