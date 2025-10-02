// Content script that runs on all pages
console.log('🔧 AI Quiz Solver content script loaded on:', window.location.href);

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('📨 Content script received message:', request);
  
  if (request.action === 'extractContent') {
    try {
      const content = extractPageContent();
      console.log('📄 Extracted content:', { 
        contentLength: content.content.length,
        textNodesCount: content.layout.textNodes.length,
        formElementsCount: content.layout.formElements.length
      });
      sendResponse(content);
    } catch (error) {
      console.error('❌ Error extracting content:', error);
      sendResponse({ error: error.message });
    }
  }
  
  if (request.action === 'highlightAnswer') {
    try {
      highlightCorrectOption(request.questionIndex, request.optionIndex);
      console.log('✅ Answer highlighted successfully');
      sendResponse({ success: true });
    } catch (error) {
      console.error('❌ Error highlighting answer:', error);
      sendResponse({ error: error.message });
    }
  }
});

function extractPageContent() {
  console.log('🔍 Starting content extraction...');
  
  // Get all text content
  const content = document.body.innerText;
  console.log('📝 Text content length:', content.length);
  
  // Get structured HTML for layout analysis
  const layout = {
    html: document.documentElement.outerHTML,
    title: document.title,
    url: window.location.href,
    textNodes: getAllTextNodes(),
    formElements: getFormElements()
  };
  
  console.log('🏗️ Layout info:', {
    title: layout.title,
    url: layout.url,
    textNodesCount: layout.textNodes.length,
    formElementsCount: layout.formElements.length
  });
  
  return { content, layout };
}

function getAllTextNodes() {
  const textNodes = [];
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );
  
  let node;
  while (node = walker.nextNode()) {
    if (node.textContent.trim()) {
      textNodes.push({
        text: node.textContent.trim(),
        tagName: node.parentElement.tagName,
        className: node.parentElement.className,
        id: node.parentElement.id
      });
    }
  }
  
  return textNodes;
}

function getFormElements() {
  const formElements = [];
  const inputs = document.querySelectorAll('input[type="radio"], input[type="checkbox"], select, button');
  
  inputs.forEach((element, index) => {
    formElements.push({
      type: element.type || element.tagName.toLowerCase(),
      id: element.id,
      name: element.name,
      value: element.value,
      text: element.textContent || element.value,
      className: element.className,
      index: index
    });
  });
  
  return formElements;
}

function highlightCorrectOption(questionIndex, optionIndex) {
  // Remove existing highlights
  document.querySelectorAll('.ai-quiz-highlight').forEach(el => {
    el.classList.remove('ai-quiz-highlight');
  });
  
  // Add styles if not already present
  if (!document.getElementById('ai-quiz-styles')) {
    const style = document.createElement('style');
    style.id = 'ai-quiz-styles';
    style.innerHTML = `
      .ai-quiz-highlight {
        background-color: #90EE90 !important;
        border: 2px solid #32CD32 !important;
        box-shadow: 0 0 10px rgba(50, 205, 50, 0.5) !important;
        border-radius: 4px !important;
        padding: 4px !important;
        animation: pulse 2s infinite;
      }
      
      @keyframes pulse {
        0% {
          box-shadow: 0 0 10px rgba(50, 205, 50, 0.5);
        }
        50% {
          box-shadow: 0 0 20px rgba(50, 205, 50, 0.8);
        }
        100% {
          box-shadow: 0 0 10px rgba(50, 205, 50, 0.5);
        }
      }
    `;
    document.head.appendChild(style);
  }
  
  // Try to find and highlight the correct option
  // This is a heuristic approach - in practice, you'd need more sophisticated detection
  const optionLetters = ['A', 'B', 'C', 'D', 'E'];
  const targetLetter = optionLetters[optionIndex];
  
  // Look for radio buttons, checkboxes, or text patterns
  const radioButtons = document.querySelectorAll('input[type="radio"]');
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  const allElements = document.querySelectorAll('*');
  
  // Try radio buttons first
  if (radioButtons.length > 0) {
    const questionRadios = Array.from(radioButtons).filter((radio, index) => {
      return Math.floor(index / 4) === questionIndex; // Assuming 4 options per question
    });
    
    if (questionRadios[optionIndex]) {
      questionRadios[optionIndex].parentElement.classList.add('ai-quiz-highlight');
      questionRadios[optionIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
  }
  
  // Fall back to text pattern matching
  allElements.forEach(el => {
    const text = el.textContent?.trim();
    if (text && (
      text.startsWith(`${targetLetter}.`) ||
      text.startsWith(`${targetLetter})`) ||
      text.startsWith(`(${targetLetter})`) ||
      text.match(new RegExp(`^${targetLetter}\\s*[\\.):]`))
    )) {
      // Check if this is likely an option (not too long, reasonable parent structure)
      if (text.length < 200 && text.length > 2) {
        el.classList.add('ai-quiz-highlight');
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  });
}