import React, { useCallback, useState } from 'react';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import './FileUpload.css';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isUploading: boolean;
  error: string | null;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, isUploading, error }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(file => file.type === 'application/pdf');
    
    if (pdfFile) {
      onFileSelect(pdfFile);
    }
  }, [onFileSelect]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const getUploadZoneClasses = () => {
    let classes = 'upload-zone';
    if (isDragging) classes += ' dragging';
    if (isUploading) classes += ' uploading';
    return classes;
  };

  return (
    <div className="file-upload-container">
      <div
        className={getUploadZoneClasses()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          {isUploading ? (
            <div className="upload-spinner"></div>
          ) : (
            <Upload className="upload-icon" />
          )}
          
          <div className="upload-text">
            <h3>
              {isUploading ? 'Analyzing Contract...' : 'Upload PDF Contract'}
            </h3>
            <p>
              {isUploading 
                ? 'Please wait while we analyze your document'
                : 'Drag and drop a PDF file here, or click to select'
              }
            </p>
          </div>

          {!isUploading && (
            <label className="upload-button">
              <input
                type="file"
                className="upload-input"
                accept=".pdf"
                onChange={handleFileSelect}
              />
              <FileText style={{ height: '16px', width: '16px' }} />
              Choose PDF File
            </label>
          )}
        </div>
      </div>

      {error && (
        <div className="upload-error">
          <div className="upload-error-content">
            <AlertCircle className="upload-error-icon" />
            <span className="upload-error-text">{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};