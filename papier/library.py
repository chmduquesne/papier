import papier
import sqlite3


def init() -> sqlite3.Connection:
    con = sqlite3.connect(papier.config["library"].get())
    with con as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS library("
                       "sha256sum PRIMARY KEY, "
                       "path TEXT PRIMARY KEY, "
                       "mtime REAL, "
                       "text TEXT, "
                       "tags TEXT, "
                       ")")
        # TODO find a way to store manual inputs
    return con


def add(doc: papier.Document) -> None:
    pass
