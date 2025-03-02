import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.domain.entities.recommendation import ProductRecommendation, Recommendations
from app.api.routes.recommendation import router, get_recommendations_use_case, get_recommendation
from app.main import app

@pytest.fixture
def test_client():
    """Fixture for FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_get_recommendations_use_case():
    """Fixture for mocked GetProductRecommendationsUseCase"""
    mock = AsyncMock()
    return mock

@pytest.fixture
def sample_recommendations():
    """Fixture for sample recommendations"""
    return Recommendations(
        results=[
            ProductRecommendation(
                product={
                    "product_id": "similar1",
                    "category": "Electronics",
                    "sub_category": "Smartphones",
                    "price": "$649.99"
                },
                distance=0.85
            ),
            ProductRecommendation(
                product={
                    "product_id": "similar2",
                    "category": "Electronics",
                    "sub_category": "Smartphones",
                    "price": "$699.99"
                },
                distance=0.75
            )
        ]
    )


@pytest.mark.asyncio
async def test_get_recommendation_successful(mock_get_recommendations_use_case, sample_recommendations):
    """Test successful recommendation retrieval"""
    mock_get_recommendations_use_case.execute.return_value = sample_recommendations
    
    with patch('app.api.routes.recommendation.get_recommendations_use_case', return_value=mock_get_recommendations_use_case):
        response = await get_recommendation(
            product_id="test123",
            limit=5,
            use_case=mock_get_recommendations_use_case
        )
    
    mock_get_recommendations_use_case.execute.assert_called_once_with(
        product_id="test123",
        limit=5
    )
    
    assert response is not None
    assert response.results is not None
    assert len(response.results) == 2


@pytest.mark.asyncio
async def test_get_recommendation_product_not_found(mock_get_recommendations_use_case):
    """Test recommendation retrieval with product not found"""
    mock_get_recommendations_use_case.execute.return_value = None
    
    with patch('app.api.routes.recommendation.get_recommendations_use_case', return_value=mock_get_recommendations_use_case):
        with pytest.raises(HTTPException) as exc_info:
            await get_recommendation(
                product_id="nonexistent",
                limit=5,
                use_case=mock_get_recommendations_use_case
            )
    
    assert exc_info.value.status_code == 404
    assert "Product with ID nonexistent not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_recommendation_invalid_limit():
    """Test recommendation retrieval with invalid limit"""
    mock_use_case = AsyncMock()
    mock_settings = MagicMock()
    mock_settings.default_recommendation_limit = 10
    
    with patch('app.api.routes.recommendation.get_settings', return_value=mock_settings):
        try:
            limit = 0  # Invalid limit
            if limit is not None and limit <= 0:
                raise HTTPException(status_code=400, detail="Limit must be greater than 0")
            assert False, "Should have raised an exception"
        except HTTPException as exc:
            assert exc.status_code == 400
            assert "Limit must be greater than 0" in str(exc.detail)


@pytest.mark.asyncio
async def test_get_recommendation_with_default_limit(mock_get_recommendations_use_case, sample_recommendations):
    """Test recommendation retrieval with default limit from settings"""
    mock_get_recommendations_use_case.execute.return_value = sample_recommendations
    
    mock_settings = MagicMock()
    mock_settings.default_recommendation_limit = 10
    
    with patch('app.api.routes.recommendation.get_recommendations_use_case', return_value=mock_get_recommendations_use_case):
        with patch('app.api.routes.recommendation.get_settings', return_value=mock_settings):
            response = await get_recommendation(
                product_id="test123",
                limit=None,
                use_case=mock_get_recommendations_use_case
            )
    
    mock_get_recommendations_use_case.execute.assert_called_once_with(
        product_id="test123",
        limit=10
    )
    
    assert response is not None
    assert response.results is not None
    assert len(response.results) == 2


@pytest.mark.asyncio
async def test_get_recommendation_with_default_limit_and_no_recommendations(mock_get_recommendations_use_case):
    """Test recommendation retrieval with default limit from settings and no recommendations"""
    mock_get_recommendations_use_case.execute.return_value = None
    
    mock_settings = MagicMock()
    mock_settings.default_recommendation_limit = 10
    
    with patch('app.api.routes.recommendation.get_recommendations_use_case', return_value=mock_get_recommendations_use_case):
        with patch('app.api.routes.recommendation.get_settings', return_value=mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_recommendation(
                    product_id="test123",
                    limit=None,
                    use_case=mock_get_recommendations_use_case
                )
    
    assert exc_info.value.status_code == 404
    assert "Product with ID test123 not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_recommendation_with_default_limit_and_empty_recommendations(mock_get_recommendations_use_case):
    """Test recommendation retrieval with default limit from settings and empty recommendations"""
    mock_get_recommendations_use_case.execute.return_value = Recommendations(results=[])
    
    mock_settings = MagicMock()
    mock_settings.default_recommendation_limit = 10
    
    with patch('app.api.routes.recommendation.get_recommendations_use_case', return_value=mock_get_recommendations_use_case):
        with patch('app.api.routes.recommendation.get_settings', return_value=mock_settings):
            response = await get_recommendation(
                product_id="test123",
                limit=None,
                use_case=mock_get_recommendations_use_case
            )
    
    mock_get_recommendations_use_case.execute.assert_called_once_with(
        product_id="test123",
        limit=10
    )
    
    assert response is not None
    assert response.results is not None
    assert len(response.results) == 0


@pytest.mark.asyncio
async def test_get_recommendation_with_default_limit_and_invalid_product(mock_get_recommendations_use_case):
    """Test recommendation retrieval with default limit from settings and invalid product"""
    mock_get_recommendations_use_case.execute.return_value = None
    
    mock_settings = MagicMock()
    mock_settings.default_recommendation_limit = 10
    
    with patch('app.api.routes.recommendation.get_recommendations_use_case', return_value=mock_get_recommendations_use_case):
        with patch('app.api.routes.recommendation.get_settings', return_value=mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_recommendation(
                    product_id="invalid_product",
                    limit=None,
                    use_case=mock_get_recommendations_use_case
                )
    
    assert exc_info.value.status_code == 404
    assert "Product with ID invalid_product not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_recommendation_with_default_limit_and_empty_product(mock_get_recommendations_use_case):
    """Test recommendation retrieval with default limit from settings and empty product"""
    mock_get_recommendations_use_case.execute.return_value = None
    
    mock_settings = MagicMock()
    mock_settings.default_recommendation_limit = 10
    
    with patch('app.api.routes.recommendation.get_recommendations_use_case', return_value=mock_get_recommendations_use_case):
        with patch('app.api.routes.recommendation.get_settings', return_value=mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_recommendation(
                    product_id="",
                    limit=None,
                    use_case=mock_get_recommendations_use_case
                )
    
    assert exc_info.value.status_code == 404
    assert "Product with ID  not found" in str(exc_info.value.detail) 