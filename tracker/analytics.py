from decimal import Decimal
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404

from tracker.models import BankAccount, Transaction


def metrics_for_charts(metrics: dict) -> dict:
    top5 = metrics["by_category"][:5]
    return {
        "count": metrics["count"],
        "debit": float(metrics["debit"] or 0),
        "credit": float(metrics["credit"] or 0),
        "net": float(metrics["net"] or 0),
        "categories": [row["category"] for row in metrics["by_category"]],
        "category_spent": [float(row["spent"] or 0) for row in metrics["by_category"]],
        "top5_categories": [row["category"] for row in top5],
        "top5_spent": [float(row["spent"] or 0) for row in top5],
        "months": [
            f"{row['txn_date__year']}-{row['txn_date__month']:02d}"
            for row in metrics["monthly"]
        ],
        "month_spent": [float(row["spent"] or 0) for row in metrics["monthly"]],
        "month_credit": [float(row["received"] or 0) for row in metrics["monthly"]],
        "cumulative_net": [float(row.get("cumulative_net") or 0) for row in metrics["monthly"]],
    }


def account_metrics(user, account=None, qs=None):
    if qs is None:
        qs = Transaction.objects.filter(user=user)
        if account is not None:
            qs = qs.filter(account=account)
    totals = qs.aggregate(
        debit=Sum("debit"),
        credit=Sum("credit"),
        n=Count("id"),
    )
    avg_debit = qs.aggregate(avg_debit=Avg("debit"))["avg_debit"] or 0
    debit = totals["debit"] or Decimal("0.00")
    credit = totals["credit"] or Decimal("0.00")
    count = totals["n"] or 0

    by_category = (
        qs.values("category")
        .annotate(spent=Sum("debit"), received=Sum("credit"), n=Count("id"))
        .order_by("-spent")
    )
    by_category = list(by_category)
    for row in by_category:
        row["pct"] = (float(row["spent"] or 0) / float(debit) * 100) if debit else 0

    monthly = list(
        qs.exclude(txn_date=None)
        .values("txn_date__year", "txn_date__month")
        .annotate(spent=Sum("debit"), received=Sum("credit"))
        .order_by("txn_date__year", "txn_date__month")
    )
    running_net = 0.0
    for row in monthly:
        running_net += float(row.get("received") or 0) - float(row.get("spent") or 0)
        row["cumulative_net"] = running_net

    top_category = by_category[0] if by_category else None
    max_txn = (
        qs.filter(debit__gt=0).order_by("-debit").values("description", "debit", "txn_date").first()
    )
    top_credit = (
        qs.filter(credit__gt=0).order_by("-credit").values("description", "credit", "txn_date").first()
    )

    category_map = {row["category"]: row for row in by_category}
    vendor_row = category_map.get("Vendor Payment")
    tax_row = category_map.get("Taxes/GST")
    client_row = category_map.get("Client Payment / Revenue") or category_map.get("Income")
    salary_row = category_map.get("Salary/Payroll")
    emi_row = category_map.get("Loan/EMI")
    atm_cash_qs = qs.filter(Q(category="ATM/Cash") | Q(description__icontains="atm") | Q(description__icontains="cash wdl") | Q(description__icontains="cash withdrawal")).filter(debit__gt=0)
    atm_cash_spent = atm_cash_qs.aggregate(s=Sum("debit"))["s"] or Decimal("0.00")
    atm_cash_count = atm_cash_qs.count()
    manual_count = qs.filter(is_manual=True).count()

    base_metrics = {
        "count": count,
        "debit": debit,
        "credit": credit,
        "net": credit - debit,
        "avg_debit": avg_debit,
        "by_category": by_category,
        "category_map": category_map,
        "monthly": monthly,
        "top_category": top_category,
        "max_txn": max_txn,
        "top_credit": top_credit,
        "vendor_spent": vendor_row["spent"] if vendor_row else Decimal("0.00"),
        "tax_spent": tax_row["spent"] if tax_row else Decimal("0.00"),
        "client_received": client_row["received"] if client_row else Decimal("0.00"),
        "salary_spent": salary_row["spent"] if salary_row else Decimal("0.00"),
        "emi_spent": emi_row["spent"] if emi_row else Decimal("0.00"),
        "atm_cash_spent": atm_cash_spent,
        "atm_cash_count": atm_cash_count,
        "atm_cash_txns": list(atm_cash_qs.values("id", "txn_date", "description", "debit")[:10]),
        "manual_count": manual_count,
        "num_accounts": qs.values("account").distinct().count(),
        "num_statements": qs.values("statement").distinct().count(),
        "num_categories_used": len(by_category),
    }

    base_metrics["executive_summary"] = generate_executive_summary(base_metrics)
    return base_metrics


def generate_executive_summary(metrics: dict) -> str:
    """Generate business-oriented executive summary text."""
    debit = float(metrics.get("debit") or 0)
    credit = float(metrics.get("credit") or 0)
    net = float(metrics.get("net") or 0)
    count = metrics.get("count") or 0
    top_cat = metrics.get("top_category")
    vendor_spent = float(metrics.get("vendor_spent") or 0)
    tax_spent = float(metrics.get("tax_spent") or 0)
    salary_spent = float(metrics.get("salary_spent") or 0)
    emi_spent = float(metrics.get("emi_spent") or 0)
    atm_spent = float(metrics.get("atm_cash_spent") or 0)

    status = "healthy net operating surplus" if net >= 0 else "operating cash burn deficit"

    parts = [
        f"Executive Business Briefing: Over {count} indexed transaction(s), your business recorded total revenue and commercial receipts of ₹{credit:,.2f} against total operating expenditures and disbursements of ₹{debit:,.2f}, resulting in a {status} of ₹{net:,.2f}."
    ]

    exp_details = []
    if vendor_spent > 0:
        exp_details.append(f"Vendor & supplier procurement totaled ₹{vendor_spent:,.2f} ({(vendor_spent/debit*100) if debit else 0:.1f}% of outflows)")
    if salary_spent > 0:
        exp_details.append(f"Payroll and salary disbursements totaled ₹{salary_spent:,.2f}")
    if tax_spent > 0:
        exp_details.append(f"Statutory tax compliance (GST/TDS) totaled ₹{tax_spent:,.2f}")
    if emi_spent > 0:
        exp_details.append(f"Debt servicing & working capital facilities stood at ₹{emi_spent:,.2f}")
    if atm_spent > 0:
        exp_details.append(f"Cash / ATM withdrawals totaled ₹{atm_spent:,.2f}")

    if exp_details:
        parts.append("Key Expenditure Breakdown: " + "; ".join(exp_details) + ".")

    if top_cat:
        parts.append(
            f"Primary Cost Driver: '{top_cat['category']}' represents your highest spending concentration at ₹{float(top_cat['spent']):,.2f} ({top_cat.get('pct', 0):.1f}% of total spend)."
        )

    if net >= 0:
        parts.append("Working Capital Recommendation: Positive operating cash flow provides runway for strategic supplier discounts or growth investments while reserving statutory GST and tax compliance funds.")
    else:
        parts.append("Working Capital Recommendation: Monitor vendor invoice payment terms and optimize top expense categories to extend business runway and achieve positive operating cashflow.")

    return "\n\n".join(parts)


def user_accounts(user):
    return BankAccount.objects.filter(user=user).annotate(txn_count=Count("transactions"))


def get_user_account(user, pk):
    return get_object_or_404(BankAccount, user=user, pk=pk)
