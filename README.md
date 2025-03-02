# Similar Product Recommendation Service

A service that recommends similar products to users based on product content using text embeddings and vector search.

## Visualization

![Capture-2025-03-01-143017](https://github.com/user-attachments/assets/916112e7-ed40-465e-8740-3e0ee44157d2)

```
{
  "limit": 1457,
  "color_by": {
    "payload": "sub_category"
  }
}
```
## Architecture

This project follows Clean Architecture principles with the following layers:

- **Domain Layer**: Contains business entities and repository interfaces
- **Application Layer**: Contains use cases that orchestrate business logic
- **Infrastructure Layer**: Contains implementations of repositories and external services
- **API Layer**: Contains FastAPI routes and controllers

## Model

The service uses text embeddings to find similar products. By default, it uses the `all-MiniLM-L6-v2` model from sentence-transformers which has the following characteristics:

- **Model Type**: Sentence Transformer (based on BERT architecture)
- **Vector Size**: 384 dimensions
- **Performance**: Good balance between quality and computational efficiency
- **Use Case**: Optimized for semantic similarity tasks
- **Languages**: Supports multiple languages with primary focus on English
- **Size**: ~90MB, making it suitable for deployment in containers
- **Speed**: Relatively fast inference time compared to larger models

The model converts product descriptions and metadata into dense vector representations (embeddings). These embeddings capture semantic meaning, allowing the system to find products that are conceptually similar rather than just matching keywords.

The embedding process works as follows:

1. Product text (name, description, category) is tokenized and processed
2. The transformer model generates a fixed-size vector (384 dimensions)
3. These vectors are stored in Qdrant vector database 
4. Similarity search uses cosine similarity to find the most relevant products
5. Products within the same sub-category are prioritized to ensure recommendations are contextually relevant

### Model Configuration

You can configure the embedding model through environment variables:

```
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Default model
VECTOR_SIZE=384                   # Vector dimensions
```

Alternative models that can be used:
- `paraphrase-MiniLM-L6-v2`: Optimized for paraphrase detection
- `multi-qa-MiniLM-L6-cos-v1`: Better for question-answering tasks
- `all-mpnet-base-v2`: Higher quality but more computationally expensive

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

4. Customizing the environment and configuration:

   You can specify the environment and override configuration values by creating a `.env` file in the project root:
   
   ```
   # Set the environment
   APP_ENV=production
   
   # Override specific settings
   EMBEDDING_MODEL=all-mpnet-base-v2
   VECTOR_SIZE=768
   DEFAULT_RECOMMENDATION_LIMIT=10
   ```
   
   Then restart the services:
   ```
   docker-compose down
   docker-compose up -d
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
   
   To run with a specific environment configuration:
   ```
   # Set environment
   export APP_ENV=production
   
   # Run the server
   uvicorn app.main:app --reload
   ```
   
   Or in a single command:
   ```
   APP_ENV=production uvicorn app.main:app --reload
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

## Configuration Management

The service uses a centralized configuration management system based on Pydantic for type validation and environment variables for flexibility.

### Environment-Based Configuration

You can run the service in different environments by setting the `APP_ENV` environment variable:

```bash
# For development (default)
export APP_ENV=development

# For production
export APP_ENV=production

# For testing
export APP_ENV=testing
```

Each environment can have its own configuration values defined in environment-specific files:
- `.env` - Base configuration for all environments
- `.env.development` - Development-specific overrides
- `.env.production` - Production-specific overrides
- `.env.testing` - Testing-specific overrides

### Available Configuration Options

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| API Host | `API_HOST` | 0.0.0.0 | Host to bind the API server |
| API Port | `API_PORT` | 8000 | Port for the API server |
| Qdrant Host | `QDRANT_HOST` | localhost | Qdrant vector database host |
| Qdrant Port | `QDRANT_PORT` | 6333 | Qdrant vector database port |
| Qdrant Collection | `QDRANT_COLLECTION` | products | Qdrant collection name |
| Embedding Model | `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Model name from sentence-transformers |
| Vector Size | `VECTOR_SIZE` | 384 | Embedding vector dimensions |
| Default Recommendation Limit | `DEFAULT_RECOMMENDATION_LIMIT` | 5 | Default number of recommendations |
| Distance Threshold | `DISTANCE_THRESHOLD` | 0.95 | Similarity threshold for recommendations |

### Using the Configuration in Code

The configuration can be accessed in any part of the application using:

```python
from app.config import get_settings

settings = get_settings()
vector_size = settings.vector_size
```

The configuration is cached for performance, ensuring minimal overhead when accessed from multiple places.

## Prefect Dashboard

The Prefect dashboard is available at http://localhost:4200 when running with Docker Compose.

## Running Tests

The project uses pytest for testing. Tests are organized to mirror the application structure, following the Clean Architecture principles.

### Running Tests Locally

1. Make sure you have installed the development dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install pytest-asyncio (required for async tests):
   ```
   pip install pytest-asyncio
   ```

3. Run all tests:
   ```
   pytest
   ```

4. Run tests with coverage report:
   ```
   pytest --cov=app
   ```

5. Run tests for a specific module:
   ```
   pytest tests/unit/domain/
   pytest tests/unit/application/
   pytest tests/unit/infrastructure/
   pytest tests/unit/api/
   ```

6. Run tests with verbose output:
   ```
   pytest -v
   ```

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
