# MediAI - Deployment & Production Checklist

## Pre-Deployment Verification

### ✅ Code Quality
- [ ] All imports are available in requirements.txt
- [ ] No hardcoded API keys or passwords
- [ ] Error handling is comprehensive
- [ ] Logging is configured
- [ ] Comments are clear and helpful

### ✅ Functionality Testing
- [ ] Safety checker blocks all unsafe requests
- [ ] RAG works with various PDF types
- [ ] Chat history persists correctly
- [ ] File uploads are handled safely
- [ ] API calls don't exceed rate limits

### ✅ Documentation
- [ ] README.md is complete
- [ ] QUICKSTART.md is clear
- [ ] API_GUIDE.md covers integration
- [ ] ARCHITECTURE.md explains design
- [ ] All code has docstrings

### ✅ Security
- [ ] .env not in version control
- [ ] No credentials in code
- [ ] Input validation implemented
- [ ] File upload restrictions set
- [ ] API key rotation plan documented

---

## Deployment Options

### Option 1: Local (Development)

**Use Case**: Personal use, testing, low-security environments

```bash
# Setup
python setup.py

# Run
streamlit run app.py
```

**Pros**: Simple, no infrastructure, immediate
**Cons**: Not shareable, single-machine only

**Checklist**:
- [ ] Python 3.8+ installed
- [ ] requirements.txt dependencies installed
- [ ] .env file with API key created
- [ ] data/ directories created
- [ ] Tested with sample PDF

---

### Option 2: Docker (Containerized)

**Use Case**: Consistent environment, easy deployment, sharing

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=""

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Deploy**:
```bash
# Build
docker build -t mediai:latest .

# Run locally
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... mediai:latest

# Push to registry
docker tag mediai:latest myregistry/mediai:latest
docker push myregistry/mediai:latest
```

**Checklist**:
- [ ] Docker installed
- [ ] Dockerfile created and tested
- [ ] requirements.txt up to date
- [ ] Image builds successfully
- [ ] Tested locally before pushing
- [ ] .dockerignore configured
- [ ] Environment variables handled

---

### Option 3: Streamlit Cloud

**Use Case**: Easy web deployment, free tier available

**Setup**:
1. Create GitHub repository
2. Push code to GitHub
3. Go to https://share.streamlit.io/
4. Connect GitHub account
5. Select repository and branch
6. Add secrets (OPENAI_API_KEY)

**Checklist**:
- [ ] GitHub account created
- [ ] Code pushed to GitHub
- [ ] .gitignore prevents data/ upload
- [ ] secrets.toml created locally for testing
- [ ] OPENAI_API_KEY added to Streamlit secrets
- [ ] README.md explains usage
- [ ] No hardcoded paths in code
- [ ] data/chats.json doesn't contain sensitive info

**Note**: Free tier has limitations
- 1 app, 1 region only
- 1GB RAM, limited CPU
- Restart every 7 days of inactivity
- Data persists between restarts

---

### Option 4: Heroku

**Use Case**: Traditional Python web app hosting, paid

**Procfile**:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Deploy**:
```bash
heroku login
heroku create mediai-app
heroku config:set OPENAI_API_KEY=sk-...
git push heroku main
```

**Checklist**:
- [ ] Heroku account created
- [ ] Git repository initialized
- [ ] Procfile created
- [ ] requirements.txt complete
- [ ] Tested locally
- [ ] Environment variables set
- [ ] Buildpack configured (Python)
- [ ] Monitor dyno usage

---

### Option 5: Azure Container Apps

**Use Case**: Enterprise, HIPAA-compliant option

**Setup** (via Azure CLI):
```bash
az containerapp create \
  --name mediai \
  --resource-group mygroup \
  --image myregistry.azurecr.io/mediai:latest \
  --target-port 8501 \
  --environment myenv \
  --secrets "apikey=$OPENAI_API_KEY"
```

**Checklist**:
- [ ] Azure account created
- [ ] Container registry set up
- [ ] Docker image built and pushed
- [ ] Resource group created
- [ ] Container app environment created
- [ ] Secrets configured
- [ ] Network security configured
- [ ] Data encryption enabled
- [ ] Monitoring set up

---

### Option 6: AWS Deployment

**Use Case**: Large scale, AWS ecosystem

**Services**:
- EC2: Compute
- RDS: Database (optional)
- S3: Storage
- CloudFront: CDN

**Setup**:
```bash
# Create EC2 instance
# Install Python, dependencies
# Upload code
# Run Streamlit with gunicorn
```

**Checklist**:
- [ ] AWS account created
- [ ] EC2 instance configured
- [ ] Security groups configured
- [ ] SSH access set up
- [ ] Python environment installed
- [ ] Nginx/Apache configured (reverse proxy)
- [ ] SSL certificate installed
- [ ] Auto-scaling configured
- [ ] Monitoring/CloudWatch set up

---

## Production Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional but recommended
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0
RAG_CHUNK_SIZE=1000
RAG_SEARCH_K=3

# For scaling
MAX_REQUESTS_PER_HOUR=1000
MAX_TOKENS_PER_HOUR=100000
REQUEST_TIMEOUT=30
```

### Security Settings

**API Key Management**:
- [ ] Use environment variables only
- [ ] Never commit .env to git
- [ ] Rotate keys monthly
- [ ] Use separate keys per environment
- [ ] Monitor API usage

**Data Security**:
- [ ] Enable HTTPS/TLS
- [ ] Encrypt data at rest
- [ ] Restrict file upload types
- [ ] Validate all inputs
- [ ] Sanitize user input

**Access Control**:
- [ ] Add authentication (if multi-user)
- [ ] Implement rate limiting
- [ ] Log all access
- [ ] Set up alerts

---

## Monitoring & Maintenance

### Performance Monitoring

```python
# Add monitoring to app.py
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track response times
start_time = time.time()
response = rag_manager.query(question)
duration = time.time() - start_time
logger.info(f"Query took {duration:.2f}s")
```

### Health Checks

```bash
# Health endpoint (add to app)
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now()}
```

### Logging

```python
# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics to Track

- [ ] API response time (target: <3s)
- [ ] Error rate (target: <1%)
- [ ] Uptime (target: 99.9%)
- [ ] Token usage (cost monitoring)
- [ ] User sessions active
- [ ] PDF processing time
- [ ] Safety warning triggers

---

## Cost Management

### API Cost Monitoring

**Check OpenAI Usage**:
1. Go to https://platform.openai.com/account/usage/overview
2. Set monthly budget alerts
3. Review costs weekly

**Cost Optimization**:
- [ ] Reduce RAG_SEARCH_K (3 → 2)
- [ ] Limit document size
- [ ] Cache embeddings
- [ ] Use gpt-3.5-turbo (cheaper than gpt-4)
- [ ] Set max_tokens limit

### Infrastructure Cost

| Option | Monthly Cost |
|--------|-------------|
| Local | $0 |
| Docker | $5-50 |
| Streamlit Cloud | Free (1 app) |
| Heroku | $7-50 |
| Azure Container Apps | $20-100 |
| AWS EC2 | $10-100 |

---

## Backup & Recovery

### Data Backup Strategy

**Chat History**:
```bash
# Backup chats
cp -r data/chats/ backup/chats-$(date +%Y%m%d)/

# Restore
cp -r backup/chats-20240126/* data/chats/
```

**Embeddings**:
```bash
# Backup embeddings (FAISS)
cp -r data/embeddings/ backup/embeddings-$(date +%Y%m%d)/
```

**Automated Backup** (cron job):
```bash
0 2 * * * /home/user/backup.sh  # Daily at 2 AM
```

### Recovery Procedure

1. Stop the application
2. Restore from latest backup
3. Verify data integrity
4. Restart application
5. Test functionality

---

## Scale-Up Plan

As usage grows:

### Phase 1: Optimize (Local → Docker)
- Containerize application
- Move to cloud hosting
- Set up monitoring

### Phase 2: Enhance (Add Features)
- Add user authentication
- Implement database (PostgreSQL)
- Add more safety checks
- Enhance RAG (re-ranking)

### Phase 3: Scale (Production Ready)
- Load balancer
- Multiple instances
- Redis cache for embeddings
- Dedicated database server
- CDN for assets
- Advanced monitoring

---

## Rollback Plan

If deployment fails:

1. **Immediate**: Stop new deployment
2. **Quick**: Revert to previous version
3. **Verify**: Test previous version
4. **Communicate**: Update users
5. **Investigate**: Root cause analysis
6. **Fix**: Address issue
7. **Retry**: Slow, careful redeployment

---

## Testing Before Production

### Unit Tests
```python
# Test safety checker
assert is_unsafe_request("Do I have diabetes?")[0] == True
assert is_unsafe_request("What is diabetes?")[0] == False
```

### Integration Tests
```python
# Test PDF upload + RAG query
pdf = upload_test_file()
response = query_rag("What's in the document?")
assert len(response) > 0
```

### Load Tests
```bash
# Use Apache Bench
ab -n 100 -c 10 http://localhost:8501/
```

### Security Tests
- [ ] SQL injection attempts
- [ ] File upload attacks
- [ ] API key exposure
- [ ] Rate limiting effectiveness

---

## Incident Response

### Common Issues

| Issue | Solution | Severity |
|-------|----------|----------|
| API key expired | Rotate key immediately | HIGH |
| High latency | Check OpenAI status, optimize queries | MEDIUM |
| Storage full | Archive old chats, clean logs | MEDIUM |
| High costs | Reduce RAG search, optimize tokens | LOW |

### Escalation Path

1. **Level 1**: Auto-restart service
2. **Level 2**: Alert operations team
3. **Level 3**: Incident commander
4. **Level 4**: Executive notification

---

## Compliance Checklist

### GDPR Compliance
- [ ] Data retention policy (delete chats after 30 days?)
- [ ] User consent for data processing
- [ ] Right to deletion implemented
- [ ] Data processing agreement in place
- [ ] Privacy policy updated

### HIPAA Compliance (If handling medical data)
- [ ] Use Azure OpenAI (not public OpenAI)
- [ ] Private endpoints configured
- [ ] Encryption at rest and in transit
- [ ] Access logging enabled
- [ ] Regular security audits
- [ ] Business associate agreements signed

### PCI-DSS Compliance (If handling payments)
- [ ] No credit card data in code
- [ ] Secure payment processing
- [ ] Regular security assessments

---

## Documentation Updates

- [ ] Update deployment runbooks
- [ ] Document infrastructure diagrams
- [ ] Create disaster recovery plan
- [ ] Maintain runbooks for operations
- [ ] Document all environment variables
- [ ] Create incident response playbooks

---

## Post-Deployment

### First Week
- [ ] Monitor error logs daily
- [ ] Track API usage
- [ ] Gather user feedback
- [ ] Fix critical bugs immediately

### First Month
- [ ] Performance analysis
- [ ] Cost optimization review
- [ ] Security audit
- [ ] User satisfaction survey

### Ongoing
- [ ] Monthly maintenance windows
- [ ] Quarterly security reviews
- [ ] Annual compliance audit
- [ ] Regular backups

---

## Success Criteria

✅ **Deployment is successful when**:
- Application loads in <3 seconds
- API responses are <2 seconds
- Uptime is >99%
- Error rate is <1%
- No security incidents
- Users report satisfaction
- API costs are within budget

---

## Contact & Escalation

**Production Support**:
- On-call: [Contact info]
- Escalation: [Manager contact]
- Emergency: [Emergency contact]

**Monitoring Dashboard**:
- https://monitoring.example.com/mediai

**Status Page**:
- https://status.example.com/

---

## Final Checklist

Before going live:

- [ ] All tests passing
- [ ] Security review completed
- [ ] Documentation complete
- [ ] Backup system working
- [ ] Monitoring configured
- [ ] Incident response plan ready
- [ ] Team training completed
- [ ] Go/no-go decision made

---

**Deployment Status**: Ready for Production ✅

**Last Updated**: January 26, 2026

**Maintained By**: Development Team
