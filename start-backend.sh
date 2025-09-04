#!/bin/bash
# Start backend server for akAIfe Travel Advisor

echo "🚀 Starting akAIfe Travel Advisor Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please create one based on env.example"
    echo "   Required: ANTHROPIC_API_KEY and GOOGLE_MAPS_API_KEY"
    exit 1
fi

# Start the backend server
cd akaife-back
echo "📦 Installing backend dependencies..."
npm install
echo "🌐 Starting Express server on port 5000..."
node server.js
