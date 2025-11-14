import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.services.document_processor import DocumentProcessor
from app.services.ai.risk_analyzer import HybridRiskAnalyzer
from app.core.config import settings

def test_system():
    print("🧪 Testing Contract Risk Analyzer System...")
    
    try:
        # Test document processor
        processor = DocumentProcessor()
        print("✅ Document Processor loaded")
        
        # Test risk analyzer
        analyzer = HybridRiskAnalyzer("./app/services/ai/rules.json", "./app/data/models/production", settings.ML_MODEL_CHOICE)
        print("✅ Risk Analyzer loaded")
        
        # Test with sample contract text
        sample_contract = """
        This agreement shall auto-renew for successive one-year terms unless either party provides 
        written notice of non-renewal at least 1 day prior to expiration. Liability is limited 
        to $1000 for any claims. All intellectual property developed during the term of this 
        agreement shall belong exclusively to the company. Either party may terminate this 
        agreement with 7 days written notice.
        """
        
        print("📄 Analyzing sample contract...")
        result = analyzer.analyze_contract(sample_contract)
        
        print(f"✅ Analysis completed!")
        print(f"📊 Overall Risk Score: {result['overall_risk_score']:.2f}")
        print(f"⚠️  Risk Level: {result['risk_level'].value}")  # Use .value for enum
        print(f"🔍 Total Risks Found: {result['total_risks_found']}")
        print(f"⏱️  Processing Time: {result['processing_time']:.2f}s")
        
        print("\n📋 Identified Risks:")
        for i, risk in enumerate(result['risks'], 1):
            print(f"{i}. {risk.risk_type.value} - {risk.text[:60]}...")  # Use .value for enum
            print(f"   Description: {risk.description}")
            print(f"   Suggestion: {risk.suggestion}")
            print(f"   Confidence: {risk.confidence:.2f}, Level: {risk.risk_level.value}")
            print(f"   Detector: {risk.detector}")
            print()
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system()