from django.contrib import admin

from tracker.models import BankAccount, StatementFile, Transaction, UploadBatch


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "account_holder", "display_account", "user")
    search_fields = ("bank_name", "account_holder", "account_number")


@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "file_count", "transaction_count", "created_at")


@admin.register(StatementFile)
class StatementFileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "account", "batch", "created_at")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("txn_date", "description", "debit", "credit", "category", "account")
    list_filter = ("category", "account__bank_name")
    search_fields = ("description",)
