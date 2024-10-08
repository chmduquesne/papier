import papier
import sqlite3
import logging
import os.path
import json
from typing import Generator

# Logger for this plugin
log = logging.getLogger(__name__)

# path of the database
db = papier.config["library"].get()


def init_db() -> None:
    with sqlite3.connect(db) as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS library("
                       "sha256sum PRIMARY KEY, "
                       "path TEXT, "
                       "mtime REAL, "
                       "text TEXT, "
                       "tags TEXT"
                       ")")
        # TODO find a way to store manual inputs


# Initialize the database if it does not exist
if not os.path.exists(db):
    init_db()


def add(doc: papier.Document, tags: dict = {}) -> None:
    log.info(f'inserting {doc} in the library')
    sql = ('INSERT INTO library'
           '(sha256sum, path, mtime, text, tags) '
           'VALUES(?, ?, ?, ?, ?)')
    with sqlite3.connect(db) as cursor:
        cursor.execute(sql, (doc.sha256sum(), doc.path, doc.mtime(),
                             doc.text, json.dumps(tags)))


def has(doc: papier.Document) -> bool:
    log.info(f'checking if {doc} is in the library')
    # First, check if the path of the document exists with the same mtime
    sql = 'SELECT * FROM library WHERE path = ? and mtime = ?'
    with sqlite3.connect(db) as cursor:
        res = cursor.execute(sql, (doc.path, doc.mtime()))
        rows = res.fetchall()
        if len(rows) == 1:
            return True
    # Then, check the checksum
    sql = 'SELECT * FROM library WHERE sha256sum = ?'
    with sqlite3.connect(db) as cursor:
        res = cursor.execute(sql, (doc.sha256sum(),))
        if len(res.fetchall()) > 0:
            return True
    return False


def update(doc: papier.Document, tags: dict = {}) -> None:
    log.info(f'updating {doc} in the library')
    sql = ('UPDATE library SET '
           'path = ?, '
           'mtime = ?, '
           'text = ?, '
           'tags = ?, '
           'WHERE sha256sum = ?')
    with sqlite3.connect(db) as cursor:
        cursor.execute(sql, (doc.path, doc.mtime(), doc.text,
                             json.dumps(tags), doc.sha256sum()))


def delete(doc: papier.Document) -> None:
    log.info(f'removing {doc} from the library')
    sql = ('DELETE FROM library WHERE sha256sum = ?')
    with sqlite3.connect(db) as cursor:
        cursor.execute(sql, (doc.sha256sum(),))


def list() -> Generator[tuple, tuple, None]:
    sql = 'SELECT * from library'
    with sqlite3.connect(db) as cursor:
        res = cursor.execute(sql, ())
        yield res.fetchone()
