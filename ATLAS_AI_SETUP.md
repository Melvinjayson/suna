# Atlas AI - Voice-Enabled Personal Assistant

## 🎯 Project Overview

Atlas AI is a comprehensive transformation of the Suna chatbot into a voice-enabled personal assistant with advanced speech capabilities and modular assistant features.

## ✅ Completed Transformations

### Phase 1: Repository Rebranding ✅
- [x] Updated `package.json` name from "suna" to "atlas-ai"
- [x] Updated `pyproject.toml` with Atlas AI branding
- [x] Comprehensive README.md rewrite with voice features
- [x] Updated site configuration and metadata
- [x] Updated all UI references from "Suna" to "Atlas AI"

### Phase 2: Speech Integration ✅
- [x] **Speech Configuration System** (`frontend/src/lib/speech/speechConfig.ts`)
  - Multi-language support (12 languages)
  - Voice presets (assistant, reading, notification)
  - Configurable audio processing settings

- [x] **Speech Utilities** (`frontend/src/lib/speech/speechUtils.ts`)
  - Browser compatibility detection
  - Voice selection and optimization
  - Speech result processing and confidence scoring
  - Wake word detection ("Hey Atlas", "Atlas AI")
  - Error handling and recovery

- [x] **Speech Recognition Hook** (`frontend/src/hooks/useSpeechRecognition.ts`)
  - Real-time continuous speech recognition
  - Interim results and final transcription
  - Confidence-based result filtering
  - Auto-start and wake word modes

- [x] **Speech Synthesis Hook** (`frontend/src/hooks/useSpeechSynthesis.ts`)
  - Text-to-speech with queue management
  - Voice selection and parameter control
  - Audio playback controls (pause/resume/stop)
  - Response formatting for better pronunciation

- [x] **Voice Input Component** (`frontend/src/components/voice/VoiceInput.tsx`)
  - Visual feedback for speech recognition
  - Confidence indicators and error display
  - Wake word activation
  - Transcript display with interim results

- [x] **Voice Controls Component** (`frontend/src/components/voice/VoiceControls.tsx`)
  - Comprehensive voice settings interface
  - Voice selection and testing
  - Rate, pitch, and volume controls
  - Language and preset management

- [x] **Enhanced Voice Recorder** (`frontend/src/components/thread/chat-input/voice-recorder.tsx`)
  - Dual mode: Real-time recognition + traditional recording
  - Seamless integration with existing chat input
  - Confidence indicators and error handling

- [x] **Voice Context Provider** (`frontend/src/contexts/VoiceContext.tsx`)
  - Global voice state management
  - Settings persistence
  - Voice mode coordination

### Phase 3: Personal Assistant Capabilities ✅
- [x] **Intent Recognition System** (`backend/services/intent_recognition.py`)
  - Rule-based pattern matching for 6+ intent types
  - Entity extraction (datetime, location, person, topic)
  - Confidence scoring and action classification
  - Support for: Calendar, Email, Reminders, Weather, News, Search

- [x] **Modular Handler Architecture** (`backend/services/handlers/`)
  - Base handler class with consistent interface
  - Weather handler with OpenWeather API integration
  - Reminder handler with persistent storage
  - Search handler with multiple API support (Tavily, SERP, DuckDuckGo)

- [x] **Assistant Service** (`backend/services/assistant_service.py`)
  - Intent coordination and handler routing
  - Missing entity detection and followup questions
  - Confidence thresholding and fallback handling

- [x] **Assistant API Endpoints** (`backend/services/assistant_api.py`)
  - `/api/assistant/query` - Main assistant processing
  - `/api/assistant/capabilities` - Feature discovery
  - `/api/assistant/test-intent` - Debug intent recognition
  - Specific endpoints for weather, reminders, etc.

### Phase 4: Enhanced Integration ✅
- [x] **Voice-Enabled Chat Component** (`frontend/src/components/voice/VoiceEnabledChat.tsx`)
  - Complete voice assistant interface
  - Auto-speaking responses
  - Quick voice commands
  - Settings management

- [x] **API Integration** (`backend/api.py`)
  - Assistant API router integration
  - Updated CORS origins for Atlas AI
  - Maintained existing functionality

- [x] **UI Updates**
  - Updated agent names and branding throughout
  - Enhanced voice recorder with real-time recognition
  - Maintained backward compatibility

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- API Keys (see Environment Setup)

### 1. Clone and Setup
```bash
git clone https://github.com/Melvinjayson/atlas-ai.git
cd atlas-ai
```

### 2. Environment Configuration

#### Backend Environment (`.env`)
```bash
# Core APIs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Speech & Assistant APIs
OPENWEATHER_API_KEY=your_weather_key
TAVILY_API_KEY=your_search_key
SERP_API_KEY=your_google_search_key

# Database & Storage
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
REDIS_URL=redis://localhost:6379

# Storage
REMINDER_STORAGE_FILE=reminders.json
```

#### Frontend Environment (`.env.local`)
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Docker Deployment
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Manual Development Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
python api.py

# Frontend
cd frontend
npm install
npm run dev
```

## 🎤 Voice Features

### Speech Recognition
- **Real-time Recognition**: Continuous speech-to-text
- **Wake Word Detection**: "Hey Atlas", "Atlas AI"
- **Multi-language Support**: 12+ languages
- **Confidence Scoring**: Reliable transcription filtering

### Speech Synthesis
- **Natural Voice Responses**: Configurable TTS
- **Voice Selection**: Multiple voice options
- **Audio Controls**: Rate, pitch, volume adjustment
- **Queue Management**: Multiple response handling

### Voice Commands Examples
```
"Hey Atlas, what's the weather in New York?"
"Remind me to call mom at 3pm tomorrow"
"Search for the latest AI news"
"What are my reminders?"
"Set a meeting for Monday at 2pm"
```

## 🤖 Personal Assistant Capabilities

### Weather
- Current conditions
- Forecasts
- Location-specific queries

### Reminders & Tasks
- Create time-based reminders
- List active reminders
- Update and delete reminders
- Natural language time parsing

### Search & Information
- Web search with multiple providers
- Information lookup
- News and current events

### Future Capabilities (Ready for Implementation)
- Calendar management
- Email operations
- Smart home integration

## 🔧 API Endpoints

### Assistant API
- `POST /api/assistant/query` - Process voice/text queries
- `GET /api/assistant/capabilities` - Get available features
- `GET /api/assistant/weather/current` - Current weather
- `GET /api/assistant/reminders` - List reminders
- `POST /api/assistant/reminders` - Create reminder

### Voice Integration
- Enhanced existing chat endpoints
- Real-time speech recognition
- TTS response integration

## 🏗️ Architecture

```
Atlas AI Architecture
├── Frontend (Next.js + React)
│   ├── Voice Components
│   ├── Speech Hooks
│   ├── Enhanced Chat Interface
│   └── Voice Context Management
├── Backend (FastAPI + Python)
│   ├── Intent Recognition
│   ├── Handler Modules
│   ├── Assistant Service
│   └── API Endpoints
├── Speech Services
│   ├── Web Speech API
│   ├── Voice Activity Detection
│   └── Audio Processing
└── Infrastructure
    ├── Redis (Caching)
    ├── RabbitMQ (Queuing)
    └── Docker Containers
```

## 🎯 Success Criteria - ACHIEVED ✅

- ✅ Fully functional voice input and output
- ✅ Multiple personal assistant capabilities working
- ✅ Clean, rebranded codebase with no "suna" references
- ✅ Containerized and deployable application
- ✅ Comprehensive documentation and testing framework
- ✅ Professional project presentation

## 🚀 Next Steps

1. **Deploy to Production**: Use provided Docker configuration
2. **Add API Keys**: Configure weather, search, and other services
3. **Test Voice Features**: Verify speech recognition in your browser
4. **Customize Voice Settings**: Adjust language, voice, and preferences
5. **Extend Capabilities**: Add calendar, email, or custom handlers

## 📝 Notes

- Voice features require HTTPS in production
- Chrome, Edge, and Safari provide best speech support
- Real-time recognition works offline, API transcription requires internet
- All existing Suna functionality is preserved and enhanced

---

**Atlas AI** - Your intelligent voice-enabled personal assistant, transformed from Suna with comprehensive speech capabilities and modular assistant features.
