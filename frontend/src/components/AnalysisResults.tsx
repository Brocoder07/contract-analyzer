import React from 'react';
import { AlertTriangle, AlertCircle, Info, Shield, Clock, FileText, Sparkles, Edit3 } from 'lucide-react';
import type { AnalysisResponse, RiskItem, RiskLevel, RiskType, StagedEdit } from '../types';
import { SuggestionCard } from './SuggestionCard';
import { SummaryCard } from './SummaryCard';
import './AnalysisResults.css';

interface AnalysisResultsProps {
  analysis: AnalysisResponse;
  className?: string;
  onStageEdit?: (edit: StagedEdit) => void;
}

const DETECTOR_LABELS: Record<string, string> = {
  'custom_ml_model':  '🤖 MiniLM (CUAD)',
  'rule_engine':      '📋 Rule Engine',
  // legacy / fallback patterns
  'ml_model_bert_contracts':         '🤖 BERT Contracts',
  'ml_model_local_contracts_bert':   '🤖 BERT Contracts',
};

const getDetectorLabel = (detector: string): string => {
  if (DETECTOR_LABELS[detector]) return DETECTOR_LABELS[detector];
  // Handle dynamic ml_model_* names
  if (detector.startsWith('ml_model_')) {
    const name = detector.replace('ml_model_', '').replace(/_/g, ' ');
    return `🤖 ${name}`;
  }
  return detector;
};

const getRiskLevelColor = (level: RiskLevel): string => {
  switch (level) {
    case 'high':
      return 'high';
    case 'medium':
      return 'medium';
    case 'low':
      return 'low';
    default:
      return 'none';
  }
};

const getRiskLevelIcon = (level: RiskLevel) => {
  switch (level) {
    case 'high':
      return <AlertTriangle className="h-5 w-5" />;
    case 'medium':
      return <AlertCircle className="h-5 w-5" />;
    case 'low':
      return <Info className="h-5 w-5" />;
    default:
      return <Shield className="h-5 w-5" />;
  }
};

const formatRiskType = (type: RiskType): string => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const RiskCard: React.FC<{ risk: RiskItem; onStageEdit?: (edit: StagedEdit) => void }> = ({ risk, onStageEdit }) => {
  const colorClass = getRiskLevelColor(risk.risk_level);
  const icon = getRiskLevelIcon(risk.risk_level);

  const bestSuggestion = risk.best_suggestion ?? risk.suggestions?.[0];
  const canStage =
    onStageEdit &&
    bestSuggestion &&
    risk.start_pos !== undefined &&
    risk.end_pos !== undefined;

  const handleStage = () => {
    if (!canStage || risk.start_pos === undefined || risk.end_pos === undefined) return;
    // Normalise extracted text: PDF extraction often inserts newlines between words.
    // Collapse any run of whitespace (including \n) down to a single space.
    const normalise = (s: string) => s.replace(/\s+/g, ' ').trim();
    onStageEdit({
      riskId: risk.id,
      riskType: formatRiskType(risk.risk_type),
      original: normalise(risk.text),
      replacement: normalise(bestSuggestion!.suggestion_text),
      start_pos: risk.start_pos,
      end_pos: risk.end_pos,
      comment: bestSuggestion!.rationale,
    });
  };

  return (
    <div className={`risk-card ${colorClass}`}>
      <div className="risk-header">
        <div className="risk-type">
          {icon}
          <span className="risk-type-label">
            {formatRiskType(risk.risk_type)}
          </span>
        </div>
        <div className="risk-badges">
          <span className="risk-badge">
            {Math.round(risk.confidence * 100)}% confident
          </span>
          <span className="risk-badge">
            {getDetectorLabel(risk.detector)}
          </span>
        </div>
      </div>

      <div className="risk-content">
        <div className="risk-section">
          <h4>Found Text:</h4>
          <p className="risk-text">
            "{risk.text}"
          </p>
        </div>

        <div className="risk-section">
          <h4>Risk Description:</h4>
          <p>{risk.description}</p>
        </div>

        {/* Legacy suggestion for backward compatibility */}
        {risk.suggestion && !risk.suggestions && (
          <div className="risk-section">
            <h4>Suggested Action:</h4>
            <p>{risk.suggestion}</p>
          </div>
        )}

        {/* AI-Generated Suggestions */}
        {risk.suggestions && risk.suggestions.length > 0 && (
          <SuggestionCard suggestions={risk.suggestions} />
        )}

        {/* Apply suggestion to document */}
        {canStage && (
          <button className="stage-edit-btn" onClick={handleStage}>
            <Edit3 className="stage-edit-btn-icon" />
            Stage this fix for editing
          </button>
        )}
      </div>
    </div>
  );
};

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysis, className = '', onStageEdit }) => {
  const overallColorClass = getRiskLevelColor(analysis.risk_level);
  const overallIcon = getRiskLevelIcon(analysis.risk_level);

  return (
    <div className={`analysis-results ${className}`}>
      {/* Overall Summary */}
      <div className={`overall-summary ${overallColorClass}`}>
        <div className="summary-header">
          <div className="summary-title">
            {overallIcon}
            <h2>
              Overall Risk Assessment: {analysis.risk_level.toUpperCase()}
            </h2>
          </div>
          <div className="summary-score">
            <div className="score-value">
              {Math.round(analysis.overall_risk_score * 100)}%
            </div>
            <div className="score-label">Risk Score</div>
          </div>
        </div>

        <div className="summary-stats">
          <div className="summary-stat">
            <AlertTriangle style={{ height: '16px', width: '16px' }} />
            <span>{analysis.total_risks_found} risks found</span>
          </div>
          <div className="summary-stat">
            <Clock style={{ height: '16px', width: '16px' }} />
            <span>Analyzed in {analysis.processing_time.toFixed(2)}s</span>
          </div>
          <div className="summary-stat">
            <FileText style={{ height: '16px', width: '16px' }} />
            <span>{analysis.document_metadata.text_length} characters</span>
          </div>
          {analysis.suggestion_model_type && (
            <div className="summary-stat">
              <Sparkles style={{ height: '16px', width: '16px' }} />
              <span>{analysis.suggestion_model_type} suggestions</span>
            </div>
          )}
        </div>
      </div>

      {/* NEW: Contract Summary */}
      {analysis.summary && (
        <SummaryCard summary={analysis.summary} />
      )}

      {/* NEW: Summary Metadata */}
      {analysis.summary_metadata && (
        <div className="summary-metadata-card">
          <h3>📊 Summarization Statistics</h3>
          <div className="metadata-stats-grid">
            <div className="metadata-stat-item">
              <span className="metadata-stat-value">
                {analysis.summary_metadata.total_summaries_generated}
              </span>
              <span className="metadata-stat-label">Summaries Generated</span>
            </div>
            <div className="metadata-stat-item">
              <span className="metadata-stat-value">
                {analysis.summary_metadata.processing_time.toFixed(2)}s
              </span>
              <span className="metadata-stat-label">Processing Time</span>
            </div>
            <div className="metadata-stat-item">
              <span className="metadata-stat-value">
                {analysis.summary_metadata.compression_ratio.toFixed(1)}x
              </span>
              <span className="metadata-stat-label">Compression Ratio</span>
            </div>
            <div className="metadata-stat-item">
              <span className="metadata-stat-value">
                {analysis.summary_metadata.original_word_count} → {analysis.summary_metadata.summary_word_count}
              </span>
              <span className="metadata-stat-label">Words (Original → Summary)</span>
            </div>
          </div>
          {analysis.summary_metadata.models_used.length > 0 && (
            <div className="models-used-section">
              <span className="models-label">Models Used:</span>
              {analysis.summary_metadata.models_used.map((model) => (
                <span key={model} className="model-tag">
                  {model.replace('_', ' ')}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Suggestion Statistics */}
      {analysis.suggestion_stats && (
        <div className="suggestion-stats-card">
          <h3>💡 AI Suggestion Statistics</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-value">{analysis.suggestion_stats.total_suggestions}</span>
              <span className="stat-label">Total Suggestions</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{analysis.suggestion_stats.risks_with_suggestions}</span>
              <span className="stat-label">Risks with Suggestions</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{Math.round(analysis.suggestion_stats.average_confidence * 100)}%</span>
              <span className="stat-label">Avg Confidence</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{analysis.suggestion_stats.suggestions_per_risk.toFixed(1)}</span>
              <span className="stat-label">Per Risk</span>
            </div>
          </div>
          {analysis.suggestion_stats.suggestions_by_source && (
            <div className="source-breakdown">
              <span className="source-label">Sources:</span>
              {Object.entries(analysis.suggestion_stats.suggestions_by_source).map(([source, count]) => (
                <span key={source} className="source-tag">
                  {source.replace('_', ' ')}: {count}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Document Metadata */}
      <div className="document-metadata">
        <h3>Document Analysis Details</h3>
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="label">Text Length:</span> {analysis.document_metadata.text_length.toLocaleString()} characters
          </div>
          <div className="metadata-item">
            <span className="label">Paragraphs:</span> {analysis.document_metadata.paragraphs_count}
          </div>
          <div className="metadata-item">
            <span className="label">Sentences:</span> {analysis.document_metadata.sentences_count}
          </div>
        </div>
      </div>

      {/* Risk Items */}
      {analysis.risks.length > 0 ? (
        <div className="risks-section">
          <h3>
            Identified Risks ({analysis.risks.length})
          </h3>
          <div className="risks-list">
            {analysis.risks.map((risk, index) => (
              <RiskCard key={index} risk={risk} onStageEdit={onStageEdit} />
            ))}
          </div>
        </div>
      ) : (
        <div className="no-risks">
          <Shield className="no-risks-icon" />
          <h3>No significant risks detected</h3>
          <p>The contract appears to have acceptable risk levels.</p>
        </div>
      )}
    </div>
  );
};