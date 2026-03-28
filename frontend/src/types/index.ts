export const RiskLevel = {
  HIGH: "high",
  MEDIUM: "medium",
  LOW: "low",
  NONE: "none"
} as const;

export type RiskLevel = typeof RiskLevel[keyof typeof RiskLevel];

export type OutputLanguage = 'en' | 'hi';

export const RiskType = {
  AUTO_RENEWAL: "auto_renewal",
  LIABILITY_LIMITATION: "liability_limitation",
  TERMINATION: "termination",
  INDEMNIFICATION: "indemnification",
  CONFIDENTIALITY: "confidentiality",
  PAYMENT_TERMS: "payment_terms",
  INTELLECTUAL_PROPERTY: "intellectual_property",
  JURISDICTION: "jurisdiction",
  WARRANTY_DISCLAIMER: "warranty_disclaimer",
  DATA_PRIVACY: "data_privacy",
  FORCE_MAJEURE: "force_majeure",
  CHANGE_OF_CONTROL: "change_of_control",
  NON_COMPETE: "non_compete",
  ASSIGNMENT: "assignment",
  // CUAD custom model categories
  TERMINATION_FOR_CONVENIENCE: "termination_for_convenience",
  UNCAPPED_LIABILITY: "uncapped_liability",
  CAP_ON_LIABILITY: "cap_on_liability",
  LIQUIDATED_DAMAGES: "liquidated_damages",
  EXCLUSIVITY: "exclusivity",
  COVENANT_NOT_TO_SUE: "covenant_not_to_sue",
  MINIMUM_COMMITMENT: "minimum_commitment",
  IP_OWNERSHIP_ASSIGNMENT: "ip_ownership_assignment",
  NO_SOLICIT_OF_EMPLOYEES: "no_solicit_of_employees",
  NON_DISPARAGEMENT: "non_disparagement",
  ANTI_ASSIGNMENT: "anti_assignment",
  ROFR_ROFO_ROFN: "rofr_rofo_rofn",
  POST_TERMINATION_SERVICES: "post_termination_services",
} as const;

export type RiskType = typeof RiskType[keyof typeof RiskType];

// Suggestion interface
export interface Suggestion {
  suggestion_text: string;
  rationale: string;
  confidence: number;
  source: "rule_based" | "t5_model" | "gpt_model" | "hybrid";
  priority: number;
}

// RiskItem with suggestions
export interface RiskItem {
  id: string;
  risk_type: RiskType;
  text: string;
  description: string;
  suggestion: string;
  risk_level: RiskLevel;
  confidence: number;
  start_pos?: number;
  end_pos?: number;
  detector: string;
  suggestions?: Suggestion[];
  best_suggestion?: Suggestion;
}

// Suggestion statistics
export interface SuggestionStats {
  total_suggestions: number;
  risks_with_suggestions: number;
  risks_without_suggestions: number;
  suggestions_by_source: {
    rule_based?: number;
    t5_model?: number;
    gpt_model?: number;
  };
  average_confidence: number;
  suggestions_per_risk: number;
}

// NEW: Summary interface
export interface Summary {
  summary_text: string;
  key_points: string[];
  parties_involved: string[];
  important_dates: string[];
  contract_type: string | null;
  confidence: number;
  source: "rule_based" | "bart" | "pegasus" | "t5" | "bart_samsum" | "hybrid";
  word_count: number;
  compression_ratio: number;
}

// NEW: Summary metadata
export interface SummaryMetadata {
  total_summaries_generated: number;
  models_used: string[];
  processing_time: number;
  original_word_count: number;
  summary_word_count: number;
  compression_ratio: number;
}

// AnalysisResponse with summary
export interface AnalysisResponse {
  risks: RiskItem[];
  overall_risk_score: number;
  risk_level: RiskLevel;
  total_risks_found: number;
  processing_time: number;
  suggestion_model_type?: string;
  suggestion_stats?: SuggestionStats;
  summary?: Summary;  // NEW
  summary_metadata?: SummaryMetadata;  // NEW
  document_metadata: {
    text_length: number;
    paragraphs_count: number;
    sentences_count: number;
  };
  extracted_text?: string;  // Raw text returned by backend for position-based editing
  output_language?: OutputLanguage;
}

export interface UploadState {
  isUploading: boolean;
  error: string | null;
  file: File | null;
  analysis: AnalysisResponse | null;
}

// ── Document Editing ──────────────────────────────────────────────────────────

export interface TextModification {
  start_pos: number;
  end_pos: number;
  replacement_text: string;
  comment?: string;
}

export interface ModificationRequest {
  original_text: string;
  modifications: TextModification[];
}

export interface EditResponse {
  modified_text: string;
  changes_applied: number;
  download_url?: string;
}

/** A staged edit: one risk + the text replacement the user wants to apply. */
export interface StagedEdit {
  riskId: string;
  riskType: string;
  original: string;
  replacement: string;
  start_pos: number;
  end_pos: number;
  comment?: string;
}

// ── Authentication ───────────────────────────────────────────────────────────

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: AuthUser;
}

export interface RegisterResponse {
  message: string;
  user?: AuthUser;
}