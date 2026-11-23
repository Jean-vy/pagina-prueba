"""Páginas de la versión inicial (seguras): portada y catálogo."""
from flask import Blueprint, render_template, request

from app.db import a_dicts, get_db

bp = Blueprint("inicio", __name__)


@bp.route("/")
def portada():
    return render_template("inicio.html", nombre=request.args.get("nombre", "visitante"))


@bp.route("/catalogo")
def catalogo():
    autor = request.args.get("autor", "")
    cur = get_db().cursor()
    if autor:
        cur.execute("SELECT titulo, autor, anio FROM libros WHERE autor LIKE ?", (f"%{autor}%",))
    else:
        cur.execute("SELECT titulo, autor, anio FROM libros ORDER BY titulo")
    return render_template("catalogo.html", libros=a_dicts(cur.fetchall()), autor=autor)
