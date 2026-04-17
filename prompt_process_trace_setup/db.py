"""
db.py — PostgreSQL logging for OSS vs Commercial LLM runs.
Railway injects DATABASE_URL automatically when a Postgres service is linked.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def _conn():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise EnvironmentError("DATABASE_URL not set — link a PostgreSQL service in Railway")
    return psycopg2.connect(url)


def init_db() -> None:
    """Create the llm_runs table if it doesn't exist."""
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS llm_runs (
                id          SERIAL PRIMARY KEY,
                run_at      TIMESTAMPTZ DEFAULT NOW(),
                model_id    TEXT NOT NULL,
                model_type  TEXT NOT NULL,          -- 'oss' or 'commercial'
                prompt      TEXT NOT NULL,
                output      TEXT,
                error       TEXT,
                elapsed_sec FLOAT,
                mode        TEXT                    -- 'single' or 'comparison'
            );
        """)
        conn.commit()
    print("DB initialised — llm_runs table ready")


def log_run(
    model_id: str,
    model_type: str,
    prompt: str,
    output: str | None,
    error: str | None,
    elapsed_sec: float,
    mode: str = "single",
) -> int:
    """Insert one LLM run and return its id."""
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO llm_runs
                (model_id, model_type, prompt, output, error, elapsed_sec, mode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (model_id, model_type, prompt, output or "", error, elapsed_sec, mode),
        )
        row_id = cur.fetchone()[0]
        conn.commit()
    return row_id


def fetch_runs(limit: int = 50) -> list[dict]:
    """Return the most recent runs as a list of dicts."""
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM llm_runs ORDER BY run_at DESC LIMIT %s;",
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]
