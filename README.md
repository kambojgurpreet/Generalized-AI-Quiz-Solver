# AI Quiz Solver

A Chrome extension with AI-powered BE that detects Multiple Choice Questions (MCQs) on web pages and provides answers using advanced AI models with consensus-based validation.

## Features

- **🔍 MCQ Detection**: Automatically detects MCQs from any webpage
- **🤖 AI-Powered Answers**: Uses ChatGPT 4.1 and other AI models to solve questions
- **🎯 Multi-Model Consensus**: Option to use multiple AI models for higher accuracy
- **💡 Smart Highlighting**: Highlights correct answers directly on the webpage
- **📊 Detailed Reasoning**: Shows AI reasoning for each answer
- ** Google Search Integration**: Quick search for questions when needed

## Architecture

### Frontend (Chrome Extension)
- **React-based UI** with two main pages:
  1. Main popup with "Detect MCQs" button and Single/Multi model toggle
  2. Results page showing questions, answers, and AI reasoning
- **Content Script** for webpage interaction and answer highlighting
- **Background Script** for extension lifecycle management

### Backend (FastAPI)
- **FastAPI server** with async processing
- **Multiple AI model integration** (GPT-4.1, Gemini 2.5 Pro)
- **RESTful API** for extension communication

## Project Structure

```
.
├── UI/          # React-based Chrome extension
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Main pages (MainPage, ResultsPage)
│   │   ├── styles/           # CSS styles
│   │   ├── utils/            # Utility functions
│   │   ├── popup.js          # Extension entry point
│   │   ├── content.js        # Content script
│   │   └── background.js     # Background script
│   ├── public/               # Static assets
│   ├── manifest.json         # Extension manifest
│   ├── package.json          # Dependencies
│   └── webpack.config.js     # Build configuration
│
├── BE/                  # FastAPI BE server
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── models/           # Pydantic models
│   │   └── services/         # Business logic
│   │       └── ai_service.py     # AI model integration
│   ├── main.py               # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variables template
│
└── README.md                 # This file
```

## Setup Instructions

### Prerequisites

- Node.js 18+ and Python 3.8+
- OpenAI API key

### Backend Setup

1. **Navigate to BE directory:**
   ```bash
   cd BE
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   ```bash
   copy .env.example .env  # On Windows
   # cp .env.example .env  # On macOS/Linux
   ```
   
   Edit `.env` file and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the BE server:**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Chrome Extension Setup

1. **Navigate to extension directory:**
   ```bash
   cd UI
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Build the extension:**
   ```bash
   npm run build
   ```

4. **Load extension in Chrome:**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `UI/dist` folder

## Usage

1. **Start the BE server**
2. **Load the Chrome extension** in your browser
3. **Navigate to a webpage** with MCQ questions
4. **Click the extension icon** to open the popup
5. **Choose processing mode:**
   - **Single Model**: Fast processing with GPT-4.1
   - **Multi Model**: Consensus-based processing with multiple AI models
6. **Click "Detect MCQs"** to analyze the page
7. **View results** with answers, reasoning, and consensus information
8. **Highlight answers** on the webpage or search on Google

## API Endpoints

### POST `/api/detect-mcqs`
Detect and solve MCQs from webpage content.

**Request:**
```json
{
  "content": "webpage text content",
  "layout": {"html": "...", "title": "...", "url": "..."},
  "url": "https://example.com/quiz",
  "useMultiModel": false
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "What is the capital of France?",
      "options": ["London", "Berlin", "Paris", "Madrid"],
      "correct_option": 2,
      "confidence": 95,
      "reasoning": "Paris is the capital and largest city of France...",
      "model_responses": [...]
    }
  ],
  "processing_mode": "single",
  "consensus": [true],
  "total_questions": 1,
  "cached": false
}
```

### POST `/api/answer-question`
Answer a single MCQ question.

### GET `/api/health`
Health check endpoint.

### GET `/api/models`
Get available AI models.

## Features in Detail

### Single Model Mode
- Uses GPT-4.1 for quick and accurate answers
- Provides confidence scores and detailed reasoning
- Ideal for simple MCQs and fast processing

### Multi Model Mode
- Processes questions through multiple AI models
- Achieves consensus when models agree
- Shows individual model responses and reasoning
- Higher accuracy through model agreement validation

### Answer Highlighting
- Automatically highlights correct answers on the webpage
- Uses visual indicators (green background, border, animation)
- Scrolls to highlighted answers for better visibility

## Development

### Extension Development
```bash
cd UI
npm run dev  # Watch mode for development
```

### Backend Development
```bash
cd BE
python main.py  # Run with auto-reload in debug mode
```

### Testing
- Test the extension on various quiz websites
- Verify API responses with tools like Postman

## Configuration

### Environment Variables

**Backend (.env):**
```
OPENAI_API_KEY=your_openai_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Chrome Extension Configuration
- Modify `manifest.json` for permissions and settings
- Update API endpoint in the React components if needed
- Customize styling in `src/styles/popup.css`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please ensure you have proper API keys and comply with all service terms of use.

## Troubleshooting

### Common Issues

1. **Extension not loading:**
   - Check if the build completed successfully
   - Verify manifest.json syntax
   - Check Chrome extension developer console

2. **API connection failed:**
   - Ensure BE server is running on port 8000
   - Check CORS configuration
   - Verify network connectivity

3. **AI model errors:**
   - Verify OpenAI API key is valid
   - Check API quota and rate limits
   - Monitor API response status codes

### Logs and Debugging

- **Extension logs**: Check Chrome DevTools console
- **Backend logs**: Check terminal output where server is running
- **API logs**: Monitor FastAPI automatic request logging

## Future Enhancements

- Support for additional AI models (Claude, Grok, etc.)
- Advanced quiz format detection (fill-in-the-blank, images based questions, mathematical questions)
- User authentication and answer history
- Export functionality for quiz results
- Mobile app version
- Integration with learning management systems (LMS)
