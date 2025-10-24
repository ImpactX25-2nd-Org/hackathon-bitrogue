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
  cropName: string;
  description: string;
  voiceFile: Blob | null;
  language?: string; // Language code (e.g., 'mr', 'hi', 'kn', 'en')
}

export interface CommunityPrefill {
  image?: File | string;
  cropName?: string;
  description?: string;
}

export interface DetectionResult {
  scanId: string;
  diseaseName: string;
  reliability: number;
  nextSteps: string[];
  isCommon: boolean;
  communityAdvice?: any[];
  timestamp?: string; // When the scan was performed
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
 * - Accept multipart/form-data with image, cropName, description, and optional voice file
 * - Process image through ML model
 * - Convert voice to text and translate to English if needed
 * - Return detection result with scanId
 * 
 * Example endpoint: POST /api/scan
 * 
 * Request format:
 * {
 *   image: File,
 *   cropName: string,
 *   description: string,
 *   voiceFile?: Blob,
 *   language?: string
 * }
 * 
 * Response format:
 * {
 *   scanId: string,
 *   status: 'processing' | 'completed',
 *   estimatedTime?: number
 * }
 * 
 * Sample payload comment:
 * {
 *   scanId: "scan_12345",
 *   imageUrl: "https://...",
 *   cropName: "Groundnut",
 *   description: "Yellow spots on leaves",
 *   voiceFileMeta: { filename: "recording.webm", language: "mr" }
 * }
 */
/**
 * Send crop image and description for disease detection
 * 
 * Uses real backend ML API for disease detection
 */
export const onSendForDetection = async (payload: ScanPayload): Promise<DetectionResult> => {
  console.log('[API] Sending image for disease detection:', {
    imageSize: payload.image.size,
    cropName: payload.cropName,
    description: payload.description,
    language: payload.language,
  });

  try {
    // Use the real API from api.ts
    const { createScan } = await import('@/lib/api');
    
    const result = await createScan({
      image: payload.image,
      crop_name: payload.cropName.toLowerCase(),
      description: payload.description,
      language: payload.language
    });

    if (result.success && result.data) {
      return {
        scanId: result.data.scan_id,
        diseaseName: result.data.disease_detected,
        reliability: result.data.confidence,
        nextSteps: [], // Will be populated from backend later
        isCommon: true,
        timestamp: new Date().toISOString(), // Add timestamp
      };
    } else {
      throw new Error(result.message || 'Detection failed');
    }
  } catch (error: any) {
    console.error('Detection failed:', error);
    throw error;
  }
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

/**
 * Share detection result to community dashboard
 * 
 * Backend should:
 * - Create a new community post with prefilled data
 * - Associate post with the detection result
 * - Redirect user to community dashboard with new post
 * 
 * Example endpoint: POST /api/community/share
 * 
 * Request format:
 * {
 *   scanId?: string,
 *   image: File | string,
 *   cropName: string,
 *   description: string
 * }
 * 
 * Response format:
 * {
 *   postId: string,
 *   success: boolean
 * }
 */
export const shareToCommunity = async (prefill: CommunityPrefill): Promise<{ postId: string; success: boolean }> => {
  console.log('[PLACEHOLDER] shareToCommunity called with:', prefill);

  await new Promise(resolve => setTimeout(resolve, 800));

  return {
    postId: `post_${Date.now()}`,
    success: true,
  };
};

/**
 * Open new post modal/form with prefilled data
 * 
 * Frontend function to open community post creation with prefilled fields.
 * This is typically called when sharing from disease detection or other sources.
 * 
 * Prefill structure:
 * {
 *   image?: File | string,
 *   cropName?: string,
 *   description?: string
 * }
 */
export const openNewPostWithPrefill = (prefill: CommunityPrefill): void => {
  console.log('[PLACEHOLDER] openNewPostWithPrefill called with:', prefill);
  
  // Frontend implementation will:
  // 1. Store prefill data in state/context
  // 2. Open the new post modal/form
  // 3. Populate form fields with prefill data
  // 4. Allow user to edit/submit
};
