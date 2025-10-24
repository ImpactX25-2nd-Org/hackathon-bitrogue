# ML Models Directory

## Required Model Files

Place the following trained model files in this directory:

1. **chilli_model_best.pth** - Chilli disease detection model
2. **groundnut_model_best.pth** - Groundnut disease detection model  
3. **rice_model_best.pth** - Rice disease detection model

## Model Architecture

- Base Model: EfficientNet-B3 (timm library)
- Input Size: 224x224 RGB images
- Custom Classification Head:
  - Linear(1536 → 512)
  - BatchNorm1d(512)
  - ReLU()
  - Dropout(0.3)
  - Linear(512 → num_classes)

## Class Files

The class names for each crop are stored in:
- `chilli_classes.txt` (6 classes)
- `groundnut_classes.txt` (6 classes)
- `rice_classes.txt` (6 classes)

## Usage

Models are automatically loaded on backend startup by the `DiseaseDetectionService`.
