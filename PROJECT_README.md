# 🌐 Enterprise Network AI Assistant

A modern, enterprise-grade telecom customer support platform powered by AI and RAG (Retrieval-Augmented Generation). Features a clean, Airtel-inspired UI with intelligent chat assistance.

![Platform](https://img.shields.io/badge/Platform-Web-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Overview

This application provides an intelligent AI-powered customer support system tailored for telecom and network service providers. It combines:
- **RAG-based Knowledge Retrieval** from historical support data
- **Perplexity AI** for generating contextual, professional responses
- **Enterprise-grade UI** with step-based forms and professional design
- **Automatic escalation** to human agents when needed

---

## ✨ Features

### 🎨 **Modern UI Design**
- Clean, light-themed enterprise portal
- Airtel-inspired navigation and layout
- Step-based form progression with visual indicators
- Responsive design for all devices
- Glassmorphism effects and smooth animations

### 🤖 **AI-Powered Support**
- Retrieval-Augmented Generation (RAG) for accurate responses
- Context-aware answers from historical support logs
- Smart citation system for source attribution
- Automatic human escalation for complex queries
- Professional, empathetic response tone

### 🔍 **Intelligent Search**
- TF-IDF based document retrieval (current)
- Semantic similarity matching
- Configurable similarity thresholds
- Multi-source data support (CSV, JSON)

### 💬 **Chat Widget**
- Floating chat launcher
- Real-time messaging interface
- Quick action chips for common queries
- Typing indicators
- Citation-linked responses

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Perplexity API key

### Step 1: Clone/Download the Project
```bash
cd "C:\Users\patib\OneDrive\Desktop\Telecalling bot"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- flask
- flask-cors
- pandas
- scikit-learn
- numpy
- requests
- python-dotenv

### Step 3: Configure Environment Variables
Create a `.env` file in the project root:
```env
PERPLEXITY_API_KEY=your_api_key_here
```

### Step 4: Add Your Data
Place your support data files in the `data/` folder:
- Supported formats: CSV, JSON
- Required columns: `conversation`, `text`, `dialogue`, or similar text fields
- The system auto-detects the text column

---

## 🎯 Usage

### Start the Server
```bash
python app.py
```

The application will:
1. Load/build the TF-IDF index from data files
2. Start the Flask server at `http://localhost:5000`
3. Open your browser and navigate to the URL

### Using the Chat Widget
1. Click the floating red chat button (bottom-right)
2. Type your query or use quick action chips
3. Receive AI-generated responses with citations
4. Escalate to human agent if needed

---

## 📁 Project Structure

```
Telecalling bot/
│
├── app.py                      # Flask application entry point
├── rag_service.py              # RAG service with TF-IDF retrieval
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys)
├── README.md                   # This file
│
├── data/                       # Support data files (CSV/JSON)
│   └── tfidf_index.pkl        # Cached TF-IDF index
│
├── templates/
│   └── index.html             # Main HTML template
│
└── static/
    ├── css/
    │   ├── style.css          # Main stylesheet
    │   ├── enhancements.css   # UI enhancements & animations
    │   └── escalation.css     # Escalation modal styles
    │
    └── js/
        └── script.js          # Frontend JavaScript logic
```

---

## ⚙️ Configuration

### RAG Settings (`rag_service.py`)
```python
TOP_K_RETRIEVE = 10        # Number of documents to retrieve
FINAL_K = 5                # Number of documents sent to AI
SIMILARITY_THRESHOLD = 0.1 # Minimum similarity score
MAX_CONTEXT_CHARS = 6000   # Maximum context length
PERPLEXITY_MODEL = "sonar" # AI model to use
```

### UI Customization (`static/css/style.css`)
```css
:root {
    --primary: #e60000;           /* Primary brand color */
    --bg-light: #f5f7fa;          /* Light background */
    --text-dark: #1a1a1a;         /* Dark text */
    --shadow-lg: 0 10px 15px...;  /* Shadow effects */
}
```

---

## 🔧 API Endpoints

### `POST /query`
Send a user query and receive an AI-generated response.

**Request:**
```json
{
    "query": "Internet is slow",
    "api_key": "optional_override_key"
}
```

**Response:**
```json
{
    "answer": "AI-generated response with citations [1]",
    "context": "Retrieved context from knowledge base",
    "sources": [...],
    "escalation": false
}
```

---

## 🎨 Design Philosophy

### Visual Style
- **Clean & Minimal**: Ample whitespace, clear hierarchy
- **Enterprise-Grade**: Professional color palette (grays, blues, purple accents)
- **Trustworthy**: Subtle animations, polished interactions
- **Accessible**: High contrast, readable typography

### UX Patterns
- **Progressive Disclosure**: Step-by-step forms
- **Visual Feedback**: Hover states, focus rings, loading indicators
- **Status Indicators**: Completion checkmarks, active state pulses
- **Clear Actions**: Prominent CTAs, intuitive navigation

---

## 🔮 Future Enhancements

### ✅ Planned for Next Update
- **FAISS Integration**: Upgrade from TF-IDF to FAISS with semantic embeddings
- **Better Semantic Search**: Using sentence-transformers for context understanding
- **Performance**: Faster retrieval with optimized vector search
- **Scalability**: Handle larger datasets efficiently

### 🎯 Roadmap
- Multi-language support
- Advanced analytics dashboard
- User authentication
- Conversation history
- Admin panel for data management
- Real-time human agent handoff

---

## 🛠️ Technologies Used

### Backend
- **Flask** - Web framework
- **scikit-learn** - TF-IDF vectorization
- **Pandas** - Data processing
- **NumPy** - Numerical operations

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling (with CSS variables)
- **JavaScript** - Interactivity
- **FontAwesome** - Icons
- **Marked.js** - Markdown rendering

### AI & ML
- **Perplexity API** - LLM for response generation
- **TF-IDF** - Document retrieval (current)
- **FAISS** (planned) - Semantic vector search

---

## 📝 Citation System

The AI uses numbered citations `[1]`, `[2]`, etc. to reference source documents:
- Citations appear inline within responses
- Strict rules prevent citation overuse
- Only factual statements are cited
- Greetings and empathy are citation-free

---

## 🚨 Troubleshooting

### Issue: "Perplexity API Key is missing"
**Solution:** Create a `.env` file with your API key
```env
PERPLEXITY_API_KEY=your_key_here
```

### Issue: Index not found or outdated
**Solution:** Delete `data/tfidf_index.pkl` and restart the app to rebuild

### Issue: No documents indexed
**Solution:** Ensure data files are in the `data/` folder with text columns

### Issue: Port 5000 already in use
**Solution:** Change the port in `app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## 📄 License

MIT License - Feel free to use and modify for your projects.

---

## 👤 Author

Built with ❤️ for enterprise telecom support

---

## 🙏 Acknowledgments

- Inspired by modern telecom portals (Airtel, Cloudflare, AWS)
- UI design principles from enterprise SaaS applications
- Powered by Perplexity AI for intelligent responses

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the configuration settings
3. Ensure all dependencies are installed
4. Verify API key is correctly set

---

**Last Updated:** January 2026  
**Version:** 1.0.0
