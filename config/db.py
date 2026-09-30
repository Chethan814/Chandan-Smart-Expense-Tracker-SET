"""Prefer PostgreSQL; fall back to SQLite if the server is not running yet."""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # unused here, kept for clarity


def postgres_config():
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "smt_db"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }


def sqlite_config(base_dir: Path):
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": base_dir / "db.sqlite3",
    }


def postgres_is_available(cfg: dict) -> bool:
    try:
        import psycopg

        with psycopg.connect(
            dbname="postgres",
            user=cfg["USER"],
            password=cfg["PASSWORD"],
            host=cfg["HOST"],
            port=cfg["PORT"],
            connect_timeout=3,
        ) as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


def ensure_database(cfg: dict) -> None:
    import psycopg
    from psycopg import sql

    with psycopg.connect(
        dbname="postgres",
        user=cfg["USER"],
        password=cfg["PASSWORD"],
        host=cfg["HOST"],
        port=cfg["PORT"],
        autocommit=True,
    ) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (cfg["NAME"],),
        ).fetchone()
        if not exists:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(cfg["NAME"])))


def build_databases(base_dir: Path) -> dict:
    if os.environ.get("SMT_USE_SQLITE") == "1":
        print("SMT: using SQLite (SMT_USE_SQLITE=1).", file=sys.stderr)
        return {"default": sqlite_config(base_dir)}

    cfg = postgres_config()
    if postgres_is_available(cfg):
        try:
            ensure_database(cfg)
            print("SMT: using PostgreSQL database", cfg["NAME"], file=sys.stderr)
            return {"default": cfg}
        except Exception as exc:
            print("SMT: PostgreSQL reachable but setup failed:", exc, file=sys.stderr)

    print(
        "SMT: PostgreSQL not available — using SQLite. Install PostgreSQL and restart to switch.",
        file=sys.stderr,
    )
    return {"default": sqlite_config(base_dir)}
