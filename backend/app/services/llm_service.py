"""
LLM Service for generating treatment advice using OpenRouter API
"""
import os
import json
import asyncio
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.config import settings


class LLMService:
    """Service for generating AI-powered treatment advice using OpenRouter API"""
    
    def __init__(self):
        """Initialize LLM service with OpenRouter configuration"""
        self.api_key = settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY", "")
        self.model = "mistralai/ministral-3b"
        self.base_url = "https://openrouter.ai/api/v1"
        
        if self.api_key:
            print(f"✓ LLM Service initialized with model: {self.model}")
            print(f"✓ API Key configured: {self.api_key[:20]}...")
        else:
            print("⚠️  OPENROUTER_API_KEY not set - LLM service will use fallback mode")
        
        # Response cache (simple in-memory cache)
        self.cache: Dict[str, tuple] = {}  # {disease_name: (response, timestamp)}
        self.cache_duration = timedelta(hours=24)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the LLM"""
        return """You are an expert agricultural advisor helping Indian farmers treat crop diseases. 
Provide clear, practical, and affordable advice in simple language suitable for farmers with limited resources.
Focus on actionable steps, local remedies, and cost-effective solutions.
Be concise, direct, and farmer-friendly. Avoid overly technical jargon."""
    
    def _get_user_prompt(
        self, 
        disease_name: str, 
        crop_type: str, 
        context: str, 
        confidence: float,
        language: str = "en"
    ) -> str:
        """Create user prompt with disease context"""
        
        # Language mapping
        lang_names = {
            "en": "English",
            "hi": "Hindi",
            "ta": "Tamil",
            "te": "Telugu",
            "kn": "Kannada",
            "mr": "Marathi"
        }
        language_name = lang_names.get(language, "English")
        
        prompt = f"""A farmer in India has detected {disease_name} in their {crop_type} crop with {confidence:.1f}% confidence.

Agricultural Database Information:
{context}

Please provide treatment advice in {language_name} language with the following structure:

1. SUMMARY (2-3 sentences): Brief explanation of the disease and what it means for the farmer
2. IMMEDIATE ACTIONS (3-5 steps): Practical steps the farmer should take right now
3. TREATMENT PLAN:
   - Chemical options: Specific products with dosages in simple terms
   - Organic options: Natural/traditional remedies available locally
4. PREVENTION TIPS (3-5 tips): How to prevent this in future crops
5. TIMELINE: Expected time for recovery/improvement
6. COST ESTIMATE: Approximate cost range in Indian Rupees
7. URGENCY: Low/Medium/High/Critical

Keep advice practical, affordable, and easy to understand. Use simple language that farmers can follow.
Include local product names where applicable. Focus on what's available in Indian agricultural markets."""
        
        return prompt
    
    def _call_openrouter_api_sync(
        self, 
        system_prompt: str, 
        user_prompt: str
    ) -> Optional[str]:
        """
        Call OpenRouter API using requests library (compatible with all versions)
        """
        if not self.api_key:
            print("❌ No API key available")
            return None
        
        try:
            print(f"🔄 Calling OpenRouter API with model: {self.model}")
            
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8080",
                "X-Title": "KrishiLok Agricultural Assistant",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"✓ OpenRouter API SUCCESS - Got {len(content)} chars")
                print(f"📝 First 100 chars: {content[:100]}...")
                return content
            else:
                print(f"❌ OpenRouter API error {response.status_code}: {response.text}")
                return None
            
        except Exception as e:
            print(f"❌ OpenRouter API error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _call_openrouter_api(
        self, 
        system_prompt: str, 
        user_prompt: str,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Async wrapper for OpenRouter API call
        """
        # Run sync function in executor to make it async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._call_openrouter_api_sync,
            system_prompt,
            user_prompt
        )
    
    def _parse_llm_response(self, llm_text: str, disease_info: Dict) -> Dict:
        """
        Parse LLM response into structured format
        
        Args:
            llm_text: Raw text from LLM
            disease_info: Original disease information for fallback
        
        Returns:
            Structured dictionary with treatment advice
        """
        # Initialize result structure
        result = {
            "summary": "",
            "immediate_actions": [],
            "treatment_plan": {
                "chemical": [],
                "organic": []
            },
            "prevention_tips": [],
            "timeline": "",
            "cost_estimate": "",
            "urgency": "medium",
            "raw_llm_response": llm_text
        }
        
        if not llm_text:
            return result
        
        # Simple parsing (split by sections)
        lines = llm_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            line_lower = line.lower()
            
            if 'summary' in line_lower or line.startswith('1.'):
                current_section = 'summary'
                continue
            elif 'immediate' in line_lower or line.startswith('2.'):
                current_section = 'immediate'
                continue
            elif 'treatment' in line_lower or line.startswith('3.'):
                current_section = 'treatment'
                continue
            elif 'prevention' in line_lower or line.startswith('4.'):
                current_section = 'prevention'
                continue
            elif 'timeline' in line_lower or line.startswith('5.'):
                current_section = 'timeline'
                continue
            elif 'cost' in line_lower or line.startswith('6.'):
                current_section = 'cost'
                continue
            elif 'urgency' in line_lower or line.startswith('7.'):
                current_section = 'urgency'
                continue
            
            # Extract content based on section
            if current_section == 'summary' and not line.startswith(('1.', '#')):
                result['summary'] += line + ' '
            
            elif current_section == 'immediate':
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    clean_line = line.lstrip('-•*0123456789. ')
                    if clean_line:
                        result['immediate_actions'].append(clean_line)
            
            elif current_section == 'treatment':
                if 'chemical' in line_lower:
                    current_section = 'treatment_chemical'
                elif 'organic' in line_lower:
                    current_section = 'treatment_organic'
            
            elif current_section == 'treatment_chemical':
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    clean_line = line.lstrip('-•*0123456789. ')
                    if clean_line and 'organic' not in clean_line.lower():
                        result['treatment_plan']['chemical'].append(clean_line)
            
            elif current_section == 'treatment_organic':
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    clean_line = line.lstrip('-•*0123456789. ')
                    if clean_line:
                        result['treatment_plan']['organic'].append(clean_line)
            
            elif current_section == 'prevention':
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    clean_line = line.lstrip('-•*0123456789. ')
                    if clean_line:
                        result['prevention_tips'].append(clean_line)
            
            elif current_section == 'timeline':
                if not line.startswith(('5.', '#', 'Timeline')):
                    result['timeline'] += line + ' '
            
            elif current_section == 'cost':
                if not line.startswith(('6.', '#', 'Cost')):
                    result['cost_estimate'] += line + ' '
            
            elif current_section == 'urgency':
                if not line.startswith(('7.', '#', 'Urgency')):
                    urgency_text = line.lower()
                    if 'critical' in urgency_text or 'very high' in urgency_text:
                        result['urgency'] = 'critical'
                    elif 'high' in urgency_text:
                        result['urgency'] = 'high'
                    elif 'low' in urgency_text:
                        result['urgency'] = 'low'
                    else:
                        result['urgency'] = 'medium'
        
        # Clean up
        result['summary'] = result['summary'].strip()
        result['timeline'] = result['timeline'].strip()
        result['cost_estimate'] = result['cost_estimate'].strip()
        
        # Fallback to disease_info if parsing failed
        if not result['summary'] and disease_info:
            result['summary'] = disease_info.get('disease_name', 'Disease detected')
        
        if not result['timeline'] and disease_info:
            result['timeline'] = disease_info.get('timeline', 'Varies based on severity')
        
        if not result['cost_estimate'] and disease_info:
            result['cost_estimate'] = disease_info.get('cost_estimate', 'Consult local supplier')
        
        return result
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if response is cached and still valid"""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                print(f"✓ Using cached response for: {cache_key}")
                return response
            else:
                # Cache expired
                del self.cache[cache_key]
        return None
    
    def _update_cache(self, cache_key: str, response: Dict):
        """Update cache with new response"""
        self.cache[cache_key] = (response, datetime.now())
        
        # Limit cache size (keep last 100 entries)
        if len(self.cache) > 100:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
    
    async def generate_treatment_advice(
        self,
        disease_name: str,
        crop_type: str,
        context: str,
        confidence: float,
        disease_info: Optional[Dict] = None,
        language: str = "en"
    ) -> Dict:
        """
        Generate AI-powered treatment advice using OpenRouter API
        
        Args:
            disease_name: Detected disease name
            crop_type: Type of crop (chilli, groundnut, rice)
            context: Formatted disease context from RAG
            confidence: ML model confidence score
            disease_info: Raw disease information for fallback
            language: Target language code (en, hi, ta, te, kn, mr)
        
        Returns:
            Dictionary with structured treatment advice
        """
        # Check cache first
        cache_key = f"{disease_name}_{language}"
        cached_response = self._check_cache(cache_key)
        if cached_response:
            return cached_response
        
        # Create prompts
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(disease_name, crop_type, context, confidence, language)
        
        # Call OpenRouter API
        llm_response = await self._call_openrouter_api(system_prompt, user_prompt)
        
        if llm_response:
            # Parse LLM response
            result = self._parse_llm_response(llm_response, disease_info or {})
            
            # Translate to target language if not English
            if language != "en" and language in ["ta", "kn"]:
                result = self._translate_response(result, "en", language)
            
            # Cache successful response
            self._update_cache(cache_key, result)
            
            print(f"✓ Generated AI advice for: {disease_name} ({language})")
            return result
        
        else:
            # Fallback: Use RAG knowledge base only
            print(f"⚠️  LLM failed, using RAG fallback for: {disease_name}")
            fallback = self._create_fallback_response(disease_info or {})
            
            # Translate fallback if needed
            if language != "en" and language in ["ta", "kn"]:
                fallback = self._translate_response(fallback, "en", language)
            
            return fallback
    
    def _translate_response(self, response: Dict, src_lang: str, tgt_lang: str) -> Dict:
        """Translate AI response to target language"""
        try:
            from app.services import translation_service
            if translation_service.translation_service:
                # Fields to translate
                fields = ["summary", "immediate_actions", "prevention_tips", "timeline", "cost_estimate"]
                return translation_service.translation_service.translate_dict(
                    response, fields, src_lang, tgt_lang
                )
        except Exception as e:
            print(f"⚠️ Translation failed: {e}")
        
        return response
    
    def _create_fallback_response(self, disease_info: Dict) -> Dict:
        """
        Create fallback response from RAG knowledge base when LLM fails
        
        Args:
            disease_info: Disease information from knowledge base
        
        Returns:
            Structured response using only RAG data
        """
        treatment = disease_info.get('treatment', {})
        
        return {
            "summary": disease_info.get('disease_name', 'Disease detected'),
            "immediate_actions": treatment.get('immediate', ['Consult agricultural expert']),
            "treatment_plan": {
                "chemical": treatment.get('chemical', []),
                "organic": treatment.get('organic', [])
            },
            "prevention_tips": disease_info.get('prevention', []),
            "timeline": disease_info.get('timeline', 'Varies based on severity'),
            "cost_estimate": disease_info.get('cost_estimate', 'Consult local supplier'),
            "urgency": disease_info.get('urgency', 'medium'),
            "raw_llm_response": None
        }
