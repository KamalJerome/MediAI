# MediAI - Quick Start Guide

## Installation (5 minutes)

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (free trial available)

### Step 1: Install Python Packages
```bash
cd c:\THINGS\MediAI
pip install -r requirements.txt
```

### Step 2: Set Up API Key
Create `.env` file:
```
OPENAI_API_KEY=sk-...your-key-here...
```

### Step 3: Run the App
```bash
streamlit run app.py
```

Browser opens to: `http://localhost:8501`

---

## First Time Usage

### Step 1: Create a Chat
- Click **➕ New Chat** button in sidebar
- Chat ID appears (timestamp format)

### Step 2: Upload a Document (Optional)
- Click **Upload PDF** in sidebar
- Select a prescription or medical report
- Click **📤 Process PDF**
- Wait for "✅ Processed" message

### Step 3: Start Asking Questions
- Type in the chat box: "Tell me about diabetes"
- Chatbot responds with general medical info
- Chat history saves automatically

### Step 4: Ask About Your Documents
- If you uploaded a PDF, ask: "What medications are in my prescription?"
- Chatbot answers based on YOUR document

---

## Test Cases

### ✅ Allowed Questions
```
1. "What is hypertension?"
2. "Explain this blood pressure reading: 140/90"
3. "What does 'HDL cholesterol' mean?"
4. "Tell me about common cold symptoms"
5. "What is in my prescription based on this PDF?"
```

### ❌ Blocked Questions
```
1. "I have chest pain, what's wrong?" → EMERGENCY WARNING
2. "How much aspirin should I take?" → MEDICATION WARNING
3. "Do I have diabetes?" → DIAGNOSIS WARNING
4. "What treatment do you recommend?" → TREATMENT WARNING
```

---

## Common Tasks

### Load Previous Chat
1. Click chat in "Recent Chats" list
2. All messages load
3. Continue conversation

### Delete a Chat
- Right-click chat file in `./data/chats/` and delete

### Clear All Documents
- Click 🗑️ next to each document in sidebar
- Or delete files in `./data/embeddings/faiss_index/`

### Export Chat
1. Chat automatically saved to `./data/chats/`
2. Open JSON file to see messages

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Add OPENAI_API_KEY to .env file |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Slow responses" | OpenAI API rate limit - wait 30 seconds |
| "No documents" | Upload a PDF first |
| "I don't have information" | Document doesn't contain answer |

---

## Cost Estimate

- **Per conversation**: $0.01 - $0.05 USD
- **Per uploaded PDF**: $0.001 - $0.01 USD
- **Free tier**: 3 months, then paid

Monitor at: https://platform.openai.com/account/usage/overview

---

## Safety Reminders

⚠️ **This is NOT for:**
- Medical emergencies → Call 911
- Getting diagnosed → See a doctor
- Getting prescribed medicine → Talk to pharmacist/doctor
- Treatment plans → Consult healthcare professionals

✅ **This IS for:**
- General medical knowledge
- Understanding your own medical documents
- Learning about health topics
- Q&A based on uploaded reports

---

## Next Steps

1. ✅ Install packages
2. ✅ Set API key
3. ✅ Run `streamlit run app.py`
4. ✅ Create first chat
5. ✅ Upload a test PDF
6. ✅ Ask a question
7. ✅ Explore chat history

**You're ready to go!** 🎉

---

For more details, see:
- `README.md` - Full documentation
- `CONFIG.md` - Configuration guide
- `utils/` - Source code
