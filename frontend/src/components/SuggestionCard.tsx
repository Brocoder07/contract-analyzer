import React, { useState } from 'react';
import { Lightbulb, ChevronDown, ChevronUp, CheckCircle, Brain, FileText } from 'lucide-react';
import type { Suggestion } from '../types';
import './SuggestionCard.css';

interface SuggestionCardProps {
  suggestions: Suggestion[];
  isExpanded?: boolean;
}

const getSourceIcon = (source: string) => {
  switch (source) {
    case 'rule_based':
      return <FileText className="h-4 w-4" />;
    case 't5_model':
      return <Brain className="h-4 w-4" />;
    case 'gpt_model':
      return <Brain className="h-4 w-4" />;
    case 'hybrid':
      return <Lightbulb className="h-4 w-4" />;
    default:
      return <Lightbulb className="h-4 w-4" />;
  }
};

const getSourceLabel = (source: string): string => {
  switch (source) {
    case 'rule_based':
      return 'Template';
    case 't5_model':
      return 'T5 AI';
    case 'gpt_model':
      return 'GPT AI';
    case 'hybrid':
      return 'Hybrid AI';
    default:
      return source;
  }
};

const getPriorityLabel = (priority: number): string => {
  switch (priority) {
    case 1:
      return 'Critical';
    case 2:
      return 'Important';
    case 3:
      return 'Optional';
    default:
      return 'Normal';
  }
};

export const SuggestionCard: React.FC<SuggestionCardProps> = ({ 
  suggestions, 
  isExpanded: initialExpanded = false 
}) => {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);

  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  const topSuggestion = suggestions[0];
  const additionalSuggestions = suggestions.slice(1);

  return (
    <div className="suggestion-card">
      {/* Top Suggestion - Always Visible */}
      <div className="suggestion-top">
        <div className="suggestion-header">
          <div className="suggestion-icon-title">
            <CheckCircle className="h-5 w-5 suggestion-check-icon" />
            <h4>Recommended Action</h4>
          </div>
          <div className="suggestion-badges">
            <span className={`priority-badge priority-${topSuggestion.priority}`}>
              {getPriorityLabel(topSuggestion.priority)}
            </span>
            <span className="confidence-badge">
              {Math.round(topSuggestion.confidence * 100)}% confidence
            </span>
            <span className="source-badge">
              {getSourceIcon(topSuggestion.source)}
              {getSourceLabel(topSuggestion.source)}
            </span>
          </div>
        </div>

        <div className="suggestion-content">
          <p className="suggestion-text">{topSuggestion.suggestion_text}</p>
          <p className="suggestion-rationale">
            <strong>Why:</strong> {topSuggestion.rationale}
          </p>
        </div>
      </div>

      {/* Additional Suggestions - Expandable */}
      {additionalSuggestions.length > 0 && (
        <>
          <button
            className="expand-button"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-4 w-4" />
                Hide {additionalSuggestions.length} alternative suggestion{additionalSuggestions.length > 1 ? 's' : ''}
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                Show {additionalSuggestions.length} more suggestion{additionalSuggestions.length > 1 ? 's' : ''}
              </>
            )}
          </button>

          {isExpanded && (
            <div className="additional-suggestions">
              {additionalSuggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-alternative">
                  <div className="suggestion-alt-header">
                    <span className="alt-number">Alternative {index + 1}</span>
                    <div className="suggestion-alt-badges">
                      <span className={`priority-badge priority-${suggestion.priority}`}>
                        {getPriorityLabel(suggestion.priority)}
                      </span>
                      <span className="confidence-badge">
                        {Math.round(suggestion.confidence * 100)}%
                      </span>
                      <span className="source-badge-small">
                        {getSourceIcon(suggestion.source)}
                        {getSourceLabel(suggestion.source)}
                      </span>
                    </div>
                  </div>
                  <p className="suggestion-text-alt">{suggestion.suggestion_text}</p>
                  <p className="suggestion-rationale-alt">
                    <strong>Why:</strong> {suggestion.rationale}
                  </p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};