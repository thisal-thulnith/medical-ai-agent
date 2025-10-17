# Medical AI Agent - Quick Setup Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy your API key (starts with `sk-`)

### Step 2: Set Up Database (Choose One)

**Option A: Supabase (Easiest - Free)**

1. Go to https://supabase.com
2. Click "Start your project"
3. Create new project
4. Go to Settings → Database
5. Copy "Connection string" (URI format)

**Option B: Neon (Alternative - Free)**

1. Go to https://neon.tech
2. Sign up and create project
3. Copy connection string

**Option C: Local PostgreSQL**

```bash
# macOS
brew install postgresql
brew services start postgresql
createdb medicalai
# Connection string: postgresql://username:password@localhost:5432/medicalai
```

### Step 3: Set Up Redis (Choose One)

**Option A: Upstash (Easiest - Free)**

1. Go to https://upstash.com
2. Create account
3. Create Redis database
4. Copy connection URL

**Option B: Local Redis**

```bash
# macOS
brew install redis
brew services start redis
# Connection string: redis://localhost:6379
```

### Step 4: Configure Backend

```bash
cd backend
cp .env.example .env
```

Edit `.env`:

```env
# REQUIRED
OPENAI_API_KEY=sk-your-key-here

# Database (paste your connection string)
DATABASE_URL=postgresql://...

# Redis (paste your connection string)
REDIS_URL=redis://...

# JWT Secret (any random string)
JWT_SECRET_KEY=change-this-to-random-string-123456

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Step 5: Install & Run Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at http://localhost:8000
✅ API docs at http://localhost:8000/docs

### Step 6: Install & Run Frontend

Open new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

✅ Frontend running at http://localhost:3000

---

## 🎉 You're Done!

Open http://localhost:3000 in your browser

### First Steps:

1. **Register** a new account
2. Start chatting with the AI:
   - "I have a headache"
   - "My blood pressure is 120/80"
   - "Tell me about aspirin"
3. View your **Dashboard** to see tracked data

---

## 📝 How to Use

### Symptom Tracking
```
"I've had a fever and cough for 2 days"
→ AI logs symptoms automatically
```

### Medication Tracking
```
"I'm taking aspirin 100mg twice daily"
→ AI adds to your medication list
```

### Health Questions
```
"What foods should I eat for high blood pressure?"
→ AI provides personalized advice
```

### Data Retrieval
```
"Show me my symptoms this week"
→ AI displays your logged symptoms
```

---

## 🔧 Troubleshooting

### Backend won't start

**Error: "No module named 'app'"**
```bash
# Make sure you're in backend directory
cd backend
# Make sure venv is activated
source venv/bin/activate
```

**Error: "Could not connect to database"**
```bash
# Check your DATABASE_URL in .env
# Make sure PostgreSQL is running
# Test connection: psql [YOUR_DATABASE_URL]
```

**Error: "OpenAI API key not found"**
```bash
# Check .env file has OPENAI_API_KEY
# Make sure no spaces around =
# Make sure key starts with sk-
```

### Frontend won't start

**Error: "Cannot find module"**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Error: "API request failed"**
```bash
# Check backend is running on port 8000
# Check .env.local has correct API_URL
# Check CORS settings in backend
```

### ChromaDB Issues

**Error: "ChromaDB connection failed"**
```bash
# ChromaDB will auto-create ./chroma_db directory
# Make sure backend has write permissions
# Delete ./chroma_db and restart if corrupted
```

---

## 🌐 Free Service Setup Details

### Supabase (PostgreSQL)

1. Sign up: https://supabase.com
2. Create project (choose region close to you)
3. Wait ~2 minutes for provisioning
4. Go to Settings → Database
5. Find "Connection string" (URI)
6. Click "Copy" next to URI format
7. Paste into `.env` as `DATABASE_URL`

### Upstash (Redis)

1. Sign up: https://upstash.com
2. Click "Create Database"
3. Choose region, select "Redis"
4. Copy "REST URL" or "Connection String"
5. Paste into `.env` as `REDIS_URL`

### OpenFDA, PubMed (Already Configured!)

These APIs are already integrated and require NO API keys!

### USDA Food Database (Optional)

1. Go to: https://fdc.nal.usda.gov/api-key-signup.html
2. Fill form (instant approval)
3. Copy API key from email
4. Add to `.env`:
   ```
   USDA_API_KEY=your-key-here
   ```

---

## 📱 Production Deployment

### Backend (FastAPI)

**Deploy to:**
- Railway.app (free tier)
- Render.com (free tier)
- Fly.io (free tier)

**Steps:**
1. Push code to GitHub
2. Connect repo to hosting platform
3. Set environment variables
4. Deploy!

### Frontend (Next.js)

**Deploy to:**
- Vercel (free for Next.js)
- Netlify (free tier)

**Steps:**
1. Push code to GitHub
2. Import to Vercel
3. Set NEXT_PUBLIC_API_URL
4. Deploy!

---

## 🔐 Security Checklist for Production

- [ ] Change JWT_SECRET_KEY to strong random string
- [ ] Use HTTPS for all connections
- [ ] Enable database SSL
- [ ] Set DEBUG=False
- [ ] Configure proper CORS origins
- [ ] Enable rate limiting
- [ ] Set up database backups
- [ ] Add monitoring/logging
- [ ] Review HIPAA compliance requirements

---

## 📚 Additional Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **OpenAI API**: https://platform.openai.com/docs

---

## 🆘 Get Help

**Common Issues:**
- Check logs: Backend shows errors in terminal
- API Docs: http://localhost:8000/docs (test endpoints)
- Network: Make sure backend + frontend both running
- Environment: Double-check all .env variables

**Still stuck?**
- Review error messages carefully
- Check Prerequisites are installed
- Try restarting both servers
- Check firewall/antivirus settings

---

## ✨ Features to Try

1. **Track Symptoms**: "I have chest pain, shortness of breath"
2. **Log Vitals**: "My blood pressure is 140/90, heart rate 85"
3. **Medication Info**: "Tell me about metformin"
4. **Drug Interactions**: "Can I take aspirin with ibuprofen?"
5. **Nutrition**: "What are healthy foods for diabetes?"
6. **Medical Questions**: "What causes high cholesterol?"
7. **View Data**: "Show me my symptoms this month"
8. **Health Advice**: "How can I lower my blood pressure naturally?"

---

**Enjoy your AI medical assistant! 🏥🤖**
