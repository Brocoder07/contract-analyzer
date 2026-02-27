"""
Download and cache summarization models
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
    BartTokenizer,
    BartForConditionalGeneration,
    PegasusTokenizer,
    PegasusForConditionalGeneration,
    T5Tokenizer,
    T5ForConditionalGeneration
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default cache directory: contract-analyzer/backend/data/models
DEFAULT_CACHE_DIR = Path(__file__).parent.parent / "backend" / "app" / "data" / "models"


def download_bart_model(model_name: str = "facebook/bart-large-cnn", cache_dir: str = None):
    """Download BART model and tokenizer"""
    try:
        logger.info(f"📥 Downloading BART model: {model_name}")
        
        tokenizer = BartTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        logger.info(f"  ✓ BART tokenizer downloaded")
        
        model = BartForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_dir)
        logger.info(f"  ✓ BART model downloaded")
        
        model_size = sum(p.numel() for p in model.parameters()) / 1e6
        logger.info(f"  ℹ Model size: {model_size:.1f}M parameters")
        
        logger.info(f"✅ BART model '{model_name}' downloaded successfully!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download BART model '{model_name}': {e}\n")
        return False


def download_pegasus_model(model_name: str = "google/pegasus-cnn_dailymail", cache_dir: str = None):
    """Download Pegasus model and tokenizer"""
    try:
        logger.info(f"📥 Downloading Pegasus model: {model_name}")
        
        tokenizer = PegasusTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        logger.info(f"  ✓ Pegasus tokenizer downloaded")
        
        model = PegasusForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_dir)
        logger.info(f"  ✓ Pegasus model downloaded")
        
        model_size = sum(p.numel() for p in model.parameters()) / 1e6
        logger.info(f"  ℹ Model size: {model_size:.1f}M parameters")
        
        logger.info(f"✅ Pegasus model '{model_name}' downloaded successfully!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download Pegasus model '{model_name}': {e}\n")
        return False


def download_t5_model(model_name: str = "t5-base", cache_dir: str = None):
    """Download T5 model and tokenizer"""
    try:
        logger.info(f"📥 Downloading T5 model: {model_name}")
        
        tokenizer = T5Tokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        logger.info(f"  ✓ T5 tokenizer downloaded")
        
        model = T5ForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_dir)
        logger.info(f"  ✓ T5 model downloaded")
        
        model_size = sum(p.numel() for p in model.parameters()) / 1e6
        logger.info(f"  ℹ Model size: {model_size:.1f}M parameters")
        
        logger.info(f"✅ T5 model '{model_name}' downloaded successfully!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download T5 model '{model_name}': {e}\n")
        return False


def ensure_cache_directory(cache_dir: Path) -> bool:
    """Ensure cache directory exists and is writable"""
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
    """Check if sufficient disk space is available"""
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
    """Calculate total size of directory in GB"""
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
        description="Download summarization models for contract analyzer"
    )
    parser.add_argument(
        "--bart-model",
        type=str,
        default="facebook/bart-large-cnn",
        help="BART model to download (default: facebook/bart-large-cnn)"
    )
    parser.add_argument(
        "--pegasus-model",
        type=str,
        default="google/pegasus-cnn_dailymail",
        help="Pegasus model to download (default: google/pegasus-cnn_dailymail)"
    )
    parser.add_argument(
        "--t5-model",
        type=str,
        default="t5-base",
        help="T5 model to download (default: t5-base)"
    )
    parser.add_argument(
        "--bart-samsum-model",
        type=str,
        default="philschmid/bart-large-cnn-samsum",
        help="BART-SAMSum model to download (default: philschmid/bart-large-cnn-samsum)"
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help=f"Custom cache directory (default: {DEFAULT_CACHE_DIR})"
    )
    parser.add_argument(
        "--skip-bart",
        action="store_true",
        help="Skip downloading BART model"
    )
    parser.add_argument(
        "--skip-pegasus",
        action="store_true",
        help="Skip downloading Pegasus model"
    )
    parser.add_argument(
        "--skip-t5",
        action="store_true",
        help="Skip downloading T5 model"
    )
    parser.add_argument(
        "--skip-bart-samsum",
        action="store_true",
        help="Skip downloading BART-SAMSum model"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all available model variants"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("📦 Contract Analyzer - Summarization Model Downloader")
    logger.info("=" * 70)
    logger.info(f"👤 User: akashrajeshnair")
    logger.info(f"📅 Date: 2025-11-15 01:00:45 UTC\n")
    
    # Set cache directory
    cache_dir = Path(args.cache_dir) if args.cache_dir else DEFAULT_CACHE_DIR
    logger.info(f"📁 Target directory: {cache_dir.absolute()}\n")
    
    # Ensure directory exists and is writable
    if not ensure_cache_directory(cache_dir):
        logger.error("Cannot proceed without valid cache directory")
        return 1
    
    # Check disk space (need more for summarization models)
    if not check_disk_space(cache_dir, min_gb=5.0):
        logger.warning("⚠️  Proceeding anyway, but download may fail if space runs out\n")
    
    results = []
    
    # Download models based on arguments
    if args.all:
        logger.info("🔄 Downloading ALL available summarization model variants...\n")
        
        # BART variants
        bart_models = [
            "facebook/bart-large-cnn",
            "facebook/bart-base",
            "philschmid/bart-large-cnn-samsum"
        ]
        for model in bart_models:
            results.append(("BART", model, download_bart_model(model, str(cache_dir))))
        
        # Pegasus variants
        pegasus_models = [
            "google/pegasus-cnn_dailymail",
            "google/pegasus-xsum"
        ]
        for model in pegasus_models:
            results.append(("Pegasus", model, download_pegasus_model(model, str(cache_dir))))
        
        # T5 variants
        t5_models = [
            "t5-small",
            "t5-base",
            "t5-large"
        ]
        for model in t5_models:
            results.append(("T5", model, download_t5_model(model, str(cache_dir))))
    
    else:
        # Download specified models
        if not args.skip_bart:
            results.append(("BART", args.bart_model, download_bart_model(args.bart_model, str(cache_dir))))
        
        if not args.skip_pegasus:
            results.append(("Pegasus", args.pegasus_model, download_pegasus_model(args.pegasus_model, str(cache_dir))))
        
        if not args.skip_t5:
            results.append(("T5", args.t5_model, download_t5_model(args.t5_model, str(cache_dir))))
        
        if not args.skip_bart_samsum:
            results.append(("BART-SAMSum", args.bart_samsum_model, download_bart_model(args.bart_samsum_model, str(cache_dir))))
    
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
        logger.info("\n🎉 All summarization models downloaded successfully!")
        logger.info("You can now run the application with summarization enabled.")
        logger.info("\nTo use these models, add to your .env file:")
        logger.info(f"TRANSFORMERS_CACHE={cache_dir.absolute()}")
        logger.info(f"HF_HOME={cache_dir.absolute()}")
        return 0
    else:
        logger.error("\n⚠️  Some models failed to download.")
        logger.error("Check your internet connection and try again.")
        logger.error("You can still use rule-based summarization without ML models.")
        return 1


if __name__ == "__main__":
    sys.exit(main())