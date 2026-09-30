"""Create demo HDFC / SBI / ICICI statements for viva demonstration."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parent.parent / "sample_statements"


def _rows(start: date, days: int, seed_desc: list[tuple[str, float, str]]):
    data = []
    d = start
    bal = 85000.0
    i = 0
    while d < start + timedelta(days=days):
        desc, amount, side = seed_desc[i % len(seed_desc)]
        debit = amount if side == "dr" else 0.0
        credit = amount if side == "cr" else 0.0
        bal = bal - debit + credit
        data.append(
            {
                "Date": d.strftime("%d-%m-%Y"),
                "Narration": desc,
                "Withdrawal(Dr)": debit or "",
                "Deposit(Cr)": credit or "",
                "Balance": round(bal, 2),
            }
        )
        d += timedelta(days=3)
        i += 1
    return data


HDFC = [
    ("UPI/SWIGGY/8821 POS IND", 420.0, "dr"),
    ("NEFT SALARY ACME PVT LTD", 55000.0, "cr"),
    ("UPI/IRCTC/4412", 1850.0, "dr"),
    ("POS INDIAN OIL BANGALORE", 2100.0, "dr"),
    ("UPI/AMAZON/9001", 2499.0, "dr"),
    ("UPI/NETFLIX.COM/112", 199.0, "dr"),
    ("ATM WDL NFS", 5000.0, "dr"),
    ("UPI/BIGBASKET/330", 1760.0, "dr"),
]

SBI = [
    ("UPI/ZOMATO/221", 560.0, "dr"),
    ("IMPS SENT FAMILY", 8000.0, "dr"),
    ("UPI/PVR CINEMAS/88", 780.0, "dr"),
    ("LIC PREMIUM NACH", 2450.0, "dr"),
    ("UPI/UBER TRIP/19", 340.0, "dr"),
    ("INTEREST CREDIT", 210.0, "cr"),
]

ICICI = [
    ("UPI/BLINKIT/77", 890.0, "dr"),
    ("HOUSE RENT UPI LANDLORD", 15000.0, "dr"),
    ("GROWW SIP MUTUAL FUND", 3000.0, "dr"),
    ("UPI/APOLLO PHARMACY/4", 640.0, "dr"),
    ("UPI/JIO FIBER/91", 999.0, "dr"),
]


def write_csv(path: Path, bank: str, holder: str, acct: str, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        f"{bank}",
        f"Account Statement",
        f"Customer Name: {holder}",
        f"Account No: {acct}",
        f"Branch: Bengaluru",
        "",
    ]
    df = pd.DataFrame(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(header) + "\n")
        df.to_csv(handle, index=False)


def write_pdf(path: Path, bank: str, holder: str, acct: str, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(bank, styles["Title"]),
        Paragraph("Account Statement", styles["Heading2"]),
        Paragraph(f"Customer Name: {holder}", styles["Normal"]),
        Paragraph(f"Account No: {acct}", styles["Normal"]),
        Spacer(1, 12),
    ]
    table_data = [["Date", "Narration", "Withdrawal(Dr)", "Deposit(Cr)", "Balance"]]
    for row in rows:
        table_data.append(
            [
                row["Date"],
                row["Narration"],
                str(row["Withdrawal(Dr)"]),
                str(row["Deposit(Cr)"]),
                str(row["Balance"]),
            ]
        )
    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a28")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(table)
    doc.build(story)


def main():
    hdfc_a = _rows(date(2026, 1, 2), 60, HDFC)
    hdfc_b = _rows(date(2026, 3, 3), 60, HDFC)
    sbi = _rows(date(2026, 2, 1), 90, SBI)
    icici = _rows(date(2026, 1, 5), 80, ICICI)

    write_csv(
        OUT / "HDFC_Chandan_JanFeb2026.csv",
        "HDFC Bank",
        "CHANDAN M",
        "50100123456789",
        hdfc_a,
    )
    write_pdf(
        OUT / "HDFC_Chandan_MarApr2026.pdf",
        "HDFC Bank",
        "CHANDAN M",
        "50100123456789",
        hdfc_b,
    )
    write_pdf(
        OUT / "SBI_Ananya_Q1_2026.pdf",
        "State Bank of India",
        "ANANYA RAO",
        "38920111223344",
        sbi,
    )
    df = pd.DataFrame(icici)
    xlsx = OUT / "ICICI_Rohit_2026.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        # identity lives in sheet title + a cover sheet
        cover = pd.DataFrame(
            {
                "Field": ["Bank", "Customer Name", "Account No"],
                "Value": ["ICICI Bank", "ROHIT SHARMA", "62481000998877"],
            }
        )
        cover.to_excel(writer, sheet_name="Profile", index=False)
        df.to_excel(writer, sheet_name="Transactions", index=False)
    # also a clean csv for ICICI so identity parsing is reliable
    write_csv(
        OUT / "ICICI_Rohit_2026.csv",
        "ICICI Bank",
        "ROHIT SHARMA",
        "62481000998877",
        icici,
    )
    print(f"Wrote samples to {OUT}")


if __name__ == "__main__":
    main()
