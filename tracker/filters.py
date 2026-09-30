from datetime import datetime
from urllib.parse import urlencode

from django.db.models import Min, Max, Q

from tracker.models import BankAccount, StatementFile, Transaction


def parse_iso_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def requested_filters(request):
    return {
        "date_from": parse_iso_date(request.GET.get("from")),
        "date_to": parse_iso_date(request.GET.get("to")),
        "account_id": request.GET.get("account") or "",
        "statement_id": request.GET.get("statement") or "",
        "category": request.GET.get("category") or "",
        "txn_type": request.GET.get("type") or "",
        "min_amount": request.GET.get("min_amount") or "",
        "max_amount": request.GET.get("max_amount") or "",
        "search": request.GET.get("q") or "",
        "bank": request.GET.get("bank") or "",
        "date_from_raw": request.GET.get("from") or "",
        "date_to_raw": request.GET.get("to") or "",
    }


def apply_transaction_filters(qs, filters):
    if filters["date_from"]:
        qs = qs.filter(txn_date__gte=filters["date_from"])
    if filters["date_to"]:
        qs = qs.filter(txn_date__lte=filters["date_to"])
    if filters["account_id"]:
        qs = qs.filter(account_id=filters["account_id"])
    if filters["statement_id"]:
        qs = qs.filter(statement_id=filters["statement_id"])
    if filters.get("category"):
        qs = qs.filter(category=filters["category"])
    if filters.get("bank"):
        qs = qs.filter(account__bank_name=filters["bank"])
    if filters.get("txn_type") == "debit":
        qs = qs.filter(debit__gt=0)
    elif filters.get("txn_type") == "credit":
        qs = qs.filter(credit__gt=0)
    if filters.get("search"):
        qs = qs.filter(description__icontains=filters["search"])
    if filters.get("min_amount"):
        try:
            val = float(filters["min_amount"])
            qs = qs.filter(Q(debit__gte=val) | Q(credit__gte=val))
        except ValueError:
            pass
    if filters.get("max_amount"):
        try:
            val = float(filters["max_amount"])
            qs = qs.filter(
                (Q(debit__gt=0) & Q(debit__lte=val)) | (Q(credit__gt=0) & Q(credit__lte=val))
            )
        except ValueError:
            pass
    return qs


def query_string(filters, extra=None):
    data = {}
    if filters.get("date_from_raw"):
        data["from"] = filters["date_from_raw"]
    if filters.get("date_to_raw"):
        data["to"] = filters["date_to_raw"]
    if filters.get("account_id"):
        data["account"] = filters["account_id"]
    if filters.get("statement_id"):
        data["statement"] = filters["statement_id"]
    if filters.get("category"):
        data["category"] = filters["category"]
    if filters.get("bank"):
        data["bank"] = filters["bank"]
    if filters.get("txn_type"):
        data["type"] = filters["txn_type"]
    if filters.get("min_amount"):
        data["min_amount"] = filters["min_amount"]
    if filters.get("max_amount"):
        data["max_amount"] = filters["max_amount"]
    if filters.get("search"):
        data["q"] = filters["search"]
    if extra:
        data.update({k: v for k, v in extra.items() if v})
    return urlencode(data)


def user_banks(user):
    return (
        BankAccount.objects.filter(user=user)
        .values_list("bank_name", flat=True)
        .distinct()
        .order_by("bank_name")
    )


def user_statements(user):
    return (
        StatementFile.objects.filter(batch__user=user)
        .select_related("account")
        .order_by("original_name", "id")
    )


def date_bounds(user):
    bounds = Transaction.objects.filter(user=user).exclude(txn_date=None).aggregate(
        first=Min("txn_date"),
        last=Max("txn_date"),
    )
    return bounds["first"], bounds["last"]
