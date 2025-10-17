# Complete Medical AI Agent Setup Guide

## Overview
This is an advanced medical AI agent with:
- ✅ **Medical-only responses** (rejects non-medical questions)
- ✅ **Free OCR** for medical report reading (no API key needed)
- ✅ **File upload** (PDF, JPG, PNG)
- ✅ **Clean formatting** (no ** markdown in responses)
- ✅ **Short & long-term memory** (remembers conversations)
- ✅ **8 specialized AI agents** (symptoms, medication, diagnosis, etc.)
- ✅ **5 free medical APIs** (OpenFDA, RxNorm, PubMed, ICD-10, OCR.space)

---

## Quick Start

### 1. Backend Setup
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Default Login
- Email: `demo@medical.ai`
- Password: `demo123`

---

## Features Completed

### 1. Medical-Only AI Agent
The AI will **only** answer health and medical-related questions:
- ✅ Symptoms, diagnoses, conditions
- ✅ Medications and treatments
- ✅ Medical reports and test results
- ✅ Health tracking (vitals, nutrition, exercise)
- ✅ Mental health and well-being
- ❌ Weather, sports, coding, etc. (politely declined)

### 2. File Upload & OCR
**Upload medical reports directly in chat:**
1. Click the 📎 paperclip icon in chat
2. Select PDF, JPG, or PNG file (max 10MB)
3. The AI will automatically extract text using FREE OCR.space API
4. Type "analyze" or just send a message after uploading
5. The AI will read the report and provide detailed analysis

**Supported formats:**
- PDF documents
- JPG/JPEG images
- PNG images

**How it works:**
- When you upload a file, it gets a Report ID (e.g., Report ID: 1)
- The backend automatically extracts text using OCR
- When you send a message mentioning the report, the AI fetches the extracted text
- The report_agent analyzes the content and explains it in simple terms

### 3. Clean Message Formatting
- ✅ Removed all ** markdown bold formatting
- ✅ Clean, readable responses
- ✅ Proper line breaks and spacing

### 4. Memory System
**Short-term memory (20 messages):**
- Remembers your recent conversation
- Asks "what was my last message?" - it will remember!

**Long-term memory (ChromaDB vector storage):**
- Stores summaries every 10 messages
- Retrieves relevant past context
- Remembers important health information

---

## Free APIs Used (No API Keys Required)

### 1. OCR.space (FREE)
**What it does:** Extracts text from medical report images
- **API Docs:** https://ocr.space/ocrapi
- **Free Tier:** 25,000 requests/month
- **API Key:** Uses "helloworld" (free tier)
- **Usage:** Automatic when you upload images

### 2. OpenFDA (FREE)
**What it does:** Drug information, warnings, side effects
- **API Docs:** https://open.fda.gov/apis/drug/
- **Free Tier:** Unlimited
- **No API Key:** Required
- **Usage:** Automatically used when you ask about medications

### 3. RxNorm (FREE)
**What it does:** Drug interactions, formulations
- **API Docs:** https://rxnav.nlm.nih.gov/
- **Free Tier:** Unlimited
- **No API Key:** Required
- **Usage:** Used for drug interaction checks

### 4. PubMed (FREE)
**What it does:** Medical research articles
- **API Docs:** https://www.ncbi.nlm.nih.gov/home/develop/api/
- **Free Tier:** Unlimited
- **No API Key:** Required
- **Usage:** Used for medical literature searches

### 5. ICD-10 API (FREE)
**What it does:** Medical condition codes and descriptions
- **API Docs:** https://clinicaltables.nlm.nih.gov/
- **Free Tier:** Unlimited
- **No API Key:** Required
- **Usage:** Used for diagnosis coding

---

## API Key Required

### OpenAI API Key
**What it does:** Powers the AI agents (GPT-4)
- **Get API Key:** https://platform.openai.com/api-keys
- **Pricing:** ~$0.03 per 1000 tokens (very affordable)

**How to set it up:**
1. Create account at https://platform.openai.com/
2. Go to API Keys section
3. Create new secret key
4. Add to `backend/.env`:
   ```
   OPENAI_API_KEY=sk-...your-key-here
   ```

---

## Testing the System

### Test 1: Medical Question
```
User: "I have a headache and fever. What should I do?"
AI: Provides medical advice ✅
```

### Test 2: Non-Medical Question
```
User: "What's the weather today?"
AI: "I'm a medical AI assistant and I can only help with health and medical-related questions..." ✅
```

### Test 3: File Upload and Analysis
```
1. Click 📎 in chat
2. Upload a medical report (PDF/JPG/PNG)
3. File uploads successfully (shows "Report ID: 1")
4. Type "analyze" or "what does this report say?"
5. AI extracts text via FREE OCR and provides detailed analysis ✅
```

### Test 4: Memory
```
User: "My name is John and I have diabetes"
AI: "Hello John, I understand you have diabetes..."

User: "What did I just tell you?"
AI: "You mentioned your name is John and that you have diabetes" ✅
```

### Test 5: Medication Query
```
User: "Tell me about Aspirin"
AI: Provides info from OpenFDA API ✅
```

---

## Troubleshooting

### Issue: Chat responses appearing multiple times
**Status:** ✅ FIXED
**Solution:** Updated Pydantic schema to avoid SQLAlchemy metadata conflict

### Issue: OCR not working
**Check:**
1. File size < 10MB
2. Format is PDF, JPG, or PNG
3. Backend is running
4. Check backend logs for OCR.space API errors

### Issue: Memory not working
**Check:**
1. ChromaDB is running (should start automatically)
2. Check `backend/chroma_data/` directory exists
3. Memory is stored automatically every 10 messages

### Issue: File upload fails
**Check:**
1. File size < 10MB
2. You're logged in
3. Backend API is running on port 8000
4. Check browser console for errors

---

## Project Structure

```
medicalagent/
├── backend/
│   ├── app/
│   │   ├── agents/          # 8 specialized AI agents
│   │   ├── api/             # FastAPI routes
│   │   ├── services/        # External APIs + file processing
│   │   └── models/          # Database models
│   ├── uploads/             # Uploaded files stored here
│   └── chroma_data/         # Vector database for memory
├── frontend/
│   └── src/
│       ├── pages/           # React pages (ChatPage, Dashboard)
│       └── lib/             # API client + state management
└── docs/                    # Documentation files
```

---

## Next Steps

### Optional Enhancements
1. **Add more medical APIs**
   - DrugBank (requires registration)
   - UMLS (requires license)

2. **Improve OCR accuracy**
   - OCR.space has engine 1 and 2
   - Currently using engine 2 (better for medical docs)

3. **Add voice input**
   - Use browser's speech recognition API

4. **Export chat history**
   - Download as PDF or text file

---

## Support

### Check Logs
**Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
# Watch for errors in terminal
```

**Frontend:**
```bash
cd frontend
npm run dev
# Open browser console (F12) for errors
```

### Common Error Codes
- **401 Unauthorized:** Not logged in, refresh and login again
- **422 Validation Error:** Check request format
- **500 Internal Server Error:** Check backend logs

---

## Summary

✅ **All Features Working:**
- Medical-only responses
- File upload with FREE OCR
- Clean formatting (no ** markdown)
- Short & long-term memory
- 8 specialized AI agents
- 5 free medical APIs

**No API keys needed for:**
- OCR.space
- OpenFDA
- RxNorm
- PubMed
- ICD-10

**Only 1 API key required:**
- OpenAI (for AI agents)

**Ready to use!** 🎉
