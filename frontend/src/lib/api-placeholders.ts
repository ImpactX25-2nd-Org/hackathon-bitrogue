/**
 * API Placeholder Functions for Backend Integration
 * 
 * These functions are frontend placeholders that will be replaced
 * with actual backend API calls. They return Promises to simulate
 * async operations and can be easily replaced with fetch/axios calls.
 */

// Types for better developer experience
export interface ScanPayload {
  image: File;
  description: string;
  voiceFile: Blob | null;
  transcription: string;
  language?: string; // Language code (e.g., 'mr', 'hi', 'kn')
}

export interface DetectionResult {
  scanId: string;
  diseaseName: string;
  reliability: number;
  nextSteps: string[];
  isCommon: boolean;
  communityAdvice?: any[];
}

export interface Suggestion {
  id: string;
  text: string;
  author: {
    name: string;
    avatar?: string;
  };
  usefulness: number;
  details?: string;
}

/**
 * Send crop image and description for disease detection
 * 
 * Backend should:
 * - Accept multipart/form-data with image, text, and optional voice file
 * - Process image through ML model
 * - Convert voice to text and translate to English if needed
 * - Return detection result with scanId
 * 
 * Example endpoint: POST /api/scan
 * 
 * Request format:
 * {
 *   image: File,
 *   description: string,
 *   voiceFile?: Blob,
 *   transcription?: string,
 *   language?: string
 * }
 * 
 * Response format:
 * {
 *   scanId: string,
 *   status: 'processing' | 'completed',
 *   estimatedTime?: number
 * }
 */
export const onSendForDetection = async (payload: ScanPayload): Promise<{ scanId: string }> => {
  console.log('[PLACEHOLDER] onSendForDetection called with:', {
    imageSize: payload.image.size,
    description: payload.description,
    hasVoice: !!payload.voiceFile,
    transcription: payload.transcription,
  });

  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1500));

  // Return mock response
  return {
    scanId: `scan_${Date.now()}`,
  };
};

/**
 * Fetch detection result for a given scan
 * 
 * Backend should:
 * - Return complete detection result including disease info and suggestions
 * - Include community advice if disease is common
 * 
 * Example endpoint: GET /api/detection/:scanId
 * 
 * Response format: See DetectionResult interface
 */
export const fetchDetectionResult = async (scanId: string): Promise<DetectionResult> => {
  console.log('[PLACEHOLDER] fetchDetectionResult called with scanId:', scanId);

  await new Promise(resolve => setTimeout(resolve, 1000));

  // Return mock data
  return {
    scanId,
    diseaseName: "Early Blight (Alternaria solani)",
    reliability: 92,
    nextSteps: [
      "Remove and destroy infected leaves immediately",
      "Apply copper-based fungicide every 7-10 days",
      "Ensure proper spacing between plants",
    ],
    isCommon: true,
    communityAdvice: [],
  };
};

/**
 * Play translated audio message for detection result
 * 
 * Backend should:
 * - Generate audio file in user's selected language
 * - Return audio file URL or stream
 * - Support text-to-speech in multiple Indian languages
 * 
 * Example endpoint: GET /api/detection/:scanId/audio?lang=mr
 * 
 * Response format:
 * {
 *   audioUrl: string,
 *   language: string,
 *   duration: number
 * }
 */
export const playTranslatedMessage = async (scanId: string, language: string = 'en'): Promise<{ audioUrl: string }> => {
  console.log('[PLACEHOLDER] playTranslatedMessage called with:', { scanId, language });

  await new Promise(resolve => setTimeout(resolve, 500));

  return {
    audioUrl: '/mock-audio-url', // Backend should return actual audio file URL
  };
};

/**
 * Fetch community suggestions for a specific disease/scan
 * 
 * Backend should:
 * - Return ranked suggestions based on usefulness score
 * - Include farmer details and trust scores
 * 
 * Example endpoint: GET /api/suggestions/:scanId
 * 
 * Response format: Array of Suggestion objects
 */
export const fetchSuggestions = async (scanId: string): Promise<Suggestion[]> => {
  console.log('[PLACEHOLDER] fetchSuggestions called with scanId:', scanId);

  await new Promise(resolve => setTimeout(resolve, 800));

  return [
    {
      id: '1',
      text: 'Apply Mancozeb fungicide twice with 10 days gap',
      author: { name: 'Suresh Deshmukh' },
      usefulness: 85,
      details: 'Detailed instructions...',
    },
  ];
};

/**
 * Submit trust score/feedback for a suggestion
 * 
 * Backend should:
 * - Update farmer's trust score based on feedback
 * - Update suggestion usefulness score
 * - Trigger dashboard refresh for updated scores
 * - Schedule follow-up reminder (~10-15 days)
 * 
 * Example endpoint: POST /api/trust-score
 * 
 * Request format:
 * {
 *   suggestionId: string,
 *   score: number (1-5),
 *   farmerId?: string,
 *   feedback?: string
 * }
 * 
 * Response format:
 * {
 *   success: boolean,
 *   newTrustScore: number,
 *   followUpScheduled: boolean
 * }
 */
export const submitTrustScore = async (
  suggestionId: string,
  score: number
): Promise<{ success: boolean; newTrustScore: number }> => {
  console.log('[PLACEHOLDER] submitTrustScore called with:', { suggestionId, score });

  await new Promise(resolve => setTimeout(resolve, 1000));

  return {
    success: true,
    newTrustScore: 87, // Mock updated trust score
  };
};

/**
 * Fetch updated trust scores for dashboard refresh
 * 
 * Backend should:
 * - Return all updated trust scores after feedback submission
 * - Include timestamp of last update
 * 
 * Example endpoint: GET /api/trust-scores?updated_after=timestamp
 * 
 * Response format:
 * {
 *   farmers: Array<{ id: string, trustScore: number }>,
 *   lastUpdate: string
 * }
 */
export const fetchUpdatedTrustScores = async (): Promise<any> => {
  console.log('[PLACEHOLDER] fetchUpdatedTrustScores called');

  await new Promise(resolve => setTimeout(resolve, 500));

  return {
    farmers: [],
    lastUpdate: new Date().toISOString(),
  };
};
