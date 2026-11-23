# Biblioteca TAIS — repositorio de prueba de secfix

Web Flask sencilla (portada y catálogo de libros) que usa **secfix** como GitHub Action
desde [`Jean-vy/tais-secfix1`](https://github.com/Jean-vy/tais-secfix1). La herramienta no
se copia aquí: el workflow `.github/workflows/secfix.yml` la llama con
`uses: Jean-vy/tais-secfix1@main`.

La demostración consiste en abrir un PR que agrega un módulo de reseñas con vulnerabilidades
reales. secfix debe detectarlas, descartar el falso positivo y proponer parches validados.

## Estructura

```
app/                    la web (Flask + SQLite)
  routes/inicio.py      portada y catálogo (código seguro)
  templates/ static/    HTML y CSS
tests/                  pruebas de la versión inicial
demo-pr/                lo que se agrega en el PR de prueba
  resenas.py            módulo vulnerable → va a app/routes/
  test_resenas.py       pruebas funcionales y de ataque → va a tests/
.github/workflows/      secfix.yml
```

## 1. Crear el repositorio (una vez)

1. En GitHub crea un repositorio **vacío** (sin README), por ejemplo `tais-secfix-demo`.
2. Sube esta carpeta a `main`:

   ```bash
   git init -b main
   git add -A
   git commit -m "Web inicial de la biblioteca"
   git remote add origin https://github.com/<tu-usuario>/tais-secfix-demo.git
   git push -u origin main
   ```

3. **API key del LLM:** en *Settings → Secrets and variables → Actions → New repository secret*,
   crea `LLM_API_KEY` con tu key de Groq (la misma que usas en `tais-secfix1`; los secrets no se
   comparten entre repositorios). Para otro proveedor, crea en *Variables* `LLM_ENDPOINT` y `LLM_MODEL`.
4. (Opcional, para que bloquee el merge) *Settings → Branches → Add branch protection rule* para
   `main`: *Require a pull request before merging* y *Require status checks to pass* con el check
   **`secfix`** (aparece en la lista después de la primera ejecución).

## 2. Abrir el PR de prueba

```bash
git checkout -b agrega-resenas
cp demo-pr/resenas.py app/routes/resenas.py
cp demo-pr/test_resenas.py tests/test_resenas.py
git add -A
git commit -m "Agrega módulo de reseñas"
git push -u origin agrega-resenas
```

Abre el PR de `agrega-resenas` hacia `main`.

## 3. Qué debería pasar

| Ruta del módulo | Problema | Lo esperado |
|---|---|---|
| `buscar_libro` | Inyección SQL (CWE-89): f-string en `execute` | Verdadero positivo, sugerencia con consulta parametrizada |
| `vista_previa` | XSS reflejado (CWE-79): texto sin escapar | Verdadero positivo, sugerencia con `escape` |
| `subir_portada` | Carga insegura (CWE-434): nombre del cliente y sin lista blanca | 2 hallazgos, 1 sugerencia con `secure_filename` + extensiones permitidas |
| `libro_por_id` | Semgrep lo marca, pero los valores pasan por `int` | **Falso positivo**, descartado por el LLM |

En unos minutos verás en el PR 3 comentarios con sugerencias, un resumen con el falso positivo
descartado y el check `secfix` en rojo. Pulsa **Commit suggestion** en cada comentario
(o *Add suggestion to batch* → *Commit suggestions*). El workflow vuelve a correr y el check
queda en verde.

Cómo valida secfix cada parche aquí:
- **V1** compila; **V2** Semgrep ya no lo reporta;
- **V3** `pytest` no tiene fallas nuevas;
- **V4** bajan las pruebas `test_exploit_*` que fallaban. Con el código vulnerable fallan 4:
  la quinta (`test_exploit_sqli_libro_no_explotable`) pasa siempre, porque esa ruta es el
  falso positivo.

## Probar en local

```bash
pip install -r requirements.txt
python -m pytest -q tests          # en main: 4 pruebas pasan
flask --app "app:create_app()" run # http://127.0.0.1:5000
```

Con el módulo de reseñas copiado, `pytest` muestra las 4 pruebas de ataque fallando: es lo
que secfix debe corregir.

## Notas

- Úsalo solo con PRs desde ramas del mismo repositorio: en PRs desde forks no llega el secret.
- Las reglas de secfix son para Python/Flask; por eso la web está hecha en Flask.
