import { useState } from 'react';
import { FileUpload } from './components/FileUpload';
import { PDFViewer } from './components/PDFViewer';
import { AnalysisResults } from './components/AnalysisResults';
import { contractAnalysisAPI } from './services/api';
import type { UploadState } from './types';
import { FileText, BarChart3 } from 'lucide-react';
import './App.css';

function App() {
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    error: null,
    file: null,
    analysis: null,
  });

  const handleFileSelect = async (file: File) => {
    setUploadState({
      isUploading: true,
      error: null,
      file,
      analysis: null,
    });

    try {
      const analysis = await contractAnalysisAPI.analyzeContract(file);
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
            <button
              onClick={handleReset}
              className="header-button"
            >
              Analyze New Contract
            </button>
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
                <AnalysisResults analysis={uploadState.analysis} />
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
