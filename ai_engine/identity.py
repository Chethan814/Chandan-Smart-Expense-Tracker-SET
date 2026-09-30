"""Identify bank, account holder and account number from statement text."""

from __future__ import annotations

import hashlib
import re

from ai_engine.categories import INDIAN_BANKS
from ai_engine.classifier import classify_bank

ACCOUNT_PATTERNS = [
    re.compile(r"account\s*(?:no|number|num|#)?\s*[:.\-]*\s*([X\d\-\s]{6,28})", re.I),
    re.compile(r"a/?c\s*(?:no|number)?\s*[:.\-]*\s*([X\d\-\s]{6,28})", re.I),
    re.compile(r"acct\.?\s*(?:no)?\s*[:.\-]*\s*([X\d\-\s]{6,28})", re.I),
]

NAME_PATTERNS = [
    re.compile(r"name of the account holder\s*[:.\-,]*\s*([A-Za-z .]{3,80})", re.I),
    re.compile(r"my name\s*[:.\-,]*\s*([A-Za-z .]{3,80})", re.I),
    re.compile(r"welcome\s+(?:mr\.?|ms\.?|mrs\.?|dr\.?)?\s*([A-Za-z .]{3,80})", re.I),
    re.compile(r"customer\s*name\s*[:.\-,]*\s*([A-Za-z .]{3,80})", re.I),
    re.compile(r"account\s*holder\s*[:.\-,]*\s*([A-Za-z .]{3,80})", re.I),
    re.compile(r"a/?c\s*holder\s*[:.\-,]*\s*([A-Za-z .]{3,80})", re.I),
    re.compile(r"name of customer\s*[:.\-,]*\s*([A-Za-z .]{3,80})", re.I),
    re.compile(r"(?:^|\n)\s*name\s*[:.\-]*\s*([A-Za-z .]{3,80})", re.I),
]


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def extract_account_number(text: str) -> str:
    for pat in ACCOUNT_PATTERNS:
        match = pat.search(text or "")
        if match:
            digits = _digits(match.group(1))
            if len(digits) >= 4:
                return digits[-18:]
    # last resort: a long digit run
    runs = re.findall(r"\d{9,18}", text or "")
    return runs[0] if runs else "UNKNOWN"


def extract_holder_name(text: str) -> str:
    for pat in NAME_PATTERNS:
        match = pat.search(text or "")
        if match:
            name = re.sub(r"\s+", " ", match.group(1)).strip(" :-")
            lowered = name.lower()
            if lowered in {"statement", "savings", "account", "customer", "bank", "name", "value", "field"}:
                continue
            if 3 <= len(name) <= 60:
                return name.title()
    return "Unknown Customer"


def extract_bank_name(text: str) -> str:
    upper = (text or "").upper()
    aliases = {
        "HDFC": "HDFC Bank",
        "ICICI": "ICICI Bank",
        "STATE BANK OF INDIA": "State Bank of India",
        "SBI": "State Bank of India",
        "AXIS": "Axis Bank",
        "KOTAK": "Kotak Mahindra Bank",
        "PUNJAB NATIONAL": "Punjab National Bank",
        "PNB": "Punjab National Bank",
        "CANARA": "Canara Bank",
        "BANK OF BARODA": "Bank of Baroda",
        "UNION BANK": "Union Bank of India",
        "YES BANK": "Yes Bank",
        "IDFC": "IDFC First Bank",
        "INDUSIND": "IndusInd Bank",
        "FEDERAL BANK": "Federal Bank",
        "BANK OF INDIA": "Bank of India",
        "INDIAN BANK": "Indian Bank",
    }
    for key, official in aliases.items():
        if key in upper:
            return official
    predicted, confidence = classify_bank(text)
    if confidence >= 0.35 and predicted in INDIAN_BANKS:
        return predicted
    return predicted if predicted else "Unknown Bank"


def fingerprint(bank_name: str, holder: str, account_no: str) -> str:
    acct = _digits(account_no)[-4:] if _digits(account_no) else "0000"
    raw = f"{(bank_name or '').lower().strip()}|{(holder or '').lower().strip()}|{acct}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def identify_statement(header_text: str, fallback_filename: str = "") -> dict:
    blob = f"{header_text or ''}\n{fallback_filename or ''}"
    bank = extract_bank_name(blob)
    holder = extract_holder_name(blob)
    account = extract_account_number(blob)
    return {
        "bank_name": bank,
        "account_holder": holder,
        "account_number": account,
        "fingerprint": fingerprint(bank, holder, account),
        "display_account": ("XXXX" + account[-4:]) if len(account) >= 4 else account,
    }
