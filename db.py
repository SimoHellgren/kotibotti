from pathlib import Path
import sqlite3
import json

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# might be favorable to eventually just do __conform__ instead
sqlite3.register_adapter(dict, json.dumps)
sqlite3.register_converter("JSON", json.loads)

def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row

    # run init script
    conn.executescript(SCHEMA_PATH.read_text())

    # conn.execute("PRAGMA foreign_keys = ON") # just in case
    return conn