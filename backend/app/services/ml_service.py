"""
Machine Learning service for crop disease detection
Uses EfficientNet-B3 models trained on crop-specific datasets
"""
import os
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from typing import Dict, List, Optional
import timm
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DiseaseDetectionService:
    """
    Service for detecting crop diseases using deep learning models
    Supports: chilli, groundnut, and rice crops
    """
    
    def __init__(self, models_dir: str = "ml_models"):
        """
        Initialize the disease detection service
        
        Args:
            models_dir: Directory containing model files
        """
        self.models_dir = Path(models_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Supported crop types
        self.supported_crops = ["chilli", "groundnut", "rice"]
        
        # Storage for loaded models and classes
        self.models: Dict[str, nn.Module] = {}
        self.class_names: Dict[str, List[str]] = {}
        
        # Image preprocessing pipeline
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet stats
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Load all models
        self._load_models()
        
    def _load_models(self):
        """Load all crop disease detection models"""
        logger.info(f"🔍 Loading disease detection models...")
        logger.info(f"📱 Device: {self.device}")
        
        for crop in self.supported_crops:
            try:
                # Load class names
                classes_file = self.models_dir / f"{crop}_classes.txt"
                with open(classes_file, 'r') as f:
                    class_names = [line.strip() for line in f.readlines()]
                self.class_names[crop] = class_names
                
                # Create model architecture
                num_classes = len(class_names)
                model = self._create_model(num_classes)
                
                # Load trained weights
                model_file = self.models_dir / f"{crop}_model_best.pth"
                
                if not model_file.exists():
                    logger.warning(f"⚠️  Model file not found: {model_file}")
                    logger.warning(f"⚠️  {crop.upper()} model will not be available")
                    continue
                
                # Load state dict
                try:
                    state_dict = torch.load(model_file, map_location=self.device)
                    model.load_state_dict(state_dict)
                    logger.info(f"✓ Loaded {crop} model from {model_file}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {crop} model weights: {str(e)}")
                    # Try loading with strict=False
                    try:
                        model.load_state_dict(state_dict, strict=False)
                        logger.warning(f"⚠️  Loaded {crop} model with strict=False")
                    except:
                        logger.error(f"❌ Could not load {crop} model even with strict=False")
                        continue
                
                # Move to device and set to eval mode
                model = model.to(self.device)
                model.eval()
                
                self.models[crop] = model
                logger.info(f"✓ {crop.upper()} model ready ({num_classes} classes)")
                
            except Exception as e:
                logger.error(f"❌ Error loading {crop} model: {str(e)}")
        
        logger.info(f"✅ Loaded {len(self.models)}/{len(self.supported_crops)} models successfully")
        
    def _create_model(self, num_classes: int) -> nn.Module:
        """
        Create EfficientNet-B3 model with custom classification head
        
        Args:
            num_classes: Number of output classes
            
        Returns:
            PyTorch model
        """
        # Create base EfficientNet-B3 model without classifier
        model = timm.create_model('efficientnet_b3', pretrained=False, num_classes=0)
        
        # Custom classification head
        model.classifier = nn.Sequential(
            nn.Linear(1536, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
        return model
    
    async def predict(
        self, 
        image_path: str, 
        crop_type: str
    ) -> Dict[str, any]:
        """
        Predict disease from crop image
        
        Args:
            image_path: Path to image file
            crop_type: Type of crop (chilli, groundnut, rice)
            
        Returns:
            Dictionary containing prediction results
            
        Raises:
            ValueError: If crop_type is invalid or image cannot be loaded
            RuntimeError: If model inference fails
        """
        # Validate crop type
        crop_type = crop_type.lower()
        if crop_type not in self.supported_crops:
            raise ValueError(
                f"Invalid crop type: {crop_type}. "
                f"Supported crops: {', '.join(self.supported_crops)}"
            )
        
        # Check if model is loaded
        if crop_type not in self.models:
            raise ValueError(
                f"Model for {crop_type} is not available. "
                f"Please ensure the model file exists in {self.models_dir}"
            )
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0)  # Add batch dimension
            image_tensor = image_tensor.to(self.device)
            
        except Exception as e:
            raise ValueError(f"Failed to load or preprocess image: {str(e)}")
        
        try:
            # Run inference
            model = self.models[crop_type]
            
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
                
                # Get all predictions
                all_probs = probabilities[0].cpu().numpy()
                
            # Get class names
            class_names = self.class_names[crop_type]
            predicted_disease = class_names[predicted_idx.item()]
            confidence_score = float(confidence.item() * 100)  # Convert to percentage
            
            # Create all predictions dictionary
            all_predictions = {
                class_names[i]: float(all_probs[i] * 100)
                for i in range(len(class_names))
            }
            
            # Sort by confidence
            all_predictions = dict(
                sorted(all_predictions.items(), key=lambda x: x[1], reverse=True)
            )
            
            return {
                "disease": predicted_disease,
                "confidence": round(confidence_score, 2),
                "all_predictions": all_predictions
            }
            
        except RuntimeError as e:
            # Handle CUDA out of memory errors
            if "out of memory" in str(e).lower():
                logger.warning("⚠️  CUDA out of memory, falling back to CPU")
                self.device = torch.device("cpu")
                # Move model to CPU
                self.models[crop_type] = self.models[crop_type].to(self.device)
                # Retry prediction
                return await self.predict(image_path, crop_type)
            else:
                raise RuntimeError(f"Model inference failed: {str(e)}")
        
        except Exception as e:
            raise RuntimeError(f"Prediction failed: {str(e)}")
    
    def get_supported_crops(self) -> List[str]:
        """Get list of supported crop types"""
        return self.supported_crops
    
    def is_model_loaded(self, crop_type: str) -> bool:
        """Check if model for specific crop is loaded"""
        return crop_type.lower() in self.models
    
    def get_class_names(self, crop_type: str) -> Optional[List[str]]:
        """Get class names for specific crop"""
        return self.class_names.get(crop_type.lower())


# Global instance (will be initialized in main.py)
ml_service: Optional[DiseaseDetectionService] = None


def get_ml_service() -> DiseaseDetectionService:
    """Get the global ML service instance"""
    global ml_service
    if ml_service is None:
        raise RuntimeError("ML service not initialized")
    return ml_service
