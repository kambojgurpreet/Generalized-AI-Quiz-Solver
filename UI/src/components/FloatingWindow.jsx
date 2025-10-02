import React from 'react';

const FloatingWindow = ({ children, title = "AI Quiz Solver" }) => {
  const handleClose = () => {
    console.log('🗂️ Close button clicked in FloatingWindow');
    
    // For Chrome extension popup, simply close the window
    try {
      if (typeof chrome !== 'undefined' && chrome.windows) {
        // If running in popup window context
        console.log('🔄 Attempting to close via window.close()');
        window.close();
      } else if (window.close) {
        // Fallback for regular window close
        console.log('🔄 Fallback: closing via window.close()');
        window.close();
      } else {
        // Last resort - hide the popup by removing focus
        console.log('🔄 Last resort: blurring window');
        if (window.blur) {
          window.blur();
        }
      }
    } catch (error) {
      console.error('❌ Error closing window:', error);
      // Additional fallback - try to trigger a close event
      if (window.parent && window.parent !== window) {
        window.parent.postMessage({ action: 'closePopup' }, '*');
      }
    }
  };

  return (
    <div className="floating-window">
      <div className="floating-title-bar">
        <span className="floating-title-text">{title}</span>
        <button 
          className="floating-close-button close-button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            handleClose();
          }}
          onMouseDown={(e) => {
            e.stopPropagation();
          }}
          title="Close"
          type="button"
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