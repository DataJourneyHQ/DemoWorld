"""
db.py — PostgreSQL logging for OSS vs Commercial LLM runs.
Railway injects DATABASE_URL automatically when a Postgres service is linked.
"""
import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor


def _conn():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise EnvironmentError("DATABASE_URL not set — link a PostgreSQL service in Railway")
    return psycopg2.connect(url)


def init_db() -> None:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS llm_runs (
                id              SERIAL PRIMARY KEY,
                run_at          TIMESTAMPTZ DEFAULT NOW(),
                run_group_id    TEXT,
                model_id        TEXT NOT NULL,
                model_type      TEXT NOT NULL,
                prompt          TEXT NOT NULL,
                output          TEXT,
                error           TEXT,
                elapsed_sec     FLOAT,
                prompt_tokens   INT,
                output_tokens   INT,
                mode            TEXT
            );
        """)
        # idempotent migrations
        cur.execute("ALTER TABLE llm_runs ADD COLUMN IF NOT EXISTS run_group_id TEXT;")
        cur.execute("ALTER TABLE llm_runs ADD COLUMN IF NOT EXISTS prompt_tokens INT;")
        cur.execute("ALTER TABLE llm_runs ADD COLUMN IF NOT EXISTS output_tokens INT;")
        cur.execute("ALTER TABLE llm_runs DROP COLUMN IF EXISTS trace_id;")
        conn.commit()
    print("DB initialised — llm_runs table ready")


def log_run(
    model_id: str,
    model_type: str,        # 'oss' | 'commercial' | 'osscom'
    prompt: str,
    output: str | None,
    error: str | None,
    elapsed_sec: float,
    mode: str = "single",
    run_group_id: str | None = None,
    prompt_tokens: int | None = None,
    output_tokens: int | None = None,
) -> int:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO llm_runs
                (model_id, model_type, prompt, output, error, elapsed_sec,
                 mode, run_group_id, prompt_tokens, output_tokens)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (model_id, model_type, prompt, output or "", error, elapsed_sec,
             mode, run_group_id, prompt_tokens, output_tokens),
        )
        row_id = cur.fetchone()[0]
        conn.commit()
    return row_id


def log_comparison_runs(prompt: str, results: list[dict]) -> str:
    """
    Insert two rows for a side-by-side (osscom) run sharing a run_group_id.
    Each dict: model_id, output, error, elapsed_sec, prompt_tokens, output_tokens
    Returns the shared run_group_id.
    """
    run_group_id = str(uuid.uuid4())
    for r in results:
        log_run(
            model_id=r["model_id"],
            model_type=r.get("model_type", "osscom"),
            prompt=prompt,
            output=r.get("output"),
            error=r.get("error"),
            elapsed_sec=r["elapsed_sec"],
            mode="comparison",
            run_group_id=run_group_id,
            prompt_tokens=r.get("prompt_tokens"),
            output_tokens=r.get("output_tokens"),
        )
    return run_group_id


def fetch_runs(limit: int = 50) -> list[dict]:
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM llm_runs ORDER BY run_at DESC LIMIT %s;",
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]


def fetch_comparison_runs(run_group_id: str) -> list[dict]:
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM llm_runs WHERE run_group_id = %s ORDER BY id;",
            (run_group_id,),
        )
        return [dict(row) for row in cur.fetchall()]
