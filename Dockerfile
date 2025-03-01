FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy download model script
COPY scripts/download_model.py ./scripts/

# Create models directory
RUN mkdir -p models

# Download the model during build
RUN python scripts/download_model.py --model-name sentence-transformers/all-MiniLM-L6-v2 --output-dir models

# Copy the rest of the application
COPY . .

EXPOSE 8000
EXPOSE 4200

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 