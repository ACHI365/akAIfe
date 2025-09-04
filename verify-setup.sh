#!/bin/bash
# Verification script for akAIfe Travel Advisor

echo "🔍 Verifying akAIfe Travel Advisor Setup..."
echo "========================================="

# Check if .env file exists
if [ -f .env ]; then
    echo "✅ .env file found"
else
    echo "⚠️  .env file missing - copy from env.example and add your API keys"
fi

# Check Python dependencies
echo "🐍 Checking Python setup..."
if command -v uv &> /dev/null; then
    echo "✅ uv package manager found"
    if uv run python --version &> /dev/null; then
        echo "✅ Python environment ready"
    else
        echo "❌ Python environment issue"
    fi
else
    echo "❌ uv package manager not found"
fi

# Check Node.js dependencies
echo "📦 Checking Node.js setup..."
if [ -d "akaife-back/node_modules" ]; then
    echo "✅ Backend dependencies installed"
else
    echo "❌ Backend dependencies missing - run: cd akaife-back && npm install"
fi

if [ -d "akaife-front/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Frontend dependencies missing - run: cd akaife-front && npm install"
fi

# Check if startup scripts are executable
if [ -x "start-backend.sh" ] && [ -x "start-frontend.sh" ]; then
    echo "✅ Startup scripts are executable"
else
    echo "❌ Startup scripts need permissions - run: chmod +x start-*.sh"
fi

echo ""
echo "🚀 Setup Summary:"
echo "=================="
echo "To start the application:"
echo "1. Terminal 1: ./start-backend.sh"
echo "2. Terminal 2: ./start-frontend.sh"
echo "3. Visit: http://localhost:5173"
echo ""
echo "For development with both at once:"
echo "npm run dev"
echo ""
echo "Ready for portfolio deployment! 🎨"
