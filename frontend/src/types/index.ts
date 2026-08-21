export type RightsType = 'PUBLIC_DOMAIN' | 'OPEN_LICENSE' | 'ORIGINAL' | 'LICENSED' | 'UNKNOWN' | 'RESTRICTED';
export type PublicationStatus = 'DRAFT' | 'PROCESSING' | 'IN_REVIEW' | 'PUBLISHED' | 'REJECTED' | 'ARCHIVED';
export type Role = 'USER' | 'REVIEWER' | 'ADMIN';

export interface Story {
  id: string;
  title: string;
  originalAuthor?: string;
  originalLanguage: string;
  category: string;
  description?: string;
  coverImageUrl?: string;
  rightsType: RightsType;
  rightsVerified: boolean;
  rightsEvidence?: string;
  status: PublicationStatus;
  totalWords?: number;
  createdAt: string;
  updatedAt?: string;
}

export interface Entity {
  id: string;
  name: string;
  type: 'character' | 'location' | 'organization' | 'object' | 'concept';
  aliases?: string[];
  description: string;
  importance_score: number;
}

export interface StoryEvent {
  id: string;
  sequence: number;
  title: string;
  description: string;
  chronological_order: number;
  importance_score: number;
  is_crucial: boolean;
  is_spoiler: boolean;
}

export interface Relationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relation_type: string;
  description?: string;
}

export interface CausalLink {
  cause_event_id: string;
  effect_event_id: string;
  link_type: string;
}

export interface StoryGraphData {
  schema_version: string;
  story_id: string;
  title: string;
  summary: string;
  entities: Entity[];
  events: StoryEvent[];
  relationships: Relationship[];
  causal_links: CausalLink[];
  themes: string[];
}

export interface StoryGraphEntity {
  id: string;
  storyId: string;
  version: number;
  graphDataJson: string;
  qaReportJson?: string;
  approved: boolean;
  approvedBy?: string;
}

export interface CanonicalChapter {
  chapter_id: string;
  chapter_number: number;
  title: string;
  content: string;
  word_count: number;
  estimated_duration_seconds: number;
}

export interface NarrativeData {
  schema_version: string;
  story_id: string;
  duration_preset: string;
  title: string;
  tagline: string;
  synopsis: string;
  chapters: CanonicalChapter[];
  total_word_count: number;
  estimated_total_duration_seconds: number;
}

export interface NarrativeEntity {
  id: string;
  storyId: string;
  durationPreset: 'quick' | 'standard' | 'complete';
  targetDurationMinutes: number;
  wordCount: number;
  blueprintJson?: string;
  narrativeJson: string;
  approved: boolean;
}

export interface LocalizedChapter {
  chapter_id: string;
  chapter_number: number;
  title: string;
  content: string;
  cultural_notes?: string;
  word_count: number;
  estimated_duration_seconds: number;
}

export interface LocalizedScriptData {
  schema_version: string;
  story_id: string;
  duration_preset: string;
  language: string;
  language_name: string;
  title: string;
  synopsis: string;
  chapters: LocalizedChapter[];
  entity_name_map?: Record<string, string>;
  total_word_count: number;
  estimated_total_duration_seconds: number;
}

export interface LocalizationEntity {
  id: string;
  storyId: string;
  durationPreset: string;
  languageCode: string;
  languageName: string;
  scriptJson: string;
  qaReportJson?: string;
  approved: boolean;
}

export interface AudioChapter {
  chapter_id: string;
  chapter_number: number;
  title: string;
  audio_path: string;
  audio_format: string;
  duration_seconds: number;
  file_size_bytes: number;
}

export interface AudioAssetData {
  story_id: string;
  language: string;
  duration_preset: string;
  voice_id: string;
  chapters: AudioChapter[];
  total_duration_seconds: number;
  created_at: string;
}

export interface AudioEntity {
  id: string;
  storyId: string;
  durationPreset: string;
  languageCode: string;
  voiceId: string;
  totalDurationSeconds: number;
  chaptersJson: string;
  qaReportJson?: string;
  approved: boolean;
}

export interface PipelineJob {
  id: string;
  storyId: string;
  stage: string;
  status: 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  progressPercentage: number;
  currentStep: string;
  errorMessage?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  role: Role;
}
