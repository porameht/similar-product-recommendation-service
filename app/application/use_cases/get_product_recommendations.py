from typing import List, Optional

from app.domain.entities.product import Product
from app.domain.entities.recommendation import ProductRecommendation, Recommendations
from app.domain.repositories.product_repository import ProductRepository


class GetProductRecommendationsUseCase:
    """Use case for getting product recommendations"""
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    async def execute(self, product_id: str, limit: int = 5) -> Optional[Recommendations]:
        """
        Execute the use case to get product recommendations
        
        Args:
            product_id: The ID of the product to get recommendations for
            limit: The maximum number of recommendations to return
            
        Returns:
            Recommendations object containing similar products, or None if product not found
        """
        product = await self.product_repository.get_product_by_id(product_id)
        if not product:
            return None
        
        similar_products = await self.product_repository.find_similar_products(
            product_id=product_id,
            limit=limit
        )
        
        results = []
        for product, distance in similar_products:
            results.append(
                ProductRecommendation(
                    product={
                        "product_id": product.product_id,
                        "category": product.main_category,
                        "sub_category": product.sub_category,
                        "price": product.price_usd,
                    },
                    distance=distance
                )
            )
        
        return Recommendations(results=results) 