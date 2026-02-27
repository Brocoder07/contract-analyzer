import React, { useState } from 'react';
import { FileText, Users, Calendar, Tag, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import type { Summary } from '../types';
import './SummaryCard.css';

interface SummaryCardProps {
  summary: Summary;
  isExpanded?: boolean;
}

const getSourceIcon = (source: string) => {
  switch (source) {
    case 'rule_based':
      return <FileText className="h-4 w-4" />;
    case 'hybrid':
      return <Sparkles className="h-4 w-4" />;
    default:
      return <Sparkles className="h-4 w-4" />;
  }
};

const getSourceLabel = (source: string): string => {
  switch (source) {
    case 'rule_based':
      return 'Extractive';
    case 'bart':
      return 'BART AI';
    case 'pegasus':
      return 'Pegasus AI';
    case 't5':
      return 'T5 AI';
    case 'bart_samsum':
      return 'BART-SAMSum AI';
    case 'hybrid':
      return 'Hybrid AI';
    default:
      return source;
  }
};

export const SummaryCard: React.FC<SummaryCardProps> = ({ 
  summary, 
  isExpanded: initialExpanded = true 
}) => {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);

  if (!summary) {
    return null;
  }

  return (
    <div className="summary-card">
      {/* Header */}
      <div className="summary-header">
        <div className="summary-title-section">
          <FileText className="h-6 w-6 summary-icon" />
          <h3>Contract Summary</h3>
        </div>
        <div className="summary-badges">
          {summary.contract_type && (
            <span className="contract-type-badge">
              <Tag className="h-3 w-3" />
              {summary.contract_type}
            </span>
          )}
          <span className="confidence-badge">
            {Math.round(summary.confidence * 100)}% confidence
          </span>
          <span className="source-badge">
            {getSourceIcon(summary.source)}
            {getSourceLabel(summary.source)}
          </span>
          <span className="compression-badge">
            {summary.compression_ratio.toFixed(1)}x compression
          </span>
        </div>
      </div>

      {/* Main Summary Text */}
      <div className="summary-content">
        <p className="summary-text">{summary.summary_text}</p>
      </div>

      {/* Stats Bar */}
      <div className="summary-stats-bar">
        <div className="stat-item">
          <span className="stat-label">Words:</span>
          <span className="stat-value">{summary.word_count}</span>
        </div>
        {summary.parties_involved.length > 0 && (
          <div className="stat-item">
            <Users className="h-4 w-4" />
            <span className="stat-value">{summary.parties_involved.length} parties</span>
          </div>
        )}
        {summary.important_dates.length > 0 && (
          <div className="stat-item">
            <Calendar className="h-4 w-4" />
            <span className="stat-value">{summary.important_dates.length} dates</span>
          </div>
        )}
        {summary.key_points.length > 0 && (
          <div className="stat-item">
            <Tag className="h-4 w-4" />
            <span className="stat-value">{summary.key_points.length} key points</span>
          </div>
        )}
      </div>

      {/* Expandable Details */}
      {(summary.key_points.length > 0 || 
        summary.parties_involved.length > 0 || 
        summary.important_dates.length > 0) && (
        <>
          <button
            className="expand-details-button"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-4 w-4" />
                Hide Details
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                Show Details
              </>
            )}
          </button>

          {isExpanded && (
            <div className="summary-details">
              {/* Key Points */}
              {summary.key_points.length > 0 && (
                <div className="detail-section">
                  <h4>
                    <Tag className="h-4 w-4" />
                    Key Points
                  </h4>
                  <ul className="detail-list">
                    {summary.key_points.map((point, index) => (
                      <li key={index}>{point}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Parties Involved */}
              {summary.parties_involved.length > 0 && (
                <div className="detail-section">
                  <h4>
                    <Users className="h-4 w-4" />
                    Parties Involved
                  </h4>
                  <ul className="detail-list parties-list">
                    {summary.parties_involved.map((party, index) => (
                      <li key={index} className="party-item">{party}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Important Dates */}
              {summary.important_dates.length > 0 && (
                <div className="detail-section">
                  <h4>
                    <Calendar className="h-4 w-4" />
                    Important Dates
                  </h4>
                  <ul className="detail-list dates-list">
                    {summary.important_dates.map((date, index) => (
                      <li key={index} className="date-item">{date}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};