import React, { useState } from 'react';
import MainPage from '../pages/MainPage';
import ResultsPage from '../pages/ResultsPage';
import FloatingWindow from './FloatingWindow';

const App = () => {
  const [currentPage, setCurrentPage] = useState('main');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  // Helper function to get active tab from normal browser windows (excluding popup)
  const getActiveTab = async () => {
    const windows = await chrome.windows.getAll({ populate: true, windowTypes: ['normal'] });
    
    let activeTab = null;
    // First, try to find the focused window's active tab
    for (const window of windows) {
      if (window.focused) {
        activeTab = window.tabs.find(tab => tab.active);
        if (activeTab) break;
      }
    }
    
    // Fallback: get any active tab from normal windows
    if (!activeTab) {
      for (const window of windows) {
        activeTab = window.tabs.find(tab => tab.active);
        if (activeTab) break;
      }
    }
    
    if (!activeTab) {
      throw new Error('No active tab found. Please make sure you have a web page open.');
    }
    
    return activeTab;
  };

  const handleDetectMCQs = async (useMultiModel) => {
    console.log('🔍 Starting MCQ detection...', { useMultiModel });
    setLoading(true);
    try {
      // Get the active tab from the most recently focused normal window
      const activeTab = await getActiveTab();
      console.log('📄 Active tab:', activeTab);
      
      // Inject content script and get page content
      const result = await chrome.scripting.executeScript({
        target: { tabId: activeTab.id },
        function: extractPageContent
      });

      const pageContent = result[0].result;
      console.log('📝 Extracted content length:', pageContent.content.length);
      
      // Send to backend API
      console.log('🚀 Sending request to backend...');
      const response = await fetch('http://localhost:8000/api/detect-mcqs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: pageContent.content,
          layout: pageContent.layout,
          url: activeTab.url,
          useMultiModel
        })
      });

      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Received data:', data);
      setResults(data);
      setCurrentPage('results');
    } catch (error) {
      console.error('❌ Error detecting MCQs:', error);
      alert(`Error detecting MCQs: ${error.message}. Please check the console for details.`);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setCurrentPage('main');
    setResults(null);
  };

  const handleHighlightAnswer = async (questionIndex, optionIndex) => {
    console.log('🎯 Highlighting answer:', { questionIndex, optionIndex });
    try {
      // Get the active tab from normal windows (excluding popup)
      const activeTab = await getActiveTab();
      
      await chrome.scripting.executeScript({
        target: { tabId: activeTab.id },
        function: highlightCorrectOption,
        args: [questionIndex, optionIndex]
      });
      console.log('✅ Answer highlighted successfully');
    } catch (error) {
      console.error('❌ Error highlighting answer:', error);
      alert(`Error highlighting answer: ${error.message}`);
    }
  };

  const handleGoogleSearch = (questionObj) => {
    console.log('🔍 Opening Google search for:', questionObj.question.substring(0, 50) + '...');
    
    // Create a comprehensive search query with question and options
    let searchQuery = questionObj.question;
    
    // Add options to the search query for better context
    if (questionObj.options && questionObj.options.length > 0) {
      const optionsText = questionObj.options.map((option, index) => 
        `${String.fromCharCode(65 + index)}) ${option}`
      ).join(' ');
      searchQuery += ` ${optionsText}`;
    }
    
    const encodedQuery = encodeURIComponent(searchQuery);
    const searchUrl = `https://www.google.com/search?q=${encodedQuery}`;
    console.log('🔍 Search URL:', searchUrl);
    chrome.tabs.create({ url: searchUrl });
  };

  return (
    <FloatingWindow title="AI Quiz Solver">
      {currentPage === 'main' ? (
        <MainPage 
          onDetectMCQs={handleDetectMCQs}
          loading={loading}
        />
      ) : (
        <ResultsPage 
          results={results}
          onBack={handleBack}
          onHighlightAnswer={handleHighlightAnswer}
          onGoogleSearch={handleGoogleSearch}
        />
      )}
    </FloatingWindow>
  );
};

// Function to be injected into the page
function extractPageContent() {
  const content = document.body.innerText;
  const layout = {
    html: document.documentElement.outerHTML,
    title: document.title,
    url: window.location.href
  };
  
  return { content, layout };
}

// Function to highlight correct option on the page
function highlightCorrectOption(questionIndex, optionIndex) {
  // This is a simplified implementation
  // In a real scenario, you'd need more sophisticated DOM traversal
  const style = document.createElement('style');
  style.innerHTML = `
    .ai-quiz-highlight {
      background-color: #90EE90 !important;
      border: 2px solid #32CD32 !important;
      box-shadow: 0 0 10px rgba(50, 205, 50, 0.5) !important;
    }
  `;
  document.head.appendChild(style);
  
  // Simple heuristic to find and highlight options
  // This would need to be more sophisticated based on actual quiz layouts
  const allElements = document.querySelectorAll('*');
  allElements.forEach(el => {
    if (el.textContent && el.textContent.includes('Option') || 
        el.textContent.match(/^[A-D][\.\)]/)) {
      if (el.textContent.includes(String.fromCharCode(65 + optionIndex))) {
        el.classList.add('ai-quiz-highlight');
      }
    }
  });
}

export default App;