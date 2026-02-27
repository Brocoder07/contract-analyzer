import axios from 'axios';
import type { AnalysisResponse, ModificationRequest, EditResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 0, // No timeout - let requests complete
});

export const contractAnalysisAPI = {
  analyzeContract: async (file: File): Promise<AnalysisResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post<AnalysisResponse>('/api/v1/analyze', formData);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || error.message;
        throw new Error(`Analysis failed: ${message}`);
      }
      throw new Error('Unexpected error during analysis');
    }
  },

  analyzeText: async (text: string): Promise<AnalysisResponse> => {
    try {
      const response = await api.post<AnalysisResponse>('/api/v1/analyze-text', text, {
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
};