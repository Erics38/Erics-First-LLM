@echo off
REM Start Restaurant AI in Template Mode (Fast responses)
REM Windows batch script

echo 🚀 Starting Restaurant AI (Template Mode)...
echo ⚡ Fast responses, no AI model needed
echo.

REM Stop any existing containers
docker-compose down 2>nul

REM Start only the app (no llama-server)
docker-compose up --build -d

echo.
echo ✅ Restaurant AI is starting up!
echo 🌐 Chat Interface: http://localhost:8000/static/restaurant_chat.html
echo 📚 API Docs: http://localhost:8000/api/docs
echo.
echo 📊 View logs: docker-compose logs -f
echo 🛑 Stop: docker-compose down
