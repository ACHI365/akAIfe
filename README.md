# akAIfe - AI Travel Advisor 🌍✈️

A sophisticated AI-powered travel advisory application that helps users plan their trips with real-time information about Georgian Railway bookings, car rentals, and location-based recommendations.

## 🚀 Features

- **🤖 AI-Powered Travel Assistant**: Uses Anthropic's Claude for intelligent travel advice
- **🚂 Georgian Railway Integration**: Real-time train booking information
- **🚗 Car Rental Service**: Search and compare rental cars from MyAuto.ge
- **📍 Location Services**: Find restaurants, bars, cafes, and attractions near any location
- **💬 Interactive Chat Interface**: Beautiful, responsive chat UI built with React and Tailwind CSS

## 🏗️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Lucide React** for icons

### Backend
- **Node.js** with Express
- **Python** with FastMCP and Anthropic SDK
- **Model Context Protocol (MCP)** for AI integration
- **Google Maps API** for location services

## 📋 Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- **uv** (Python package manager)
- **npm** or **yarn**

## 🛠️ Installation & Setup

### 1. Clone the Repository
\`\`\`bash
git clone <repository-url>
cd akAIfe
\`\`\`

### 2. Environment Configuration
Create a \`.env\` file in the project root based on \`env.example\`:

\`\`\`bash
cp env.example .env
\`\`\`

Edit the \`.env\` file and add your API keys:
\`\`\`env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
\`\`\`

#### How to Get API Keys:
- **Anthropic API**: Visit [console.anthropic.com](https://console.anthropic.com/) and create an account
- **Google Maps API**: Visit [Google Cloud Console](https://console.cloud.google.com/), enable Maps API, and create credentials

### 3. Install Dependencies

#### Python Dependencies
\`\`\`bash
uv sync
\`\`\`

#### Backend Dependencies
\`\`\`bash
cd akaife-back
npm install
cd ..
\`\`\`

#### Frontend Dependencies
\`\`\`bash
cd akaife-front
npm install
cd ..
\`\`\`

## 🏃‍♂️ Running the Application

### Option 1: Using Startup Scripts (Recommended)

#### Terminal 1 - Backend:
\`\`\`bash
./start-backend.sh
\`\`\`

#### Terminal 2 - Frontend:
\`\`\`bash
./start-frontend.sh
\`\`\`

### Option 2: Manual Start

#### Backend (Terminal 1):
\`\`\`bash
cd akaife-back
node server.js
\`\`\`

#### Frontend (Terminal 2):
\`\`\`bash
cd akaife-front
npm run dev
\`\`\`

### 🌐 Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 🎯 Usage Examples

### Sample Queries to Try:
- "I want to travel from Tbilisi to Batumi next week"
- "Find me rental cars under $50 per day"
- "What restaurants are near Rustaveli Avenue?"
- "Plan a weekend trip to Kutaisi"

## 📁 Project Structure
\`\`\`
akAIfe/
├── akaife-front/          # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
│   └── package.json
├── akaife-back/           # Express backend
│   ├── server.js          # Main server file
│   ├── client.py          # MCP client
│   └── package.json
├── main.py                # MCP server with travel tools
├── utils.py               # Utility functions
├── mapsAPIutils.py        # Google Maps integration
├── pyproject.toml         # Python dependencies
├── start-backend.sh       # Backend startup script
├── start-frontend.sh      # Frontend startup script
└── env.example           # Environment variables template
\`\`\`

## 🧪 Available Tools & APIs

The AI assistant has access to the following tools:

1. **Railway_Stations**: Get all available train stations
2. **Plan_Journey**: Search for train routes with dates
3. **List_Rental_Locations**: Get car rental locations
4. **Search_Rental_Cars**: Find rental cars with filters
5. **Get_Some_Spots_Around_Location**: Find places near coordinates
6. **Open_URL_in_Browser**: Open booking URLs

## 🚀 Deployment

### For Portfolio Hosting:

#### Frontend (Static Hosting)
\`\`\`bash
cd akaife-front
npm run build
# Deploy the 'dist' folder to services like Vercel, Netlify, or GitHub Pages
\`\`\`

#### Backend (Server Hosting)
- Deploy to platforms like Railway, Render, or DigitalOcean
- Ensure environment variables are set
- The backend needs Python and Node.js runtime

### Environment Variables for Production:
\`\`\`env
NODE_ENV=production
ANTHROPIC_API_KEY=your_production_key
GOOGLE_MAPS_API_KEY=your_production_key
\`\`\`

## 🐛 Troubleshooting

### Common Issues:

1. **Python command not found**: Make sure Python 3.10+ is installed
2. **uv command not found**: Install uv: \`curl -LsSf https://astral.sh/uv/install.sh | sh\`
3. **API key errors**: Verify your API keys are correctly set in the \`.env\` file
4. **Port conflicts**: Ensure ports 5000 and 5173 are available

### Development Mode:
- Frontend hot-reload on http://localhost:5173
- Backend runs on http://localhost:5000
- API endpoints accessible via \`/query\` and \`/health\`

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues or questions, please open an issue on the GitHub repository.

---

**Built with ❤️ using modern web technologies for seamless travel planning**