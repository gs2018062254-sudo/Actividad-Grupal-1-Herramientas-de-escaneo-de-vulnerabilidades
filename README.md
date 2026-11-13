# Catálogo Verde — laboratorio DAST

Aplicación web pequeña para practicar un escaneo dinámico autorizado con Nuclei. Es un catálogo demostrativo sin cuentas, pagos, formularios de escritura ni almacenamiento de datos personales. La aplicación aplica escape automático de Jinja y cabeceras de seguridad para que la práctica pueda mostrar también cómo documentar una línea base segura.

## Funciones

- Catálogo con búsqueda por nombre, descripción o categoría.
- Ficha individual de cada producto.
- API JSON en `/api/products` con filtros opcionales `q` y `category`.
- Comprobación de estado en `/healthz`.
- Cabeceras CSP, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy`.
- Workflow de GitHub Actions para ejecutar Nuclei en cada push a `main`, semanalmente o a demanda.
- Despliegue preparado para Render mediante `render.yaml`.

## Ejecutar localmente

Requiere Python 3.12 o superior.

```bash
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

En macOS o Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:5000`. La API está en `http://127.0.0.1:5000/api/products`.

## Ejecutar con Docker

```bash
docker build -t catalogo-verde .
docker run --rm -p 10000:10000 catalogo-verde
```

Abre `http://127.0.0.1:10000`.

## Publicar en GitHub

1. Crea un repositorio público vacío para el equipo.
2. Copia estos archivos a la raíz del repositorio.
3. Sube el código a la rama `main`.
4. En **Settings → Secrets and variables → Actions → Variables**, crea `TARGET_URL` con la URL de tu aplicación desplegada.
5. Revisa **Actions → DAST con Nuclei**. El escaneo solo se ejecuta si `TARGET_URL` está configurado.

Configura `TARGET_URL` únicamente con la dirección del laboratorio que controla tu equipo o que está autorizado a probar. No apuntes el workflow a sitios de terceros.

## Despliegue en Render

Conecta el repositorio en Render y crea un **Blueprint** usando `render.yaml`. El servicio usa `pip install -r requirements.txt`, arranca con Gunicorn y comprueba `/healthz`. Render crea una URL pública `onrender.com`; las instancias gratuitas pueden suspenderse cuando no reciben tráfico, así que espera a que el servicio despierte antes de lanzar el escaneo.

También puedes crear un Web Service manualmente con:

- Runtime: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Health check path: `/healthz`

## Interpretación del escaneo

Nuclei prueba las plantillas seleccionadas contra la URL indicada y deja el resultado en los registros de GitHub Actions. Un escaneo sin alertas solo significa que las plantillas ejecutadas no detectaron coincidencias en ese alcance y en ese momento; no certifica que la aplicación sea invulnerable. Registra la fecha, versión usada, URL, severidad y resultados. Verifica manualmente cada hallazgo antes de reportarlo.

## Evidencia para el artículo

Completa el artículo con los enlaces reales del repositorio, la URL de Render y la ejecución de GitHub Actions. Graba una demostración de máximo cinco minutos que muestre el código, el despliegue y el resultado del workflow. No describas como realizado ningún paso que siga pendiente.

## Referencias

- [OWASP: Vulnerability Scanning Tools](https://community.owasp.org/Vulnerability_Scanning_Tools)
- [ProjectDiscovery: Nuclei Action v3](https://github.com/projectdiscovery/nuclei-action/tree/v3)
- [Render: despliegue de Flask](https://render.com/docs/deploy-flask)
- [Render: referencia de Blueprints](https://render.com/docs/blueprint-spec)
