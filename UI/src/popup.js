import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './components/App';
import ErrorBoundary from './components/ErrorBoundary';
import './styles/popup.css';

console.log('🚀 AI Quiz Solver popup starting...');

try {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  );
  console.log('✅ React app mounted successfully');
} catch (error) {
  console.error('❌ Failed to mount React app:', error);
}