from typing import Optional, List
from pydantic import BaseModel


class Product(BaseModel):
    """Product entity representing a product in our system"""
    
    product_id: str
    product_name: str
    main_category: str
    sub_category: str
    ratings: Optional[float] = None
    no_of_ratings: Optional[int] = None
    price: str
    price_usd: Optional[str] = None
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> dict:
        """Convert product to dictionary format"""
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "main_category": self.main_category,
            "sub_category": self.sub_category,
            "ratings": self.ratings,
            "no_of_ratings": self.no_of_ratings,
            "price": self.price,
            "price_usd": self.price_usd,
            "embedding": self.embedding
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create product from dictionary"""
        return cls(**data) 