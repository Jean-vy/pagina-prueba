"""Módulo de reseñas: lo que agrega el pull request de prueba.

Simula código escrito (o generado por un LLM) sin pensar en seguridad:
  - buscar_libro:     inyección SQL (CWE-89)
  - vista_previa:     XSS reflejado (CWE-79)
  - subir_portada:    carga insegura de archivos (CWE-434)
  - libro_por_id:     FALSO POSITIVO para Semgrep (los valores pasan por int)
"""
import os

from flask import Blueprint, current_app, jsonify, request

from app.db import a_dicts, get_db

bp = Blueprint("resenas", __name__)


@bp.route("/resenas/buscar")
def buscar_libro():
    titulo = request.args.get("titulo", "")
    cur = get_db().cursor()
    cur.execute(f"SELECT titulo, autor, anio FROM libros WHERE titulo LIKE '%{titulo}%'")
    return jsonify(a_dicts(cur.fetchall()))


@bp.route("/resenas/vista-previa")
def vista_previa():
    texto = request.args.get("texto", "")
    return f"<h2>Vista previa de tu reseña</h2><p>{texto}</p>"


@bp.route("/resenas/portada", methods=["POST"])
def subir_portada():
    portada = request.files["portada"]
    portada.save(os.path.join(current_app.config["UPLOAD_DIR"], portada.filename))
    return jsonify({"ok": True})


@bp.route("/resenas/libro/<int:libro_id>")
def libro_por_id(libro_id):
    limite = int(request.args.get("limite", "5"))
    cur = get_db().cursor()
    cur.execute(f"SELECT titulo, autor, anio FROM libros WHERE id = {libro_id} LIMIT {limite}")
    return jsonify(a_dicts(cur.fetchall()))
