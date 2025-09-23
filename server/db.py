# server/db.py
import sqlite3
from contextlib import contextmanager

@contextmanager
def db():
    cn = sqlite3.connect("skos.sqlite", check_same_thread=False)
    try:
        yield cn
    finally:
        cn.close()
