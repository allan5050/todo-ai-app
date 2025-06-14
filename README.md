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

The recommended way to run tests is within a virtual environment.

### For Windows (PowerShell)
```powershell
# From the project root, navigate to the backend directory
cd backend

# Create and activate a virtual environment if you haven't already
python -m venv venv
.\\venv\\Scripts\\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v
```

### For macOS / Linux (Bash)
```bash
# From the project root, navigate to the backend directory
cd backend

# Create and activate a virtual environment if you haven't already
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v

# Alternatively, you can use the Makefile shortcut from the root directory
make test-backend
```

## 🏗️ Architectural Justifications & Trade-offs

This section highlights the key technical decisions made during development, the reasons behind them, and the trade-offs considered.

### Backend: Clean Architecture (API → Service → Repository)
- **Decision**: The backend is structured into three distinct layers: an API layer for handling HTTP requests, a Service layer for business logic, and a Repository layer for data access.
- **Justification**: This separation of concerns makes the codebase highly modular, easier to test, and simpler to maintain. For example, the business logic in `TaskService` can be tested without needing a real database by simply mocking the `TaskRepository`. It also allows for a different database or ORM to be swapped in with minimal changes to the business logic.
- **Trade-off**: For a very small, simple CRUD application, this three-layer architecture introduces more files and a little more boilerplate than a monolithic approach. However, this trade-off is well worth it for any project that is expected to grow or be maintained over time.

### LLM: Primary AI Parser with Rule-Based Fallback
- **Decision**: The core AI feature uses the Anthropic Claude API for flexible parsing but includes a complete, rule-based parser as a fallback. The system automatically switches to the fallback if the API key is missing or if the API call fails.
- **Justification**: This dual-parser approach provides maximum resilience and a superior developer/user experience. The app is fully functional offline or without API credentials, satisfying a key project tip. The LLM provides a "wow" factor and handles complex queries, while the fallback guarantees core functionality is never broken.
- **Trade-off**: The primary trade-off is the development overhead of building and maintaining two separate parsing logics. The rule-based parser is also inherently less flexible than the LLM and can only handle patterns it has been explicitly programmed to recognize.

### Frontend: Singleton API Service
- **Decision**: All API communication in the React application is handled through a single, instantiated `ApiService` class (a singleton pattern).
- **Justification**: This centralizes all API logic, including base URL configuration, request/response interceptors for logging, and error handling. Any change to authentication or error reporting only needs to be made in one place. It's also trivial to mock for testing purposes.
- **Trade-off**: In a massive application with needs for multiple, different API configurations (e.g., connecting to different domains with different headers), this pattern could be too restrictive. In such a case, a factory function that creates configured Axios instances might be more appropriate. For this project's scope, the singleton is the cleanest solution.

### Database: SQLite in a Docker Named Volume
- **Decision**: The application uses a simple SQLite database file, which is stored in a Docker named volume (`backend_data`) separate from the application's source code.
- **Justification**: SQLite was chosen for its simplicity and zero-configuration setup, making the project easy for anyone to run. Storing it in a named volume is a critical decision for stability in a Dockerized development environment, as it prevents file-locking issues that can occur when a database file is on a host-mounted volume that is also being watched by a hot-reloader.
- **Trade-off**: SQLite is not suitable for high-concurrency, production-scale applications. A production deployment would necessitate a switch to a more robust client-server database like PostgreSQL, but for this exercise, SQLite is the ideal choice.

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
