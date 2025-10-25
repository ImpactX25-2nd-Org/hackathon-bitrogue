"""
Audio Transcription Service using OpenAI Whisper
Converts audio (Tamil, Kannada, English) to text
"""
import os
import tempfile
from typing import Optional

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    print("⚠️ Whisper not available. Install with: pip install openai-whisper")
    WHISPER_AVAILABLE = False
    whisper = None

from app.config import settings


class AudioService:
    """Service for transcribing audio to text using Whisper"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       'base' is good balance of speed and accuracy
        """
        if not WHISPER_AVAILABLE:
            print("⚠️ Audio service disabled - Whisper not installed")
            self.model = None
            return
        
        print(f"📥 Loading Whisper model: {model_size}...")
        self.model = whisper.load_model(model_size)
        print(f"✓ Audio Service initialized with Whisper-{model_size}")
        
        # Supported languages
        self.supported_langs = {
            "en": "english",
            "ta": "tamil",
            "kn": "kannada"
        }
    
    def transcribe_audio(
        self, 
        audio_file_path: str, 
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file (mp3, wav, m4a, etc.)
            language: Expected language code (en, ta, kn) or None for auto-detect
        
        Returns:
            Dictionary with:
                - text: Transcribed text
                - language: Detected language
                - segments: Timestamped segments
        """
        if not WHISPER_AVAILABLE or self.model is None:
            return {
                "text": "",
                "language": "unknown",
                "segments": [],
                "success": False,
                "error": "Whisper not available"
            }
        
        try:
            # Convert language code to Whisper format
            whisper_lang = None
            if language and language in self.supported_langs:
                whisper_lang = self.supported_langs[language]
            
            print(f"🎤 Transcribing audio: {os.path.basename(audio_file_path)}")
            
            # Transcribe
            result = self.model.transcribe(
                audio_file_path,
                language=whisper_lang,
                task="transcribe",  # Use "translate" to translate to English
                fp16=False  # Use fp32 for CPU compatibility
            )
            
            detected_lang = result.get("language", "unknown")
            text = result.get("text", "").strip()
            
            print(f"✓ Transcribed ({detected_lang}): {text[:100]}...")
            
            return {
                "text": text,
                "language": detected_lang,
                "segments": result.get("segments", []),
                "success": True
            }
        
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return {
                "text": "",
                "language": "unknown",
                "segments": [],
                "success": False,
                "error": str(e)
            }
    
    def transcribe_bytes(
        self, 
        audio_bytes: bytes, 
        language: Optional[str] = None,
        filename: str = "audio.mp3"
    ) -> dict:
        """
        Transcribe audio from bytes (for uploaded files)
        
        Args:
            audio_bytes: Audio file bytes
            language: Expected language code
            filename: Original filename (for extension detection)
        
        Returns:
            Transcription result dictionary
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=os.path.splitext(filename)[1]
        ) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            result = self.transcribe_audio(tmp_path, language)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


# Global instance
audio_service: Optional[AudioService] = None
