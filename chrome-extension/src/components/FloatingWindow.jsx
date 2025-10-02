import React from 'react';

const FloatingWindow = ({ children, title = "AI Quiz Solver" }) => {
  const handleClose = () => {
    if (chrome?.runtime?.sendMessage) {
      chrome.runtime.sendMessage({ action: 'closeWindow' });
    } else {
      window.close();
    }
  };

  return (
    <div className="floating-window">
      <div className="floating-title-bar">
        <span className="floating-title-text">{title}</span>
        <button 
          className="floating-close-button close-button"
          onClick={handleClose}
          title="Close"
        >
          ×
        </button>
      </div>
      
      <div className="floating-content">
        {children}
      </div>
    </div>
  );
};

export default FloatingWindow;