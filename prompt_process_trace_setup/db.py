"""
db.py — PostgreSQL logging for OSS vs Commercial LLM runs.
Railway injects DATABASE_URL automatically when a Postgres service is linked.
Each row optionally stores the Confident AI trace_id so DB rows and
dashboard traces share the same identity.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor


def _conn():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise EnvironmentError("DATABASE_URL not set — link a PostgreSQL service in Railway")
    return psycopg2.connect(url)


def init_db() -> None:
    """Create the llm_runs table if it doesn't exist; migrate old deployments."""
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS llm_runs (
                id             SERIAL PRIMARY KEY,
                run_at         TIMESTAMPTZ DEFAULT NOW(),
                trace_id       TEXT,
                model_id       TEXT NOT NULL,
                model_type     TEXT NOT NULL,
                prompt         TEXT NOT NULL,
                output         TEXT,
                error          TEXT,
                elapsed_sec    FLOAT,
                prompt_tokens  INT,
                output_tokens  INT,
                mode           TEXT
            );
        """)
        # idempotent migrations for tables that existed before trace_id was added
        cur.execute("ALTER TABLE llm_runs ADD COLUMN IF NOT EXISTS trace_id TEXT;")
        cur.execute("ALTER TABLE llm_runs ADD COLUMN IF NOT EXISTS prompt_tokens INT;")
        cur.execute("ALTER TABLE llm_runs ADD COLUMN IF NOT EXISTS output_tokens INT;")
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
    trace_id: str | None = None,
    prompt_tokens: int | None = None,
    output_tokens: int | None = None,
) -> int:
    """Insert one LLM run and return its id."""
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO llm_runs
                (model_id, model_type, prompt, output, error, elapsed_sec,
                 mode, trace_id, prompt_tokens, output_tokens)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (model_id, model_type, prompt, output or "", error, elapsed_sec,
             mode, trace_id, prompt_tokens, output_tokens),
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
