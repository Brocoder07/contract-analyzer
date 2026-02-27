"""
Download and cache suggestion generation models
Run this script before deployment to pre-download all required models
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers import (
    T5Tokenizer, 
    T5ForConditionalGeneration,
    GPT2Tokenizer, 
    GPT2LMHeadModel
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default cache directory: contract-analyzer/backend/app/data/models
DEFAULT_CACHE_DIR = Path(__file__).parent.parent / "app" / "data" / "models"


def download_t5_model(model_name: str = "google/flan-t5-base", cache_dir: str = None):
    """
    Download T5 model and tokenizer
    
    Args:
        model_name: HuggingFace model identifier
        cache_dir: Directory to cache the model
    """
    try:
        logger.info(f"📥 Downloading T5 model: {model_name}")
        
        tokenizer = T5Tokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        logger.info(f"  ✓ T5 tokenizer downloaded")
        
        model = T5ForConditionalGeneration.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        logger.info(f"  ✓ T5 model downloaded")
        
        # Get model size
        model_size = sum(p.numel() for p in model.parameters()) / 1e6
        logger.info(f"  ℹ Model size: {model_size:.1f}M parameters")
        
        logger.info(f"✅ T5 model '{model_name}' downloaded successfully!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download T5 model '{model_name}': {e}\n")
        return False


def download_gpt_model(model_name: str = "distilgpt2", cache_dir: str = None):
    """
    Download GPT-2 model and tokenizer
    
    Args:
        model_name: HuggingFace model identifier
        cache_dir: Directory to cache the model
    """
    try:
        logger.info(f"📥 Downloading GPT model: {model_name}")
        
        tokenizer = GPT2Tokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        logger.info(f"  ✓ GPT tokenizer downloaded")
        
        model = GPT2LMHeadModel.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        logger.info(f"  ✓ GPT model downloaded")
        
        # Get model size
        model_size = sum(p.numel() for p in model.parameters()) / 1e6
        logger.info(f"  ℹ Model size: {model_size:.1f}M parameters")
        
        logger.info(f"✅ GPT model '{model_name}' downloaded successfully!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download GPT model '{model_name}': {e}\n")
        return False


def ensure_cache_directory(cache_dir: Path) -> bool:
    """
    Ensure cache directory exists and is writable
    
    Args:
        cache_dir: Path to cache directory
    
    Returns:
        bool: True if directory is ready
    """
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Cache directory created/verified: {cache_dir}")
        
        # Test write permissions
        test_file = cache_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Cannot create/write to cache directory: {e}")
        return False


def check_disk_space(path: Path, min_gb: float = 5.0):
    """
    Check if sufficient disk space is available
    
    Args:
        path: Path to check disk space
        min_gb: Minimum required GB of free space
    
    Returns:
        bool: True if sufficient space available
    """
    try:
        import shutil
        total, used, free = shutil.disk_usage(str(path))
        free_gb = free / (1024 ** 3)
        
        logger.info(f"💾 Disk space at {path}: {free_gb:.2f} GB free")
        
        if free_gb < min_gb:
            logger.warning(f"⚠️  Low disk space! Recommended: {min_gb}GB, Available: {free_gb:.2f}GB")
            return False
        return True
        
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
        return True


def get_directory_size(path: Path) -> float:
    """
    Calculate total size of directory in GB
    
    Args:
        path: Directory path
    
    Returns:
        Size in GB
    """
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                if filepath.exists():
                    total_size += filepath.stat().st_size
        return total_size / (1024 ** 3)
    except Exception as e:
        logger.warning(f"Could not calculate directory size: {e}")
        return 0.0


def main():
    parser = argparse.ArgumentParser(
        description="Download suggestion generation models for contract analyzer"
    )
    parser.add_argument(
        "--t5-model",
        type=str,
        default="google/flan-t5-base",
        help="T5 model to download (default: google/flan-t5-base)"
    )
    parser.add_argument(
        "--gpt-model",
        type=str,
        default="distilgpt2",
        help="GPT model to download (default: distilgpt2)"
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help=f"Custom cache directory (default: {DEFAULT_CACHE_DIR})"
    )
    parser.add_argument(
        "--skip-t5",
        action="store_true",
        help="Skip downloading T5 model"
    )
    parser.add_argument(
        "--skip-gpt",
        action="store_true",
        help="Skip downloading GPT model"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all available model variants"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("📦 Contract Analyzer - Suggestion Model Downloader")
    logger.info("=" * 70)
    logger.info(f"👤 User: akashrajeshnair")
    logger.info(f"📅 Date: 2025-11-14 18:49:08 UTC\n")
    
    # Set cache directory
    cache_dir = Path(args.cache_dir) if args.cache_dir else DEFAULT_CACHE_DIR
    logger.info(f"📁 Target directory: {cache_dir.absolute()}\n")
    
    # Ensure directory exists and is writable
    if not ensure_cache_directory(cache_dir):
        logger.error("Cannot proceed without valid cache directory")
        return 1
    
    # Check disk space
    if not check_disk_space(cache_dir, min_gb=2.0):
        logger.warning("⚠️  Proceeding anyway, but download may fail if space runs out\n")
    
    results = []
    
    # Download models based on arguments
    if args.all:
        logger.info("🔄 Downloading ALL available model variants...\n")
        
        # T5 variants
        t5_models = [
            "google/flan-t5-small",
            "google/flan-t5-base",
            "google/flan-t5-large"
        ]
        for model in t5_models:
            results.append(("T5", model, download_t5_model(model, str(cache_dir))))
        
        # GPT variants
        gpt_models = [
            "distilgpt2",
            "gpt2",
            "gpt2-medium"
        ]
        for model in gpt_models:
            results.append(("GPT", model, download_gpt_model(model, str(cache_dir))))
    
    else:
        # Download specified models
        if not args.skip_t5:
            results.append(("T5", args.t5_model, download_t5_model(args.t5_model, str(cache_dir))))
        
        if not args.skip_gpt:
            results.append(("GPT", args.gpt_model, download_gpt_model(args.gpt_model, str(cache_dir))))
    
    # Calculate total size
    total_size = get_directory_size(cache_dir)
    
    # Summary
    logger.info("=" * 70)
    logger.info("📊 DOWNLOAD SUMMARY")
    logger.info("=" * 70)
    
    success_count = sum(1 for _, _, success in results if success)
    total_count = len(results)
    
    for model_type, model_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{status} - {model_type}: {model_name}")
    
    logger.info("")
    logger.info(f"📦 Total models downloaded: {success_count}/{total_count}")
    logger.info(f"💾 Total disk space used: {total_size:.2f} GB")
    logger.info(f"📁 Models location: {cache_dir.absolute()}")
    
    if success_count == total_count:
        logger.info("\n🎉 All models downloaded successfully!")
        logger.info("You can now run the application with suggestion generation enabled.")
        logger.info("\nTo use these models, add to your .env file:")
        logger.info(f"TRANSFORMERS_CACHE={cache_dir.absolute()}")
        logger.info(f"HF_HOME={cache_dir.absolute()}")
        return 0
    else:
        logger.error("\n⚠️  Some models failed to download.")
        logger.error("Check your internet connection and try again.")
        logger.error("You can still use rule-based suggestions without ML models.")
        return 1


if __name__ == "__main__":
    sys.exit(main())