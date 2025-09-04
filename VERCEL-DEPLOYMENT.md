# 🚀 Vercel Deployment Guide for akAIfe Travel Advisor

## 📋 Pre-Deployment Checklist

✅ **Project Structure Configured**
- Frontend build tested and working
- Demo mode enabled (no API keys required)
- Vercel configuration file created

✅ **Files Ready**
- `vercel.json` - Deployment configuration
- `akaife-front/dist/` - Build output ready
- Demo API responses configured

## 🌐 Deploy to Vercel

### Option 1: GitHub Integration (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin master
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with your GitHub account
   - Click "New Project"
   - Import your `akAIfe` repository

3. **Configure Build Settings**
   - Framework Preset: **Vite**
   - Root Directory: **akaife-front**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Deploy**
   - Click "Deploy"
   - Wait for build completion
   - Your app will be live at `https://your-project-name.vercel.app`

### Option 2: Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy from project root**
   ```bash
   cd /home/nika-rusishvili/Nika/Projects/akAIfe
   vercel
   ```

3. **Follow prompts:**
   - Set up and deploy: `Y`
   - Which scope: (your account)
   - Link to existing project: `N`
   - Project name: `akaife-travel-advisor`
   - Directory: `./akaife-front`

## 🎯 Expected Result

Your deployed app will show:
- ✅ Beautiful travel advisor chat interface
- ✅ Sample conversations with realistic responses
- ✅ Responsive design on all devices
- ✅ Professional portfolio-ready presentation

## 🔧 Build Configuration Details

The `vercel.json` is configured to:
- Build from `akaife-front` directory
- Use Vite framework detection
- Handle SPA routing with catch-all rewrites
- Optimize for static deployment

## 📱 Demo Mode Features

Your deployed app includes:
- 🤖 Simulated AI travel advisor responses
- 🚂 Sample train booking information
- 🚗 Mock car rental search results  
- 📍 Example restaurant recommendations
- 💬 Realistic conversation flow

## 🌟 Portfolio Highlights

Emphasize these technical achievements:
- **Full-Stack Architecture**: Frontend + Backend integration ready
- **Modern Tech Stack**: React, TypeScript, Tailwind CSS
- **AI Integration**: Claude AI implementation (demo mode)
- **Responsive Design**: Mobile-first approach
- **Professional UI**: shadcn/ui component library

## 🔄 Switching to Production Mode

When you want to enable full AI features:

1. Deploy backend to Railway/Render
2. Update API endpoint in `src/hooks/useChat.ts`:
   ```typescript
   import { sendQuery } from '../api'; // Switch back to real API
   ```
3. Add environment variables in Vercel dashboard:
   - `ANTHROPIC_API_KEY`
   - `GOOGLE_MAPS_API_KEY`

## 📊 Performance Optimization

The build includes:
- ✅ Code splitting and lazy loading
- ✅ CSS optimization and minification
- ✅ Image optimization
- ✅ Fast loading performance
- ✅ SEO-friendly structure

---

**Ready to impress recruiters with your AI-powered travel advisor! 🎉**
