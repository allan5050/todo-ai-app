# Todo AI App

A well-structured Todo/Task-List application with natural language task creation powered by LLM (Claude API).

## 🌟 Features

### Core Features
- ✅ Add, edit, delete, and mark tasks as done
- 💾 SQLite persistence (no authentication required)
- 🎯 Clean architecture with separation of concerns
- 🔧 Comprehensive error handling and logging

### AI Feature: Natural Language Task Creation
- 🤖 Convert natural language to structured tasks (e.g., "remind me to submit taxes next Monday at noon")
- 📅 Intelligent date/time parsing
- 🏷️ Priority extraction from natural language
- 🔄 Graceful fallback to rule-based parser when LLM is unavailable

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Frontend**: React 18, TypeScript
- **Database**: SQLite
- **LLM**: Anthropic Claude API (with fallback parser)
- **Styling**: Tailwind CSS
- **Testing**: Pytest (backend)
- **Containerization**: Docker & Docker Compose

## 📁 Project Structure

```
todo-ai-app/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/    # API route definitions
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access layer
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # Database setup
│   │   └── main.py          # FastAPI application
│   └── tests/               # Unit tests
├── frontend/
│   └── src/
│       ├── components/      # React components
│       ├── services/        # API service layer
│       └── types/          # TypeScript type definitions
└── docker-compose.yml      # Container orchestration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn
- Docker & Docker Compose (optional)

### Option 1: One-Command Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd todo-ai-app

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Add your Anthropic API key to backend/.env (optional - app works without it)
# ANTHROPIC_API_KEY=your-api-key-here

# Start everything with Docker Compose
docker-compose up
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your Anthropic API key (optional)

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Run the frontend
npm start
```

### Option 3: Using Make

```bash
# Install all dependencies
make install

# Run both frontend and backend (requires two terminals)
make run

# Or run separately:
make run-backend  # In terminal 1
make run-frontend # In terminal 2
```

## 🧪 Running Tests

```bash
# Run backend tests
make test-backend

# Or manually:
cd backend
pytest -v
```

## 🏗️ Architecture & Design Decisions

### Backend Architecture
- **Clean Architecture**: Separation of concerns with distinct layers (API, Service, Repository)
- **Dependency Injection**: Using FastAPI's dependency system for loose coupling
- **Environment Configuration**: All settings managed through environment variables
- **Error Handling**: Comprehensive error handling with proper logging at each layer
- **Type Safety**: Full type hints throughout the codebase

### LLM Integration
- **Prompt Engineering**: Structured prompts for consistent task parsing
- **Graceful Fallback**: Rule-based parser when LLM is unavailable
- **Error Recovery**: Automatic fallback on API failures
- **Cost Optimization**: Using Claude Haiku model for efficiency

### Frontend Architecture
- **Component-Based**: Reusable React components with TypeScript
- **Service Layer**: Centralized API communication with interceptors
- **Type Safety**: Full TypeScript coverage with defined interfaces
- **User Experience**: Real-time feedback and loading states

## 🔑 Key Design Choices

1. **SQLite Database**: Chosen for simplicity and portability, perfect for a demo application
2. **No Authentication**: Simplified scope as per requirements
3. **Fallback Parser**: Ensures the app works without API keys, demonstrating resilience
4. **Clean Commit History**: Structured development process shown through commits
5. **Docker Support**: Easy deployment and consistent environments

## 🛡️ Error Handling & Fallbacks

- **LLM Unavailable**: Automatically falls back to rule-based parser
- **API Errors**: Graceful error messages with user-friendly feedback
- **Database Errors**: Proper rollback and error logging
- **Network Issues**: Retry logic and timeout handling

## 📝 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Key Endpoints:
- `POST /api/v1/tasks/parse` - Create task from natural language
- `GET /api/v1/tasks` - Get all tasks
- `POST /api/v1/tasks` - Create task manually
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

## 🔄 Development Workflow

1. Backend changes are auto-reloaded with `--reload` flag
2. Frontend changes trigger hot module replacement
3. Use the Makefile for common operations
4. Check logs for debugging (comprehensive logging implemented)

## 🚦 Health Check

The application includes a health check endpoint that reports:
- Overall application status
- LLM service availability

Access at: http://localhost:8000/health
