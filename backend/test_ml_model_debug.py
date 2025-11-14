#!/usr/bin/env python3
"""
Debug ML Model Predictions

This script tests the ML model specifically to see why it's not detecting risks.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai.ml_model import MLModel
from app.core.config import settings

def test_ml_model():
    print("🔍 Testing ML Model Predictions")
    print("=" * 50)
    
    # Sample contract with known exploitative clauses
    test_sentences = [
        "This agreement shall auto-renew for successive one-year terms unless either party provides written notice of non-renewal at least 1 day prior to expiration.",
        "Liability is limited to $1000 for any claims.",
        "All intellectual property developed during the term of this agreement shall belong exclusively to the company.",
        "Either party may terminate this agreement with 7 days written notice."
    ]
    
    print("🤖 Initializing ML Model...")
    ml_model = MLModel(settings.ML_MODEL_PATH, settings.ML_MODEL_CHOICE)
    ml_model.load()
    
    print(f"\n🔧 Current model: {getattr(ml_model, 'current_model', 'Unknown')}")
    print(f"📊 Model loaded: {ml_model._loaded}")
    
    if hasattr(ml_model, 'classifier') and ml_model.classifier:
        print("🔄 Using zero-shot classification")
    elif ml_model.current_model != "enhanced_rules" and not ml_model.is_untrained_model:
        print("🔄 Using BERT-style prediction")
    else:
        print("🔄 Using enhanced rule-based fallback")
    
    print("\n" + "=" * 50)
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n📝 Testing sentence {i}:")
        print(f"Text: {sentence[:80]}...")
        
        # Test individual prediction methods (using same logic as analyze method)
        if hasattr(ml_model, 'classifier') and ml_model.classifier:
            prediction = ml_model._predict_with_zero_shot(sentence)
        elif ml_model.current_model != "enhanced_rules" and not ml_model.is_untrained_model:
            prediction = ml_model._predict_with_bert(sentence)
        else:
            prediction = ml_model._predict_sentence(sentence)
            
        print(f"Raw prediction: {prediction}")
        
        if prediction:
            is_significant = ml_model._is_significant_risk(prediction)
            print(f"Is significant risk: {is_significant}")
            
            if is_significant:
                label_info = ml_model.label_mapping[prediction["label"]]
                print(f"Risk type: {label_info['risk_type']}")
                print(f"Risk level: {label_info['risk_level']}")
                print(f"Confidence threshold: {label_info['threshold']}")
                print(f"Confidence: {prediction['confidence']:.3f}")
        else:
            print("No prediction returned")
    
    print("\n" + "=" * 50)
    
    # Test full analyze method
    full_contract = " ".join(test_sentences)
    print(f"\n🔄 Testing full contract analysis...")
    risks = ml_model.analyze(full_contract)
    print(f"ML model found {len(risks)} risks total")
    
    for risk in risks:
        print(f"- {risk.risk_type.value}: {risk.description} (confidence: {risk.confidence:.3f})")

if __name__ == "__main__":
    test_ml_model()