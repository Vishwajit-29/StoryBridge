import axios from 'axios';
import {
  Story,
  StoryGraphEntity,
  NarrativeEntity,
  LocalizationEntity,
  AudioEntity,
  PipelineJob,
  UserProfile,
} from '../types';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('storybridge_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: (data: { username: string; password: string }) =>
    api.post<{ token: string; username: string; email: string; role: string }>('/auth/login', data),
  register: (data: { username: string; email: string; password: string; role?: string }) =>
    api.post<{ token: string; username: string; email: string; role: string }>('/auth/register', data),
  getProfile: () => api.get<UserProfile>('/auth/me'),
};

export const storiesApi = {
  getPublished: (category?: string) =>
    api.get<Story[]>('/stories', { params: { category } }),
  getById: (id: string) => api.get<Story>(`/stories/${id}`),
  getGraph: (id: string) => api.get<StoryGraphEntity>(`/stories/${id}/graph`),
  getNarratives: (id: string) => api.get<NarrativeEntity[]>(`/stories/${id}/narratives`),
  getNarrativeByPreset: (id: string, preset: string) =>
    api.get<NarrativeEntity>(`/stories/${id}/narratives/${preset}`),
  getLocalizations: (id: string) =>
    api.get<LocalizationEntity[]>(`/stories/${id}/localizations`),
  getLocalization: (id: string, preset: string, lang: string) =>
    api.get<LocalizationEntity>(`/stories/${id}/localizations/${preset}/${lang}`),
  getAudioAssets: (id: string) => api.get<AudioEntity[]>(`/stories/${id}/audio`),
  getAudioAsset: (id: string, preset: string, lang: string) =>
    api.get<AudioEntity>(`/stories/${id}/audio/${preset}/${lang}`),
  search: (query: string) => api.get<Story[]>('/search', { params: { q: query } }),
};

export const userApi = {
  getBookmarks: () => api.get<Story[]>('/me/bookmarks'),
  toggleBookmark: (storyId: string) =>
    api.post<{ storyId: string; bookmarked: boolean }>(`/me/bookmarks/${storyId}`),
  getBookmarkStatus: (storyId: string) =>
    api.get<{ bookmarked: boolean }>(`/me/bookmarks/${storyId}/status`),
  getHistory: () => api.get<any[]>('/me/history'),
  updateProgress: (data: {
    storyId: string;
    languageCode: string;
    durationPreset: string;
    chapterIndex: number;
    progressSeconds: number;
    completed: boolean;
  }) => api.post<{ status: string }>('/me/history', data),
};

export const adminApi = {
  getAllStories: () => api.get<Story[]>('/admin/stories'),
  createStory: (data: Partial<Story>) => api.post<Story>('/admin/stories', data),
  verifyRights: (id: string, data: { rightsType: string; verified: boolean; evidence?: string }) =>
    api.post<Story>(`/admin/stories/${id}/verify-rights`, data),
  triggerPipeline: (
    id: string,
    data: {
      sourceText: string;
      sourceFormat?: string;
      fileName?: string;
      durationPresets?: string[];
      languages?: string[];
    }
  ) => api.post<PipelineJob>(`/admin/stories/${id}/pipeline/trigger`, data),
  syncArtifacts: (id: string) =>
    api.post<{ status: string; artifactsCount: number }>(`/admin/stories/${id}/sync-artifacts`),
  publishStory: (id: string) => api.post<Story>(`/admin/stories/${id}/publish`),
  unpublishStory: (id: string, reason?: string) =>
    api.post<Story>(`/admin/stories/${id}/unpublish`, null, { params: { reason } }),
  getAllJobs: () => api.get<PipelineJob[]>('/admin/jobs'),
  getJobById: (id: string) => api.get<PipelineJob>(`/admin/jobs/${id}`),
};

export default api;
