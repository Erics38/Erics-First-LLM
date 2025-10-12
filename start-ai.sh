#!/bin/bash
# Start Restaurant AI in AI Mode (Smart, natural language)
# Requires: models/phi-2.Q4_K_M.gguf (1.7GB)

echo "🤖 Starting Restaurant AI (AI Mode)..."
echo "🧠 Natural language AI responses using Phi-2"
echo ""

# Check if model exists
if [ ! -f "models/phi-2.Q4_K_M.gguf" ]; then
    echo "❌ ERROR: Model file not found!"
    echo ""
    echo "Please download the Phi-2 model first:"
    echo "  mkdir -p models"
    echo "  curl -L -o models/phi-2.Q4_K_M.gguf https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
    echo ""
    exit 1
fi

# Stop any existing containers
docker-compose down 2>/dev/null

# Start with AI profile enabled
USE_LOCAL_AI=true docker-compose --profile ai up --build -d

echo ""
echo "✅ Restaurant AI is starting up!"
echo "⏳ AI model is loading (this takes 30-60 seconds)..."
echo ""
echo "🌐 Chat Interface: http://localhost:8000/static/restaurant_chat.html"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo "🤖 AI Server: http://localhost:8080"
echo ""
echo "📊 View logs:"
echo "  App:  docker-compose logs -f app"
echo "  AI:   docker-compose logs -f llama-server"
echo ""
echo "🛑 Stop: docker-compose --profile ai down"
