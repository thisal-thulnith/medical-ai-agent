# 🏥 Medical AI Agent - START HERE

## What is This?

A complete **AI-powered medical assistant** that you can chat with like ChatGPT, but specifically for healthcare:

- 💬 **Chat Interface** - Ask medical questions, describe symptoms
- 🤖 **AI Agent System** - Uses LangGraph with specialized medical agents
- 📊 **Health Dashboard** - Visual analytics of your health data
- 💊 **Medication Tracking** - AI extracts and tracks meds from conversation
- 📈 **Symptom Tracking** - Log symptoms naturally through chat
- 🧠 **Memory System** - AI remembers your medical history
- 🌐 **Free APIs** - Integrates OpenFDA, PubMed for drug info

**Technology:** LangGraph + FastAPI (Backend) + Next.js (Frontend)

---

## ⚡ Quick Start Commands

### First Time Setup (One Time Only)

```bash
# 1. Backend Setup
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 2. Configure .env (EDIT THIS FILE!)
cp .env.example .env
# Now edit .env and add your:
# - OpenAI API key
# - Database URL
# - Redis URL

# 3. Frontend Setup
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Every Time You Run

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

**Open:** http://localhost:3000

---

## 📋 What You Need

### Required (Must Have)

1. **OpenAI API Key**
   - Get it: https://platform.openai.com/api-keys
   - Cost: ~$0.002 per conversation (very cheap)
   - Needed for: AI agent conversations

2. **PostgreSQL Database**
   - Free option: https://supabase.com (recommended)
   - Or install locally: `brew install postgresql`
   - Needed for: Storing user data, conversations, health records

3. **Redis**
   - Free option: https://upstash.com (recommended)
   - Or install locally: `brew install redis`
   - Needed for: Caching and sessions

### Optional (Nice to Have)

4. **USDA API Key** (for nutrition info)
   - Get it: https://fdc.nal.usda.gov/api-key-signup.html
   - Free, instant approval

---

## 🎯 Example Conversations

Once running, try these with the AI:

### Symptom Tracking
```
You: "I've had a headache and fever for 2 days, moderate pain"
AI: "I understand you're experiencing a moderate headache and fever for 2 days.
     I've logged these symptoms. Based on the duration and symptoms,
     you may want to monitor your temperature..."
```

### Medication Questions
```
You: "Tell me about aspirin"
AI: "Aspirin (acetylsalicylic acid) is a common pain reliever and
     anti-inflammatory medication. Uses: pain relief, fever reduction,
     anti-inflammatory..."
[Fetches real data from OpenFDA API]
```

### Health Data Logging
```
You: "My blood pressure is 120/80, heart rate 75"
AI: "I've recorded your vital signs:
     - Blood Pressure: 120/80 mmHg (Normal range)
     - Heart Rate: 75 bpm (Normal)
     Your blood pressure is within healthy range..."
```

### Data Retrieval
```
You: "Show me my symptoms from this week"
AI: "Here are your symptoms from the past 7 days:
     • Headache (moderate) - 2 days ago
     • Fever (mild) - 2 days ago
     Would you like me to analyze any patterns?"
```

---

## 🏗️ System Architecture

```
User chats → Frontend (Next.js)
              ↓
          FastAPI Backend
              ↓
         LangGraph Orchestrator
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
Specialized Agents  OpenAI GPT-4
    ↓                   ↓
- Symptom Analyzer  Conversation
- Medication Expert
- Report Analyzer
- Lifestyle Coach
              ↓
    Save to PostgreSQL
              ↓
    Store in ChromaDB (Memory)
```

---

## 📁 Project Structure

```
medicalagent/
├── backend/              # Python FastAPI
│   ├── app/
│   │   ├── agents/       # LangGraph AI agents
│   │   ├── api/          # REST endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt  # Python packages
│   └── .env             # Configuration (YOU EDIT THIS)
│
├── frontend/            # Next.js React
│   ├── app/             # Pages
│   ├── components/      # UI components
│   ├── lib/             # Utilities
│   └── .env.local      # Frontend config
│
├── README.md           # Full documentation
├── SETUP_GUIDE.md     # Detailed setup
└── START_HERE.md      # This file
```

---

## 🔑 Required Configuration

### Backend `.env` File

Create `backend/.env`:

```env
# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-your-key-here

# Database (REQUIRED) - Choose one:
# Supabase:
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
# Local:
# DATABASE_URL=postgresql://user:pass@localhost:5432/medicalai

# Redis (REQUIRED) - Choose one:
# Upstash:
REDIS_URL=redis://default:password@endpoint.upstash.io:6379
# Local:
# REDIS_URL=redis://localhost:6379

# Security (REQUIRED)
JWT_SECRET_KEY=change-this-to-random-string

# Application
FRONTEND_URL=http://localhost:3000
DEBUG=True
ENVIRONMENT=development

# Optional
USDA_API_KEY=optional-for-nutrition-info
```

### Frontend `.env.local` File

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## ✅ Checklist Before Running

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] OpenAI API key obtained
- [ ] Database setup (Supabase or local PostgreSQL)
- [ ] Redis setup (Upstash or local Redis)
- [ ] Backend `.env` configured
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend `.env.local` configured

---

## 🚨 Troubleshooting

### "ModuleNotFoundError"
```bash
cd backend
source venv/bin/activate  # Make sure venv is activated!
pip install -r requirements.txt
```

### "Connection refused" / "Cannot connect to database"
```bash
# Check your DATABASE_URL in backend/.env
# Make sure PostgreSQL is running
# Test: psql [YOUR_DATABASE_URL]
```

### "OpenAI API error"
```bash
# Check OPENAI_API_KEY in backend/.env
# Make sure it starts with sk-
# Check you have credits: https://platform.openai.com/usage
```

### "404 Not Found" from frontend
```bash
# Make sure backend is running on port 8000
# Check http://localhost:8000/health
# Check backend/.env has FRONTEND_URL=http://localhost:3000
```

---

## 📚 Learn More

- **Full Documentation:** `README.md`
- **Setup Guide:** `SETUP_GUIDE.md`
- **API Docs:** http://localhost:8000/docs (when backend running)
- **LangGraph:** https://langchain-ai.github.io/langgraph/

---

## 🎓 How It Works

### LangGraph Agent System

1. **User sends message** → "I have a headache"

2. **Intent Classifier** → Determines this is "symptom_analysis"

3. **Context Retriever** → Loads user's medical history from database + memory

4. **Symptom Analyzer Agent** →
   - Analyzes symptom severity
   - Checks medical history for patterns
   - Extracts structured data: `{"symptom": "headache", "severity": "moderate"}`
   - Generates empathetic response

5. **Data Logger** → Saves symptom to PostgreSQL

6. **Memory Service** → Stores in ChromaDB for future context

7. **Response Generator** → Sends response back to user

---

## 💡 Key Features

### 1. Everything Through Chat
No forms or buttons - just natural conversation:
- Log symptoms: "I have a headache"
- Track vitals: "My BP is 120/80"
- Ask questions: "What causes high blood pressure?"

### 2. AI Memory
The AI remembers:
- Your medical conditions
- Your medications
- Your allergies
- Previous conversations
- Health patterns

### 3. Real Medical Data
Integrates with free APIs:
- **OpenFDA:** Drug information, interactions, side effects
- **PubMed:** Medical research articles
- **USDA:** Nutritional information
- **ICD-10:** Medical coding

### 4. Privacy & Security
- JWT authentication
- Password hashing
- HTTPS ready
- HIPAA-compliance features

---

## 🚀 Next Steps After Setup

1. **Register Account** at http://localhost:3000
2. **Start Chatting** - Try the example conversations above
3. **View Dashboard** - See your health data visualized
4. **Track Health** - Use daily for symptom/vitals logging
5. **Ask Questions** - Get medical information
6. **Explore API** - Check http://localhost:8000/docs

---

## ⚠️ Medical Disclaimer

This AI assistant is for **informational purposes only**. It is NOT a substitute for professional medical advice. Always consult with qualified healthcare providers for medical decisions.

In emergencies, call 911 or your local emergency number immediately.

---

## 🤝 Support

**Need help?**
1. Check `SETUP_GUIDE.md` for detailed instructions
2. Review error messages in terminal
3. Test API at http://localhost:8000/docs
4. Check Prerequisites are installed correctly

**Common first-time issues:**
- Forgot to activate venv: `source venv/bin/activate`
- Wrong directory: Make sure you're in `backend/` or `frontend/`
- Missing .env: Copy from .env.example and configure
- Port already in use: Kill other processes on ports 8000/3000

---

## 🎉 You're Ready!

Follow the "Quick Start Commands" above to get started.

**Estimated setup time:** 10-15 minutes

**Good luck! 🏥🤖**
