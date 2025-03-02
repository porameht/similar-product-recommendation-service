import os
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
import numpy as np
from prefect import flow, task
from sentence_transformers import SentenceTransformer

from app.domain.entities.product import Product
from app.infrastructure.repositories.qdrant_product_repository import QdrantProductRepository


def get_model_path(model_name: str = "all-MiniLM-L6-v2") -> str:
    """Get the path to the embedding model, prioritizing local model if available"""
    base_name = os.path.basename(model_name) if "/" in model_name else model_name
    local_model_path = os.path.join("models", base_name)
    
    if os.path.exists(local_model_path):
        print(f"Using local model from {local_model_path}")
        return local_model_path
    
    if "/" not in model_name:
        model_name = f"sentence-transformers/{model_name}"
    
    print(f"Using model from HuggingFace: {model_name}")
    return model_name


@task(name="Read Products Data")
def read_products_data(csv_path: str) -> pd.DataFrame:
    """Read products data from CSV file"""
    df = pd.read_csv(csv_path)
    
    df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
    df["no_of_ratings"] = pd.to_numeric(df["no_of_ratings"], errors="coerce")
    
    return df


def convert_price_to_usd(price_str: str, exchange_rate: float = 0.035) -> str:
    """
    Convert price from Thai Baht to USD.
    
    Args:
        price_str: Price string in Thai Baht format (e.g. ฿7,999)
        exchange_rate: Exchange rate from THB to USD (default: 0.035)
        
    Returns:
        Price string in USD format (e.g. $279.97)
    """
    try:
        price_str = price_str.replace('฿', '').replace(',', '')
        price_thb = float(price_str)
        
        price_usd = price_thb * exchange_rate
        return f"${price_usd:.2f}"
    except (ValueError, AttributeError):
        return price_str


@task(name="Create Text Embeddings")
def create_embeddings(
    df: pd.DataFrame, 
    model_name: str = None
) -> List[Dict[str, Any]]:
    """Create text embeddings for products"""
    if model_name is None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    model_path = get_model_path(model_name)
    
    model = SentenceTransformer(model_path)
    
    products_with_embeddings = []
    
    for _, row in df.iterrows():
        text = f"{row['product_name']}. Category: {row['main_category']}. Sub-category: {row['sub_category']}"
        
        embedding = model.encode(text).tolist()
        
        product_dict = row.to_dict()
        product_dict["embedding"] = embedding
        
        product_dict["price_usd"] = convert_price_to_usd(product_dict["price"])
        
        if pd.isna(product_dict["no_of_ratings"]):
            product_dict["no_of_ratings"] = None
        else:
            try:
                product_dict["no_of_ratings"] = int(product_dict["no_of_ratings"])
            except (ValueError, TypeError):
                product_dict["no_of_ratings"] = None
        
        if pd.isna(product_dict["ratings"]):
            product_dict["ratings"] = None
            
        products_with_embeddings.append(product_dict)
    
    return products_with_embeddings


@task(name="Save to Vector Database")
async def save_to_vector_db(products_data: List[Dict[str, Any]]) -> None:
    """Save products with embeddings to Qdrant vector database"""
    repository = QdrantProductRepository()
    
    products = []
    for prod in products_data:
        try:
            products.append(Product.from_dict(prod))
        except Exception as e:
            print(f"Error creating Product from data: {e}")
            print(f"Problematic data: {prod}")
    
    await repository.batch_save_products(products)


@task(name="Save Daily Snapshot")
def save_daily_snapshot(products_data: List[Dict[str, Any]]) -> str:
    """Save daily snapshot of products with embeddings in parquet format"""
    df = pd.DataFrame(products_data)
    
    snapshot_dir = os.path.join("snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    partition_dir = os.path.join(snapshot_dir, f"date={today}")
    os.makedirs(partition_dir, exist_ok=True)
    
    parquet_path = os.path.join(partition_dir, "products.parquet")
    df.to_parquet(parquet_path, index=False)
    
    return parquet_path


@flow(name="Products Embedding Pipeline")
async def product_embedding_pipeline(csv_path: str = "data/products.csv", model_name: str = None):
    """
    Prefect flow to process products data:
    1. Read products from CSV
    2. Create text embeddings
    3. Save to vector database
    4. Save daily snapshot as parquet
    
    Args:
        csv_path: Path to the products CSV file
        model_name: Name or path to the embedding model
    """
    df = read_products_data(csv_path)
    
    products_with_embeddings = create_embeddings(df, model_name=model_name)
    
    await save_to_vector_db(products_with_embeddings)
    
    snapshot_path = save_daily_snapshot(products_with_embeddings)
    
    print(f"Pipeline completed successfully. Snapshot saved to {snapshot_path}")
    return snapshot_path


if __name__ == "__main__":
    import asyncio
    asyncio.run(product_embedding_pipeline()) 