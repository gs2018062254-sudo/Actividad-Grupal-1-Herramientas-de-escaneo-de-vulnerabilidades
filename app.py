"""Small, intentionally simple web application for an authorized DAST exercise."""

from __future__ import annotations

from flask import Flask, abort, jsonify, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=64 * 1024,
    JSON_SORT_KEYS=False,
)

# Render terminates TLS at its edge and forwards the original scheme.
# Trust exactly one proxy hop; do not broaden this without reviewing the topology.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

PRODUCTS = [
    {
        "slug": "cafe-de-altura",
        "name": "Café de altura",
        "category": "Despensa",
        "description": "Café tostado en lotes pequeños, cultivado en los Andes.",
        "price": 28.50,
        "unit": "bolsa de 250 g",
    },
    {
        "slug": "miel-de-monte",
        "name": "Miel de monte",
        "category": "Despensa",
        "description": "Miel de temporada de apicultura responsable.",
        "price": 24.00,
        "unit": "frasco de 300 g",
    },
    {
        "slug": "jaboncillo-natural",
        "name": "Jabón de avena",
        "category": "Cuidado personal",
        "description": "Jabón artesanal con avena y aceites vegetales.",
        "price": 16.90,
        "unit": "barra de 100 g",
    },
    {
        "slug": "bolsa-reutilizable",
        "name": "Bolsa reutilizable",
        "category": "Hogar",
        "description": "Bolsa de algodón resistente para compras cotidianas.",
        "price": 19.90,
        "unit": "unidad",
    },
]


@app.after_request
def add_security_headers(response):
    """Set a small baseline of browser security headers on every response."""
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; object-src 'none'; base-uri 'self'; "
        "frame-ancestors 'none'; form-action 'self'",
    )
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(), geolocation=()",
    )
    if request.is_secure:
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    return response


def filtered_products(query: str = "", category: str = ""):
    query = query.casefold().strip()
    category = category.strip()
    return [
        product
        for product in PRODUCTS
        if (not category or product["category"] == category)
        and (
            not query
            or query in product["name"].casefold()
            or query in product["description"].casefold()
            or query in product["category"].casefold()
        )
    ]


@app.get("/")
def home():
    query = request.args.get("q", "")[:100]
    category = request.args.get("category", "")[:80]
    categories = sorted({item["category"] for item in PRODUCTS})
    return render_template(
        "index.html",
        products=filtered_products(query, category),
        query=query,
        category=category,
        categories=categories,
    )


@app.get("/products/<slug>")
def product_detail(slug: str):
    product = next((item for item in PRODUCTS if item["slug"] == slug), None)
    if product is None:
        abort(404)
    return render_template("product.html", product=product)


@app.get("/api/products")
def products_api():
    query = request.args.get("q", "")[:100]
    category = request.args.get("category", "")[:80]
    return jsonify({"items": filtered_products(query, category)})


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.get("/robots.txt")
def robots():
    return "User-agent: *\nAllow: /\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    # Local development only. Production uses Gunicorn (see Dockerfile/Render config).
    app.run(host="127.0.0.1", port=5000, debug=False)
