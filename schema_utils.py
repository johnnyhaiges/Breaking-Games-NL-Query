

import sqlite3


def get_schema_text(db_path: str, sample_rows: int = 2) -> str:
    """Return a text block describing every table, its columns/types, and
    a few sample rows (helps the model understand value formats, e.g.
    whether a date column is '2026-08-09' or a unix timestamp)."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]

    blocks = []
    for table in tables:
        cur.execute(f"PRAGMA table_info('{table}')")
        cols = cur.fetchall()  # cid, name, type, notnull, dflt_value, pk
        col_lines = [f"    - {c[1]} ({c[2]}){' PRIMARY KEY' if c[5] else ''}" for c in cols]

        block = f"TABLE {table}\n" + "\n".join(col_lines)

        if sample_rows > 0:
            try:
                cur.execute(f"SELECT * FROM '{table}' LIMIT {sample_rows}")
                rows = cur.fetchall()
                col_names = [c[1] for c in cols]
                if rows:
                    sample_lines = [", ".join(str(v) for v in row) for row in rows]
                    block += f"\n    sample ({', '.join(col_names)}):\n"
                    block += "\n".join(f"      {line}" for line in sample_lines)
            except sqlite3.Error:
                pass  # skip sampling if a table is weird (e.g. locked, empty)

        blocks.append(block)

    conn.close()
    return "\n\n".join(blocks)


def list_tables(db_path: str) -> list[str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables


if __name__ == "__main__":
    # Quick manual check: python schema_utils.py path/to/your.db
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "breaking_games_p2.db"
    print(get_schema_text(path))
