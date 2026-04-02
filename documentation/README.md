# MediAI - Medical Information Chatbot

A ChatGPT-style medical chatbot built with Python, Streamlit, and LangChain. Provides general medical information while strictly preventing diagnosis, medication prescriptions, and emergency medical advice.

## Features

✅ **Safe Medical Information**
- Provides general medical information only
- Blocks diagnosis requests
- Blocks medication/dosage requests
- Blocks emergency calls (directs to 911)
- Blocks treatment advice

✅ **Document-Based Q&A (RAG)**
- Upload PDFs (prescriptions, medical reports)
- Extract and process document text
- Answer questions based on uploaded documents
- Returns "I don't have enough information" when needed

✅ **Chat Management**
- Create new conversations
- Load and continue existing chats
- View chat history
- Export chats to text files
- In-chat memory (remembers conversation context)

✅ **User-Friendly Interface**
- ChatGPT-like interface with Streamlit
- Sidebar for document management and chat history
- Real-time safety warnings
- Emergency mode alerts

## Tech Stack

- **Python 3.8+** - Core language
- **Streamlit** - Web UI
- **OpenAI GPT** - Language model
- **LangChain** - RAG + memory management
- **FAISS** - Vector embeddings storage (local)
- **PyPDF2** - PDF processing
- **Local storage** - No cloud deployment

## Installation

### 1. Clone or Setup Project

```bash
cd c:\THINGS\MediAI
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up OpenAI API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

Or set it as an environment variable:

```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Mac/Linux
export OPENAI_API_KEY=your_api_key_here
```

## Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
MediAI/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── utils/
│   ├── safety_checker.py     # Safety detection for unsafe requests
│   ├── pdf_processor.py      # PDF text extraction
│   ├── rag_manager.py        # RAG implementation with embeddings
│   └── chat_manager.py       # Chat history management
├── data/
│   ├── chats/               # Chat history files (JSON)
│   ├── embeddings/          # Vector embeddings (FAISS)
│   │   ├── faiss_index/     # FAISS vector store
│   │   └── documents_info.json
│   └── uploads/             # Temporary file storage
└── .env                      # OpenAI API key (create this)
```

## Usage Guide

### Starting a New Chat

1. Click **➕ New Chat** in the sidebar
2. A new chat session is created
3. Start asking questions

### Uploading Documents

1. Click **Upload PDF** in the sidebar
2. Select a prescription or medical report (PDF format)
3. Click **📤 Process PDF**
4. The document is analyzed and embeddings are created
5. Ask questions about the document

### Asking Questions

**Safe Questions** (will be answered):
- "What is diabetes?"
- "Can you explain this blood test result from my report?"
- "What does this medication name mean?"
- "Tell me about cholesterol levels"

**Unsafe Questions** (will be blocked):
- "I think I have diabetes, what should I do?" (Diagnosis)
- "How much aspirin should I take?" (Medication/dosage)
- "I'm having chest pain" (Emergency)
- "What treatment do you recommend?" (Treatment advice)

### Loading Previous Chats

1. Click **📂 Load Chat** or click a chat in "Recent Chats"
2. All previous messages reload
3. You can continue the conversation

### Viewing Chat History

- **Recent Chats** - Shows last 5 chats in sidebar
- **Export Chat** - Download chat as text file (upcoming feature)

## Safety Features

### Blocked Request Types

1. **Diagnosis Requests**
   - Keywords: "diagnosis", "do i have", "could i have", "symptoms mean"
   - Response: Warning to consult a healthcare professional

2. **Medication Requests**
   - Keywords: "prescription", "dosage", "how much should", "can i take"
   - Response: Warning that only doctors can prescribe

3. **Emergency Requests**
   - Keywords: "emergency", "dying", "heart attack", "call 911", "can't breathe"
   - Response: Immediate action required message with 911 direction

4. **Treatment Requests**
   - Keywords: "treat", "cure", "therapy", "surgery", "how to recover"
   - Response: Warning to consult qualified healthcare providers

### Response Rules

- All responses are checked against safety filters
- Emergency requests get highest priority
- Generic/hallucinated medical facts are avoided
- Chatbot acknowledges limitations clearly
- RAG ensures answers come from documents only

## RAG (Retrieval Augmented Generation) Details

### How It Works

1. **Document Processing**
   - PDFs are converted to text
   - Text is split into 1000-token chunks
   - Chunks overlap by 200 tokens for context

2. **Embeddings**
   - OpenAI embeddings convert text to vectors
   - Vectors stored locally using FAISS
   - No cloud storage, all local

3. **Query Answering**
   - User question is converted to embedding
   - Top 3 relevant chunks retrieved
   - GPT-3.5 answers based on retrieved context
   - Response marked "insufficient information" if no match

### Vector Store Management

- **Location**: `./data/embeddings/faiss_index`
- **Metadata**: `./data/embeddings/documents_info.json`
- **Documents**: Tracked by name and hash
- **Deletion**: Removes document from metadata

## Chat History Storage

- **Format**: JSON files
- **Location**: `./data/chats/YYYYMMDD_HHMMSS.json`
- **Contents**:
  - Chat ID (timestamp)
  - Creation date
  - All messages (user + assistant)
  - Documents used in chat

## Important Notes

⚠️ **This chatbot is NOT for emergency medical advice**
- Always call 911 for emergencies
- Always consult healthcare professionals for diagnosis
- Always consult healthcare professionals for medications
- Use this tool for informational purposes only

🔒 **Data Privacy**
- All data stored locally on your machine
- No data sent to cloud except API calls to OpenAI
- Chat history saved in `./data/chats/`
- Embeddings saved in `./data/embeddings/`

💾 **No Deployment Infrastructure**
- Single-machine local application
- No databases, servers, or cloud services
- Runs entirely on your computer

## API Costs

OpenAI API calls will incur costs:
- **Embeddings**: ~$0.0001 per 1K tokens
- **GPT-3.5-turbo**: ~$0.001-0.002 per completion
- **Estimate**: $0.01-0.05 per conversation

Monitor usage in your OpenAI dashboard.

## Troubleshooting

### Issue: "Error: OpenAI API key not found"
**Solution**: Set OPENAI_API_KEY in .env file or environment variable

### Issue: "PyPDF2 is not installed"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "No documents uploaded yet"
**Solution**: Upload a PDF using the "Upload PDF" button in sidebar

### Issue: "I don't have enough information"
**Solution**: This means the uploaded documents don't contain relevant information

### Issue: Slow responses
**Solution**: May be OpenAI API rate limiting - wait a moment and retry

## Future Enhancements

- [ ] Export chat to PDF
- [ ] Multi-document search
- [ ] Chat search/filtering
- [ ] Settings page for model selection
- [ ] Response confidence scores
- [ ] Document citation in responses
- [ ] Custom instruction templates
- [ ] Dark mode

## License

This project is for educational purposes.

## Support

For issues or questions, please refer to the documentation or create an issue.

---

**Remember: This chatbot provides information only. Always consult qualified healthcare professionals for medical decisions.**
