"""Base de datos SQLite de la biblioteca.

La tabla `usuarios` guarda un administrador con una nota secreta (FLAG).
Ninguna página legítima la muestra: si aparece en una respuesta, hubo
inyección SQL.
"""
import sqlite3

from flask import current_app, g

LIBROS = [
    (1, "Don Quijote de la Mancha", "Miguel de Cervantes", 1605),
    (2, "Cien años de soledad", "Gabriel García Márquez", 1967),
    (3, "Los ríos profundos", "José María Arguedas", 1958),
    (4, "La ciudad y los perros", "Mario Vargas Llosa", 1963),
]

USUARIOS = [
    (1, "ana", "ana@example.com", "lector", "Le gusta la novela"),
    (2, "luis", "luis@example.com", "lector", "Prefiere ensayo"),
    (3, "admin", "admin@example.com", "admin", "FLAG{clave_secreta_admin}"),
]


def init_db(path: str) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        DROP TABLE IF EXISTS libros;
        DROP TABLE IF EXISTS usuarios;
        CREATE TABLE libros (id INTEGER PRIMARY KEY, titulo TEXT, autor TEXT, anio INTEGER);
        CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT, rol TEXT, nota TEXT);
        """
    )
    con.executemany("INSERT INTO libros VALUES (?, ?, ?, ?)", LIBROS)
    con.executemany("INSERT INTO usuarios VALUES (?, ?, ?, ?, ?)", USUARIOS)
    con.commit()
    con.close()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def a_dicts(filas):
    return [dict(f) for f in filas]
