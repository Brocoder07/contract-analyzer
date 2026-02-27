import { useState } from 'react';
import { FileUpload } from './components/FileUpload';
import { PDFViewer } from './components/PDFViewer';
import { AnalysisResults } from './components/AnalysisResults';
import { EditModal } from './components/EditModal';
import { contractAnalysisAPI } from './services/api';
import type { UploadState, StagedEdit } from './types';
import { FileText, BarChart3, Edit3 } from 'lucide-react';
import './App.css';

function App() {
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    error: null,
    file: null,
    analysis: null,
  });

  // Editing state
  const [originalText, setOriginalText] = useState<string>('');
  const [stagedEdits, setStagedEdits] = useState<StagedEdit[]>([]);
  const [showEditModal, setShowEditModal] = useState(false);
  const [modifiedText, setModifiedText] = useState<string | null>(null);

  // Reset all editing state when a new file is selected
  const handleFileSelect = async (file: File) => {
    setUploadState({
      isUploading: true,
      error: null,
      file,
      analysis: null,
    });
    setStagedEdits([]);
    setModifiedText(null);

    // Reset any previously extracted text
    setOriginalText('');

    try {
      const analysis = await contractAnalysisAPI.analyzeContract(file);
      // Use the server-extracted text (works for PDF, DOCX, and TXT)
      setOriginalText(analysis.extracted_text ?? '');
      setUploadState({
        isUploading: false,
        error: null,
        file,
        analysis,
      });
    } catch (error) {
      setUploadState({
        isUploading: false,
        error: error instanceof Error ? error.message : 'Analysis failed',
        file,
        analysis: null,
      });
    }
  };

  const handleReset = () => {
    setUploadState({
      isUploading: false,
      error: null,
      file: null,
      analysis: null,
    });
    setStagedEdits([]);
    setOriginalText('');
    setModifiedText(null);
    setShowEditModal(false);
  };

  const handleStageEdit = (edit: StagedEdit) => {
    setStagedEdits((prev) => {
      // Replace if same risk was already staged
      const exists = prev.find((e) => e.riskId === edit.riskId);
      if (exists) return prev.map((e) => (e.riskId === edit.riskId ? edit : e));
      return [...prev, edit];
    });
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-title">
            <FileText style={{ height: '32px', width: '32px', color: '#2563eb' }} />
            <h1>Contract Risk Analyzer</h1>
          </div>
          {uploadState.file && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {modifiedText && (
                <span className="modified-badge">✓ Document modified</span>
              )}
              <button
                onClick={handleReset}
                className="header-button"
              >
                Analyze New Contract
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="main-content">
        {!uploadState.file ? (
          /* Upload State */
          <div className="upload-section">
            <div className="upload-hero">
              <BarChart3 style={{ height: '64px', width: '64px', color: '#2563eb', margin: '0 auto 16px' }} />
              <h2>AI-Powered Contract Analysis</h2>
              <p>
                Upload your PDF contract and get instant risk assessment with detailed insights
                and recommendations from our advanced AI system.
              </p>
            </div>
            
            <FileUpload
              onFileSelect={handleFileSelect}
              isUploading={uploadState.isUploading}
              error={uploadState.error}
            />
          </div>
        ) : (
          /* Analysis State */
          <div className="analysis-layout">
            {/* PDF Viewer */}
            <div className="analysis-section">
              <h2 className="section-header">
                <FileText style={{ height: '20px', width: '20px' }} />
                Document: {uploadState.file.name}
              </h2>
              <PDFViewer file={uploadState.file} />
            </div>

            {/* Analysis Results */}
            <div className="analysis-section">
              <h2 className="section-header">
                <BarChart3 style={{ height: '20px', width: '20px' }} />
                Risk Analysis
              </h2>
              
              {uploadState.isUploading && (
                <div className="loading-state">
                  <div>
                    <div className="loading-spinner" style={{ height: '48px', width: '48px', margin: '0 auto 16px' }}></div>
                    <h3>Analyzing Contract...</h3>
                    <p>This may take a few moments</p>
                  </div>
                </div>
              )}

              {uploadState.error && (
                <div className="error-state">
                  <h3>Analysis Failed</h3>
                  <p>{uploadState.error}</p>
                  <button
                    onClick={() => handleFileSelect(uploadState.file!)}
                    className="retry-button"
                  >
                    Retry Analysis
                  </button>
                </div>
              )}

              {uploadState.analysis && (
                <AnalysisResults
                  analysis={uploadState.analysis}
                  onStageEdit={handleStageEdit}
                />
              )}
            </div>
          </div>
        )}
      </main>

      {/* Floating edit toolbar – visible when at least one edit is staged */}
      {stagedEdits.length > 0 && (
        <div className="edit-toolbar">
          <span className="edit-toolbar-count">
            {stagedEdits.length} fix{stagedEdits.length !== 1 ? 'es' : ''} staged
          </span>
          <button
            className="edit-toolbar-btn"
            onClick={() => setShowEditModal(true)}
          >
            <Edit3 style={{ width: '16px', height: '16px' }} />
            Review &amp; Apply
          </button>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && (
        <EditModal
          originalText={originalText}
          stagedEdits={stagedEdits}
          onClose={() => setShowEditModal(false)}
          onApplySuccess={(text) => {
            setModifiedText(text);
            setStagedEdits([]);
          }}
        />
      )}
    </div>
  );
}

export default App;
