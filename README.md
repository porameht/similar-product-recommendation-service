# Similar Product Recommendation Service

A service that recommends similar products to users based on product content using text embeddings and vector search.

## Visualize limit 500

<img width="1398" alt="Screenshot 2025-03-01 at 1 21 34 PM" src="https://github.com/user-attachments/assets/f35672f3-a801-4fbb-9228-7b7ffd2fa8d8" />

## Architecture

This project follows Clean Architecture principles with the following layers:

- **Domain Layer**: Contains business entities and repository interfaces
- **Application Layer**: Contains use cases that orchestrate business logic
- **Infrastructure Layer**: Contains implementations of repositories and external services
- **API Layer**: Contains FastAPI routes and controllers

## Features

1. **Text Embedding Batch Orchestration**:
   - Processes product data from CSV files
   - Creates text embeddings using sentence-transformers
   - Stores embeddings in Qdrant vector database
   - Saves daily snapshots in parquet format with date partitioning

2. **Recommendation API**:
   - Provides an API to get similar product recommendations
   - Finds similar products within the same sub-category
   - Returns product details with similarity scores

## Requirements

- Python 3.10+
- Docker and Docker Compose

## Setup and Running

### Using Docker Compose (Recommended)

1. Clone the repository:
   ```
   git clone <repository-url>
   cd similar-product-rec-service
   ```

2. Start the services:
   ```
   docker-compose up -d
   ```

   This will start:
   - FastAPI service on port 8000
   - Qdrant vector database on port 6333
   - Prefect server on port 4200

   Note: The Docker build process will automatically download the embedding model and save it in the container.

3. Run the embedding pipeline to process product data:
   ```
   docker-compose exec api python run_pipeline.py --csv-path data/products.csv
   ```

### Running Locally (Development)

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Download the embedding model to use it locally (optional):
   ```
   python scripts/download_model.py
   ```
   This will download the model to the `models` directory, which will be used by the application instead of downloading it at runtime.

3. Start Qdrant (using Docker):
   ```
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```

4. Run the embedding pipeline:
   ```
   python run_pipeline.py --csv-path data/products.csv
   ```
   
   If you want to specify a different model:
   ```
   python run_pipeline.py --csv-path data/products.csv --model-name your-model-name
   ```

5. Start the API server:
   ```
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the service is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Get Product Recommendations

```
GET /get-recommendation?product_id={product_id}&limit={limit}
```

Parameters:
- `product_id`: (required) ID of the product to get recommendations for
- `limit`: (optional) Maximum number of recommendations to return (default: 5)

Response:
```json
{
  "results": [
    {
      "product": {
        "product_id": "...",
        "category": "...",
        "sub_category": "...",
        "price": "..."
      },
      "distance": 0.1234
    },
    ...
  ]
}
```

## Prefect Dashboard

The Prefect dashboard is available at http://localhost:4200 when running with Docker Compose.

## Project Structure

```
.
├── app/
│   ├── api/                 # API layer
│   │   └── routes/          # API routes
│   ├── application/         # Application layer
│   │   └── use_cases/       # Application use cases
│   ├── domain/              # Domain layer
│   │   ├── entities/        # Domain entities
│   │   └── repositories/    # Repository interfaces
│   └── infrastructure/      # Infrastructure layer
│       ├── batch/           # Batch processing
│       └── repositories/    # Repository implementations
├── data/                    # Data files
├── snapshots/               # Daily snapshots
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
├── run_pipeline.py          # Pipeline runner script
└── README.md                # This file
``` 
