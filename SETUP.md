# Restaurant AI - Complete Setup Guide

This guide will help someone on a different computer set up and run the Restaurant AI project from scratch.

## Prerequisites

### Required
- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))

### Optional (for AI features)
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop))
- **WSL2** (Windows only - [Setup Guide](https://learn.microsoft.com/en-us/windows/wsl/install))

## Quick Start (Template Mode - No AI)

If you just want to run the chatbot with fast template responses:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd restaurant-ai

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment file
cp .env.example .env

# 6. Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 7. Open browser
# Navigate to: http://localhost:8000/static/restaurant_chat.html
```

**Done!** The chatbot will work with instant template responses.

## Full Setup (AI Mode)

To enable the real AI powered by Phi-2 model:

### Step 1: Get the Project

```bash
git clone <your-repo-url>
cd restaurant-ai
```

### Step 2: Python Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Download AI Model

Download the Phi-2 model (1.7GB):

```bash
# Create models directory
mkdir -p models

# Download Phi-2 model
# Option A: Direct download
curl -L -o models/phi-2.Q4_K_M.gguf https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf

# Option B: Use huggingface-cli (if installed)
huggingface-cli download TheBloke/phi-2-GGUF phi-2.Q4_K_M.gguf --local-dir models
```

**Note**: The `.gitignore` excludes `.gguf` files, so models need to be downloaded separately.

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file and set:
USE_LOCAL_AI=true
LLAMA_SERVER_URL=http://localhost:8080
```

### Step 5: Start AI Server

Choose your platform:

#### Windows with WSL2 (Recommended)

```bash
# 1. Copy model to WSL2 filesystem (faster access)
wsl mkdir -p ~/llama-models
wsl cp models/phi-2.Q4_K_M.gguf ~/llama-models/

# 2. Start llama-server in Docker via WSL2
wsl docker run -d \
  --name llama-server \
  -p 8080:8080 \
  -v ~/llama-models:/models \
  ghcr.io/ggerganov/llama.cpp:server \
  -m /models/phi-2.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080

# 3. Check it's running
wsl docker logs llama-server
```

#### macOS/Linux with Docker

```bash
# 1. Start llama-server
docker run -d \
  --name llama-server \
  -p 8080:8080 \
  -v $(pwd)/models:/models \
  ghcr.io/ggerganov/llama.cpp:server \
  -m /models/phi-2.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080

# 2. Check it's running
docker logs llama-server
```

#### Without Docker (Native Python)

```bash
# Install llama-cpp-python (requires C++ compiler)
pip install llama-cpp-python

# Start Python server
python -m llama_cpp.server \
  --model models/phi-2.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080
```

### Step 6: Start Restaurant AI

```bash
# Make sure you're in the restaurant-ai directory
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 7: Open Chat Interface

Open your browser to: **http://localhost:8000/static/restaurant_chat.html**

## Project Structure

```
restaurant-ai/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI endpoints
│   ├── config.py         # Configuration settings
│   ├── models.py         # Pydantic data models
│   ├── database.py       # SQLite database operations
│   ├── tobi_ai.py        # AI/template chatbot logic
│   └── menu_data.py      # Restaurant menu data
├── static/
│   └── restaurant_chat.html  # Chat interface
├── data/
│   └── orders.db         # SQLite database (auto-created)
├── logs/
│   └── app.log           # Application logs (auto-created)
├── models/               # AI models (download separately)
├── .env                  # Configuration (copy from .env.example)
├── .env.example          # Example configuration
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker image definition
└── docker-compose.yml   # Multi-container setup
```

## Configuration Options

Edit [.env](.env) to customize:

```bash
# Server
PORT=8000
HOST=0.0.0.0

# AI Mode
USE_LOCAL_AI=true              # false = templates (fast), true = AI (smart)
LLAMA_SERVER_URL=http://localhost:8080

# Restaurant
RESTAURANT_NAME=The Common House
MAGIC_PASSWORD=i'm on yelp     # VIP trigger phrase

# Database
DATABASE_URL=sqlite:///./data/orders.db
```

## Testing

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get menu
curl http://localhost:8000/menu

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "what burgers do you have?"}'
```

### Test AI Server

```bash
# Check if llama-server is running
curl http://localhost:8080/health

# Test direct inference
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, I am", "max_tokens": 10}'
```

## Troubleshooting

### Port Already in Use

```bash
# Windows: Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# macOS/Linux: Find and kill process
lsof -ti:8000 | xargs kill -9
```

### llama-server Not Starting

```bash
# Check Docker logs
docker logs llama-server

# Restart container
docker restart llama-server

# Remove and recreate
docker rm -f llama-server
# Then run the docker run command again
```

### AI Responses Showing "undefined"

1. **Hard refresh browser**: Ctrl+Shift+R (or Cmd+Shift+R)
2. **Check browser console**: F12 → Console tab for errors
3. **Verify llama-server**: `curl http://localhost:8080/health`
4. **Check restaurant-ai logs**: Look for error messages in terminal

### Slow AI Responses

- **First response**: 10-15 seconds (model loading)
- **Subsequent responses**: 2-5 seconds
- **To speed up**: Set `USE_LOCAL_AI=false` for instant template responses
- **Hardware note**: Phi-2 runs on CPU; GPU would be faster but requires NVIDIA GPU + CUDA setup

## API Documentation

When running in development mode, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Deployment

### Option 1: Docker Compose (Easiest)

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down
```

### Option 2: Traditional Hosting

1. **Set environment to production**:
   ```bash
   ENVIRONMENT=production
   DEBUG=False
   ```

2. **Use proper WSGI server**:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Set up reverse proxy** (nginx/Apache)

4. **Use proper database** (PostgreSQL instead of SQLite)

### Option 3: Cloud Platforms

**Heroku**:
```bash
heroku create restaurant-ai
git push heroku main
```

**AWS/GCP/Azure**:
- Use EC2/Compute Engine/VM
- Install Docker
- Run docker-compose

**Important**: AI mode requires ~2GB RAM. Use cloud instances with sufficient memory.

## Development

### Adding Menu Items

Edit [app/menu_data.py](app/menu_data.py):

```python
MENU_DATA = {
    "starters": [
        {
            "name": "Your New Dish",
            "description": "Description here",
            "price": 12.00
        }
    ]
}
```

### Customizing Tobi's Personality

Edit [app/tobi_ai.py](app/tobi_ai.py) - change the prompt in `get_ai_response()`:

```python
menu_context = f"""You are Tobi, a [YOUR PERSONALITY HERE]...
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## System Requirements

### Minimum (Template Mode)
- **RAM**: 512MB
- **CPU**: 1 core
- **Storage**: 100MB

### Recommended (AI Mode)
- **RAM**: 4GB (2GB for model + 2GB for system)
- **CPU**: 4+ cores
- **Storage**: 5GB (model + dependencies)

## Performance Comparison

| Feature | Template Mode | AI Mode |
|---------|--------------|---------|
| Response Time | <10ms | 2-10 seconds |
| Memory Usage | ~50MB | ~2GB |
| Natural Language | Limited | Excellent |
| Menu Awareness | Keyword matching | Full understanding |
| Setup Complexity | Easy | Moderate |
| Cost (Cloud) | $5-10/month | $20-50/month |

## Getting Help

1. **Check logs**: `logs/app.log`
2. **Read documentation**: [README.md](README.md), [README_AI_INTEGRATION.md](../README_AI_INTEGRATION.md)
3. **GitHub Issues**: Report problems on the repository

## Next Steps

After setup, you can:
- Customize the menu in `app/menu_data.py`
- Modify Tobi's personality in `app/tobi_ai.py`
- Add new endpoints in `app/main.py`
- Deploy to production
- Fine-tune the AI model on custom data

---

**Quick Links:**
- [Main README](README.md) - Project overview
- [AI Integration Guide](../README_AI_INTEGRATION.md) - Deep dive into AI features
- [Migration Guide](MIGRATION_GUIDE.md) - Upgrading from old version
