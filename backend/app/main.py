"""
KrishiLok Backend - Main FastAPI Application
Agricultural Community Support Platform
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, scans, community, suggestions, notifications, language
from app.services import ml_service
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.translation_service import TranslationService
from app.services.audio_service import AudioService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("🚀 Starting KrishiLok Backend...")
    logger.info("=" * 60)
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Initialize ML Service
    try:
        logger.info("🤖 Initializing ML Disease Detection Service...")
        ml_service.ml_service = ml_service.DiseaseDetectionService()
        logger.info("✅ ML Service initialized successfully")
    except Exception as e:
        logger.error(f"⚠️  Failed to initialize ML service: {str(e)}")
        logger.warning("⚠️  Disease detection will not be available")
    
    # Initialize RAG Service
    try:
        logger.info("📚 Loading RAG Knowledge Base...")
        scans.rag_service = RAGService()
        logger.info("✅ RAG Service initialized successfully")
    except Exception as e:
        logger.error(f"⚠️  Failed to initialize RAG service: {str(e)}")
        logger.warning("⚠️  RAG knowledge base will not be available")
    
    # Initialize LLM Service
    try:
        logger.info("🧠 Initializing LLM Service (OpenRouter)...")
        scans.llm_service = LLMService()
        logger.info("✅ LLM Service initialized successfully")
    except Exception as e:
        logger.error(f"⚠️  Failed to initialize LLM service: {str(e)}")
        logger.warning("⚠️  AI-powered treatment advice will not be available")
    
    # Initialize Translation Service
    try:
        logger.info("🌐 Initializing Translation Service (IndicTrans2)...")
        from app.services import translation_service
        translation_service.translation_service = TranslationService()
        logger.info("✅ Translation Service initialized successfully")
    except Exception as e:
        logger.error(f"⚠️  Failed to initialize Translation service: {str(e)}")
        logger.warning("⚠️  Multi-language support will not be available")
    
    # Initialize Audio Service
    try:
        logger.info("🎤 Initializing Audio Service (Whisper)...")
        from app.services import audio_service
        audio_service.audio_service = AudioService(model_size="base")
        logger.info("✅ Audio Service initialized successfully")
    except Exception as e:
        logger.error(f"⚠️  Failed to initialize Audio service: {str(e)}")
        logger.warning("⚠️  Audio transcription will not be available")
    
    logger.info("=" * 60)
    print("✓ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down KrishiLok Backend...")
    await close_mongo_connection()
    print("✓ Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="KrishiLok API",
    description="Agricultural Community Support Platform with AI-powered disease detection",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Mount static files (uploads)
if os.path.exists(settings.UPLOAD_FOLDER):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify service is running
    """
    return {
        "status": "ok",
        "service": "KrishiLok Backend",
        "version": "1.0.0",
        "message": "Service is running"
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Welcome to KrishiLok API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(scans.router, prefix="/api")
app.include_router(community.router, prefix="/api")
app.include_router(suggestions.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(language.router, prefix="/api")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions
    """
    return {
        "success": False,
        "message": "An unexpected error occurred",
        "detail": str(exc) if settings.HOST == "0.0.0.0" else "Internal server error"
    }


if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔════════════════════════════════════════════════════════╗
    ║           KrishiLok Backend Server                     ║
    ║   Agricultural Community Support Platform              ║
    ╚════════════════════════════════════════════════════════╝
    
    🌾 Server: http://{settings.HOST}:{settings.PORT}
    📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs
    💚 Health: http://{settings.HOST}:{settings.PORT}/health
    
    📡 Frontend URL: {settings.FRONTEND_URL}
    🗄️  Database: {settings.DATABASE_NAME}
    
    Press Ctrl+C to stop the server
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
