# TreeLLM Frontend Integration Guide

## 📋 Overview
This document describes the integration between the TreeLLM backend and the new React frontend.

## 🚀 Quick Start

### 1. Setup Frontend
```bash
cd /Users/kimminjun/Desktop/TreeLLM
chmod +x setup_frontend.sh
./setup_frontend.sh
```

### 2. Run Full Stack Application
```bash
chmod +x run_fullstack.sh
./run_fullstack.sh
```

Or run separately:

**Backend:**
```bash
cd /Users/kimminjun/Desktop/TreeLLM
python app.py
```

**Frontend:**
```bash
cd /Users/kimminjun/Desktop/TreeLLM/frontend
npm install  # First time only
npm run dev
```

## 🔧 Configuration

### Backend Configuration (.env)
```env
OPENAI_API_KEY=your-api-key-here
PORT=5001
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

### Frontend Configuration
Edit `/frontend/src/config/api.ts` to change API endpoints if needed.

## 📁 Project Structure

```
TreeLLM/
├── app.py                 # Flask backend server
├── Orchestrator.py        # Core TreeLLM engine
├── config.py             # Backend configuration
├── frontend/             # React frontend application
│   ├── src/
│   │   ├── components/   # UI components
│   │   │   ├── Header.tsx         # Enhanced header with presets
│   │   │   ├── AnalysisPanel.tsx  # Progress tracking
│   │   │   ├── FeedbackPanel.tsx  # AI chat interface
│   │   │   ├── FileSidebar.tsx    # File management
│   │   │   └── Viewer.tsx         # Document viewer
│   │   ├── pages/
│   │   │   └── EditorPage.tsx     # Main editor with TreeLLM integration
│   │   ├── services/
│   │   │   └── treeLLMService.ts  # API service layer
│   │   └── config/
│   │       └── api.ts             # API configuration
│   └── package.json
├── setup_frontend.sh     # Frontend setup script
└── run_fullstack.sh     # Full stack runner

```

## 🎯 Key Features

### 1. File Upload & Management
- Upload documents (PDF, TXT, DOCX, MD)
- Real-time text extraction
- File size validation (max 10MB)
- Session management

### 2. Analysis Pipeline
- **Presets**: Fast, Balanced, Precision, Research
- **Real-time Progress**: 7-stage pipeline tracking
- **Quality Metrics**: Score, tokens, cost estimation
- **Caching**: Intelligent result caching

### 3. AI Assistant
- Interactive chat interface
- Commands: `status`, `metrics`, `download`
- Context-aware responses
- Analysis insights

### 4. Visual Feedback
- Live server connection status
- Progress bars and stage indicators
- Quality score visualization
- Time estimates

## 🔌 API Integration

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload file for analysis |
| `/api/analyze` | POST | Start analysis with preset |
| `/api/progress/{id}` | GET | Get real-time progress |
| `/api/results/{id}` | GET | Fetch analysis results |
| `/api/metrics/{id}` | GET | Get quality metrics |
| `/api/presets` | GET | Available configurations |

### Analysis Flow

1. **Upload File** → Returns session ID
2. **Start Analysis** → Begins processing
3. **Poll Progress** → Track stages (2s intervals)
4. **Get Results** → Retrieve final output
5. **Download** → Export as JSON

## 🎨 UI Components

### Header Component
- Server connection indicator
- Preset selector dropdown
- Generate analysis button
- Download current file

### Analysis Panel
- 7-stage progress visualization
- Current stage details
- Time remaining estimate
- Quality score preview

### Feedback Panel
- Chat history display
- Message input with Enter support
- Command suggestions
- Status updates

## 📊 Analysis Presets

| Preset | Model | Time | Quality | Use Case |
|--------|-------|------|---------|----------|
| Fast | GPT-3.5 | 2-3 min | Draft | Quick review |
| Balanced | GPT-4 | 5-7 min | Good | Standard analysis |
| Precision | GPT-4 | 10-12 min | Excellent | Publication |
| Research | GPT-4 | 15-20 min | Best | Academic |

## 🛠️ Development

### Frontend Development
```bash
cd frontend
npm run dev  # Start dev server with hot reload
npm run build  # Build for production
npm run lint  # Run linter
```

### Backend Development
```bash
python app.py  # Run with Flask debug mode
```

## 🐛 Troubleshooting

### Server Not Connected
1. Check if backend is running on port 5001
2. Verify CORS settings in app.py
3. Check browser console for errors

### Analysis Fails
1. Verify OpenAI API key in .env
2. Check file size < 10MB
3. Ensure valid file format

### Progress Not Updating
1. Check network tab for API calls
2. Verify session ID is correct
3. Check backend logs for errors

## 📝 Notes

- The frontend automatically detects server connection
- Analysis results are cached for performance
- Multiple files can be managed simultaneously
- Each file gets a unique session ID
- Progress polling stops automatically on completion

## 🔄 Updates Made

1. **API Service Layer**: Created `treeLLMService.ts` for all backend communication
2. **Progress Tracking**: Real-time 7-stage pipeline visualization
3. **Preset Selection**: Dropdown for quality/speed tradeoffs
4. **Server Status**: Live connection indicator
5. **Enhanced Chat**: Command support and context awareness
6. **Analysis Panel**: Beautiful progress overlay
7. **Error Handling**: Comprehensive error messages
8. **File Metadata**: Display word count, tokens, file size

## 🎉 Success!

The TreeLLM frontend is now fully integrated with the backend API. The application provides:

- ✅ Seamless file upload and management
- ✅ Real-time analysis progress tracking
- ✅ Interactive AI assistant
- ✅ Quality metrics and insights
- ✅ Multiple analysis presets
- ✅ Download results as JSON

Enjoy using TreeLLM with its new enhanced frontend!