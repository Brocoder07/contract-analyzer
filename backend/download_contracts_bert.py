#!/usr/bin/env python3
"""
Download BERT Contracts Model with Proper Configuration

This script downloads the nlpaueb/bert-base-uncased-contracts model
and sets it up for local use with our contract analysis system.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def download_contracts_bert():
    """Download and setup the BERT contracts model"""
    print("📥 Downloading BERT Contracts Model")
    print("=" * 50)
    
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch
    except ImportError:
        print("❌ Required packages not installed. Please run:")
        print("   pip install transformers torch")
        return False
    
    model_name = "nlpaueb/bert-base-uncased-contracts"
    local_path = "./app/data/models/bert_contracts"
    
    print(f"🔄 Downloading {model_name}...")
    print(f"📂 Local path: {local_path}")
    
    # Create directory
    os.makedirs(local_path, exist_ok=True)
    
    try:
        # Download tokenizer
        print("📝 Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(local_path)
        
        # Download the base model (without classification head)
        print("🤖 Downloading BERT model...")
        model = AutoModel.from_pretrained(model_name)
        model.save_pretrained(local_path)
        
        print("✅ Model downloaded successfully!")
        
        # Create model info file
        info_file = os.path.join(local_path, "model_info.txt")
        with open(info_file, "w") as f:
            f.write(f"Model: {model_name}\n")
            f.write("Type: BERT base model for contracts\n")
            f.write("Usage: Feature extraction + rule-based classification\n")
            f.write("Downloaded: Local cache\n")
        
        print(f"📋 Model info saved to {info_file}")
        
        # Test loading
        print("🧪 Testing model loading...")
        test_tokenizer = AutoTokenizer.from_pretrained(local_path)
        test_model = AutoModel.from_pretrained(local_path)
        print("✅ Model loads correctly!")
        
        print("\n🎉 BERT Contracts model ready for use!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        return False

def update_config_for_local_model():
    """Show instructions for updating config"""
    print("\n📝 Configuration Update Instructions:")
    print("=" * 50)
    print("To use the local model, update your config.py:")
    print()
    print("1. Change ML_MODEL_PATH to point to local directory:")
    print('   ML_MODEL_PATH: str = "./app/data/models/bert_contracts"')
    print()
    print("2. Set model choice to use local version:")
    print('   ML_MODEL_CHOICE: str = "local_contracts_bert"')
    print()
    print("3. The system will automatically use feature extraction + rule-based classification")

def main():
    """Main download process"""
    success = download_contracts_bert()
    
    if success:
        update_config_for_local_model()
        print("\n🚀 Ready to use local BERT contracts model!")
    else:
        print("\n❌ Download failed. Please check your internet connection and try again.")

if __name__ == "__main__":
    main()