"""Pruebas del módulo de reseñas.

- test_*:          la funcionalidad legítima (secfix las usa para V3: el parche no rompe nada).
- test_exploit_*:  el ataque NO debe funcionar. Con el código vulnerable fallan;
                   secfix exige que el parche haga pasar alguna (V4).
"""
import io


def subir(client, nombre, contenido=b"\x89PNG\r\n\x1a\n datos"):
    return client.post("/resenas/portada", data={"portada": (io.BytesIO(contenido), nombre)},
                       content_type="multipart/form-data")


# --- funcionalidad -----------------------------------------------------------

def test_buscar_libro(client):
    r = client.get("/resenas/buscar?titulo=Quijote")
    assert r.status_code == 200
    assert "Miguel de Cervantes" in r.get_data(as_text=True)


def test_vista_previa(client):
    r = client.get("/resenas/vista-previa?texto=Me gustó mucho")
    assert r.status_code == 200
    assert "Me gustó mucho" in r.get_data(as_text=True)


def test_subir_portada_png(client, app):
    r = subir(client, "portada.png")
    assert r.status_code == 200
    import os
    assert any(f.endswith(".png") for f in os.listdir(app.config["UPLOAD_DIR"]))


def test_libro_por_id(client):
    r = client.get("/resenas/libro/1?limite=1")
    assert r.status_code == 200
    assert "Don Quijote" in r.get_data(as_text=True)


# --- ataques -----------------------------------------------------------------

def test_exploit_sqli_buscar(client):
    ataque = "x' UNION SELECT nombre, email, nota FROM usuarios --"
    r = client.get("/resenas/buscar", query_string={"titulo": ataque})
    assert "FLAG{" not in r.get_data(as_text=True)


def test_exploit_xss_vista_previa(client):
    r = client.get("/resenas/vista-previa", query_string={"texto": "<script>alert(1)</script>"})
    assert "<script>alert(1)</script>" not in r.get_data(as_text=True)


def test_exploit_upload_extension_peligrosa(client, tmp_path):
    subir(client, "shell.php", b"<?php system($_GET['c']); ?>")
    guardados = [p.name for p in tmp_path.rglob("*") if p.is_file()]
    assert not any(n.endswith(".php") for n in guardados), guardados


def test_exploit_upload_path_traversal(client, tmp_path):
    subir(client, "../fuera.png")
    assert not (tmp_path / "fuera.png").exists()


def test_exploit_sqli_libro_no_explotable(client):
    # El falso positivo: int() rechaza el ataque, así que esta prueba pasa siempre.
    r = client.get("/resenas/libro/1", query_string={"limite": "1 UNION SELECT nombre, email, nota FROM usuarios"})
    assert "FLAG{" not in r.get_data(as_text=True)
