"""
Translation and Audio API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from app.utils.dependencies import get_current_user
from app.models.user import UserInDB
from app.services import translation_service, audio_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/language", tags=["Language & Audio"])


@router.post("/translate", response_model=dict)
async def translate_text(
    texts: List[str],
    src_lang: str = Form(..., description="Source language: en, ta, kn"),
    tgt_lang: str = Form(..., description="Target language: en, ta, kn"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Translate text between English, Tamil, and Kannada
    
    - **texts**: List of texts to translate
    - **src_lang**: Source language code
    - **tgt_lang**: Target language code
    """
    try:
        if not translation_service.translation_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Translation service not available"
            )
        
        translations = translation_service.translation_service.translate(
            texts, src_lang, tgt_lang
        )
        
        return {
            "success": True,
            "data": {
                "translations": translations,
                "src_lang": src_lang,
                "tgt_lang": tgt_lang,
                "count": len(translations)
            }
        }
    
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/transcribe", response_model=dict)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (mp3, wav, m4a, etc.)"),
    language: Optional[str] = Form(None, description="Expected language: en, ta, kn (auto-detect if not specified)"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Transcribe audio to text using Whisper
    
    - **audio**: Audio file
    - **language**: Expected language (optional, auto-detects if not provided)
    """
    try:
        if not audio_service.audio_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audio service not available"
            )
        
        # Read audio bytes
        audio_bytes = await audio.read()
        
        # Transcribe
        result = audio_service.audio_service.transcribe_bytes(
            audio_bytes,
            language=language,
            filename=audio.filename or "audio.mp3"
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Transcription failed")
            )
        
        return {
            "success": True,
            "data": {
                "text": result["text"],
                "language": result["language"],
                "filename": audio.filename
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


@router.get("/supported-languages", response_model=dict)
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "success": True,
        "data": {
            "languages": [
                {"code": "en", "name": "English", "native": "English"},
                {"code": "ta", "name": "Tamil", "native": "தமிழ்"},
                {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ"}
            ]
        }
    }
