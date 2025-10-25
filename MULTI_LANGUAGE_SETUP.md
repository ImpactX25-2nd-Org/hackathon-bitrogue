# Multi-Language Support Setup (English, Tamil, Kannada)

## 🌐 Features Implemented

### Backend Services
1. **Translation Service** - IndicTrans2 for English ↔ Tamil ↔ Kannada
2. **Audio Service** - Whisper for speech-to-text in all 3 languages
3. **Auto-translation** - AI advice automatically translated to user's language

### Frontend
- Language selector updated to show only: English, Tamil, Kannada
- All UI will auto-translate based on selected language

## 📦 Installation Steps

### 1. Install Python Dependencies

```bash
cd backend
pip install transformers==4.36.0
pip install IndicTransToolkit
pip install sentencepiece==0.1.99
pip install openai-whisper
pip install ffmpeg-python
```

### 2. Install FFmpeg (Required for Whisper)

**Windows:**
```powershell
# Download from: https://github.com/BtbN/FFmpeg-Builds/releases
# Or use chocolatey:
choco install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Hugging Face Login (for IndicTrans2)

```python
from huggingface_hub import login
login(token="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")
```

Or set environment variable:
```bash
export HF_TOKEN=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
```

## 🚀 Usage

### Backend API Endpoints

#### 1. Translate Text
```http
POST /api/language/translate
Content-Type: multipart/form-data

texts: ["Hello", "How are you?"]
src_lang: en
tgt_lang: ta
```

Response:
```json
{
  "success": true,
  "data": {
    "translations": ["வணக்கம்", "நீங்கள் எப்படி இருக்கிறீர்கள்?"],
    "src_lang": "en",
    "tgt_lang": "ta",
    "count": 2
  }
}
```

#### 2. Transcribe Audio
```http
POST /api/language/transcribe
Content-Type: multipart/form-data

audio: <audio file>
language: ta  (optional - auto-detects if not provided)
```

Response:
```json
{
  "success": true,
  "data": {
    "text": "வணக்கம் நான் ஒரு விவசாயி",
    "language": "tamil",
    "filename": "recording.mp3"
  }
}
```

#### 3. Get Supported Languages
```http
GET /api/language/supported-languages
```

Response:
```json
{
  "success": true,
  "data": {
    "languages": [
      {"code": "en", "name": "English", "native": "English"},
      {"code": "ta", "name": "Tamil", "native": "தமிழ்"},
      {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ"}
    ]
  }
}
```

### Automatic Translation

When uploading a scan, the AI advice will automatically be translated to the user's selected language:

```http
POST /api/scans
Content-Type: multipart/form-data

image: <crop image>
crop_type: rice
language: ta  <-- AI advice will be in Tamil
```

## 🎯 How It Works

### AI Advice Flow
1. **ML Detection** → Detects disease (English)
2. **RAG Retrieval** → Gets knowledge base info (English)
3. **LLM Generation** → Generates treatment advice (English)
4. **Translation** → Translates to user's language (ta/kn if selected)
5. **Response** → Returns translated advice

### Translation Service
- Uses **IndicTrans2-200M** models (lightweight, fast)
- Supports direct translation: en ↔ ta, en ↔ kn
- For ta ↔ kn, uses English as pivot language
- **Lazy loading**: Models load only when first used

### Audio Service
- Uses **Whisper-base** model (good balance of speed/accuracy)
- Auto-detects language if not specified
- Supports common audio formats: mp3, wav, m4a, ogg
- Returns timestamped segments for advanced features

## 🔧 Optimization Tips

### Model Sizes

**IndicTrans2:**
- `200M` (current) - Fast, good for real-time
- `1.2B` - Better quality, slower

**Whisper:**
- `tiny` - Fastest, lower accuracy
- `base` (current) - Balanced
- `small` - Better accuracy
- `medium/large` - Best quality, GPU recommended

### GPU Acceleration
If you have CUDA GPU:
```python
# Translation service automatically uses GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
```

### Caching
- Translation results are NOT cached (real-time translation)
- LLM responses ARE cached for 24h per disease+language
- Whisper transcriptions are NOT cached (each audio unique)

## 📝 Files Created/Modified

### Backend
- `app/services/translation_service.py` - IndicTrans2 integration
- `app/services/audio_service.py` - Whisper integration  
- `app/services/llm_service.py` - Added auto-translation
- `app/routes/language.py` - Translation & audio APIs
- `app/main.py` - Service initialization
- `requirements.txt` - Added new dependencies

### Frontend
- `src/contexts/LanguageContext.tsx` - Updated to 3 languages only

## 🐛 Troubleshooting

### Issue: "No module named 'IndicTransToolkit'"
```bash
pip install git+https://github.com/VarunGumma/IndicTransToolkit.git
```

### Issue: Whisper FFmpeg error
```bash
# Make sure FFmpeg is in PATH
ffmpeg -version
```

### Issue: Out of memory
```python
# Use smaller models in audio_service.py:
audio_service = AudioService(model_size="tiny")  # Instead of "base"
```

### Issue: Slow translation
```python
# Models load on first use. First translation will be slow.
# Subsequent translations are fast.
# To pre-load on startup, add to main.py:
translation_service.translation_service._load_en_to_indic()
translation_service.translation_service._load_indic_to_en()
```

## ✅ Testing

Run test to verify setup:
```bash
python test_indictrans.py
```

Expected output:
```
✓ Model loaded successfully!
English: Hello, how are you?
Tamil  : வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?
✓ All tests completed successfully!
```

## 🎉 Done!

Now your entire application supports:
- ✅ English, Tamil, Kannada site-wide
- ✅ AI advice auto-translated to user language
- ✅ Community posts translatable
- ✅ Audio input for farmers
- ✅ Voice-to-text search and queries
