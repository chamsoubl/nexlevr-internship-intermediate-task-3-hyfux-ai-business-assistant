
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MENU_FILE = PROJECT_ROOT / "data" / "menu.json"

app = FastAPI(
    title="HYFUX MIXBAR API",
    description="Business data API for HYFUX MIXBAR drinks menu.",
    version="1.0.0"
)


def load_menu():
    try:
        with open(MENU_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Menu data file not found."
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Menu JSON file is invalid."
        )


@app.get("/")
def home():
    return {
        "message": "Welcome to HYFUX MIXBAR API",
        "business": "HYFUX MIXBAR",
        "documentation": "/docs",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/menu")
def get_menu():
    return load_menu()


@app.get("/products")
def get_products(
    category: Optional[str] = None,
    max_price: Optional[float] = Query(default=None, ge=0),
    orderable_only: bool = False
):
    data = load_menu()
    products = data["products"]

    if category:
        products = [
            p for p in products
            if p.get("category", "").lower() == category.lower()
        ]

    if max_price is not None:
        products = [
            p for p in products
            if p.get("price", 0) <= max_price
        ]

    if orderable_only:
        products = [
            p for p in products
            if p.get("is_orderable", False)
        ]

    return {
        "count": len(products),
        "products": products
    }


@app.get("/products/search")
def search_products(q: str = Query(min_length=1)):
    data = load_menu()

    results = [
        p for p in data["products"]
        if q.lower() in p.get("name", "").lower()
    ]

    return {
        "query": q,
        "count": len(results),
        "products": results
    }


@app.get("/products/{product_id}")
def get_product(product_id: str):
    data = load_menu()

    for product in data["products"]:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found."
    )


@app.get("/categories")
def get_categories():
    data = load_menu()

    categories = sorted({
        p["category"]
        for p in data["products"]
        if p.get("category")
    })

    return {
        "count": len(categories),
        "categories": categories
    }
