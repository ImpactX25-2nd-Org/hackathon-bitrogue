"""
Test script to verify ML service setup
Run this to check if models can be loaded
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.services.ml_service import DiseaseDetectionService
    
    print("=" * 60)
    print("🧪 Testing ML Disease Detection Service")
    print("=" * 60)
    
    # Initialize service
    print("\n1. Initializing service...")
    service = DiseaseDetectionService(models_dir="ml_models")
    
    # Check supported crops
    print(f"\n2. Supported crops: {service.get_supported_crops()}")
    
    # Check which models are loaded
    print("\n3. Model status:")
    for crop in service.get_supported_crops():
        status = "✓ Loaded" if service.is_model_loaded(crop) else "✗ Not loaded"
        print(f"   - {crop}: {status}")
        if service.is_model_loaded(crop):
            classes = service.get_class_names(crop)
            print(f"     Classes ({len(classes)}): {', '.join(classes[:3])}...")
    
    print("\n" + "=" * 60)
    print("✅ ML Service test completed!")
    print("=" * 60)
    
    # Test prediction if any model is loaded
    loaded_crops = [c for c in service.get_supported_crops() if service.is_model_loaded(c)]
    if loaded_crops:
        print(f"\n💡 Ready to accept predictions for: {', '.join(loaded_crops)}")
    else:
        print("\n⚠️  No models loaded. Add .pth files to ml_models/ directory")
        print("   See ml_models/SETUP_MODELS.txt for instructions")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
