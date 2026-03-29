#!/usr/bin/env python3
"""
Model download script for Offline Policy Gap Analyzer.

This script downloads required models while internet is available.
Models are stored locally for offline operation.
"""

import argparse
import os
import sys
from pathlib import Path


def download_embedding_model():
    """Download sentence-transformers embedding model."""
    print("Downloading embedding model: all-MiniLM-L6-v2...")
    try:
        from sentence_transformers import SentenceTransformer
        
        model_path = Path("./models/all-MiniLM-L6-v2")
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Download and save model
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        model.save(str(model_path))
        
        print(f"✓ Embedding model saved to {model_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to download embedding model: {e}")
        return False


def download_llm_model(model_name):
    """Download LLM model via Ollama."""
    print(f"Downloading LLM model: {model_name}...")
    print("Note: This requires Ollama to be installed.")
    print("Install Ollama from: https://ollama.ai")
    
    try:
        import subprocess
        
        # Pull model using Ollama CLI
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ LLM model {model_name} downloaded successfully")
            return True
        else:
            print(f"✗ Failed to download LLM model: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ Ollama not found. Please install from https://ollama.ai")
        return False
    except Exception as e:
        print(f"✗ Failed to download LLM model: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download models for Offline Policy Gap Analyzer"
    )
    parser.add_argument(
        "--embedding",
        action="store_true",
        help="Download embedding model (all-MiniLM-L6-v2)"
    )
    parser.add_argument(
        "--llm",
        type=str,
        choices=["qwen2.5-3b-instruct", "phi-3.5-mini", "mistral-7b", "qwen3-8b"],
        help="Download specified LLM model"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all models (embedding + default LLM)"
    )
    
    args = parser.parse_args()
    
    if not any([args.embedding, args.llm, args.all]):
        parser.print_help()
        sys.exit(1)
    
    success = True
    
    if args.all or args.embedding:
        success &= download_embedding_model()
    
    if args.all:
        success &= download_llm_model("qwen2.5:3b-instruct")
    elif args.llm:
        # Map model names to Ollama tags
        model_map = {
            "qwen2.5-3b-instruct": "qwen2.5:3b-instruct",
            "phi-3.5-mini": "phi3.5:3.8b",
            "mistral-7b": "mistral:7b-instruct",
            "qwen3-8b": "qwen3:8b"
        }
        success &= download_llm_model(model_map[args.llm])
    
    if success:
        print("\n✓ All models downloaded successfully!")
        print("You can now run the analyzer offline.")
    else:
        print("\n✗ Some models failed to download.")
        print("Please check the errors above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
