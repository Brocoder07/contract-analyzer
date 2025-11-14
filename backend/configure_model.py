#!/usr/bin/env python3
"""
Model Configuration Utility for Contract Risk Analyzer

Use this script to easily switch between different AI models.
"""

import os
import sys

def display_model_options():
    """Display available model options"""
    print("🤖 Available AI Models for Contract Analysis:")
    print("=" * 60)
    
    models = {
        "1": {
            "key": "contracts_bert",
            "name": "CONTRACTS-BERT (Recommended)",
            "description": "BERT specifically trained on US contracts",
            "performance": "High",
            "speed": "Medium",
            "best_for": "Contract analysis, general use"
        },
        "2": {
            "key": "legal_bert",
            "name": "LEGAL-BERT",
            "description": "BERT trained on diverse legal texts",
            "performance": "High", 
            "speed": "Medium",
            "best_for": "General legal documents"
        },
        "3": {
            "key": "legal_bert_small",
            "name": "LEGAL-BERT Small (Fast)",
            "description": "Lightweight legal BERT (4x faster)",
            "performance": "Medium",
            "speed": "Fast",
            "best_for": "Development, testing, resource-constrained environments"
        },
        "4": {
            "key": "deberta_large",
            "name": "DeBERTa-Large (Premium)",
            "description": "DeBERTa with superior reasoning capabilities",
            "performance": "Very High",
            "speed": "Slow",
            "best_for": "Maximum accuracy, complex contracts"
        },
        "5": {
            "key": "roberta_large",
            "name": "RoBERTa-Large (Fallback)",
            "description": "General RoBERTa-large model",
            "performance": "High",
            "speed": "Slow", 
            "best_for": "Fallback option"
        }
    }
    
    for num, model in models.items():
        print(f"{num}. {model['name']}")
        print(f"   Description: {model['description']}")
        print(f"   Performance: {model['performance']} | Speed: {model['speed']}")
        print(f"   Best for: {model['best_for']}")
        print()
    
    return models

def update_config_file(model_choice: str):
    """Update the configuration file with the selected model"""
    config_path = "app/core/config.py"
    
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    try:
        # Read the current config
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Find and replace the ML_MODEL_CHOICE line
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('ML_MODEL_CHOICE:'):
                lines[i] = f'    ML_MODEL_CHOICE: str = "{model_choice}"'
                updated = True
                break
        
        if updated:
            # Write back the updated config
            with open(config_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Configuration updated successfully!")
            print(f"   Model choice: {model_choice}")
            print(f"   Config file: {config_path}")
            return True
        else:
            print("❌ Could not find ML_MODEL_CHOICE in config file")
            return False
            
    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        return False

def main():
    """Main configuration interface"""
    print("🔧 Contract Risk Analyzer - Model Configuration")
    print("=" * 60)
    
    models = display_model_options()
    
    while True:
        try:
            choice = input("👆 Select a model (1-5) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                print("👋 Goodbye!")
                break
            
            if choice in models:
                model_info = models[choice]
                model_key = model_info["key"]
                
                print(f"\n🎯 You selected: {model_info['name']}")
                print(f"   Key: {model_key}")
                
                confirm = input("   Confirm this choice? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    if update_config_file(model_key):
                        print(f"\n✨ Model configuration complete!")
                        print(f"   Restart your FastAPI server to use the new model.")
                        print(f"   You can run 'python model_benchmark.py' to test performance.")
                        break
                    else:
                        print(f"❌ Failed to update configuration")
                else:
                    print("❌ Configuration cancelled")
            else:
                print("❌ Invalid choice. Please select 1-5 or 'q' to quit.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()