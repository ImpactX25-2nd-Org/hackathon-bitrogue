"""
Translation Service using IndicTrans2 for multi-language support
Supports: English (en), Tamil (ta), Kannada (kn)
"""
import os
import torch
from typing import List, Optional, Dict

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from IndicTransToolkit.processor import IndicProcessor
    TRANSLATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Translation dependencies not available: {e}")
    print("⚠️ Install with: pip install transformers>=4.40.0 IndicTransToolkit")
    TRANSLATION_AVAILABLE = False
    IndicProcessor = None
    AutoModelForSeq2SeqLM = None
    AutoTokenizer = None

from app.config import settings


class TranslationService:
    """Service for translating text between English, Tamil, and Kannada"""
    
    # Language code mappings
    LANG_MAP = {
        "en": "eng_Latn",
        "ta": "tam_Taml",
        "kn": "kan_Knda"
    }
    
    LANG_NAMES = {
        "en": "English",
        "ta": "Tamil",
        "kn": "Kannada"
    }
    
    def __init__(self):
        """Initialize translation models"""
        if not TRANSLATION_AVAILABLE:
            print("⚠️ Translation service disabled - dependencies not installed")
            self.device = "cpu"
            self.processor = None
            return
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = IndicProcessor(inference=True)
        
        # Models (lazy loaded)
        self.en_to_indic_model = None
        self.en_to_indic_tokenizer = None
        self.indic_to_en_model = None
        self.indic_to_en_tokenizer = None
        
        print(f"✓ Translation Service initialized (device: {self.device})")
    
    def _load_en_to_indic(self):
        """Load English to Indic languages model"""
        if self.en_to_indic_model is None:
            print("📥 Loading English → Indic model...")
            model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
            
            self.en_to_indic_tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                trust_remote_code=True
            )
            self.en_to_indic_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            
            print("✓ English → Indic model loaded")
    
    def _load_indic_to_en(self):
        """Load Indic languages to English model"""
        if self.indic_to_en_model is None:
            print("📥 Loading Indic → English model...")
            model_name = "ai4bharat/indictrans2-indic-en-dist-200M"
            
            self.indic_to_en_tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                trust_remote_code=True
            )
            self.indic_to_en_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            
            print("✓ Indic → English model loaded")
    
    def translate(
        self, 
        texts: List[str], 
        src_lang: str, 
        tgt_lang: str
    ) -> List[str]:
        """
        Translate text between supported languages
        
        Args:
            texts: List of sentences to translate
            src_lang: Source language code (en, ta, kn)
            tgt_lang: Target language code (en, ta, kn)
        
        Returns:
            List of translated sentences
        """
        # Check if service is available
        if not TRANSLATION_AVAILABLE or self.processor is None:
            print("⚠️ Translation not available - returning original text")
            return texts
        
        # If same language, return as-is
        if src_lang == tgt_lang:
            return texts
        
        # Validate languages
        if src_lang not in self.LANG_MAP or tgt_lang not in self.LANG_MAP:
            print(f"⚠️ Unsupported language pair: {src_lang} → {tgt_lang}")
            return texts
        
        try:
            # Determine which model to use
            if src_lang == "en":
                # English to Indic
                self._load_en_to_indic()
                model = self.en_to_indic_model
                tokenizer = self.en_to_indic_tokenizer
            elif tgt_lang == "en":
                # Indic to English
                self._load_indic_to_en()
                model = self.indic_to_en_model
                tokenizer = self.indic_to_en_tokenizer
            else:
                # Indic to Indic (via English pivot)
                print(f"🔄 Translating {src_lang} → en → {tgt_lang}")
                intermediate = self.translate(texts, src_lang, "en")
                return self.translate(intermediate, "en", tgt_lang)
            
            # Get IndicTrans language codes
            src_code = self.LANG_MAP[src_lang]
            tgt_code = self.LANG_MAP[tgt_lang]
            
            # Preprocess
            batch = self.processor.preprocess_batch(
                texts, 
                src_lang=src_code, 
                tgt_lang=tgt_code
            )
            
            # Tokenize
            inputs = tokenizer(
                batch,
                truncation=True,
                padding="longest",
                max_length=256,
                return_tensors="pt",
                return_attention_mask=True
            ).to(self.device)
            
            # Generate translation
            with torch.inference_mode():
                generated_tokens = model.generate(
                    **inputs,
                    use_cache=False,
                    min_length=0,
                    max_length=256,
                    num_beams=1,
                    num_return_sequences=1
                )
            
            # Decode
            outputs = tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            # Postprocess
            translations = self.processor.postprocess_batch(outputs, lang=tgt_code)
            
            print(f"✓ Translated {len(texts)} texts from {src_lang} to {tgt_lang}")
            return translations
        
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return texts  # Fallback to original
    
    def translate_single(self, text: str, src_lang: str, tgt_lang: str) -> str:
        """Translate a single text"""
        result = self.translate([text], src_lang, tgt_lang)
        return result[0] if result else text
    
    def translate_dict(
        self, 
        data: Dict, 
        fields: List[str], 
        src_lang: str, 
        tgt_lang: str
    ) -> Dict:
        """
        Translate specific fields in a dictionary
        
        Args:
            data: Dictionary with text fields
            fields: List of field names to translate
            src_lang: Source language
            tgt_lang: Target language
        
        Returns:
            Dictionary with translated fields
        """
        if src_lang == tgt_lang:
            return data
        
        # Collect texts to translate
        texts = []
        field_indices = []
        
        for field in fields:
            if field in data and data[field]:
                if isinstance(data[field], list):
                    # Handle list fields (e.g., immediate_actions)
                    for item in data[field]:
                        if isinstance(item, str):
                            texts.append(item)
                            field_indices.append((field, "list"))
                elif isinstance(data[field], str):
                    texts.append(data[field])
                    field_indices.append((field, "string"))
        
        if not texts:
            return data
        
        # Translate all texts in one batch
        translations = self.translate(texts, src_lang, tgt_lang)
        
        # Update dictionary with translations
        result = data.copy()
        translation_idx = 0
        
        for field in fields:
            if field in result and result[field]:
                if isinstance(result[field], list):
                    translated_list = []
                    for item in result[field]:
                        if isinstance(item, str):
                            translated_list.append(translations[translation_idx])
                            translation_idx += 1
                        else:
                            translated_list.append(item)
                    result[field] = translated_list
                elif isinstance(result[field], str):
                    result[field] = translations[translation_idx]
                    translation_idx += 1
        
        return result


# Global instance
translation_service: Optional[TranslationService] = None
