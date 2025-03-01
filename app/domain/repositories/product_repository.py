from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.product import Product


class ProductRepository(ABC):
    """Interface for product repository operations"""
    
    @abstractmethod
    async def save_product(self, product: Product) -> None:
        """Save a product to the repository"""
        pass
    
    @abstractmethod
    async def batch_save_products(self, products: List[Product]) -> None:
        """Save multiple products to the repository"""
        pass
    
    @abstractmethod
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a product by its ID"""
        pass
    
    @abstractmethod
    async def find_similar_products(
        self, 
        product_id: str, 
        limit: int = 5, 
        distance_threshold: float = 0.95
    ) -> List[tuple[Product, float]]:
        """Find similar products to the given product ID with similarity scores"""
        pass 