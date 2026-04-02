# MediAI - API Integration Guide

## OpenAI API Integration

MediAI uses the OpenAI API for two main purposes:

### 1. Text Embeddings (for RAG)
- **API**: `OpenAI Embeddings`
- **Model**: `text-embedding-ada-002`
- **Use**: Converting document chunks and user queries to vectors
- **Cost**: ~$0.0001 per 1K tokens
- **Performance**: ~100ms per embedding

### 2. Language Model (for Responses)
- **API**: `OpenAI ChatCompletion`
- **Model**: `gpt-3.5-turbo` (default)
- **Use**: Generating responses to user queries
- **Cost**: ~$0.0015 per 1K tokens
- **Performance**: ~1-3 seconds per response

### 3. Vector Store (Local)
- **Library**: FAISS (Facebook AI Similarity Search)
- **Location**: `./data/embeddings/`
- **Cost**: FREE (local, no API calls)
- **Performance**: <100ms for similarity search

---

## Cost Breakdown

### Per Action

| Action | Tokens | Estimated Cost |
|--------|--------|-----------------|
| Embed document page (1 page = ~1000 tokens) | 1000 | $0.0001 |
| User query + response (typical) | 1500 | $0.002 |
| Conversation turn with RAG | 2500 | $0.003 |

### Typical Usage Patterns

| Pattern | Tokens/Day | Cost/Day | Cost/Month |
|---------|-----------|----------|-----------|
| Light (5 chats, 2 PDFs) | 15,000 | $0.02 | $0.60 |
| Medium (15 chats, 5 PDFs) | 45,000 | $0.06 | $1.80 |
| Heavy (50 chats, 20 PDFs) | 150,000 | $0.20 | $6.00 |

---

## API Key Management

### Security Best Practices

1. **Never commit .env to git**
   ```
   .env is in .gitignore
   ```

2. **Rotate keys regularly**
   - Go to https://platform.openai.com/api_keys
   - Delete old keys
   - Create new ones

3. **Monitor usage**
   - Check https://platform.openai.com/account/usage/overview
   - Set usage limits in billing

4. **Environment-specific keys** (production)
   ```
   OPENAI_API_KEY_DEV=sk-...
   OPENAI_API_KEY_PROD=sk-...
   ```

### Using the API Key

```python
from dotenv import load_dotenv
import os

# Load from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Or set directly
os.environ["OPENAI_API_KEY"] = "sk-..."
```

---

## Rate Limiting

OpenAI has rate limits per organization:

| Plan | Requests/min | Tokens/min |
|------|-------------|-----------|
| Free Trial | 3 | 40K |
| Paid | 3,500 | 200K |
| Enterprise | Custom | Custom |

### Handling Rate Limits

The app includes automatic retry logic, but for production:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def query_gpt(question):
    # API call
    pass
```

---

## Monitoring API Usage

### 1. Real-time Monitoring
```bash
# Check usage via CLI
curl https://api.openai.com/v1/usage/tokens \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 2. Dashboard
- Go to: https://platform.openai.com/account/usage/overview
- Filter by model, date range
- View cost breakdown

### 3. Programmatic Monitoring
```python
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# Track tokens in responses
response = openai.ChatCompletion.create(...)
tokens_used = response['usage']['total_tokens']
```

---

## API Alternatives (Future)

If you want to reduce costs or use different providers:

### 1. Azure OpenAI
- Same models, often cheaper for enterprise
- Integration: Change endpoint URL
- Cost: ~30% less than OpenAI

### 2. Open Source Models
- Ollama (Llama 2, Mistral) - FREE, local
- HuggingFace API - Cheaper embeddings
- LiteLLM wrapper for switching providers

### 3. Hybrid Approach
- OpenAI for embeddings (best quality)
- Local Ollama for responses (cheaper)

---

## Troubleshooting API Issues

### Issue: "Invalid API Key"
```
Solution:
1. Check .env file has OPENAI_API_KEY=sk-...
2. No spaces or extra characters
3. Key is active (not deleted/revoked)
4. Key has appropriate permissions
```

### Issue: "Rate limit exceeded"
```
Solution:
1. Wait 30+ seconds
2. Reduce number of simultaneous requests
3. Upgrade to paid plan
4. Implement request queuing
```

### Issue: "Context length exceeded"
```
Solution:
1. Reduce RAG_SEARCH_K (fewer chunks)
2. Shorten documents
3. Increase RAG_CHUNK_OVERLAP
```

### Issue: "Slow responses"
```
Solution:
1. OpenAI experiencing issues - wait and retry
2. Network latency - check internet connection
3. Load on OpenAI servers - try different time
4. Reduce document size
```

---

## Advanced Configuration

### Custom Model Selection

```python
# In rag_manager.py
class RAGManager:
    def __init__(self, embeddings_dir: str, model_name: str = "gpt-4"):
        self.model_name = model_name  # Can use gpt-4, gpt-3.5-turbo
```

### Temperature Settings (Creativity vs Consistency)

```python
# Conservative (0.0 = deterministic)
ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
# Result: Same answer every time, no creativity

# Balanced (0.5 = recommended)
ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
# Result: Good balance

# Creative (1.0 = random)
ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1.0)
# Result: Different answer each time
```

### Token Counting

```python
import tiktoken

# Count tokens before sending
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
tokens = len(encoding.encode(text))
cost = tokens * 0.0015 / 1000
```

---

## Privacy & Data Considerations

### Data Sent to OpenAI
- ✅ Your questions/queries
- ✅ Document content (when querying)
- ✅ LLM responses

### Data NOT Sent
- ❌ Local embeddings (FAISS stores locally)
- ❌ Chat history (saved locally)
- ❌ API key (never transmitted)

### Compliance
- For HIPAA/GDPR compliance:
  - Use Azure OpenAI with private endpoints
  - Implement data retention policies
  - Encrypt local embeddings
  - See: https://openai.com/policies

---

## Cost Optimization Tips

1. **Batch similar queries**
   - Process multiple documents at once
   - Reduces overhead calls

2. **Cache embeddings**
   - Reuse embeddings for same documents
   - FAISS already does this

3. **Reduce chunk size**
   - Smaller chunks = fewer embedding calls
   - Trade-off: Less context per response

4. **Use cheaper models**
   - gpt-3.5-turbo (cheaper, faster)
   - Instead of gpt-4 (expensive, slower)

5. **Limit response length**
   - Fewer tokens = lower cost
   - Use max_tokens parameter

---

## Production Deployment

For production use beyond local testing:

```python
# Environment variables
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...
OPENAI_API_TIMEOUT=30
OPENAI_MAX_RETRIES=3

# Configuration
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_SEARCH_K=3

# Rate limiting
MAX_REQUESTS_PER_HOUR=1000
MAX_TOKENS_PER_HOUR=100000
```

---

## Support & Resources

- **API Docs**: https://platform.openai.com/docs/api-reference
- **Pricing**: https://openai.com/pricing
- **Status**: https://status.openai.com/
- **Support**: https://help.openai.com/
