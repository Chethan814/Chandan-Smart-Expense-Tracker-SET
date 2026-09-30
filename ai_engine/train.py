"""Train TF-IDF + Logistic Regression models for category and bank identity."""

from __future__ import annotations

from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ai_engine.classifier import clean_narration, clear_cache
from ai_engine.dataset import generate_bank_headers, generate_samples

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


def _text_clf() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=25000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    solver="lbfgs",
                    C=2.0,
                    random_state=42,
                ),
            ),
        ]
    )


def train_and_save() -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Train Transaction Category Model
    X, y = generate_samples(per_class=350)
    X_cleaned = [clean_narration(t) for t in X]
    X_train, X_test, y_train, y_test = train_test_split(
        X_cleaned, y, test_size=0.2, random_state=42, stratify=y
    )
    category_model = _text_clf()
    category_model.fit(X_train, y_train)
    cat_report = classification_report(y_test, category_model.predict(X_test), output_dict=True)
    joblib.dump(category_model, ARTIFACT_DIR / "category_model.joblib")

    # 2. Train Bank Identity Model
    BX, By = generate_bank_headers(500)
    BX_train, BX_test, By_train, By_test = train_test_split(
        BX, By, test_size=0.2, random_state=42, stratify=By
    )
    bank_model = _text_clf()
    bank_model.fit(BX_train, By_train)
    bank_report = classification_report(By_test, bank_model.predict(BX_test), output_dict=True)
    joblib.dump(bank_model, ARTIFACT_DIR / "bank_model.joblib")

    # 3. Clear cache so running app reloads new models
    clear_cache()

    # 4. Save Summary
    summary_text = (
        f"Category model accuracy: {cat_report['accuracy']:.4f}\n"
        f"Bank identity accuracy: {bank_report['accuracy']:.4f}\n"
        f"Total category training samples: {len(X)}\n"
    )
    (ARTIFACT_DIR / "training_summary.txt").write_text(summary_text, encoding="utf-8")

    return {
        "category_accuracy": round(cat_report["accuracy"], 4),
        "bank_accuracy": round(bank_report["accuracy"], 4),
        "total_samples": len(X),
    }


if __name__ == "__main__":
    metrics = train_and_save()
    print("Trained models successfully:", metrics)