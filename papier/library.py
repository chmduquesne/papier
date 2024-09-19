import papier
import sqlite3


def init() -> sqlite3.Connection:
    con = sqlite3.connect(papier.config["library"].get())
    with con as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS files("
                       "path TEXT PRIMARY KEY, "
                       "path_orig TEXT, "
                       "mtime REAL, "
                       "content TEXT, "
                       "tags TEXT, "
                       ")")
    return con


def add(path_orig: str, path: str, content: str, tags: str) -> None:
    pass
