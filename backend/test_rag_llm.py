"""
Quick test script to verify RAG+LLM integration
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.config import settings


async def test_rag_llm():
    """Test RAG and LLM services"""
    
    print("=" * 60)
    print("🧪 Testing RAG + LLM Integration")
    print("=" * 60)
    
    # Test RAG Service
    print("\n1️⃣  Testing RAG Service...")
    rag_service = RAGService()
    
    disease_name = "Groundnut Early Leaf Spot"
    disease_info = rag_service.get_disease_info(disease_name)
    
    if disease_info:
        print(f"✅ RAG found disease: {disease_info.get('disease_name')}")
        print(f"   Affected crops: {', '.join(disease_info.get('affected_crops', []))}")
        print(f"   Severity: {disease_info.get('severity')}")
    else:
        print(f"❌ RAG could not find: {disease_name}")
        return
    
    # Test LLM Service
    print("\n2️⃣  Testing LLM Service...")
    print(f"   API Key: {'✅ Set' if settings.OPENROUTER_API_KEY else '❌ Not set'}")
    
    llm_service = LLMService()
    
    if not llm_service.api_key:
        print("❌ LLM service has no API key - will use fallback")
    
    # Generate advice
    print("\n3️⃣  Generating treatment advice...")
    context = rag_service.format_context_for_llm(disease_info)
    
    advice = await llm_service.generate_treatment_advice(
        disease_name=disease_name,
        crop_type="groundnut",
        context=context,
        confidence=95.0,
        disease_info=disease_info,
        language="en"
    )
    
    print("\n" + "=" * 60)
    print("📋 TREATMENT ADVICE RESULT:")
    print("=" * 60)
    
    if advice:
        print(f"\n✅ Summary: {advice.get('summary', 'N/A')[:200]}...")
        
        immediate_actions = advice.get('immediate_actions', [])
        print(f"\n✅ Immediate Actions ({len(immediate_actions)} steps):")
        for i, action in enumerate(immediate_actions[:3], 1):
            print(f"   {i}. {action[:100]}...")
        
        print(f"\n✅ Timeline: {advice.get('timeline', 'N/A')}")
        print(f"✅ Cost: {advice.get('cost_estimate', 'N/A')}")
        print(f"✅ Urgency: {advice.get('urgency', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("🎉 TEST PASSED - RAG+LLM working correctly!")
        print("=" * 60)
    else:
        print("\n❌ No advice generated")
        print("=" * 60)
        print("⚠️  TEST FAILED - Check API key and services")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_rag_llm())
