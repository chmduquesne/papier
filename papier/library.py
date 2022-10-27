import papier
import sqlite3



def init():
    con = sqlite3.connect(papier.config["library"].get())
    with con as cursor:
        cur.execute("CREATE TABLE IF NOT EXISTS files("
            "path TEXT PRIMARY KEY, "
            "path_orig TEXT, "
            "mtime REAL, "
            "content TEXT, "
            "tags TEXT, "
            ")")
    return con


def add(path_orig, path, content, tags):
    pass
