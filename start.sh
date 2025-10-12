#!/bin/bash
# Start Restaurant AI with AI-powered responses
# Requires: models/phi-2.Q4_K_M.gguf (1.7GB)

echo "🤖 Starting Restaurant AI..."
echo "🧠 AI-powered natural language responses"
echo ""

# Check if model exists
if [ ! -f "models/phi-2.Q4_K_M.gguf" ]; then
    echo "❌ ERROR: Model file not found!"
    echo ""
    echo "Please download the Phi-2 model first:"
    echo "  mkdir -p models"
    echo "  curl -L -o models/phi-2.Q4_K_M.gguf \\"
    echo "    https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
    echo ""
    echo "Or run in template mode (fast responses, no AI):"
    echo "  USE_LOCAL_AI=false docker-compose up -d"
    echo ""
    exit 1
fi

# Stop any existing containers
docker-compose down 2>/dev/null

# Start everything (app + AI server)
docker-compose up --build -d

echo ""
echo "✅ Restaurant AI is starting up!"
echo "⏳ AI model is loading (this takes 30-60 seconds on first start)..."
echo ""
echo "🌐 Chat Interface: http://localhost:8000/static/restaurant_chat.html"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo "🤖 AI Server: http://localhost:8080/health"
echo ""
echo "📊 View logs:"
echo "  All:  docker-compose logs -f"
echo "  App:  docker-compose logs -f app"
echo "  AI:   docker-compose logs -f llama-server"
echo ""
echo "🛑 Stop: docker-compose down"
echo ""
echo "💡 Tip: To use fast template mode instead:"
echo "   USE_LOCAL_AI=false docker-compose up -d"
