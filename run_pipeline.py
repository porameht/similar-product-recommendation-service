#!/usr/bin/env python3
"""
Script to run the product embedding pipeline using Prefect
"""
import asyncio
import argparse

from app.infrastructure.batch.embedding_pipeline import product_embedding_pipeline


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run product embedding pipeline")
    parser.add_argument(
        "--csv-path",
        type=str,
        default="data/products.csv",
        help="Path to the products CSV file"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="Name or path of the embedding model (default: from environment variable or all-MiniLM-L6-v2)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(product_embedding_pipeline(csv_path=args.csv_path, model_name=args.model_name)) 