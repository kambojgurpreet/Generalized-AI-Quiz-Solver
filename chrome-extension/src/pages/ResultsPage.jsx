import React from 'react';

const ResultsPage = ({ results, onBack, onHighlightAnswer, onGoogleSearch }) => {
  if (!results) return null;

  const { questions, consensus, processing_mode } = results;

  return (
    <div className="results-page">
      <div className="header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        <h2>Quiz Results</h2>
        <div className="mode-indicator">
          {processing_mode === 'multi' ? 'Multi Model' : 'Single Model'}
        </div>
      </div>

      <div className="content">
        {questions.map((question, qIndex) => (
          <div key={qIndex} className="question-card">
            <div className="question-header">
              <h3>Question {qIndex + 1}</h3>
              {processing_mode === 'multi' && (
                <div className={`consensus-badge ${consensus[qIndex] ? 'consensus' : 'no-consensus'}`}>
                  {consensus[qIndex] ? 'Consensus' : 'No Consensus'}
                </div>
              )}
            </div>

            <div className="question-text">
              {question.question}
            </div>

            <div className="options">
              {question.options.map((option, oIndex) => (
                <div 
                  key={oIndex} 
                  className={`option ${question.correct_option === oIndex ? 'correct' : ''}`}
                >
                  <span className="option-label">{String.fromCharCode(65 + oIndex)}.</span>
                  <span className="option-text">{option}</span>
                  {question.correct_option === oIndex && (
                    <span className="correct-indicator">✓</span>
                  )}
                </div>
              ))}
            </div>

            <div className="actions">
              <button 
                className="highlight-button"
                onClick={() => onHighlightAnswer(qIndex, question.correct_option)}
              >
                Highlight Answer
              </button>
              <button 
                className="search-button"
                onClick={() => onGoogleSearch(question)}
              >
                Google Search
              </button>
            </div>

            {processing_mode === 'multi' ? (
              <div className="model-reasoning">
                <h4>Model Responses</h4>
                {question.model_responses.map((response, mIndex) => (
                  <div key={mIndex} className="model-response">
                    <div className="model-name">{response.model}</div>
                    <div className="model-answer">
                      Answer: {String.fromCharCode(65 + response.selected_option)}
                    </div>
                    <div className="model-confidence">
                      Confidence: {response.confidence}%
                    </div>
                    <div className="model-reasoning-text">
                      {response.reasoning}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="single-reasoning">
                <h4>AI Reasoning</h4>
                <div className="reasoning-text">
                  {question.reasoning}
                </div>
                <div className="confidence">
                  Confidence: {question.confidence}%
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {questions.length === 0 && (
        <div className="no-questions">
          <h3>No MCQs Detected</h3>
          <p>No multiple choice questions were found on this page.</p>
          <button onClick={onBack}>Try Another Page</button>
        </div>
      )}
    </div>
  );
};

export default ResultsPage;