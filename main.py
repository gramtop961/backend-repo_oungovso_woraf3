import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document

app = FastAPI(title="Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CategoryOut(BaseModel):
    id: str
    name: str
    slug: str
    icon: Optional[str] = None


class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    category: str
    brand: Optional[str] = None
    rating: float
    reviews_count: int
    images: List[str] = []
    colors: List[str] = []
    sizes: List[str] = []
    in_stock: bool = True
    discount_percent: float = 0
    tags: List[str] = []


@app.get("/")
def read_root():
    return {"message": "Store API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_name"] = getattr(db, 'name', 'unknown')
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# Utilities

def _to_id_str(doc: dict) -> dict:
    d = {**doc}
    if d.get("_id"):
        d["id"] = str(d.pop("_id"))
    return d


# Seed demo data if empty

def _ensure_seed():
    if db is None:
        return
    if "category" not in db.list_collection_names() or db["category"].count_documents({}) == 0:
        categories = [
            {"name": "Одежда", "slug": "clothes", "icon": "Shirt"},
            {"name": "Обувь", "slug": "shoes", "icon": "Shoe"},
            {"name": "Электроника", "slug": "electronics", "icon": "Smartphone"},
            {"name": "Дом и дача", "slug": "home", "icon": "Home"},
            {"name": "Красота", "slug": "beauty", "icon": "Sparkles"},
            {"name": "Спорт", "slug": "sport", "icon": "Dumbbell"},
        ]
        if len(categories):
            db["category"].insert_many(categories)
    if "product" not in db.list_collection_names() or db["product"].count_documents({}) == 0:
        demo_products = [
            {
                "title": "Кроссовки AirFlex X",
                "description": "Лёгкие, дышащие, для бега и прогулок",
                "price": 5999,
                "category": "Электроника" if i == -1 else "Обувь",
                "brand": "AirFlex",
                "rating": 4.7,
                "reviews_count": 321,
                "images": [
                    "https://images.unsplash.com/photo-1608231387042-66d1773070a5?q=80&w=1200&auto=format&fit=crop",
                ],
                "colors": ["Белый", "Черный", "Серый"],
                "sizes": ["38", "39", "40", "41", "42", "43"],
                "in_stock": True,
                "discount_percent": 20,
                "tags": ["кроссовки", "спорт"],
            }
            for i in range(1)
        ] + [
            {
                "title": "Футболка Basic Cotton",
                "description": "100% хлопок, унисекс",
                "price": 899,
                "category": "Одежда",
                "brand": "Cotty",
                "rating": 4.6,
                "reviews_count": 1542,
                "images": [
                    "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?q=80&w=1200&auto=format&fit=crop",
                ],
                "colors": ["Белый", "Черный", "Синий"],
                "sizes": ["S", "M", "L", "XL"],
                "in_stock": True,
                "discount_percent": 10,
                "tags": ["футболка", "одежда"],
            },
            {
                "title": "Наушники Sonic Pro",
                "description": "Шумоподавление, до 40ч работы",
                "price": 7990,
                "category": "Электроника",
                "brand": "Sonic",
                "rating": 4.8,
                "reviews_count": 2134,
                "images": [
                    "https://images.unsplash.com/photo-1518443895914-05b7b8ad8b3e?q=80&w=1200&auto=format&fit=crop",
                ],
                "colors": ["Черный"],
                "sizes": [],
                "in_stock": True,
                "discount_percent": 15,
                "tags": ["наушники", "аудио"],
            },
            {
                "title": "Робот-пылесос CleanMax",
                "description": "Лидар, влажная уборка, управление из приложения",
                "price": 19990,
                "category": "Дом и дача",
                "brand": "CleanMax",
                "rating": 4.5,
                "reviews_count": 624,
                "images": [
                    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?q=80&w=1200&auto=format&fit=crop",
                ],
                "colors": ["Белый"],
                "sizes": [],
                "in_stock": True,
                "discount_percent": 30,
                "tags": ["уборка", "робот"],
            },
        ]
        if len(demo_products):
            db["product"].insert_many(demo_products)


_ensure_seed()


@app.get("/api/categories", response_model=List[CategoryOut])
def get_categories():
    items = list(db["category"].find({})) if db else []
    return [CategoryOut(**_to_id_str(it)) for it in items]


@app.get("/api/products", response_model=List[ProductOut])
def get_products(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Category name"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort: Optional[str] = Query("popularity", description="price_asc|price_desc|rating|new|popularity"),
    limit: int = Query(24, ge=1, le=100),
):
    if db is None:
        return []
    flt = {}
    if q:
        flt["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
        ]
    if category:
        flt["category"] = category
    if min_price is not None or max_price is not None:
        price = {}
        if min_price is not None:
            price["$gte"] = float(min_price)
        if max_price is not None:
            price["$lte"] = float(max_price)
        flt["price"] = price

    sort_key = None
    sort_dir = 1
    if sort == "price_asc":
        sort_key, sort_dir = "price", 1
    elif sort == "price_desc":
        sort_key, sort_dir = "price", -1
    elif sort == "rating":
        sort_key, sort_dir = "rating", -1
    else:
        sort_key, sort_dir = "reviews_count", -1

    cursor = db["product"].find(flt)
    if sort_key:
        cursor = cursor.sort(sort_key, sort_dir)
    cursor = cursor.limit(int(limit))

    items = [ProductOut(**_to_id_str(d)) for d in cursor]
    return items


@app.get("/api/products/{product_id}", response_model=Optional[ProductOut])
def get_product(product_id: str):
    if db is None:
        return None
    try:
        doc = db["product"].find_one({"_id": ObjectId(product_id)})
        return ProductOut(**_to_id_str(doc)) if doc else None
    except Exception:
        return None
