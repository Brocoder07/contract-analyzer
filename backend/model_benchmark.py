#!/usr/bin/env python3
"""
Contract Risk Analyzer - Model Benchmark Script

This script helps you test and compare different pre-trained models for contract analysis.
Run this to determine which model works best for your specific use case.
"""

import time
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai.ml_model import MLModel

# Sample contract text for testing
SAMPLE_CONTRACT = """
This Agreement shall automatically renew for successive one-year terms unless either party 
provides written notice of termination at least thirty (30) days prior to the end of the 
then-current term. The Company's liability under this Agreement shall not exceed $1,000 
in the aggregate. Upon termination, all intellectual property developed during the term 
of this Agreement shall become the exclusive property of the Company. Either party may 
terminate this Agreement immediately upon written notice for any reason or no reason.
"""

def test_model(model_choice: str):
    """Test a specific model choice"""
    print(f"\n{'='*60}")
    print(f"Testing Model: {model_choice.upper()}")
    print(f"{'='*60}")
    
    try:
        # Initialize model
        ml_model = MLModel("./models", model_choice)
        
        # Time the loading
        start_time = time.time()
        ml_model.load()
        load_time = time.time() - start_time
        
        if not ml_model._loaded:
            print("❌ Model failed to load")
            return None
        
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        print(f"📊 Current model: {ml_model.current_model}")
        print(f"📝 Description: {ml_model.current_model_info.get('description', 'N/A')}")
        
        # Time the analysis
        start_time = time.time()
        risks = ml_model.analyze(SAMPLE_CONTRACT)
        analysis_time = time.time() - start_time
        
        print(f"⚡ Analysis completed in {analysis_time:.2f} seconds")
        print(f"🔍 Found {len(risks)} risk items:")
        
        for i, risk in enumerate(risks, 1):
            print(f"  {i}. {risk.risk_type.value} (confidence: {risk.confidence:.2f})")
            print(f"     Text: {risk.text[:100]}...")
            print(f"     Description: {risk.description}")
            print()
        
        return {
            "model": model_choice,
            "load_time": load_time,
            "analysis_time": analysis_time,
            "risks_found": len(risks),
            "total_confidence": sum(r.confidence for r in risks),
            "avg_confidence": sum(r.confidence for r in risks) / len(risks) if risks else 0
        }
        
    except Exception as e:
        print(f"❌ Error testing {model_choice}: {e}")
        return None

def main():
    """Run benchmark on all available models"""
    print("🚀 Contract Risk Analyzer - Model Benchmark")
    print("=" * 60)
    print("This script will test all available models and help you choose the best one.")
    print(f"Sample contract length: {len(SAMPLE_CONTRACT)} characters")
    
    # Available model choices
    model_choices = [
        "contracts_bert",    # Best for contracts
        "legal_bert",        # Good general legal model
        "legal_bert_small",  # Fastest option
        "deberta_large",     # Highest performance (if available)
        "roberta_large"      # Fallback option
    ]
    
    results = []
    
    for model_choice in model_choices:
        result = test_model(model_choice)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("📊 BENCHMARK SUMMARY")
    print("="*60)
    
    if not results:
        print("❌ No models were successfully tested")
        return
    
    print(f"{'Model':<20} {'Load Time':<12} {'Analysis Time':<15} {'Risks':<8} {'Avg Confidence':<15}")
    print("-" * 75)
    
    for result in results:
        print(f"{result['model']:<20} "
              f"{result['load_time']:<12.2f} "
              f"{result['analysis_time']:<15.2f} "
              f"{result['risks_found']:<8} "
              f"{result['avg_confidence']:<15.2f}")
    
    # Recommendations
    print("\n🎯 RECOMMENDATIONS:")
    
    # Fastest model
    fastest = min(results, key=lambda x: x['load_time'] + x['analysis_time'])
    print(f"⚡ Fastest: {fastest['model']} ({fastest['load_time'] + fastest['analysis_time']:.2f}s total)")
    
    # Most confident
    most_confident = max(results, key=lambda x: x['avg_confidence'])
    print(f"🎯 Most Confident: {most_confident['model']} (avg confidence: {most_confident['avg_confidence']:.2f})")
    
    # Most risks found
    most_thorough = max(results, key=lambda x: x['risks_found'])
    print(f"🔍 Most Thorough: {most_thorough['model']} ({most_thorough['risks_found']} risks found)")
    
    print(f"\n💡 For production use, consider: contracts_bert (balanced performance)")
    print(f"💡 For development/testing: legal_bert_small (fastest)")
    print(f"💡 For maximum accuracy: deberta_large (if available)")

if __name__ == "__main__":
    main()