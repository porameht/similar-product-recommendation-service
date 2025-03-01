from typing import List, Dict, Any
from pydantic import BaseModel


class ProductRecommendation(BaseModel):
    """Product recommendation with similarity distance"""
    product: Dict[str, Any]
    distance: float


class Recommendations(BaseModel):
    """Multiple product recommendations response"""
    results: List[ProductRecommendation] 