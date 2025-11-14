export const RiskLevel = {
  HIGH: "high",
  MEDIUM: "medium",
  LOW: "low",
  NONE: "none"
} as const;

export type RiskLevel = typeof RiskLevel[keyof typeof RiskLevel];

export const RiskType = {
  AUTO_RENEWAL: "auto_renewal",
  LIABILITY: "liability",
  TERMINATION: "termination",
  IP_OWNERSHIP: "ip_ownership",
  INDEMNIFICATION: "indemnification",
  CONFIDENTIALITY: "confidentiality"
} as const;

export type RiskType = typeof RiskType[keyof typeof RiskType];

export interface RiskItem {
  risk_type: RiskType;
  text: string;
  description: string;
  suggestion: string;
  risk_level: RiskLevel;
  confidence: number;
  start_pos?: number;
  end_pos?: number;
  detector: string;
}

export interface AnalysisResponse {
  risks: RiskItem[];
  overall_risk_score: number;
  risk_level: RiskLevel;
  total_risks_found: number;
  processing_time: number;
  document_metadata: {
    text_length: number;
    paragraphs_count: number;
    sentences_count: number;
  };
}

export interface UploadState {
  isUploading: boolean;
  error: string | null;
  file: File | null;
  analysis: AnalysisResponse | null;
}