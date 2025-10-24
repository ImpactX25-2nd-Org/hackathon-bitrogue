/**
 * API Integration for KrishiLok Backend
 * Base URL and API functions for backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Helper function to handle API responses
async function handleResponse(response: Response) {
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.message || data.detail || 'An error occurred');
  }
  
  return data;
}

// Helper function to get auth headers
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('authToken');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
}

// ==================== AUTH APIs ====================

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  phone?: string;
  language?: string;
}

export interface LoginData {
  identifier: string; // email or phone
  password: string;
  language?: string;
}

export interface AuthResponse {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    name: string;
    email: string;
    phone?: string;
    language: string;
    trustScore: number;
    role: string;
  };
  message?: string;
}

export async function registerUser(data: RegisterData): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  
  return handleResponse(response);
}

export async function loginUser(data: LoginData): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  
  return handleResponse(response);
}

export async function getCurrentUser(): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

export async function refreshToken(): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

// ==================== SCAN APIs ====================

export interface ScanData {
  image: File;
  crop_name: string;
  description?: string;
  language?: string;
}

export async function createScan(data: ScanData) {
  const formData = new FormData();
  formData.append('image', data.image);
  formData.append('crop_type', data.crop_name.toLowerCase()); // Backend expects 'crop_type'
  if (data.description) formData.append('description', data.description);
  if (data.language) formData.append('language', data.language);

  const token = localStorage.getItem('authToken');
  const response = await fetch(`${API_BASE_URL}/scans`, {
    method: 'POST',
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    body: formData,
  });
  
  return handleResponse(response);
}

export async function getUserScans(skip = 0, limit = 10) {
  const response = await fetch(`${API_BASE_URL}/scans?skip=${skip}&limit=${limit}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

export async function getScanById(scanId: string) {
  const response = await fetch(`${API_BASE_URL}/scans/${scanId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

// ==================== COMMUNITY SCAN APIs ====================

export async function getCommunityScans(skip = 0, limit = 20, cropType?: string, diseaseName?: string) {
  let url = `${API_BASE_URL}/scans/community/feed?skip=${skip}&limit=${limit}`;
  if (cropType) url += `&crop_type=${cropType}`;
  if (diseaseName) url += `&disease_name=${diseaseName}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

export async function getScanComments(scanId: string, skip = 0, limit = 10) {
  const response = await fetch(`${API_BASE_URL}/scans/${scanId}/comments?skip=${skip}&limit=${limit}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

export async function addCommentToScan(scanId: string, advice: string) {
  const formData = new FormData();
  formData.append('advice', advice);
  
  const token = localStorage.getItem('authToken');
  const response = await fetch(`${API_BASE_URL}/scans/${scanId}/comments`, {
    method: 'POST',
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    body: formData,
  });
  
  return handleResponse(response);
}

export async function markCommentHelpful(scanId: string, commentId: string) {
  const response = await fetch(`${API_BASE_URL}/scans/${scanId}/comments/${commentId}/helpful`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

// ==================== COMMUNITY APIs ====================

export interface CreatePostData {
  title: string;
  description: string;
  crop_name?: string;
  tags?: string;
  image?: File;
  language?: string;
}

export async function createCommunityPost(data: CreatePostData) {
  const formData = new FormData();
  formData.append('title', data.title);
  formData.append('description', data.description);
  if (data.crop_name) formData.append('crop_name', data.crop_name);
  if (data.tags) formData.append('tags', data.tags);
  if (data.image) formData.append('image', data.image);
  if (data.language) formData.append('language', data.language);

  const token = localStorage.getItem('authToken');
  const response = await fetch(`${API_BASE_URL}/community/posts`, {
    method: 'POST',
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    body: formData,
  });
  
  return handleResponse(response);
}

export async function getCommunityPosts(page = 1, limit = 10, statusFilter?: string) {
  let url = `${API_BASE_URL}/community/posts?page=${page}&limit=${limit}`;
  if (statusFilter) url += `&status_filter=${statusFilter}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });
  
  return handleResponse(response);
}

export async function getPostById(postId: string) {
  const response = await fetch(`${API_BASE_URL}/community/posts/${postId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });
  
  return handleResponse(response);
}

export async function addComment(postId: string, content: string, isExpertAdvice = false) {
  const response = await fetch(`${API_BASE_URL}/community/posts/${postId}/respond`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ content, is_expert_advice: isExpertAdvice }),
  });
  
  return handleResponse(response);
}

// ==================== SUGGESTIONS APIs ====================

export async function getSuggestions(scanId: string) {
  const response = await fetch(`${API_BASE_URL}/suggestions/${scanId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

export async function submitTrustFeedback(suggestionId: string, score: number, feedback: string, scanId: string) {
  const response = await fetch(`${API_BASE_URL}/suggestions/trust-score`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      suggestion_id: suggestionId,
      score,
      feedback,
      scan_id: scanId,
    }),
  });
  
  return handleResponse(response);
}

// ==================== NOTIFICATIONS APIs ====================

export async function getNotifications(unreadOnly = false, limit = 20) {
  const response = await fetch(`${API_BASE_URL}/notifications?unread_only=${unreadOnly}&limit=${limit}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

export async function markNotificationAsRead(notificationId: string) {
  const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}
