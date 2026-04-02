# MediAI - Architecture & Flow Diagrams

## System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        MediAI System Architecture                  │
└────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      User Interface Layer                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Streamlit Web Application (app.py)           │ │
│  │  • Chat Interface                                          │ │
│  │  • PDF Upload Widget                                       │ │
│  │  • Chat History Browser                                    │ │
│  │  • Document Management                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Safety Checker  │ │  Chat Manager    │ │  RAG Manager     │
│ (safety_checker) │ │ (chat_manager)   │ │ (rag_manager)    │
│                  │ │                  │ │                  │
│ • Diagnosis      │ │ • Create chat    │ │ • Add documents  │
│ • Medication     │ │ • Load chat      │ │ • Query docs     │
│ • Emergency      │ │ • Add messages   │ │ • Embeddings     │
│ • Treatment      │ │ • Get history    │ │ • Retrieval      │
└──────────────────┘ └──────────────────┘ └──────────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌──────────────────┐     ┌──────────────────┐
        │  Local Storage   │     │  OpenAI APIs     │
        │                  │     │                  │
        │ • Chat History   │     │ • Embeddings     │
        │   (JSON)         │     │ • Chat Complete  │
        │ • Embeddings     │     │                  │
        │   (FAISS)        │     │ (via LangChain)  │
        │ • PDF Docs       │     │                  │
        └──────────────────┘     └──────────────────┘
```

---

## Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   User Message Flow                             │
└─────────────────────────────────────────────────────────────────┘

    User Types Message
            │
            ▼
    ┌──────────────────────────┐
    │  Check Safety Filters    │ ← PRIORITY CHECK
    │  (is_unsafe_request)     │
    └────────┬─────────────────┘
             │
    ┌────────┴─────────────────┐
    │                          │
  UNSAFE                     SAFE
    │                          │
    ▼                          ▼
Return                  ┌──────────────────────────┐
Warning                 │ Check Uploaded Documents │
    │                   └────────┬─────────────────┘
    │                            │
    │              ┌─────────────┴─────────────┐
    │              │                           │
    │         Documents                    No Docs
    │         Uploaded?                        │
    │              │                           ▼
    │            YES                       Return:
    │              │                    "Upload a PDF"
    │              ▼
    │      ┌──────────────────────────┐
    │      │  Query RAG with LangChain│
    │      │                          │
    │      │ 1. Embed user query      │
    │      │ 2. Search FAISS (top 3)  │
    │      │ 3. Get context           │
    │      │ 4. Query GPT-3.5         │
    │      └────────┬─────────────────┘
    │              │
    │              ▼
    │      ┌──────────────────────────┐
    │      │  Receive GPT Response    │
    │      └────────┬─────────────────┘
    │              │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────────┐
    │  Add to Chat History     │
    │  (ChatManager)           │
    └────────┬─────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │  Display to User         │
    │  in Streamlit Chat UI    │
    └──────────────────────────┘
```

---

## Safety Detection System

```
┌──────────────────────────────────────────────────────────────┐
│              Safety Detection Hierarchy                       │
└──────────────────────────────────────────────────────────────┘

User Input: "I have severe chest pain"
    │
    ▼
┌─────────────────────────────────────────┐
│ PRIORITY 1: EMERGENCY CHECK             │ ◄── Highest Priority
│                                         │
│ Keywords: "emergency", "dying",         │
│          "heart attack", "can't         │
│          breathe", "severe pain"        │
│                                         │
│ Result: MATCH ✓                         │
└─────────────────────────────────────────┘
    │
    ▼ (Match found, return immediately)
┌────────────────────────────────────────────┐
│ 🚨 EMERGENCY - IMMEDIATE ACTION REQUIRED   │
│                                            │
│ This appears to be a medical emergency.    │
│ Please seek immediate medical help:        │
│ - Call 911 (US) or local emergency number │
│ - Visit the nearest emergency room        │
│                                            │
│ Do not rely on this chatbot.               │
└────────────────────────────────────────────┘

─────────────────────────────────────────────────────────────────

User Input: "Do I have diabetes?"
    │
    ▼
┌─────────────────────────────────────────┐
│ PRIORITY 1: EMERGENCY CHECK             │
│ Keywords: emergency, dying, etc.        │
│ Result: NO MATCH ✗                      │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ PRIORITY 2: DIAGNOSIS CHECK             │
│                                         │
│ Keywords: "diagnosis", "do i have",    │
│          "what disease", "symptoms"    │
│                                         │
│ Result: MATCH ✓                         │
└─────────────────────────────────────────┘
    │
    ▼ (Match found, return immediately)
┌────────────────────────────────────────────┐
│ ⚠️ I Cannot Provide Medical Diagnosis      │
│                                            │
│ I cannot diagnose conditions based on      │
│ symptoms. Please consult a qualified       │
│ healthcare professional or visit a doctor. │
└────────────────────────────────────────────┘

─────────────────────────────────────────────────────────────────

User Input: "What is diabetes?"
    │
    ▼
┌─────────────────────────────────────────┐
│ PRIORITY 1: EMERGENCY CHECK             │
│ Result: NO MATCH ✗                      │
├─────────────────────────────────────────┤
│ PRIORITY 2: DIAGNOSIS CHECK             │
│ Result: NO MATCH ✗                      │
├─────────────────────────────────────────┤
│ PRIORITY 3: MEDICATION CHECK            │
│ Result: NO MATCH ✗                      │
├─────────────────────────────────────────┤
│ PRIORITY 4: TREATMENT CHECK             │
│ Result: NO MATCH ✗                      │
└─────────────────────────────────────────┘
    │
    ▼ (All checks pass)
┌────────────────────────────────────────────┐
│ SAFE REQUEST - Proceed to RAG              │
│                                            │
│ Result: General medical information        │
│ response (if documents available)          │
└────────────────────────────────────────────┘
```

---

## RAG Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│            Retrieval Augmented Generation (RAG)              │
└──────────────────────────────────────────────────────────────┘

DOCUMENT INGESTION PHASE
═══════════════════════════════════════════════════════════════

    PDF File Upload
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Extract Text (PyPDF2)               │
    │                                     │
    │ Input: prescription.pdf             │
    │ Output: ~10,000 character text      │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Split into Chunks                   │
    │                                     │
    │ Chunk Size: 1000 tokens             │
    │ Overlap: 200 tokens                 │
    │ Result: ~20 chunks from 10K chars   │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Generate Embeddings                 │
    │                                     │
    │ API: OpenAI text-embedding-ada-002  │
    │ Input: Each chunk (text)            │
    │ Output: Vector (1536 dimensions)    │
    │ Cost: ~$0.0001 per 1K tokens        │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Store in FAISS Vector Store         │
    │                                     │
    │ Location: ./data/embeddings/        │
    │ Type: Local, no cloud storage       │
    │ Speed: <100ms retrieval             │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Save Metadata                       │
    │                                     │
    │ documents_info.json:                │
    │ - Document name                     │
    │ - Upload time                       │
    │ - Chunk count                       │
    │ - Content length                    │
    └─────────────────────────────────────┘

─────────────────────────────────────────────────────────────────

QUERY PHASE
═══════════════════════════════════════════════════════════════

    User Question
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Embed Query                         │
    │                                     │
    │ Same model: text-embedding-ada-002  │
    │ Input: "What medications in doc?"   │
    │ Output: Vector (1536 dimensions)    │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Search FAISS                        │
    │                                     │
    │ Algorithm: Similarity Search        │
    │ K: 3 (retrieve top 3)               │
    │ Speed: <100ms                       │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Retrieved Chunks                    │
    │                                     │
    │ Chunk 1: "Lisinopril 10mg daily..." │
    │ Chunk 2: "Take with water..."       │
    │ Chunk 3: "Side effects include..."  │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Build LLM Prompt                    │
    │                                     │
    │ System: "You are medical chatbot..." │
    │ Context: [Top 3 chunks]             │
    │ Question: "What medications..."     │
    │ Chat History: [Last 6 messages]     │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Query GPT-3.5-turbo                 │
    │                                     │
    │ API: OpenAI Chat Completions        │
    │ Model: gpt-3.5-turbo                │
    │ Temperature: 0 (deterministic)      │
    │ Cost: ~$0.0015 per 1K tokens        │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ LLM Response                        │
    │                                     │
    │ "Your prescription contains:        │
    │  Lisinopril: 10mg, once daily.      │
    │  Used for high blood pressure..."   │
    └─────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────┐
    │ Return to User                      │
    │                                     │
    │ Display in chat interface           │
    │ Save to chat history                │
    │ Record document usage               │
    └─────────────────────────────────────┘
```

---

## Data Storage Structure

```
┌──────────────────────────────────────────────────────────────┐
│                    Local File Storage                        │
└──────────────────────────────────────────────────────────────┘

MediAI/
│
├── data/
│   │
│   ├── chats/                          ← Chat History
│   │   ├── 20240126_140522.json        ← Chat Session 1
│   │   ├── 20240126_141033.json        ← Chat Session 2
│   │   └── ...                         ← More chats
│   │
│   └── embeddings/                     ← Vector Store
│       ├── faiss_index/
│       │   ├── index.faiss             ← FAISS index file
│       │   ├── index.pkl               ← Pickle format
│       │   └── ...
│       └── documents_info.json         ← Metadata

─────────────────────────────────────────────────────────────────

CHAT FILE STRUCTURE
═══════════════════════════════════════════════════════════════

File: 20240126_140522.json
{
  "chat_id": "20240126_140522",
  "created_at": "2024-01-26T14:05:22.123456",
  "messages": [
    {
      "role": "user",
      "content": "What is diabetes?",
      "timestamp": "2024-01-26T14:05:25.123456"
    },
    {
      "role": "assistant",
      "content": "Diabetes is a chronic condition...",
      "timestamp": "2024-01-26T14:05:27.123456"
    },
    {
      "role": "system",
      "content": "Document added: prescription.pdf",
      "timestamp": "2024-01-26T14:06:00.123456"
    }
  ],
  "documents_used": ["prescription.pdf"]
}

─────────────────────────────────────────────────────────────────

DOCUMENTS METADATA
═══════════════════════════════════════════════════════════════

File: documents_info.json
{
  "prescription.pdf": {
    "added_at": "2024-01-26T14:06:00.123456",
    "chunks": 15,
    "content_length": 12000
  },
  "report.pdf": {
    "added_at": "2024-01-26T14:10:00.123456",
    "chunks": 22,
    "content_length": 18500
  }
}

─────────────────────────────────────────────────────────────────

FAISS INDEX
═══════════════════════════════════════════════════════════════

Directory: faiss_index/
├── index.faiss          ← Binary FAISS index (multiples of 1536 dims)
├── index.pkl            ← Pickle format for metadata
└── config.json          ← Configuration
```

---

## User Interface Layout

```
┌────────────────────────────────────────────────────────────────┐
│                        MediAI Web UI                           │
└────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌─────────────────────────────────────┐
│      SIDEBAR         │  │         MAIN CHAT AREA              │
│                      │  │                                     │
│ 🏥 MediAI            │  │  🏥 MediAI - Medical Information   │
│ ─────────────────    │  │      Chatbot                        │
│                      │  │                                     │
│ 💬 CHAT              │  │  Chat ID: 20240126_140522           │
│ [➕ New Chat]        │  │  📄 1 documents(s) loaded           │
│ [📂 Load Chat]       │  │  💬 12 message(s)                   │
│                      │  │  ──────────────────────             │
│ Current Chat:        │  │                                     │
│ 20240126_140522      │  │  ┌────────────────────┐             │
│                      │  │  │ User: What is      │             │
│ 📝 RECENT CHATS      │  │  │ diabetes?          │             │
│                      │  │  └────────────────────┘             │
│ [20240126_140522]    │  │                                     │
│ [20240126_133344]    │  │  ┌────────────────────┐             │
│ [20240125_150211]    │  │  │ Assistant:         │             │
│                      │  │  │ Diabetes is a      │             │
│ 📄 DOCUMENTS         │  │  │ chronic condition  │             │
│                      │  │  │ characterized by...│             │
│ [Upload PDF]         │  │  └────────────────────┘             │
│ ┌──────────────────┐ │  │                                     │
│ │ 📋 prescription  │ │  │  ┌────────────────────┐             │
│ │   .pdf      [🗑️] │ │  │  │ User: What's the   │             │
│ │ 📋 report.pdf    │ │  │  │ difference from    │             │
│ │            [🗑️] │ │  │  │ Type 1?            │             │
│ └──────────────────┘ │  │  └────────────────────┘             │
│                      │  │                                     │
│ ⚠️ SAFETY INFO       │  │  [Type your message here...]       │
│                      │  │                                     │
│ [View Safety       │  │  [Send]                             │
│  Guidelines]       │  │                                     │
│                      │  │                                     │
└──────────────────────┘  └─────────────────────────────────────┘
```

---

## Technology Stack Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Technology Stack                          │
└──────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER                                          │
├────────────────────────────────────────────────────────────┤
│ Streamlit 1.28.1                                           │
│ ├─ Web UI Framework                                        │
│ ├─ Real-time chat interface                               │
│ ├─ File upload widget                                      │
│ └─ Responsive sidebar                                      │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│ CORE LOGIC LAYER                                           │
├────────────────────────────────────────────────────────────┤
│ Python 3.8+                                                │
│ ├─ Safety Checker (51 keywords)                            │
│ ├─ Chat Manager (JSON persistence)                         │
│ ├─ RAG Manager (LangChain)                                 │
│ └─ PDF Processor (PyPDF2)                                  │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│ EXTERNAL API LAYER                                         │
├────────────────────────────────────────────────────────────┤
│ OpenAI APIs                                                │
│ ├─ text-embedding-ada-002 (embeddings)                     │
│ ├─ gpt-3.5-turbo (chat responses)                          │
│ └─ LangChain Wrapper (via openai package)                  │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│ DATA STORAGE LAYER                                         │
├────────────────────────────────────────────────────────────┤
│ Local File System                                          │
│ ├─ JSON Files (chat history)                              │
│ ├─ FAISS (vector embeddings)                              │
│ └─ Metadata (documents info)                              │
└────────────────────────────────────────────────────────────┘

DEPENDENCIES:
  openai             → OpenAI API client
  langchain          → RAG orchestration
  faiss-cpu          → Vector storage
  PyPDF2             → PDF processing
  python-dotenv      → Environment config
```

---

## Deployment Considerations

```
┌──────────────────────────────────────────────────────────────┐
│           MediAI Deployment Options                         │
└──────────────────────────────────────────────────────────────┘

CURRENT: Local Development
═══════════════════════════════════════════════════════════════
┌──────────────────────┐
│  Your Computer       │
├──────────────────────┤
│ • Streamlit App      │
│ • Data Storage       │
│ • Embeddings (FAISS) │
│ • Chat History       │
└──────────────────────┘
         │
         └─→ [OpenAI API] (via internet)

─────────────────────────────────────────────────────────────────

OPTION 1: Cloud Deployment (Heroku/Railway)
═══════════════════════════════════════════════════════════════
┌──────────────────────┐
│  Cloud Server        │
├──────────────────────┤
│ • Streamlit App      │
│ • Data Storage       │
│ • Embeddings (FAISS) │
└──────────────────────┘
    │           │
    ▼           ▼
 [Database]  [OpenAI API]

Pros:
  ✅ Accessible from anywhere
  ✅ Always running
  ✅ Easy to share
  ✅ Scalable

Cons:
  ❌ Higher costs
  ❌ Data in cloud
  ❌ HIPAA complications
  ❌ Infrastructure management

─────────────────────────────────────────────────────────────────

OPTION 2: Docker Containerization
═══════════════════════════════════════════════════════════════
┌──────────────────────────┐
│  Docker Container        │
├──────────────────────────┤
│ • Streamlit App          │
│ • All dependencies       │
│ • Data volumes           │
│ • Environment config     │
└──────────────────────────┘

docker build -t mediAI .
docker run -p 8501:8501 mediAI

Pros:
  ✅ Reproducible environment
  ✅ Easy deployment
  ✅ Consistent across machines

Cons:
  ❌ Requires Docker knowledge
  ❌ Still need hosting solution

─────────────────────────────────────────────────────────────────

OPTION 3: Azure OpenAI + Private Endpoints (HIPAA)
═══════════════════════════════════════════════════════════════
┌──────────────────────────┐
│  Private VNet            │
├──────────────────────────┤
│ • Streamlit App          │
│ • Data Storage (ACS)     │
│ • Private Endpoint       │
│ └─→ Azure OpenAI         │
└──────────────────────────┘

Pros:
  ✅ HIPAA compliant
  ✅ No data leaves VNet
  ✅ Enterprise ready

Cons:
  ❌ High complexity
  ❌ Higher costs
  ❌ Requires Azure expertise
```

---

## Cost Analysis

```
┌──────────────────────────────────────────────────────────────┐
│                MediAI Cost Breakdown                         │
└──────────────────────────────────────────────────────────────┘

PER ACTION COSTS
═══════════════════════════════════════════════════════════════

1. PDF Document Processing
   Upload: 20-page PDF (~10,000 words)
   │
   ├─ Text Extraction: FREE (local)
   ├─ Chunking: FREE (local)
   │
   └─ Embeddings:
       Chunks: ~10 chunks × 1000 tokens = 10,000 tokens
       Cost: 10,000 × $0.0001 / 1000 = $0.001

2. User Query Response
   User: "What's in my prescription?"
   │
   ├─ Safety Check: FREE (local)
   ├─ Query Embedding: ~100 tokens × $0.0001/1K = $0.00001
   ├─ FAISS Search: FREE (local)
   │
   └─ GPT Response:
       Input: Context (3 chunks) + Query + History
       Total: ~1500 tokens
       Output: ~200 tokens
       Cost: (1500 + 200) × $0.0015 / 1000 = $0.0026

   TOTAL PER QUERY: ~$0.003

3. Chat Session (10 queries)
   Cost: 10 × $0.003 = $0.03

─────────────────────────────────────────────────────────────────

TYPICAL USAGE SCENARIOS
═══════════════════════════════════════════════════════════════

LIGHT USER (5 chats/month, 2 PDFs/month)
  PDFs: 2 × $0.001 = $0.002
  Queries: (5 chats × 5 queries) × $0.003 = $0.075
  Monthly: ~$0.08

MEDIUM USER (15 chats/month, 5 PDFs/month)
  PDFs: 5 × $0.001 = $0.005
  Queries: (15 chats × 10 queries) × $0.003 = $0.45
  Monthly: ~$0.46

HEAVY USER (50 chats/month, 20 PDFs/month)
  PDFs: 20 × $0.001 = $0.02
  Queries: (50 chats × 15 queries) × $0.003 = $2.25
  Monthly: ~$2.30

─────────────────────────────────────────────────────────────────

COST REDUCTION STRATEGIES
═══════════════════════════════════════════════════════════════

1. Reduce RAG_SEARCH_K
   Current: 3 chunks
   New: 2 chunks
   Savings: ~20%

2. Shorter documents
   Break into smaller PDFs
   Fewer tokens to process
   Savings: ~30%

3. Caching
   Reuse embeddings for same documents
   Savings: Significant

4. Batch operations
   Process multiple queries at once
   Savings: Reduced overhead
```

---

This comprehensive architecture documentation provides a complete view of MediAI's design, data flow, and operational considerations.
