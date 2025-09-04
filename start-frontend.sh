#!/bin/bash
# Start frontend for akAIfe Travel Advisor

echo "🎨 Starting akAIfe Travel Advisor Frontend..."

cd akaife-front
echo "📦 Installing frontend dependencies..."
npm install
echo "🔥 Starting Vite development server..."
npm run dev
