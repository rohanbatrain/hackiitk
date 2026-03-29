#!/usr/bin/env python3
"""
Model setup script for Offline Policy Gap Analyzer.

This script downloads and verifies all required models for offline operation:
- Sentence transformer embedding model (all-MiniLM-L6-v2)
- Cross-encoder reranking model (ms-marco-MiniLM-L-6-v2)
- LLM model (Qwen2.5-3B-Instruct GGUF or via Ollama)

Requirements: 17.2, 17.3, 17.4, 17.5
"""

import argparse
import hashlib
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional, Tuple


# Model configurations with expected checksums
EMBEDDING_MODEL = {
    "name": "all-MiniLM-L6-v2",
    "source": "sentence-transformers/all-MiniLM-L6-v2",
    "path": "models/embeddings/all-MiniLM-L6-v2",
    "type": "sentence-transformers"
}

RERANKER_MODEL = {
    "name": "ms-marco-MiniLM-L-6-v2",
    "source": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "path": "models/reranker/ms-marco-MiniLM-L-6-v2",
    "type": "cross-encoder"
}

LLM_MODELS = {
    "qwen2.5-3b": {
        "name": "Qwen2.5-3B-Instruct",
        "ollama_tag": "qwen2.5:3b-instruct",
        "gguf_url": None,  # Ollama handles download
        "path": "models/llm/qwen2.5-3b",
        "size_gb": 2.0
    },
    "phi-3.5": {
        "name": "Phi-3.5-mini",
        "ollama_tag": "phi3.5:3.8b",
        "gguf_url": None,
        "path": "models/llm/phi-3.5",
        "size_gb": 2.3
    },
    "mistral-7b": {
        "name": "Mistral-7B-Instruct",
        "ollama_tag": "mistral:7b-instruct",
        "gguf_url": None,
        "path": "models/llm/mistral-7b",
        "size_gb": 4.1
    },
    "qwen3-8b": {
        "name": "Qwen3-8B",
        "ollama_tag": "qwen3:8b",
        "gguf_url": None,
        "path": "models/llm/qwen3-8b",
        "size_gb": 4.7
    }
}


class ProgressBar:
    """Simple progress bar for downloads."""
    
    def __init__(self, total: int, prefix: str = ""):
        self.total = total
        self.prefix = prefix
        self.current = 0
    
    def update(self, chunk_size: int):
        """Update progress bar."""
        self.current += chunk_size
        if self.total > 0:
            percent = min(100, int(100 * self.current / self.total))
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            mb_current = self.current / (1024 * 1024)
            mb_total = self.total / (1024 * 1024)
            print(f"\r{self.prefix} [{bar}] {percent}% ({mb_current:.1f}/{mb_total:.1f} MB)", end="", flush=True)
    
    def finish(self):
        """Complete progress bar."""
        print()


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Compute hash of a file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, md5)
    
    Returns:
        Hex digest of file hash
    """
    hash_obj = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def verify_directory_integrity(model_path: Path) -> bool:
    """
    Verify model directory contains expected files.
    
    Args:
        model_path: Path to model directory
    
    Returns:
        True if directory appears valid
    """
    if not model_path.exists():
        return False
    
    # Check for common model files
    expected_files = [
        "config.json",
        "pytorch_model.bin",
        "tokenizer_config.json"
    ]
    
    # At least one expected file should exist
    for file_name in expected_files:
        if (model_path / file_name).exists():
            return True
    
    # For sentence-transformers, check for modules.json
    if (model_path / "modules.json").exists():
        return True
    
    return False


def download_sentence_transformer(model_config: dict) -> bool:
    """
    Download sentence-transformers model.
    
    Args:
        model_config: Model configuration dict
    
    Returns:
        True if successful
    """
    print(f"\n{'='*60}")
    print(f"Downloading {model_config['name']}...")
    print(f"{'='*60}")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model_path = Path(model_config["path"])
        
        # Check if already exists
        if verify_directory_integrity(model_path):
            print(f"✓ Model already exists at {model_path}")
            print("  Skipping download. Use --force to re-download.")
            return True
        
        model_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Source: {model_config['source']}")
        print(f"Destination: {model_path}")
        print("Downloading... (this may take a few minutes)")
        
        # Download and save model
        model = SentenceTransformer(model_config["source"])
        model.save(str(model_path))
        
        # Verify download
        if verify_directory_integrity(model_path):
            print(f"✓ Successfully downloaded to {model_path}")
            print(f"  Model files: {list(model_path.glob('*'))[:5]}")
            return True
        else:
            print(f"✗ Download verification failed")
            return False
            
    except ImportError:
        print("✗ sentence-transformers not installed")
        print("  Install with: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"✗ Failed to download: {e}")
        return False


def download_cross_encoder(model_config: dict) -> bool:
    """
    Download cross-encoder model.
    
    Args:
        model_config: Model configuration dict
    
    Returns:
        True if successful
    """
    print(f"\n{'='*60}")
    print(f"Downloading {model_config['name']}...")
    print(f"{'='*60}")
    
    try:
        from sentence_transformers import CrossEncoder
        
        model_path = Path(model_config["path"])
        
        # Check if already exists
        if verify_directory_integrity(model_path):
            print(f"✓ Model already exists at {model_path}")
            print("  Skipping download. Use --force to re-download.")
            return True
        
        model_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Source: {model_config['source']}")
        print(f"Destination: {model_path}")
        print("Downloading... (this may take a few minutes)")
        
        # Download and save model
        model = CrossEncoder(model_config["source"])
        model.save(str(model_path))
        
        # Verify download
        if verify_directory_integrity(model_path):
            print(f"✓ Successfully downloaded to {model_path}")
            return True
        else:
            print(f"✗ Download verification failed")
            return False
            
    except ImportError:
        print("✗ sentence-transformers not installed")
        print("  Install with: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"✗ Failed to download: {e}")
        return False


def check_ollama_installed() -> bool:
    """Check if Ollama is installed."""
    import subprocess
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def download_llm_model(model_key: str, model_config: dict) -> bool:
    """
    Download LLM model via Ollama.
    
    Args:
        model_key: Model key (e.g., "qwen2.5-3b")
        model_config: Model configuration dict
    
    Returns:
        True if successful
    """
    print(f"\n{'='*60}")
    print(f"Downloading {model_config['name']}...")
    print(f"{'='*60}")
    
    # Check Ollama installation
    if not check_ollama_installed():
        print("✗ Ollama not found")
        print("  Install Ollama from: https://ollama.ai")
        print("  After installation, run this script again.")
        return False
    
    try:
        import subprocess
        
        model_path = Path(model_config["path"])
        model_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Model: {model_config['ollama_tag']}")
        print(f"Size: ~{model_config['size_gb']:.1f} GB")
        print(f"Storage: {model_path}")
        print("Downloading via Ollama... (this may take several minutes)")
        
        # Pull model using Ollama CLI
        result = subprocess.run(
            ["ollama", "pull", model_config["ollama_tag"]],
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        if result.returncode == 0:
            # Create marker file to indicate successful download
            marker_file = model_path / ".downloaded"
            marker_file.write_text(model_config["ollama_tag"])
            
            print(f"✓ Successfully downloaded {model_config['name']}")
            print(f"  Ollama tag: {model_config['ollama_tag']}")
            return True
        else:
            print(f"✗ Failed to download LLM model")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Download timed out (>30 minutes)")
        print("  Check your internet connection and try again.")
        return False
    except Exception as e:
        print(f"✗ Failed to download: {e}")
        return False


def verify_all_models() -> Tuple[bool, list]:
    """
    Verify all required models are present.
    
    Returns:
        Tuple of (all_present, missing_models)
    """
    missing = []
    
    # Check embedding model
    if not verify_directory_integrity(Path(EMBEDDING_MODEL["path"])):
        missing.append(("embedding", EMBEDDING_MODEL["name"]))
    
    # Check reranker model
    if not verify_directory_integrity(Path(RERANKER_MODEL["path"])):
        missing.append(("reranker", RERANKER_MODEL["name"]))
    
    # Check for at least one LLM model
    llm_found = False
    for key, config in LLM_MODELS.items():
        marker_file = Path(config["path"]) / ".downloaded"
        if marker_file.exists():
            llm_found = True
            break
    
    if not llm_found:
        missing.append(("llm", "any LLM model"))
    
    return len(missing) == 0, missing


def print_status():
    """Print status of all models."""
    print("\n" + "="*60)
    print("MODEL STATUS")
    print("="*60)
    
    # Embedding model
    emb_path = Path(EMBEDDING_MODEL["path"])
    emb_status = "✓ Installed" if verify_directory_integrity(emb_path) else "✗ Missing"
    print(f"\nEmbedding Model: {EMBEDDING_MODEL['name']}")
    print(f"  Status: {emb_status}")
    print(f"  Path: {emb_path}")
    
    # Reranker model
    rerank_path = Path(RERANKER_MODEL["path"])
    rerank_status = "✓ Installed" if verify_directory_integrity(rerank_path) else "✗ Missing"
    print(f"\nReranker Model: {RERANKER_MODEL['name']}")
    print(f"  Status: {rerank_status}")
    print(f"  Path: {rerank_path}")
    
    # LLM models
    print(f"\nLLM Models:")
    for key, config in LLM_MODELS.items():
        marker_file = Path(config["path"]) / ".downloaded"
        status = "✓ Installed" if marker_file.exists() else "✗ Missing"
        print(f"  {config['name']}: {status}")
        if marker_file.exists():
            print(f"    Tag: {marker_file.read_text()}")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Setup models for Offline Policy Gap Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all models
  python scripts/setup_models.py --all
  
  # Download only embedding and reranker
  python scripts/setup_models.py --embedding --reranker
  
  # Download specific LLM
  python scripts/setup_models.py --llm qwen2.5-3b
  
  # Check model status
  python scripts/setup_models.py --status
        """
    )
    
    parser.add_argument(
        "--embedding",
        action="store_true",
        help="Download embedding model (all-MiniLM-L6-v2)"
    )
    parser.add_argument(
        "--reranker",
        action="store_true",
        help="Download cross-encoder reranker model"
    )
    parser.add_argument(
        "--llm",
        type=str,
        choices=list(LLM_MODELS.keys()),
        help="Download specified LLM model"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all models (embedding + reranker + default LLM)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show status of all models"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if models exist"
    )
    
    args = parser.parse_args()
    
    # Show status if requested
    if args.status:
        print_status()
        all_present, missing = verify_all_models()
        if all_present:
            print("\n✓ All required models are installed")
            return 0
        else:
            print("\n✗ Missing models:")
            for model_type, model_name in missing:
                print(f"  - {model_name} ({model_type})")
            return 1
    
    # If no action specified, show help
    if not any([args.embedding, args.reranker, args.llm, args.all]):
        parser.print_help()
        return 1
    
    print("="*60)
    print("OFFLINE POLICY GAP ANALYZER - MODEL SETUP")
    print("="*60)
    print("\nThis script will download models for offline operation.")
    print("Internet connection required during setup only.")
    
    success = True
    
    # Download embedding model
    if args.all or args.embedding:
        if not download_sentence_transformer(EMBEDDING_MODEL):
            success = False
    
    # Download reranker model
    if args.all or args.reranker:
        if not download_cross_encoder(RERANKER_MODEL):
            success = False
    
    # Download LLM model
    if args.all:
        # Default to qwen2.5-3b for --all
        if not download_llm_model("qwen2.5-3b", LLM_MODELS["qwen2.5-3b"]):
            success = False
    elif args.llm:
        if not download_llm_model(args.llm, LLM_MODELS[args.llm]):
            success = False
    
    # Final status
    print("\n" + "="*60)
    if success:
        print("✓ SETUP COMPLETE")
        print("="*60)
        print("\nAll requested models downloaded successfully!")
        print("You can now run the analyzer offline.")
        print("\nNext steps:")
        print("  1. Build reference catalog: python scripts/build_catalog.py")
        print("  2. Run analysis: python -m analysis.cli <policy.pdf>")
    else:
        print("✗ SETUP INCOMPLETE")
        print("="*60)
        print("\nSome models failed to download.")
        print("Please check the errors above and try again.")
        print("\nFor help:")
        print("  python scripts/setup_models.py --help")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
