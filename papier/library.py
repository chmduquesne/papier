import papier
import sqlite3
import logging

# Logger for this plugin
log = logging.getLogger(__name__)


def init() -> sqlite3.Connection:
    con = sqlite3.connect(papier.config["library"].get())
    with con as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS library("
                       "sha256sum PRIMARY KEY, "
                       "path TEXT, "
                       "mtime REAL, "
                       "text TEXT, "
                       "tags TEXT"
                       ")")
        # TODO find a way to store manual inputs
    return con


init()


def add(doc: papier.Document) -> None:
    log.info(f'inserting {doc} in the library')
    sql = ('INSERT INTO library'
           '(sha256sum, path, mtime, text) '
           'VALUES(?, ?, ?, ?)')
    with sqlite3.connect(papier.config['library'].get()) as cursor:
        cursor.execute(sql, (doc.sha256sum(), doc.path, doc.mtime(), doc.text))


def has(doc: papier.Document) -> bool:
    log.info(f'checking if {doc} is in the library')
    # First, check if the path of the document exists with the same mtime
    sql = 'SELECT * FROM library WHERE path = ? and mtime = ?'
    with sqlite3.connect(papier.config['library'].get()) as cursor:
        res = cursor.execute(sql, (doc.path, doc.mtime()))
        rows = res.fetchall()
        if len(rows) == 1:
            return True
    sql = 'SELECT * FROM library WHERE sha256sum = ?'
    with sqlite3.connect(papier.config['library'].get()) as cursor:
        res = cursor.execute(sql, (doc.sha256sum(),))
        if len(res.fetchall()) > 0:
            return True
    return False
