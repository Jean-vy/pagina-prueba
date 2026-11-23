def test_portada(client):
    r = client.get("/?nombre=Ana")
    assert r.status_code == 200
    assert "Hola, Ana" in r.get_data(as_text=True)


def test_portada_escapa_html(client):
    r = client.get("/?nombre=<b>x</b>")
    assert "<b>x</b>" not in r.get_data(as_text=True)


def test_catalogo_completo(client):
    html = client.get("/catalogo").get_data(as_text=True)
    assert "Los ríos profundos" in html and "Don Quijote" in html


def test_catalogo_por_autor(client):
    html = client.get("/catalogo?autor=Arguedas").get_data(as_text=True)
    assert "Los ríos profundos" in html
    assert "Don Quijote" not in html
