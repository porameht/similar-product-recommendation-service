import pytest
from app.domain.entities.recommendation import ProductRecommendation, Recommendations


def test_product_recommendation_creation():
    """Test ProductRecommendation entity creation"""
    product_data = {
        "product_id": "test123",
        "category": "Electronics",
        "sub_category": "Smartphones",
        "price": "$599.99"
    }
    
    recommendation = ProductRecommendation(
        product=product_data,
        distance=0.85
    )
    
    assert recommendation.product == product_data
    assert recommendation.distance == 0.85


def test_recommendations_creation():
    """Test Recommendations entity creation"""
    recommendation1 = ProductRecommendation(
        product={
            "product_id": "test123",
            "category": "Electronics",
            "sub_category": "Smartphones",
            "price": "$599.99"
        },
        distance=0.85
    )
    
    recommendation2 = ProductRecommendation(
        product={
            "product_id": "test456",
            "category": "Electronics",
            "sub_category": "Smartphones",
            "price": "$699.99"
        },
        distance=0.75
    )
    
    recommendations = Recommendations(results=[recommendation1, recommendation2])
    
    assert len(recommendations.results) == 2
    assert recommendations.results[0] == recommendation1
    assert recommendations.results[1] == recommendation2


def test_empty_recommendations():
    """Test Recommendations entity with empty results"""
    recommendations = Recommendations(results=[])
    
    assert len(recommendations.results) == 0
    assert recommendations.results == [] 