import axios from 'axios';
import type {
  AnalysisResponse,
  ModificationRequest,
  EditResponse,
  RegisterRequest,
  RegisterResponse,
  LoginRequest,
  TokenResponse,
  AuthUser,
  OutputLanguage,
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 0, // No timeout - let requests complete
});

export const AUTH_TOKEN_STORAGE_KEY = 'contract_analyzer_auth_token';

export const setAuthToken = (token: string | null) => {
  if (token) {
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
  } else {
    localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
  }
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
};

api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const contractAnalysisAPI = {
  analyzeContract: async (file: File, outputLanguage: OutputLanguage = 'en'): Promise<AnalysisResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post<AnalysisResponse>('/api/v1/analyze', formData, {
        params: { output_language: outputLanguage },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || error.message;
        throw new Error(`Analysis failed: ${message}`);
      }
      throw new Error('Unexpected error during analysis');
    }
  },

  analyzeText: async (text: string, outputLanguage: OutputLanguage = 'en'): Promise<AnalysisResponse> => {
    try {
      const response = await api.post<AnalysisResponse>('/api/v1/analyze-text', text, {
        params: { output_language: outputLanguage },
        headers: {
          'Content-Type': 'text/plain',
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || error.message;
        throw new Error(`Analysis failed: ${message}`);
      }
      throw new Error('Unexpected error during analysis');
    }
  },

  checkHealth: async (): Promise<{ status: string; version: string }> => {
    try {
      const response = await api.get('/api/v1/health');
      return response.data;
    } catch (error) {
      throw new Error('Backend health check failed');
    }
  },

  applyEdits: async (request: ModificationRequest): Promise<EditResponse> => {
    try {
      const response = await api.post<EditResponse>('/api/v1/edit/apply', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || error.message;
        throw new Error(`Edit failed: ${message}`);
      }
      throw new Error('Unexpected error while applying edits');
    }
  },

  downloadDocx: async (request: ModificationRequest): Promise<Blob> => {
    try {
      const response = await api.post('/api/v1/edit/download/docx', request, {
        responseType: 'blob',
      });
      return response.data as Blob;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || error.message;
        throw new Error(`Download failed: ${message}`);
      }
      throw new Error('Unexpected error while downloading document');
    }
  },

  register: async (payload: RegisterRequest): Promise<RegisterResponse> => {
    try {
      const response = await api.post<RegisterResponse>('/api/v1/auth/register', payload);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || error.message;
        throw new Error(`Registration failed: ${message}`);
      }
      throw new Error('Unexpected error during registration');
    }
  },

  login: async (payload: LoginRequest): Promise<TokenResponse> => {
    try {
      const response = await api.post<TokenResponse>('/api/v1/auth/login', payload);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || error.message;
        throw new Error(`Login failed: ${message}`);
      }
      throw new Error('Unexpected error during login');
    }
  },

  me: async (): Promise<AuthUser> => {
    try {
      const response = await api.get<AuthUser>('/api/v1/auth/me');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || error.message;
        throw new Error(`Session check failed: ${message}`);
      }
      throw new Error('Unexpected error while checking session');
    }
  },
};