import React from 'react';
import { AlertTriangle, AlertCircle, Info, Shield, Clock, FileText } from 'lucide-react';
import type { AnalysisResponse, RiskItem, RiskLevel, RiskType } from '../types';
import './AnalysisResults.css';

interface AnalysisResultsProps {
  analysis: AnalysisResponse;
  className?: string;
}

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

const RiskCard: React.FC<{ risk: RiskItem }> = ({ risk }) => {
  const colorClass = getRiskLevelColor(risk.risk_level);
  const icon = getRiskLevelIcon(risk.risk_level);

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
            {risk.detector}
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

        <div className="risk-section">
          <h4>Suggested Action:</h4>
          <p>{risk.suggestion}</p>
        </div>
      </div>
    </div>
  );
};

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysis, className = '' }) => {
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
        </div>
      </div>

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
              <RiskCard key={index} risk={risk} />
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