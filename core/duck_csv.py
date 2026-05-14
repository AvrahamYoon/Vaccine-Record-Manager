"""Load CSV via DuckDB using SQL kept under sql/ (no SQL embedded in Python)."""

from __future__ import annotations

from pathlib import Path

_SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def read_csv_with_sql(csv_path: Path, sql_filename: str) -> pd.DataFrame:
    """
    Execute sql/{sql_filename} with one bound parameter (?) = absolute CSV path.
    """
    import duckdb

    sql_path = _SQL_DIR / sql_filename
    if not sql_path.is_file():
        raise FileNotFoundError(f"Missing SQL file: {sql_path}")
    sql = sql_path.read_text(encoding="utf-8").strip()
    if not sql:
        raise ValueError(f"SQL file is empty: {sql_path}")

    conn = duckdb.connect(database=":memory:")
    try:
        return conn.execute(sql, [str(csv_path.resolve())]).df()
    finally:
        conn.close()
