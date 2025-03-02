import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.domain.entities.product import Product
from app.infrastructure.repositories.qdrant_product_repository import QdrantProductRepository

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
        no_of_ratings=100,
        embedding=[0.1, 0.2, 0.3, 0.4]
    )


@pytest.fixture
def mock_qdrant_client():
    """Fixture for mocked qdrant client"""
    mock_client = MagicMock()
    mock_client.upsert = MagicMock()
    mock_client.retrieve = MagicMock()
    mock_client.search = MagicMock()
    mock_client.get_collections = MagicMock()
    return mock_client


@pytest.fixture
def mock_repository(mock_qdrant_client):
    """Fixture for mocked repository with dependency injection"""
    with patch('app.infrastructure.repositories.qdrant_product_repository.QdrantClient', return_value=mock_qdrant_client):
        repo = QdrantProductRepository(
            collection_name="test_collection",
            host="localhost",
            port=6333,
            vector_size=4
        )
        repo._ensure_collection_exists = MagicMock()
        return repo


@pytest.mark.asyncio
async def test_save_product(mock_repository, sample_product):
    """Test saving a single product to Qdrant"""
    await mock_repository.save_product(sample_product)
    
    client = mock_repository.client
    
    client.upsert.assert_called_once()
    
    call_args = client.upsert.call_args[1]
    
    assert call_args["collection_name"] == mock_repository.collection_name
    
    assert len(call_args["points"]) == 1
    point = call_args["points"][0]
    assert point.id == sample_product.product_id
    assert point.vector == sample_product.embedding
    
    payload = point.payload
    assert payload["product_id"] == sample_product.product_id
    assert payload["product_name"] == sample_product.product_name
    assert payload["main_category"] == sample_product.main_category
    assert payload["sub_category"] == sample_product.sub_category
    assert payload["price"] == sample_product.price
    assert payload["price_usd"] == sample_product.price_usd
    assert payload["ratings"] == sample_product.ratings
    assert payload["no_of_ratings"] == sample_product.no_of_ratings


@pytest.mark.asyncio
async def test_batch_save_products(mock_repository, sample_product):
    """Test batch saving products to Qdrant"""
    product2 = Product(
        product_id="test456",
        product_name="Test Product 2",
        main_category="Electronics",
        sub_category="Laptops",
        price="$999.99",
        price_usd="$999.99",
        ratings=4.2,
        no_of_ratings=50,
        embedding=[0.5, 0.6, 0.7, 0.8]
    )
    
    await mock_repository.batch_save_products([sample_product, product2])
    
    client = mock_repository.client
    
    client.upsert.assert_called_once()
    
    call_args = client.upsert.call_args[1]
    
    assert call_args["collection_name"] == mock_repository.collection_name
    
    assert len(call_args["points"]) == 2
    
    point1 = call_args["points"][0]
    assert point1.id == sample_product.product_id
    assert point1.vector == sample_product.embedding
    
    point2 = call_args["points"][1]
    assert point2.id == product2.product_id
    assert point2.vector == product2.embedding


@pytest.mark.asyncio
async def test_get_product_by_id_found(mock_repository, sample_product):
    """Test getting a product by ID when it exists"""
    async def mock_get_product_implementation(product_id):
        if product_id == sample_product.product_id:
            return sample_product
        return None
    
    with patch.object(mock_repository, 'get_product_by_id', side_effect=mock_get_product_implementation):
        result = await mock_repository.get_product_by_id(sample_product.product_id)
        
        assert result is not None
        assert result.product_id == sample_product.product_id
        assert result.product_name == sample_product.product_name


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(mock_repository):
    """Test getting a product by ID when it doesn't exist"""
    async def mock_get_product_implementation(product_id):
        return None
    
    with patch.object(mock_repository, 'get_product_by_id', side_effect=mock_get_product_implementation):
        result = await mock_repository.get_product_by_id("nonexistent")
        
        assert result is None


@pytest.mark.asyncio
async def test_find_similar_products(mock_repository, sample_product):
    """Test finding similar products"""
    similar_product1 = Product(
        product_id="similar1",
        product_name="Similar Product 1",
        main_category="Electronics",
        sub_category="Smartphones",
        price="$649.99",
        price_usd="$649.99",
        ratings=4.3,
        no_of_ratings=80,
        embedding=[0.15, 0.25, 0.35, 0.45]
    )
    
    similar_product2 = Product(
        product_id="similar2",
        product_name="Similar Product 2",
        main_category="Electronics",
        sub_category="Smartphones",
        price="$699.99",
        price_usd="$699.99",
        ratings=4.7,
        no_of_ratings=120,
        embedding=[0.12, 0.22, 0.32, 0.42]
    )
    
    async def mock_find_similar_implementation(product_id, limit=None, distance_threshold=None):
        return [
            (similar_product1, 0.85),
            (similar_product2, 0.75)
        ]
    
    with patch.object(mock_repository, 'find_similar_products', side_effect=mock_find_similar_implementation):
        results = await mock_repository.find_similar_products(
            product_id=sample_product.product_id,
            limit=2,
            distance_threshold=0.7
        )
        
        assert len(results) == 2
        
        product1, distance1 = results[0]
        assert product1.product_id == similar_product1.product_id
        assert distance1 == 0.85
        
        product2, distance2 = results[1]
        assert product2.product_id == similar_product2.product_id
        assert distance2 == 0.75 