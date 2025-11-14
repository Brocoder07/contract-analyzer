import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ZoomIn, ZoomOut, RotateCw, ChevronLeft, ChevronRight } from 'lucide-react';
import './PDFViewer.css';

// Set up PDF.js worker - use local copy
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

// Import react-pdf styles
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

interface PDFViewerProps {
  file: File;
  className?: string;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ file, className = '' }) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading PDF:', error);
    setError(`Failed to load PDF: ${error.message}`);
    setLoading(false);
  };

  const goToPrevPage = () => {
    setPageNumber(prev => Math.max(1, prev - 1));
  };

  const goToNextPage = () => {
    setPageNumber(prev => Math.min(numPages, prev + 1));
  };

  const zoomIn = () => {
    setScale(prev => Math.min(2.0, prev + 0.2));
  };

  const zoomOut = () => {
    setScale(prev => Math.max(0.5, prev - 0.2));
  };

  const rotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  return (
    <div className={`pdf-viewer ${className}`}>
      {/* PDF Controls */}
      <div className="pdf-controls">
        <div className="pdf-navigation">
          <button
            onClick={goToPrevPage}
            disabled={pageNumber <= 1}
            className="pdf-nav-button"
          >
            <ChevronLeft style={{ height: '16px', width: '16px' }} />
          </button>
          
          <span className="pdf-page-info">
            Page {pageNumber} of {numPages}
          </span>
          
          <button
            onClick={goToNextPage}
            disabled={pageNumber >= numPages}
            className="pdf-nav-button"
          >
            <ChevronRight style={{ height: '16px', width: '16px' }} />
          </button>
        </div>

        <div className="pdf-toolbar">
          <button
            onClick={zoomOut}
            className="pdf-nav-button"
            title="Zoom Out"
          >
            <ZoomOut style={{ height: '16px', width: '16px' }} />
          </button>
          
          <span className="pdf-zoom-info">
            {Math.round(scale * 100)}%
          </span>
          
          <button
            onClick={zoomIn}
            className="pdf-nav-button"
            title="Zoom In"
          >
            <ZoomIn style={{ height: '16px', width: '16px' }} />
          </button>
          
          <button
            onClick={rotate}
            className="pdf-nav-button"
            title="Rotate"
          >
            <RotateCw style={{ height: '16px', width: '16px' }} />
          </button>
        </div>
      </div>

      {/* PDF Document */}
      <div className="pdf-document-container">
        {loading && (
          <div className="pdf-loading">
            <div className="pdf-loading-spinner"></div>
            <span className="pdf-loading-text">Loading PDF...</span>
          </div>
        )}
        
        {error && (
          <div className="pdf-error">
            <span className="pdf-error-text">{error}</span>
          </div>
        )}
        
        <Document
          file={file}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={onDocumentLoadError}
          loading=""
        >
          <Page
            pageNumber={pageNumber}
            scale={scale}
            rotate={rotation}
            renderTextLayer={true}
            renderAnnotationLayer={true}
          />
        </Document>
      </div>
    </div>
  );
};