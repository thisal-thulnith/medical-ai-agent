#!/bin/bash

# Medical AI Agent - Quick Start Script
# This script will start both backend and frontend servers

echo "🏥 Medical AI Agent - Starting..."
echo ""

# Check if OpenAI API key is set
cd backend
if grep -q "REPLACE_WITH_YOUR_OPENAI_KEY" .env; then
    echo "❌ ERROR: OpenAI API key not configured!"
    echo ""
    echo "📝 Please edit this file: backend/.env"
    echo "   Replace 'REPLACE_WITH_YOUR_OPENAI_KEY' with your actual OpenAI API key"
    echo ""
    echo "🔑 Get your API key from: https://platform.openai.com/api-keys"
    echo ""
    exit 1
fi

echo "✅ OpenAI API key found"
echo ""

# Start backend in background
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Backend URL: http://localhost:8000"
echo "   Backend logs: backend/backend.log"
cd ..

# Wait for backend to start
echo ""
echo "⏳ Waiting for backend to start..."
sleep 5

# Start frontend
echo ""
echo "🚀 Starting frontend server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Frontend URL: http://localhost:3000"
echo "   Frontend logs: frontend.log"

echo ""
echo "✅ Medical AI Agent is starting!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 To stop the servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "⏳ Waiting for servers to be ready..."
sleep 10
echo ""
echo "🎉 Ready! Open http://localhost:3000 in your browser"
