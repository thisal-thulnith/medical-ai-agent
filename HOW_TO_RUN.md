# 🚀 How to Run Medical AI Agent

## Quick Start (3 Steps)

### Step 1: Get Your OpenAI API Key

1. **Go to:** https://platform.openai.com/api-keys
2. **Sign in** (or create free account)
3. **Click:** "Create new secret key"
4. **Name it:** "Medical AI Agent"
5. **Copy the key** (starts with `sk-...`)
   - ⚠️ Save it somewhere - you can only see it once!

**Cost:** ~$0.002 per conversation (very cheap!)

---

### Step 2: Add Your API Key

Open this file in your editor:
```
/Users/thisalthulnith/medicalagent/backend/.env
```

Find this line (line 2):
```
OPENAI_API_KEY=REPLACE_WITH_YOUR_OPENAI_KEY
```

Replace it with your actual key:
```
OPENAI_API_KEY=sk-proj-abcd1234...your-actual-key-here
```

**Save the file!**

---

### Step 3: Run the Application

Open Terminal and run:

```bash
cd /Users/thisalthulnith/medicalagent
./RUN_ME.sh
```

Or run manually:

**Terminal 1 - Backend:**
```bash
cd /Users/thisalthulnith/medicalagent/backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd /Users/thisalthulnith/medicalagent/frontend
npm run dev
```

---

## 🎉 That's It!

**Open in browser:** http://localhost:3000

- Register a new account
- Start chatting with the AI
- Try: "I have a headache and fever"

---

## 📋 URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🛑 How to Stop

Press `Ctrl + C` in both terminal windows

Or if you used RUN_ME.sh, check the PIDs it printed and:
```bash
kill <BACKEND_PID> <FRONTEND_PID>
```

---

## �� Troubleshooting

### "ModuleNotFoundError"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "OpenAI API Error"
- Check your API key in `backend/.env`
- Make sure it starts with `sk-`
- Check you have credits: https://platform.openai.com/usage

### "Port already in use"
```bash
# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9

# Kill processes on port 3000
lsof -ti:3000 | xargs kill -9
```

### Frontend won't connect to backend
- Make sure backend is running on port 8000
- Check `frontend/.env.local` has: `NEXT_PUBLIC_API_URL=http://localhost:8000`

---

## 📸 Image Upload Feature

The system supports image uploads for:
- Medical reports (PDF, images)
- Symptom photos
- Lab results
- X-rays, scans

Already built in! Just use the file upload in chat.

---

## 💡 Example Conversations

```
"I have a headache and fever for 2 days"
→ AI logs symptoms, analyzes severity

"My blood pressure is 120/80"
→ AI saves vital signs

"Tell me about aspirin"
→ AI fetches drug info from OpenFDA

"Show me my symptoms this week"
→ AI displays your tracked data
```

---

## 🔒 Your Data

- Stored locally in SQLite database: `backend/medical_agent.db`
- Memory stored in: `backend/chroma_db/`
- All conversations are private
- You can delete data anytime

---

## 🆘 Need Help?

1. Check backend logs for errors
2. Test API at http://localhost:8000/docs
3. Make sure both servers are running
4. Check your OpenAI API key is valid

---

**Enjoy your AI medical assistant!** 🏥🤖
