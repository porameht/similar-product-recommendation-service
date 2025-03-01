#!/usr/bin/env python3
"""
Script to download the sentence transformer model and save it locally
"""
import os
import argparse
from sentence_transformers import SentenceTransformer

def parse_args():
    parser = argparse.ArgumentParser(description="Download a sentence transformer model")
    parser.add_argument(
        "--model-name",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Name of the model to download"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models",
        help="Directory to save the model"
    )
    return parser.parse_args()

def download_model(model_name, output_dir):
    """Download a model and save it to the specified directory"""
    print(f"Downloading model {model_name}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    model_dir = os.path.join(output_dir, os.path.basename(model_name))
    os.makedirs(model_dir, exist_ok=True)
    
    model = SentenceTransformer(model_name)
    
    model.save(model_dir)
    
    print(f"Model saved to {model_dir}")
    return model_dir

if __name__ == "__main__":
    args = parse_args()
    download_model(args.model_name, args.output_dir) 