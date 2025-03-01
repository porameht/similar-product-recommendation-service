from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.domain.entities.recommendation import Recommendations
from app.application.use_cases.get_product_recommendations import GetProductRecommendationsUseCase
from app.infrastructure.repositories.qdrant_product_repository import QdrantProductRepository
from app.config import get_settings


router = APIRouter()


def get_product_repository():
    """Dependency for product repository"""
    return QdrantProductRepository()


def get_recommendations_use_case(
    product_repository: QdrantProductRepository = Depends(get_product_repository)
):
    """Dependency for product recommendations use case"""
    return GetProductRecommendationsUseCase(product_repository)


@router.get(
    "/get-recommendation",
    response_model=Recommendations,
    summary="Get similar product recommendations",
    description="Get similar products to the given product ID within the same sub-category"
)
async def get_recommendation(
    product_id: str = Query(..., description="ID of the product to get recommendations for"),
    limit: Optional[int] = Query(None, description="Maximum number of recommendations to return"),
    use_case: GetProductRecommendationsUseCase = Depends(get_recommendations_use_case)
):
    """
    API endpoint to get product recommendations.
    
    Args:
        product_id: ID of the product to get recommendations for
        limit: Maximum number of recommendations to return (default from settings)
        
    Returns:
        Recommendations object with similar products
    """
    settings = get_settings()
    limit = limit or settings.default_recommendation_limit
    
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    
    recommendations = await use_case.execute(product_id=product_id, limit=limit)
    
    if recommendations is None:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    
    return recommendations 