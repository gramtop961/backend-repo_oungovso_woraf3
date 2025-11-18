"""
Database Schemas for the Shop

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).
These are used for validation and documentation and read by the database viewer.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Detailed description")
    price: float = Field(..., ge=0, description="Current price")
    category: str = Field(..., description="Category name")
    brand: Optional[str] = Field(None, description="Brand name")
    rating: float = Field(4.5, ge=0, le=5, description="Average rating 0-5")
    reviews_count: int = Field(0, ge=0, description="Number of reviews")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    colors: List[str] = Field(default_factory=list, description="Available colors")
    sizes: List[str] = Field(default_factory=list, description="Available sizes / variants")
    in_stock: bool = Field(True, description="Is product in stock")
    discount_percent: float = Field(0, ge=0, le=95, description="Discount percentage if any")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")


class Category(BaseModel):
    """
    Categories collection schema
    Collection name: "category"
    """
    name: str = Field(..., description="Category display name")
    slug: str = Field(..., description="URL-friendly identifier")
    icon: Optional[str] = Field(None, description="Icon keyword")
