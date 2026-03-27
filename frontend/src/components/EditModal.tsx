import React, { useState } from 'react';
import {
  X,
  Edit3,
  Download,
  CheckCircle,
  AlertTriangle,
  Trash2,
  FileDown,
} from 'lucide-react';
import type { StagedEdit, ModificationRequest } from '../types';
import { contractAnalysisAPI } from '../services/api';
import './EditModal.css';

interface EditModalProps {
  originalText: string;
  stagedEdits: StagedEdit[];
  onClose: () => void;
  /** Called when the server returns the modified text after /apply */
  onApplySuccess: (modifiedText: string) => void;
}

export const EditModal: React.FC<EditModalProps> = ({
  originalText,
  stagedEdits: initialEdits,
  onClose,
  onApplySuccess,
}) => {
  const [edits, setEdits] = useState<StagedEdit[]>(initialEdits);
  const [isApplying, setIsApplying] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [appliedText, setAppliedText] = useState<string | null>(null);

  const updateReplacement = (riskId: string, value: string) => {
    setEdits((prev) =>
      prev.map((e) => (e.riskId === riskId ? { ...e, replacement: value } : e))
    );
  };

  const removeEdit = (riskId: string) => {
    setEdits((prev) => prev.filter((e) => e.riskId !== riskId));
  };

  const buildRequest = (text: string, activeEdits: StagedEdit[]): ModificationRequest => ({
    original_text: text,
    modifications: activeEdits.map((e) => ({
      start_pos: e.start_pos,
      end_pos: e.end_pos,
      replacement_text: e.replacement,
      comment: e.comment,
    })),
  });

  const handleApply = async () => {
    if (edits.length === 0) return;
    setIsApplying(true);
    setError(null);
    try {
      const result = await contractAnalysisAPI.applyEdits(
        buildRequest(originalText, edits)
      );
      setAppliedText(result.modified_text);
      onApplySuccess(result.modified_text);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply edits');
    } finally {
      setIsApplying(false);
    }
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    setError(null);
    // If we already have applied text, download that; otherwise apply + download in one shot
    const sourceText = appliedText ?? originalText;
    const activeEdits = appliedText ? [] : edits; // no double-apply if already applied
    try {
      const blob = await contractAnalysisAPI.downloadDocx(
        buildRequest(sourceText, activeEdits)
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'modified_contract.docx';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download document');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="edit-modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="edit-modal">
        {/* Header */}
        <div className="edit-modal-header">
          <div className="edit-modal-title">
            <Edit3 className="edit-modal-title-icon" />
            <h2>Apply Suggested Edits</h2>
            <span className="edit-modal-count">{edits.length} pending</span>
          </div>
          <button className="edit-modal-close" onClick={onClose} aria-label="Close">
            <X />
          </button>
        </div>

        {/* Success banner */}
        {appliedText && (
          <div className="edit-banner edit-banner-success">
            <CheckCircle className="edit-banner-icon" />
            <span>
              Edits applied successfully.{' '}
              <button className="edit-banner-link" onClick={handleDownload}>
                Download DOCX
              </button>
            </span>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="edit-banner edit-banner-error">
            <AlertTriangle className="edit-banner-icon" />
            <span>{error}</span>
          </div>
        )}

        {/* Empty state */}
        {edits.length === 0 && !appliedText && (
          <div className="edit-modal-empty">
            <CheckCircle className="edit-modal-empty-icon" />
            <p>No pending edits. Add suggestions from the risk cards below.</p>
          </div>
        )}

        {/* Edit rows */}
        <div className="edit-modal-body">
          {edits.map((edit) => (
            <div key={edit.riskId} className="edit-row">
              <div className="edit-row-header">
                <span className="edit-row-risk-type">{edit.riskType}</span>
                <button
                  className="edit-row-remove"
                  onClick={() => removeEdit(edit.riskId)}
                  title="Remove this edit"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="edit-row-columns">
                {/* Original — display-normalise for readability; the raw bytes
                    are sent via start_pos/end_pos, not this string */}
                <div className="edit-col">
                  <label className="edit-col-label">Original text</label>
                  <div className="edit-col-original">
                    {edit.original.replace(/\s+/g, ' ').trim()}
                  </div>
                </div>

                {/* Replacement (editable) */}
                <div className="edit-col">
                  <label className="edit-col-label">Replacement text</label>
                  <textarea
                    className="edit-col-textarea"
                    value={edit.replacement}
                    onChange={(e) => updateReplacement(edit.riskId, e.target.value)}
                    rows={4}
                  />
                </div>
              </div>

              {edit.comment && (
                <p className="edit-row-comment">💡 {edit.comment}</p>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="edit-modal-footer">
          <button className="edit-btn edit-btn-ghost" onClick={onClose}>
            Cancel
          </button>

          <div className="edit-footer-actions">
            <button
              className="edit-btn edit-btn-secondary"
              onClick={handleDownload}
              disabled={isDownloading || (edits.length === 0 && !appliedText)}
            >
              {isDownloading ? (
                <span className="edit-spinner" />
              ) : (
                <FileDown className="h-4 w-4" />
              )}
              {isDownloading ? 'Generating…' : 'Download DOCX'}
            </button>

            <button
              className="edit-btn edit-btn-primary"
              onClick={handleApply}
              disabled={isApplying || edits.length === 0 || !!appliedText}
            >
              {isApplying ? (
                <span className="edit-spinner" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              {isApplying ? 'Applying…' : appliedText ? 'Applied ✓' : `Apply ${edits.length} Edit${edits.length !== 1 ? 's' : ''}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
