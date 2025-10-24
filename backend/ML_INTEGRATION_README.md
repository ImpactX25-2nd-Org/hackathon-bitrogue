# ML Disease Detection Integration

## Overview

The KrishiLok backend now includes PyTorch-based crop disease detection using EfficientNet-B3 models trained on crop-specific datasets.

## Supported Crops

- **Chilli** (6 disease classes)
- **Groundnut** (6 disease classes)
- **Rice** (6 disease classes)

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- PyTorch 2.0.0
- torchvision 0.15.0
- timm 0.9.12 (for EfficientNet)
- Pillow 10.0.0

### 2. Add Model Files

Place your trained model files in `backend/ml_models/`:

```
backend/ml_models/
├── chilli_model_best.pth
├── groundnut_model_best.pth
├── rice_model_best.pth
├── chilli_classes.txt (already provided)
├── groundnut_classes.txt (already provided)
└── rice_classes.txt (already provided)
```

**Note:** Model files are NOT included in the repository due to their size. You need to:
- Copy them from your training directory
- Download from cloud storage
- Or create placeholder models for testing

### 3. Test ML Service

Before starting the backend, test if models load correctly:

```bash
cd backend
python test_ml_service.py
```

Expected output:
```
🧪 Testing ML Disease Detection Service
================================================
1. Initializing service...
🔍 Loading disease detection models...
📱 Device: cuda / cpu
✓ Loaded chilli model from ml_models/chilli_model_best.pth
✓ CHILLI model ready (6 classes)
...
✅ ML Service test completed!
```

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

On startup, you'll see:
```
🚀 Starting KrishiLok Backend...
🤖 Initializing ML Disease Detection Service...
✓ Loaded chilli model
✓ Loaded groundnut model  
✓ Loaded rice model
✅ ML Service initialized successfully
✓ Application startup complete
```

## API Usage

### Endpoint: POST /api/scans

**Request:**
```bash
curl -X POST "http://localhost:8000/api/scans" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@path/to/image.jpg" \
  -F "crop_type=chilli" \
  -F "description=Yellow spots on leaves"
```

**Supported crop types:**
- `chilli`
- `groundnut`
- `rice`

**Response:**
```json
{
  "success": true,
  "data": {
    "scan_id": "uuid-here",
    "crop_type": "chilli",
    "disease_detected": "chilli_leafspot",
    "confidence": 96.54,
    "all_predictions": {
      "chilli_leafspot": 96.54,
      "chilli_anthracnose": 2.31,
      "chilli_healthy": 0.89,
      "chilli_leafcurl": 0.15,
      "chilli_whitefly": 0.08,
      "chilli_yellowish": 0.03
    },
    "image_url": "/uploads/scans/uuid.jpg",
    "timestamp": "2025-10-25T10:30:00",
    "status": "completed"
  },
  "message": "Disease detected: chilli_leafspot"
}
```

## Architecture Details

### Model Structure

```python
EfficientNet-B3 Base (pretrained on ImageNet)
    ↓
Remove original classifier
    ↓
Custom Classification Head:
    - Linear(1536 → 512)
    - BatchNorm1d(512)
    - ReLU()
    - Dropout(0.3)
    - Linear(512 → num_classes)
```

### Image Preprocessing

1. Resize to 256x256
2. Center crop to 224x224
3. Convert to tensor
4. Normalize with ImageNet statistics:
   - Mean: [0.485, 0.456, 0.406]
   - Std: [0.229, 0.224, 0.225]

### Inference Pipeline

1. Load image with PIL
2. Apply preprocessing transforms
3. Add batch dimension
4. Move to GPU/CPU
5. Run model.forward() with torch.no_grad()
6. Apply softmax to get probabilities
7. Return top prediction + all class probabilities

## Disease Classes

### Chilli (6 classes)
1. chilli_anthracnose
2. chilli_healthy
3. chilli_leafcurl
4. chilli_leafspot
5. chilli_whitefly
6. chilli_yellowish

### Groundnut (6 classes)
1. groundnut_early_leaf_spot
2. groundnut_early_rust
3. groundnut_healthy
4. groundnut_late_leaf_spot
5. groundnut_nutrition_deficiency
6. groundnut_rust

### Rice (6 classes)
1. rice_bacterial_blight
2. rice_blast
3. rice_brown_spot
4. rice_healthy
5. rice_leaf_scald
6. rice_sheath_blight

## Error Handling

### Invalid Crop Type
```json
{
  "detail": "Invalid crop type: tomato. Supported crops: chilli, groundnut, rice"
}
```
Status: 400 Bad Request

### Model Not Loaded
```json
{
  "detail": "Model for chilli is not available. Please contact administrator."
}
```
Status: 503 Service Unavailable

### Image Loading Error
```json
{
  "detail": "Failed to load or preprocess image: cannot identify image file"
}
```
Status: 400 Bad Request

### CUDA Out of Memory
- Automatically falls back to CPU
- Logs warning: "⚠️ CUDA out of memory, falling back to CPU"
- Retries prediction on CPU

## Performance

### GPU (CUDA)
- Single prediction: ~50-100ms
- Batch of 10: ~200-300ms

### CPU
- Single prediction: ~500-1000ms
- Batch of 10: ~5-10s

**Recommendation:** Use GPU for production deployment

## Troubleshooting

### Models Not Loading

**Problem:** "⚠️ Model file not found"

**Solution:** 
1. Check `ml_models/` directory has .pth files
2. Verify file names match exactly:
   - `chilli_model_best.pth`
   - `groundnut_model_best.pth`
   - `rice_model_best.pth`

### Wrong Predictions

**Problem:** Model returns incorrect diseases

**Solution:**
1. Verify class names in `.txt` files match training
2. Check if model was trained on same data distribution
3. Ensure image preprocessing matches training

### Memory Errors

**Problem:** "CUDA out of memory"

**Solution:**
1. Service automatically falls back to CPU
2. Or reduce batch size (already set to 1)
3. Or use smaller model variant

### Import Errors

**Problem:** "No module named 'torch'"

**Solution:**
```bash
pip install torch==2.0.0 torchvision==0.15.0
```

## Development

### Adding New Crops

1. Train EfficientNet-B3 model on new crop dataset
2. Save model weights as `{crop}_model_best.pth`
3. Create `{crop}_classes.txt` with class names
4. Add crop to `supported_crops` in `ml_service.py`
5. Update API documentation

### Model Updates

To update an existing model:
1. Replace `.pth` file in `ml_models/`
2. Restart backend server
3. Models are reloaded on startup

### Testing

Test individual components:

```python
# Test model loading
from app.services.ml_service import DiseaseDetectionService
service = DiseaseDetectionService()

# Test prediction
result = await service.predict("path/to/image.jpg", "chilli")
print(result)
```

## Production Deployment

### Checklist

- [ ] All 3 model files present in `ml_models/`
- [ ] GPU available (NVIDIA with CUDA support)
- [ ] PyTorch installed with CUDA support
- [ ] Sufficient memory (min 4GB RAM, 2GB VRAM)
- [ ] Models tested with test script
- [ ] API endpoints tested with sample images
- [ ] Error handling verified
- [ ] Logging configured

### Optimization Tips

1. **Use GPU:** Install PyTorch with CUDA
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Model Quantization:** Reduce model size
   ```python
   model = torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)
   ```

3. **Caching:** Results cached in MongoDB (already implemented)

4. **Load Balancing:** Use multiple backend instances for high traffic

## License

Model weights are proprietary. Contact the training team for access.

## Support

For issues with ML integration:
1. Check logs in backend console
2. Run test script: `python test_ml_service.py`
3. Verify model files exist and are valid PyTorch state_dicts
4. Contact ML team for model-specific issues
