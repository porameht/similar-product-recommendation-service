import pytest
from app.domain.entities.product import Product


def test_product_creation():
    """Test product entity creation with required fields"""
    product_data = {
        "product_id": "test123",
        "product_name": "Test Product",
        "main_category": "Electronics",
        "sub_category": "Smartphones",
        "price": "$599.99"
    }
    
    product = Product(**product_data)
    
    assert product.product_id == "test123"
    assert product.product_name == "Test Product"
    assert product.main_category == "Electronics"
    assert product.sub_category == "Smartphones"
    assert product.price == "$599.99"
    assert product.embedding is None
    assert product.ratings is None
    assert product.no_of_ratings is None
    assert product.price_usd is None


def test_product_creation_with_all_fields():
    """Test product entity creation with all fields"""
    product_data = {
        "product_id": "test123",
        "product_name": "Test Product",
        "main_category": "Electronics",
        "sub_category": "Smartphones",
        "price": "$599.99",
        "price_usd": "$599.99",
        "ratings": 4.5,
        "no_of_ratings": 100,
        "embedding": [0.1, 0.2, 0.3, 0.4]
    }
    
    product = Product(**product_data)
    
    assert product.product_id == "test123"
    assert product.product_name == "Test Product"
    assert product.main_category == "Electronics"
    assert product.sub_category == "Smartphones"
    assert product.price == "$599.99"
    assert product.price_usd == "$599.99"
    assert product.ratings == 4.5
    assert product.no_of_ratings == 100
    assert product.embedding == [0.1, 0.2, 0.3, 0.4]


def test_product_to_dict():
    """Test product to_dict method"""
    product_data = {
        "product_id": "test123",
        "product_name": "Test Product",
        "main_category": "Electronics",
        "sub_category": "Smartphones",
        "price": "$599.99",
        "price_usd": "$599.99",
        "ratings": 4.5,
        "no_of_ratings": 100,
        "embedding": [0.1, 0.2, 0.3, 0.4]
    }
    
    product = Product(**product_data)
    product_dict = product.to_dict()
    
    assert product_dict == product_data


def test_product_from_dict():
    """Test product from_dict method"""
    product_data = {
        "product_id": "test123",
        "product_name": "Test Product",
        "main_category": "Electronics",
        "sub_category": "Smartphones",
        "price": "$599.99"
    }
    
    product = Product.from_dict(product_data)
    
    assert product.product_id == "test123"
    assert product.product_name == "Test Product"
    assert product.main_category == "Electronics"
    assert product.sub_category == "Smartphones"
    assert product.price == "$599.99" 