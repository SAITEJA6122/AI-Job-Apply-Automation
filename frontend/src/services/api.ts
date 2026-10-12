import axios from 'axios';
import type { Profile, SessionStatus, ParsedResumeData, Application, Statistics } from '../types';

// Use environment variable for API base URL, fallback to production backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://ai-job-apply-automation-1.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Session Management
  getSessionStatus: async (): Promise<SessionStatus> => {
    const response = await api.get<SessionStatus>('/session/status');
    return response.data;
  },

  connectNaukri: async (): Promise<any> => {
    const response = await api.post('/naukri/connect');
    return response.data;
  },

  loginWithCredentials: async (credentials: { email: string; password: string }): Promise<any> => {
    const response = await api.post('/naukri/login', credentials);
    return response.data;
  },

  disconnectNaukri: async (): Promise<any> => {
    const response = await api.post('/naukri/disconnect');
    return response.data;
  },

  // Profile Management
  getProfile: async (): Promise<Profile> => {
    const response = await api.get<{ success: boolean; profile: Profile }>('/profile');
    return response.data.profile;
  },

  updateProfile: async (profile: Partial<Profile>): Promise<any> => {
    const response = await api.post('/profile', profile);
    return response.data;
  },

  // Resume Management
  uploadResume: async (file: File): Promise<{ success: boolean; resume_data: ParsedResumeData; file_path: string }> => {
    const formData = new FormData();
    formData.append('resume', file);
    const response = await api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  approveResumeData: async (approvedData: Partial<Profile>): Promise<any> => {
    const response = await api.post('/resume/approve', { approved_data: approvedData });
    return response.data;
  },

  getResumeStatus: async (): Promise<{ success: boolean; has_resume: boolean; profile_complete: boolean; profile: Profile | null }> => {
    const response = await api.get('/resume/status');
    return response.data;
  },

  // Statistics & Applications
  getStats: async (): Promise<Statistics> => {
    const response = await api.get<{ success: boolean; stats: Statistics }>('/stats');
    return response.data.stats;
  },

  getApplications: async (): Promise<Application[]> => {
    const response = await api.get<{ success: boolean; applications: Application[] }>('/applications');
    return response.data.applications;
  },

  // Automation Control
  startAutomation: async (): Promise<any> => {
    const response = await api.post('/automation/start');
    return response.data;
  },

  stopAutomation: async (): Promise<any> => {
    const response = await api.post('/automation/stop');
    return response.data;
  },

  getAutomationStatus: async (): Promise<{ success: boolean; running: boolean }> => {
    const response = await api.get('/automation/status');
    return response.data;
  },

  // Cleanup
  triggerCleanup: async (): Promise<any> => {
    const response = await api.post('/session/cleanup');
    return response.data;
  },

  // API Keys
  saveApiKeys: async (keys: { gemini_key?: string; groq_key?: string; openrouter_key?: string }): Promise<any> => {
    const response = await api.post('/api-keys', keys);
    return response.data;
  },

  getApiKeysStatus: async (): Promise<{ success: boolean; gemini_configured: boolean; groq_configured: boolean; openrouter_configured: boolean }> => {
    const response = await api.get('/api-keys');
    return response.data;
  },
};

export default apiService;
