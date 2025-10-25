"""
RAG Service for retrieving disease information from knowledge base
"""
import json
import os
from typing import Dict, Optional
from pathlib import Path


class RAGService:
    """Retrieval-Augmented Generation service for crop disease information"""
    
    def __init__(self):
        """Initialize RAG service and load disease knowledge base"""
        self.disease_db: Dict = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load crop diseases knowledge base from JSON file"""
        try:
            # Get path to knowledge_base directory
            backend_dir = Path(__file__).parent.parent.parent
            kb_path = backend_dir / "knowledge_base" / "crop_diseases.json"
            
            if not kb_path.exists():
                print(f"❌ Knowledge base not found at: {kb_path}")
                return
            
            with open(kb_path, 'r', encoding='utf-8') as f:
                self.disease_db = json.load(f)
            
            print(f"✓ RAG Knowledge Base loaded: {len(self.disease_db)} diseases")
            
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            self.disease_db = {}
    
    def get_disease_info(self, disease_name: str) -> Optional[Dict]:
        """
        Retrieve disease information from knowledge base
        
        Args:
            disease_name: Name of the disease (e.g., "chilli_leafspot")
        
        Returns:
            Dictionary with disease information or None if not found
        """
        if not self.disease_db:
            return None
        
        # Direct lookup (case-sensitive)
        if disease_name in self.disease_db:
            return self.disease_db[disease_name]
        
        # Case-insensitive lookup
        disease_name_lower = disease_name.lower()
        for key, value in self.disease_db.items():
            if key.lower() == disease_name_lower:
                return value
        
        return None
    
    def format_context_for_llm(self, disease_info: Dict) -> str:
        """
        Format disease information into structured text for LLM context
        
        Args:
            disease_info: Dictionary containing disease information
        
        Returns:
            Formatted string with disease context (optimized for LLM input)
        """
        if not disease_info:
            return ""
        
        # Extract key information
        crop = disease_info.get('crop', 'Unknown')
        disease_name = disease_info.get('disease_name', 'Unknown')
        scientific_name = disease_info.get('scientific_name', '')
        severity = disease_info.get('severity', 'unknown')
        spread_rate = disease_info.get('spread_rate', 'unknown')
        
        # Build formatted context
        context_parts = []
        
        # Header
        header = f"Disease: {disease_name}"
        if scientific_name:
            header += f" ({scientific_name})"
        context_parts.append(header)
        context_parts.append(f"Crop: {crop}")
        context_parts.append(f"Severity: {severity.title()} | Spread Rate: {spread_rate.title()}")
        context_parts.append("")
        
        # Symptoms
        symptoms = disease_info.get('symptoms', [])
        if symptoms:
            context_parts.append("Symptoms:")
            for symptom in symptoms:
                context_parts.append(f"- {symptom}")
            context_parts.append("")
        
        # Causes
        causes = disease_info.get('causes', [])
        if causes:
            context_parts.append("Causes:")
            for cause in causes:
                context_parts.append(f"- {cause}")
            context_parts.append("")
        
        # Treatment options
        treatment = disease_info.get('treatment', {})
        if treatment:
            context_parts.append("Recommended Treatment:")
            
            # Immediate actions
            immediate = treatment.get('immediate', [])
            if immediate:
                context_parts.append("Immediate Actions:")
                for action in immediate:
                    context_parts.append(f"- {action}")
            
            # Chemical treatment
            chemical = treatment.get('chemical', [])
            if chemical:
                context_parts.append("Chemical Treatment:")
                for step in chemical:
                    context_parts.append(f"- {step}")
            
            # Organic treatment
            organic = treatment.get('organic', [])
            if organic:
                context_parts.append("Organic Treatment:")
                for step in organic:
                    context_parts.append(f"- {step}")
            
            # Fertilizers (for nutrient deficiency cases)
            fertilizers = treatment.get('fertilizers', [])
            if fertilizers:
                context_parts.append("Fertilizer Application:")
                for step in fertilizers:
                    context_parts.append(f"- {step}")
            
            context_parts.append("")
        
        # Prevention
        prevention = disease_info.get('prevention', [])
        if prevention:
            context_parts.append("Prevention Tips:")
            for tip in prevention:
                context_parts.append(f"- {tip}")
            context_parts.append("")
        
        # Additional information
        cost = disease_info.get('cost_estimate', '')
        timeline = disease_info.get('timeline', '')
        urgency = disease_info.get('urgency', '')
        yield_impact = disease_info.get('yield_impact', '')
        
        if cost or timeline or urgency:
            context_parts.append("Additional Information:")
            if cost:
                context_parts.append(f"Cost Estimate: {cost}")
            if timeline:
                context_parts.append(f"Timeline: {timeline}")
            if urgency:
                context_parts.append(f"Urgency: {urgency.title()}")
            if yield_impact:
                context_parts.append(f"Yield Impact: {yield_impact}")
        
        # Special notes
        note = disease_info.get('note', '')
        if note:
            context_parts.append("")
            context_parts.append(f"Important Note: {note}")
        
        # Join all parts
        formatted_context = "\n".join(context_parts)
        
        # Truncate if too long (keep within ~1000 tokens ≈ 4000 chars)
        if len(formatted_context) > 3500:
            formatted_context = formatted_context[:3500] + "..."
        
        return formatted_context
    
    def get_all_disease_names(self) -> list:
        """Get list of all disease names in knowledge base"""
        return list(self.disease_db.keys())
    
    def get_diseases_by_crop(self, crop_type: str) -> Dict:
        """
        Get all diseases for a specific crop
        
        Args:
            crop_type: Crop name (e.g., "chilli", "groundnut", "rice")
        
        Returns:
            Dictionary of diseases for that crop
        """
        crop_diseases = {}
        for disease_key, disease_info in self.disease_db.items():
            if disease_info.get('crop', '').lower() == crop_type.lower():
                crop_diseases[disease_key] = disease_info
        
        return crop_diseases
