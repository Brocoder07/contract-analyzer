#!/usr/bin/env python3
"""
Download and Store Models Locally

This script downloads the ML models and stores them locally for faster loading.
"""

import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

def download_model(model_name: str, local_path: str):
    """Download a model and save it locally"""
    print(f"📥 Downloading {model_name}...")
    
    # Create directory if it doesn't exist
    os.makedirs(local_path, exist_ok=True)
    
    try:
        # Download tokenizer
        print("  📝 Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(local_path)
        
        # Download model
        print("  🤖 Downloading model...")
        if "mnli" in model_name.lower():
            # For zero-shot models, download the full pipeline
            classifier = pipeline(
                "zero-shot-classification",
                model=model_name,
                tokenizer=model_name
            )
            # Save model and tokenizer separately
            classifier.model.save_pretrained(local_path)
            classifier.tokenizer.save_pretrained(local_path)
        else:
            # For regular models
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            model.save_pretrained(local_path)
        
        print(f"  ✅ Successfully saved to {local_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to download {model_name}: {e}")
        return False

def main():
    """Download all recommended models"""
    print("🔄 Downloading ML Models for Local Storage")
    print("=" * 50)
    
    # Base directory for models
    base_dir = "./app/data/models"
    
    # Models to download (in order of preference)
    models_to_download = [
        {
            "name": "microsoft/deberta-large-mnli",
            "local_path": f"{base_dir}/deberta_large_mnli",
            "description": "DeBERTa-large with zero-shot classification (RECOMMENDED)"
        },
        {
            "name": "nlpaueb/legal-bert-small-uncased", 
            "local_path": f"{base_dir}/legal_bert_small",
            "description": "Legal BERT small (fast, lightweight)"
        },
        {
            "name": "nlpaueb/legal-bert-base-uncased",
            "local_path": f"{base_dir}/legal_bert_base", 
            "description": "Legal BERT base (good balance)"
        }
    ]
    
    success_count = 0
    
    for model_info in models_to_download:
        print(f"\n📦 {model_info['description']}")
        print(f"   Model: {model_info['name']}")
        print(f"   Local path: {model_info['local_path']}")
        
        # Check if already exists
        if os.path.exists(model_info['local_path']) and os.listdir(model_info['local_path']):
            print("  ✅ Model already exists locally")
            success_count += 1
            continue
        
        # Download the model
        if download_model(model_info['name'], model_info['local_path']):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Download Summary: {success_count}/{len(models_to_download)} models ready")
    
    if success_count > 0:
        print("\n🎉 Models downloaded successfully!")
        print("📝 Next steps:")
        print("   1. Update config.py to use local model paths")
        print("   2. Test the local models")
        print("   3. Enjoy faster startup times!")
    else:
        print("\n❌ No models were downloaded. Check your internet connection.")

if __name__ == "__main__":
    main()