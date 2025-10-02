// Chrome Extension Service Worker for AI Quiz Solver
console.log('🚀 AI Quiz Solver background script loaded');

// Handle extension icon click
chrome.action.onClicked.addListener(async (tab) => {
  console.log('🎯 Extension icon clicked, tab:', tab.id);
  await injectOverlay(tab);
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('📨 Received message:', request.action);
  
  if (request.action === 'detectMCQs') {
    handleDetectMCQs(request, sendResponse);
    return true; // Keep message channel open for async response
  }
});

async function injectOverlay(tab) {
  try {
    console.log('🚀 Attempting to inject overlay into tab:', tab.id);
    
    // Check if we can inject into this tab
    if (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://') || tab.url.startsWith('moz-extension://')) {
      console.log('❌ Cannot inject into browser pages:', tab.url);
      return;
    }

    console.log('✅ Injecting overlay script...');
    
    // Inject the overlay popup using function reference (most reliable in MV3)
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: createOverlayPopup
    });
    
    console.log('✅ Overlay script injected successfully');
    
  } catch (error) {
    console.error('❌ Error injecting overlay:', error);
    
    // Fallback: Simple test to verify injection works
    try {
      console.log('🔄 Trying simple test injection...');
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          console.log('🧪 Simple test injection successful');
          const testDiv = document.createElement('div');
          testDiv.innerHTML = '<div style="position: fixed; top: 10px; right: 10px; background: red; color: white; padding: 10px; z-index: 999999;">Extension Working!</div>';
          document.body.appendChild(testDiv);
        }
      });
      console.log('✅ Simple test injection successful');
    } catch (fallbackError) {
      console.error('❌ All injection methods failed:', fallbackError);
    }
  }
}

// Function to be injected - must be defined separately for MV3
function createOverlayPopup() {
  console.log('🎨 createOverlayPopup function called');
  
  const OVERLAY_ID = 'ai-quiz-solver-overlay';
  
  // Check if overlay already exists
  let existingOverlay = document.getElementById(OVERLAY_ID);
  if (existingOverlay) {
    console.log('🔄 Overlay already exists, toggling...');
    if (existingOverlay.style.display === 'none') {
      existingOverlay.style.display = 'block';
    } else {
      existingOverlay.remove();
    }
    return;
  }

  console.log('🆕 Creating new overlay...');

  // Create overlay container
  const overlay = document.createElement('div');
  overlay.id = OVERLAY_ID;
  
  // Add complete overlay HTML
  overlay.innerHTML = `
    <div id="ai-quiz-overlay-container">
      <div id="ai-quiz-title-bar">
        <span>AI Quiz Solver</span>
        <button id="ai-quiz-close-btn">×</button>
      </div>
      
      <div id="ai-quiz-content">
        <div class="quiz-header">
          <h2>AI Quiz Solver</h2>
          <p>Detect and solve MCQs with AI assistance</p>
        </div>
        
        <div class="model-toggle">
          <div class="toggle-label">
            <span>Single Model</span>
            <label class="toggle-switch">
              <input type="checkbox" id="multi-model-toggle">
              <span class="slider"></span>
            </label>
            <span>Multi Model</span>
          </div>
        </div>
        
        <div class="info-card" id="mode-info">
          <h4>Single Model Mode</h4>
          <p>Questions will be processed by ChatGPT 4.1 for quick answers</p>
          <ul>
            <li>Fast processing</li>
            <li>Single model reasoning</li>
            <li>Efficient for simple MCQs</li>
          </ul>
        </div>
        
        <button id="detect-mcqs-btn" class="detect-button">
          <span id="button-text">🔍 Detect MCQs</span>
        </button>
        
        <div class="footer">
          <p>Make sure you're on a page with MCQ questions</p>
        </div>
      </div>
      
      <div id="ai-quiz-results" style="display: none;">
        <div id="results-content"></div>
      </div>
    </div>
  `;

  // Add styles
  const styles = `
    #ai-quiz-solver-overlay {
      position: fixed !important;
      top: 50px !important;
      right: 30px !important;
      width: 380px !important;
      height: 500px !important;
      min-width: 300px !important;
      min-height: 350px !important;
      max-width: 600px !important;
      max-height: 90vh !important;
      background: white !important;
      border-radius: 10px !important;
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
      z-index: 2147483647 !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
      overflow: hidden !important;
      resize: both !important;
      border: 2px solid #e1e5e9 !important;
      transition: box-shadow 0.3s ease !important;
    }
    
    #ai-quiz-solver-overlay:hover {
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
    }
    
    #ai-quiz-overlay-container {
      display: flex !important;
      flex-direction: column !important;
      height: 100% !important;
    }
    
    #ai-quiz-title-bar {
      height: 40px !important;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      padding: 0 16px !important;
      color: white !important;
      font-size: 14px !important;
      font-weight: 600 !important;
      cursor: move !important;
      user-select: none !important;
      border-radius: 8px 8px 0 0 !important;
    }
    
    #ai-quiz-title-bar:active {
      cursor: grabbing !important;
    }
    
    #ai-quiz-close-btn {
      width: 24px !important;
      height: 24px !important;
      border-radius: 50% !important;
      background: rgba(255, 255, 255, 0.2) !important;
      border: none !important;
      color: white !important;
      cursor: pointer !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      font-size: 16px !important;
      font-weight: bold !important;
      transition: background 0.2s ease !important;
    }
    
    #ai-quiz-close-btn:hover {
      background: rgba(255, 255, 255, 0.3) !important;
      transform: scale(1.1) !important;
    }
    
    #ai-quiz-content {
      flex: 1 !important;
      padding: 16px !important;
      overflow-y: auto !important;
      background: #f8f9fa !important;
    }
    
    .quiz-header {
      text-align: center !important;
      margin-bottom: 16px !important;
      padding: 16px !important;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      color: white !important;
      border-radius: 8px !important;
    }
    
    .quiz-header h2 {
      margin: 0 0 4px 0 !important;
      font-size: 18px !important;
      font-weight: 600 !important;
    }
    
    .quiz-header p {
      margin: 0 !important;
      font-size: 13px !important;
      opacity: 0.9 !important;
    }
    
    .model-toggle {
      margin-bottom: 16px !important;
    }
    
    .toggle-label {
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      font-size: 12px !important;
      color: #666 !important;
    }
    
    .toggle-switch {
      position: relative !important;
      width: 48px !important;
      height: 24px !important;
      margin: 0 8px !important;
    }
    
    .toggle-switch input {
      opacity: 0 !important;
      width: 0 !important;
      height: 0 !important;
    }
    
    .slider {
      position: absolute !important;
      cursor: pointer !important;
      top: 0 !important;
      left: 0 !important;
      right: 0 !important;
      bottom: 0 !important;
      background-color: #ccc !important;
      transition: 0.4s !important;
      border-radius: 24px !important;
    }
    
    .slider:before {
      position: absolute !important;
      content: "" !important;
      height: 18px !important;
      width: 18px !important;
      left: 3px !important;
      bottom: 3px !important;
      background-color: white !important;
      transition: 0.4s !important;
      border-radius: 50% !important;
    }
    
    input:checked + .slider {
      background-color: #667eea !important;
    }
    
    input:checked + .slider:before {
      transform: translateX(24px) !important;
    }
    
    .info-card {
      background: white !important;
      border-radius: 8px !important;
      padding: 12px !important;
      margin-bottom: 16px !important;
      border-left: 4px solid #667eea !important;
    }
    
    .info-card h4 {
      margin: 0 0 8px 0 !important;
      font-size: 14px !important;
      color: #333 !important;
    }
    
    .info-card p {
      margin: 0 0 8px 0 !important;
      font-size: 12px !important;
      color: #666 !important;
    }
    
    .info-card ul {
      margin: 0 !important;
      padding-left: 16px !important;
      font-size: 11px !important;
      color: #666 !important;
    }
    
    .info-card li {
      margin-bottom: 2px !important;
    }
    
    .detect-button {
      width: 100% !important;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      color: white !important;
      border: none !important;
      padding: 12px 16px !important;
      border-radius: 6px !important;
      font-size: 14px !important;
      font-weight: 600 !important;
      cursor: pointer !important;
      transition: all 0.3s ease !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 8px !important;
    }
    
    .detect-button:hover:not(:disabled) {
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    .detect-button:disabled {
      opacity: 0.7 !important;
      cursor: not-allowed !important;
    }
    
    .footer {
      text-align: center !important;
      margin-top: 16px !important;
    }
    
    .footer p {
      margin: 0 !important;
      font-size: 11px !important;
      color: #666 !important;
    }
    
    .spinner {
      width: 16px !important;
      height: 16px !important;
      border: 2px solid rgba(255, 255, 255, 0.3) !important;
      border-top: 2px solid white !important;
      border-radius: 50% !important;
      animation: spin 1s linear infinite !important;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;

  // Inject styles
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);

  // Append overlay to body
  document.body.appendChild(overlay);
  console.log('✅ Overlay appended to body');

  // Setup event listeners and draggable functionality
  setupOverlayFeatures();
  console.log('✅ Overlay setup complete');

  function setupOverlayFeatures() {
    console.log('🎧 Setting up overlay features...');
    
    // Close button
    const closeBtn = document.getElementById('ai-quiz-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        console.log('❌ Close button clicked');
        document.getElementById(OVERLAY_ID).remove();
      });
    }
    
    // Make draggable
    const titleBar = document.getElementById('ai-quiz-title-bar');
    const container = document.getElementById('ai-quiz-solver-overlay');
    
    if (titleBar && container) {
      let isDragging = false;
      let startX, startY, startLeft, startTop;

      titleBar.addEventListener('selectstart', (e) => e.preventDefault());
      
      titleBar.addEventListener('mousedown', (e) => {
        if (e.target.id === 'ai-quiz-close-btn' || e.target.closest('#ai-quiz-close-btn')) {
          return;
        }
        
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        
        const rect = container.getBoundingClientRect();
        startLeft = rect.left;
        startTop = rect.top;
        
        titleBar.style.cursor = 'grabbing';
        container.style.transform = 'scale(1.02)';
        
        e.preventDefault();
      });

      document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        e.preventDefault();
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        
        const newLeft = Math.max(0, Math.min(window.innerWidth - container.offsetWidth, startLeft + deltaX));
        const newTop = Math.max(0, Math.min(window.innerHeight - container.offsetHeight, startTop + deltaY));
        
        container.style.left = newLeft + 'px';
        container.style.top = newTop + 'px';
        container.style.right = 'auto';
        container.style.bottom = 'auto';
      });

      document.addEventListener('mouseup', () => {
        if (isDragging) {
          isDragging = false;
          titleBar.style.cursor = 'move';
          container.style.transform = 'scale(1)';
        }
      });
    }
    
    // Multi-model toggle
    const toggle = document.getElementById('multi-model-toggle');
    const infoCard = document.getElementById('mode-info');
    
    if (toggle && infoCard) {
      toggle.addEventListener('change', () => {
        console.log('🔄 Toggle changed:', toggle.checked);
        if (toggle.checked) {
          infoCard.innerHTML = `
            <h4>Multi Model Mode</h4>
            <p>Questions will be processed by multiple AI models for consensus</p>
            <ul>
              <li>Multiple AI perspectives</li>
              <li>Consensus-based answers</li>
              <li>Higher accuracy for complex questions</li>
            </ul>
          `;
          infoCard.style.borderLeftColor = '#28a745';
        } else {
          infoCard.innerHTML = `
            <h4>Single Model Mode</h4>
            <p>Questions will be processed by ChatGPT 4.1 for quick answers</p>
            <ul>
              <li>Fast processing</li>
              <li>Single model reasoning</li>
              <li>Efficient for simple MCQs</li>
            </ul>
          `;
          infoCard.style.borderLeftColor = '#667eea';
        }
      });
    }
    
    // Detect MCQs button
    const detectBtn = document.getElementById('detect-mcqs-btn');
    if (detectBtn) {
      detectBtn.addEventListener('click', async () => {
        console.log('🔘 Detect MCQs button clicked');
        const button = document.getElementById('detect-mcqs-btn');
        const buttonText = document.getElementById('button-text');
        const toggle = document.getElementById('multi-model-toggle');
        const useMultiModel = toggle?.checked || false;
        
        button.disabled = true;
        buttonText.innerHTML = '<span class="spinner"></span> Detecting MCQs...';
        
        try {
          const content = document.body.innerText;
          const layout = {
            html: document.documentElement.outerHTML,
            title: document.title,
            url: window.location.href
          };
          
          console.log('📤 Sending message to background script...');
          
          const response = await new Promise((resolve, reject) => {
            chrome.runtime.sendMessage({
              action: 'detectMCQs',
              content: content,
              layout: layout,
              url: window.location.href,
              useMultiModel: useMultiModel
            }, (response) => {
              console.log('📥 Received response from background:', response);
              if (chrome.runtime.lastError) {
                console.error('❌ Chrome runtime error:', chrome.runtime.lastError);
                reject(new Error(chrome.runtime.lastError.message));
              } else {
                resolve(response);
              }
            });
          });

          if (!response || !response.success) {
            throw new Error(response?.error || 'Failed to communicate with extension background');
          }

          console.log('✅ Showing results...');
          showResults(response.data);
          
        } catch (error) {
          console.error('❌ Error detecting MCQs:', error);
          alert(`Error detecting MCQs: ${error.message}. Please check the console for details.`);
        } finally {
          button.disabled = false;
          buttonText.innerHTML = '🔍 Detect MCQs';
        }
      });
    }
  }

  function showResults(data) {
    const content = document.getElementById('ai-quiz-content');
    const results = document.getElementById('ai-quiz-results');
    
    content.style.display = 'none';
    results.style.display = 'block';
    
    let resultsHTML = `
      <div style="padding: 16px; background: #f8f9fa; height: 100%; overflow-y: auto;">
        <div style="display: flex; align-items: center; margin-bottom: 16px;">
          <button id="back-btn" style="background: #667eea; border: none; color: white; padding: 6px 12px; border-radius: 4px; cursor: pointer; margin-right: 16px;">← Back</button>
          <h3 style="margin: 0; flex: 1;">Quiz Results</h3>
        </div>
        <div style="background: white; padding: 16px; border-radius: 8px;">
          <p>Results: ${JSON.stringify(data, null, 2)}</p>
        </div>
      </div>
    `;
    
    document.getElementById('results-content').innerHTML = resultsHTML;
    
    document.getElementById('back-btn').addEventListener('click', () => {
      content.style.display = 'block';
      results.style.display = 'none';
    });
  }
}

async function handleDetectMCQs(request, sendResponse) {
  try {
    console.log('🔍 Processing detectMCQs request');
    
    const backendUrl = 'http://localhost:8000';
    const endpoint = request.useMultiModel ? '/detect-multi-model' : '/detect';
    
    console.log('🌐 Making request to:', `${backendUrl}${endpoint}`);
    
    const response = await fetch(`${backendUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: request.content,
        layout: request.layout,
        url: request.url
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Backend response received:', data);
    
    sendResponse({
      success: true,
      data: data
    });
    
  } catch (error) {
    console.error('❌ Error in handleDetectMCQs:', error);
    sendResponse({
      success: false,
      error: error.message
    });
  }
}