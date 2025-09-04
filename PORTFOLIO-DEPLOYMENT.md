# 📁 Portfolio Deployment Guide

Quick deployment guide for showcasing **akAIfe** in your portfolio.

## 🎯 For Portfolio Demo

### Option 1: Frontend-Only Demo (Recommended for Portfolio)

If you want to showcase just the UI/UX without API costs:

1. **Build the Frontend**:
   \`\`\`bash
   cd akaife-front
   npm run build
   \`\`\`

2. **Mock the Backend** (Optional):
   - Modify \`src/api.ts\` to return sample responses
   - This shows the interface without API calls

3. **Deploy to Vercel/Netlify**:
   \`\`\`bash
   # Upload the 'dist' folder or connect your GitHub repo
   \`\`\`

### Option 2: Full Stack Demo

#### Frontend Deployment (Vercel/Netlify):
\`\`\`bash
cd akaife-front
npm run build
# Deploy 'dist' folder
\`\`\`

#### Backend Deployment (Railway/Render):
1. Create account on Railway.app or Render.com
2. Connect your GitHub repository
3. Add environment variables:
   - \`ANTHROPIC_API_KEY\`
   - \`GOOGLE_MAPS_API_KEY\`
4. Set build command: \`cd akaife-back && npm install\`
5. Set start command: \`cd akaife-back && node server.js\`

#### Update API Endpoint:
In \`akaife-front/src/api.ts\`, change:
\`\`\`typescript
const response = await fetch('https://your-backend-url.com/query', {
\`\`\`

## 💰 Cost Considerations

- **Anthropic API**: ~$0.01-0.05 per query
- **Google Maps API**: Free tier covers most demo usage
- **Hosting**: Vercel/Netlify free tier is sufficient

## 🎨 Portfolio Presentation Tips

1. **Screenshots**: Include chat interface screenshots
2. **Demo Video**: Record a short video showing the features
3. **Live Demo**: Include live link with note about API keys
4. **Tech Stack**: Highlight the modern tech stack used
5. **Features**: Emphasize AI integration and real-time data

## 📋 Portfolio Description Template

> **akAIfe - AI Travel Advisor**
> 
> A full-stack travel planning application featuring AI-powered assistance, real-time train booking integration, and location-based services. Built with React, TypeScript, Node.js, and Anthropic's Claude AI.
> 
> **Key Features:**
> - 🤖 AI chat interface for travel planning
> - 🚂 Real-time Georgian Railway integration
> - 🚗 Car rental search and comparison
> - 📍 Location-based recommendations
> - 🎨 Modern, responsive UI with Tailwind CSS
> 
> **Tech Stack:** React, TypeScript, Node.js, Python, Anthropic AI, Google Maps API, Tailwind CSS, shadcn/ui

## 🔗 Quick Links for Portfolio

- **Live Demo**: [Your deployment URL]
- **GitHub**: [Repository link]
- **Tech Stack**: React + TypeScript + Node.js + Python + AI
- **Status**: Production Ready ✅
