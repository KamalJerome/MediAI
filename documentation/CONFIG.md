# MediAI Configuration

## Environment Variables

Create a `.env` file in the project root with the following:

```
OPENAI_API_KEY=your_api_key_here
```

## Optional Configuration Variables

```
# Model configuration
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0

# Embedding model
EMBEDDING_MODEL=text-embedding-ada-002

# RAG parameters
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_SEARCH_K=3

# API timeout (seconds)
OPENAI_TIMEOUT=30
```

## File Storage Locations

### Chat History
- **Path**: `./data/chats/`
- **Format**: JSON
- **Naming**: `YYYYMMDD_HHMMSS.json`

### Vector Embeddings
- **Path**: `./data/embeddings/`
- **Format**: FAISS vector store
- **Metadata**: `documents_info.json`

### Temporary Files
- **Path**: `./temp_*` (deleted after processing)

## OpenAI API Setup

### Step 1: Create OpenAI Account
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Go to Account Settings → Billing Setup
4. Add a payment method

### Step 2: Create API Key
1. Go to API Keys → Create new secret key
2. Copy the key (keep it secret!)
3. Add to `.env` file

### Step 3: Verify Connection
The app will test the API key on startup. If there's an error, check:
- Key is correctly copied
- `.env` file is in the project root
- No extra spaces or quotes around key

## Safety Configuration

Safety keywords are defined in `utils/safety_checker.py`:

- **Diagnosis keywords**: 13 keywords
- **Medication keywords**: 16 keywords
- **Emergency keywords**: 14 keywords
- **Treatment keywords**: 8 keywords

To modify safety rules, edit `utils/safety_checker.py`:

```python
DIAGNOSIS_KEYWORDS = [
    "diagnosis", "diagnose", # add more keywords here
]
```

## Performance Tuning

### For Faster Responses
```python
# In utils/rag_manager.py
RAG_SEARCH_K = 2  # Retrieve fewer chunks (default: 3)

# In app.py
OPENAI_TEMPERATURE = 0.2  # Faster, more consistent (default: 0)
```

### For Better Accuracy
```python
RAG_SEARCH_K = 5  # Retrieve more chunks
RAG_CHUNK_SIZE = 500  # Smaller chunks for precision
OPENAI_TEMPERATURE = 0.7  # More creative responses
```

### For Lower API Costs
- Reduce RAG_SEARCH_K
- Use shorter documents
- Close and reopen app to clear memory

## Monitoring

### Check API Usage
1. Go to https://platform.openai.com/account/usage/overview
2. Monitor costs and token usage

### View Chat History
- All chats saved in `./data/chats/`
- Open JSON files to inspect messages

### Inspect Embeddings
- Vector store in `./data/embeddings/faiss_index/`
- Metadata in `./data/embeddings/documents_info.json`
