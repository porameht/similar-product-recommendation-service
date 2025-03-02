import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.use_cases.get_product_recommendations import GetProductRecommendationsUseCase
from app.domain.entities.product import Product
from app.domain.entities.recommendation import Recommendations


@pytest.fixture
def mock_product_repository():
    """Fixture for mocked product repository"""
    return AsyncMock()


@pytest.fixture
def sample_product():
    """Fixture for a sample product"""
    return Product(
        product_id="test123",
        product_name="Test Product",
        main_category="Electronics",
        sub_category="Smartphones",
        price="$599.99",
        price_usd="$599.99",
        ratings=4.5,
        no_of_ratings=100
    )


@pytest.fixture
def similar_products(sample_product):
    """Fixture for similar products"""
    similar_product1 = Product(
        product_id="similar1",
        product_name="Similar Product 1",
        main_category="Electronics",
        sub_category="Smartphones",
        price="$649.99",
        price_usd="$649.99",
        ratings=4.3,
        no_of_ratings=80
    )
    
    similar_product2 = Product(
        product_id="similar2",
        product_name="Similar Product 2",
        main_category="Electronics",
        sub_category="Smartphones",
        price="$699.99",
        price_usd="$699.99",
        ratings=4.7,
        no_of_ratings=120
    )
    
    return [(similar_product1, 0.85), (similar_product2, 0.75)]


@pytest.mark.asyncio
async def test_execute_with_valid_product_id(mock_product_repository, sample_product, similar_products):
    """Test use case execution with valid product ID"""
    mock_product_repository.get_product_by_id.return_value = sample_product
    mock_product_repository.find_similar_products.return_value = similar_products
    
    use_case = GetProductRecommendationsUseCase(mock_product_repository)
    
    result = await use_case.execute(product_id="test123", limit=2)
    
    mock_product_repository.get_product_by_id.assert_called_once_with("test123")
    mock_product_repository.find_similar_products.assert_called_once_with(
        product_id="test123",
        limit=2
    )
    
    assert isinstance(result, Recommendations)
    assert len(result.results) == 2
    
    assert result.results[0].product["product_id"] == "similar1"
    assert result.results[0].product["category"] == "Electronics"
    assert result.results[0].product["sub_category"] == "Smartphones"
    assert result.results[0].product["price"] == "$649.99"
    assert result.results[0].distance == 0.85
    
    assert result.results[1].product["product_id"] == "similar2"
    assert result.results[1].product["category"] == "Electronics"
    assert result.results[1].product["sub_category"] == "Smartphones"
    assert result.results[1].product["price"] == "$699.99"
    assert result.results[1].distance == 0.75


@pytest.mark.asyncio
async def test_execute_with_nonexistent_product_id(mock_product_repository):
    """Test use case execution with non-existent product ID"""
    mock_product_repository.get_product_by_id.return_value = None
    
    use_case = GetProductRecommendationsUseCase(mock_product_repository)
    
    result = await use_case.execute(product_id="nonexistent", limit=5)
    
    mock_product_repository.get_product_by_id.assert_called_once_with("nonexistent")
    mock_product_repository.find_similar_products.assert_not_called()
    
    assert result is None


@pytest.mark.asyncio
async def test_execute_with_default_limit(mock_product_repository, sample_product, similar_products):
    """Test use case execution with default limit"""
    mock_product_repository.get_product_by_id.return_value = sample_product
    mock_product_repository.find_similar_products.return_value = similar_products
    
    use_case = GetProductRecommendationsUseCase(mock_product_repository)
    
    result = await use_case.execute(product_id="test123")
    
    mock_product_repository.get_product_by_id.assert_called_once_with("test123")
    mock_product_repository.find_similar_products.assert_called_once_with(
        product_id="test123",
        limit=5
    )
    
    assert isinstance(result, Recommendations) 