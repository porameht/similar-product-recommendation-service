import os
from typing import List, Optional, Dict, Any, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository


class QdrantProductRepository(ProductRepository):
    """Implementation of ProductRepository using Qdrant vector database"""
    
    def __init__(
        self,
        collection_name: str = "products",
        host: Optional[str] = None,
        port: Optional[int] = None,
        vector_size: int = 384  # default for all-MiniLM-L6-v2
    ):
        """Initialize Qdrant repository"""
        self.collection_name = collection_name
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.vector_size = vector_size
        
        self.client = QdrantClient(host=self.host, port=self.port)
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self) -> None:
        """Ensure the products collection exists, creating it if needed"""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )
    
    def _product_to_point(self, product: Product) -> Tuple[str, List[float], Dict[str, Any]]:
        """Convert a product to a Qdrant point"""
        if not product.embedding:
            raise ValueError("Product must have an embedding")
        
        payload = {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "main_category": product.main_category,
            "sub_category": product.sub_category,
            "ratings": product.ratings,
            "no_of_ratings": product.no_of_ratings,
            "price": product.price
        }
        
        return product.product_id, product.embedding, payload
    
    def _point_to_product(self, point_id: str, payload: Dict[str, Any], score: float = None) -> Tuple[Product, Optional[float]]:
        """Convert a Qdrant point to a product"""
        product = Product(
            product_id=payload["product_id"],
            product_name=payload["product_name"],
            main_category=payload["main_category"],
            sub_category=payload["sub_category"],
            ratings=payload.get("ratings"),
            no_of_ratings=payload.get("no_of_ratings"),
            price=payload["price"]
        )
        
        return product, score
    
    async def save_product(self, product: Product) -> None:
        """Save a product to Qdrant"""
        if not product.embedding:
            raise ValueError("Product must have an embedding")
        
        point_id, vector, payload = self._product_to_point(product)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
    
    async def batch_save_products(self, products: List[Product]) -> None:
        """Save multiple products to Qdrant in a batch"""
        points = []
        
        for product in products:
            if not product.embedding:
                raise ValueError(f"Product {product.product_id} must have an embedding")
            
            point_id, vector, payload = self._product_to_point(product)
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
    
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a product by its ID from Qdrant"""
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[product_id]
            )
            
            if not points:
                return None
            
            product, _ = self._point_to_product(
                point_id=points[0].id, 
                payload=points[0].payload
            )
            
            return product
            
        except Exception as e:
            print(f"Error retrieving product {product_id}: {e}")
            return None
    
    async def find_similar_products(
        self, 
        product_id: str, 
        limit: int = 5, 
        distance_threshold: float = 0.95
    ) -> List[Tuple[Product, float]]:
        """Find similar products to the given product ID with similarity scores"""
        product = await self.get_product_by_id(product_id)
        if not product:
            return []
        
        embedding = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[product_id],
            with_vectors=True
        )
        
        if not embedding:
            return []
        
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="sub_category",
                    match=models.MatchValue(value=product.sub_category)
                )
            ]
        )
        
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding[0].vector,
            limit=limit + 1,
            query_filter=filter_condition
        )
        
        similar_products = []
        for result in search_result:
            if result.id != product_id:
                product_obj, score = self._point_to_product(
                    point_id=result.id,
                    payload=result.payload,
                    score=result.score
                )
                similar_products.append((product_obj, score))
        
        return similar_products[:limit]