"""Local Zero-Cost Financial Vector Store & Hybrid RAG Engine for SET.

Provides local vector indexing, semantic search, and hybrid retrieval
(combining exact SQL metrics with vector similarity chunks).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LocalFinancialVectorStore:
    """In-memory local vector store for zero-cost semantic search."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            token_pattern=r"(?u)\b\w+\b",
            lowercase=True,
        )
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.matrix = None

    def build_index(self, transactions: List[Dict[str, Any]]):
        """Indexes transaction dictionaries into vector space."""
        self.documents = []
        self.metadata = []

        for txn in transactions:
            date_str = str(txn.get("date") or txn.get("txn_date") or "")
            desc = str(txn.get("description") or txn.get("narration") or "")
            debit = txn.get("debit") or (txn.get("amount") if txn.get("txn_type") == "debit" else 0.0) or 0.0
            credit = txn.get("credit") or (txn.get("amount") if txn.get("txn_type") == "credit" else 0.0) or 0.0
            cat = str(txn.get("category") or "Uncategorized")
            bank = str(txn.get("bank_name") or txn.get("account_name") or "")

            try:
                debit_f = float(debit)
            except (ValueError, TypeError):
                debit_f = 0.0

            try:
                credit_f = float(credit)
            except (ValueError, TypeError):
                credit_f = 0.0

            amt_str = f"Debit ₹{debit_f:,.2f}" if debit_f > 0 else f"Credit ₹{credit_f:,.2f}"

            chunk = (
                f"Date: {date_str} | "
                f"Payee / Narration: {desc} | "
                f"Amount: {amt_str} | "
                f"Category: {cat} | "
                f"Bank / Account: {bank}"
            )

            self.documents.append(chunk)
            self.metadata.append({
                "date": date_str,
                "description": desc,
                "debit": debit_f,
                "credit": credit_f,
                "category": cat,
                "bank": bank,
                "chunk": chunk,
            })

        if self.documents:
            try:
                self.matrix = self.vectorizer.fit_transform(self.documents)
            except Exception:
                self.matrix = None

    def search(self, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
        """Finds the most semantically relevant transactions for a query."""
        if self.matrix is None or not self.documents:
            return []

        clean_q = re.sub(r"[^\w\s]", " ", query).strip()
        if not clean_q:
            return []

        try:
            query_vec = self.vectorizer.transform([clean_q])
            scores = cosine_similarity(query_vec, self.matrix).flatten()

            top_indices = np.argsort(scores)[::-1][:top_k]
            results = []
            for idx in top_indices:
                score = float(scores[idx])
                if score > 0.04:  # Relevance threshold
                    item = dict(self.metadata[idx])
                    item["score"] = score
                    results.append(item)
            return results
        except Exception:
            return []


# In-memory session cache for vector stores
_USER_VECTOR_STORES: Dict[int, LocalFinancialVectorStore] = {}


def get_user_vector_store(user, account_id: Optional[int] = None, force_refresh: bool = False) -> LocalFinancialVectorStore:
    """Fetches or builds a LocalFinancialVectorStore for a user's transactions."""
    from tracker.models import Transaction

    user_id = user.id if user and hasattr(user, "id") else 0
    cache_key = (user_id, account_id or 0)

    if not force_refresh and cache_key in _USER_VECTOR_STORES:
        return _USER_VECTOR_STORES[cache_key]

    qs = Transaction.objects.select_related("account").filter(account__user=user)
    if account_id:
        qs = qs.filter(account_id=account_id)

    txn_data = []
    for t in qs.order_by("-txn_date")[:1500]:
        txn_data.append({
            "date": t.txn_date.isoformat() if t.txn_date else "",
            "description": t.description,
            "debit": float(t.debit or 0.0),
            "credit": float(t.credit or 0.0),
            "category": t.category or "Other",
            "bank_name": t.account.bank_name if t.account else "Default Bank",
            "account_name": str(t.account) if t.account else "Default",
        })

    vstore = LocalFinancialVectorStore()
    vstore.build_index(txn_data)
    _USER_VECTOR_STORES[cache_key] = vstore
    return vstore
