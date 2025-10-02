import React, { useState } from 'react';

const MainPage = ({ onDetectMCQs, loading }) => {
  const [useMultiModel, setUseMultiModel] = useState(true);

  const handleDetect = () => {
    onDetectMCQs(useMultiModel);
  };

  return (
    <div className="main-page">
      <div className="header">
        <h2>AI Quiz Solver</h2>
        <p>Detect and solve MCQs with AI assistance</p>
      </div>

      <div className="content">
        <div className="model-toggle">
          <label className="toggle-label">
            <span>Single Model</span>
            <div className="toggle-switch">
              <input
                type="checkbox"
                checked={useMultiModel}
                onChange={(e) => setUseMultiModel(e.target.checked)}
                disabled={loading}
              />
              <span className="slider"></span>
            </div>
            <span>Multi Model</span>
          </label>
        </div>

        <div className="model-info">
          {useMultiModel ? (
            <div className="info-card multi-model">
              <h4>Multi Model Mode</h4>
              <p>Questions will be processed by multiple AI models for consensus-based answers</p>
              <ul>
                <li>Higher accuracy through consensus</li>
                <li>Confidence indicators</li>
                <li>Model reasoning comparison</li>
              </ul>
            </div>
          ) : (
            <div className="info-card single-model">
              <h4>Single Model Mode</h4>
              <p>Questions will be processed by ChatGPT 4.1 for quick answers</p>
              <ul>
                <li>Fast processing</li>
                <li>Single model reasoning</li>
                <li>Efficient for simple MCQs</li>
              </ul>
            </div>
          )}
        </div>

        <button 
          className="detect-button"
          onClick={handleDetect}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Detecting MCQs...
            </>
          ) : (
            'Detect MCQs'
          )}
        </button>
      </div>

      <div className="footer">
        <p>Make sure you're on a page with MCQ questions</p>
      </div>
    </div>
  );
};

export default MainPage;