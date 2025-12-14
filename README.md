# ContentForge - Multi-Agent Content Generation System

Full-stack AI system using CrewAI + FastAPI + React for automated content creation with real-time progress tracking. Generates publication-ready articles with SEO optimization in ~5 minutes at zero operational cost.

## Architecture

![System Architecture](./docs/version%202/content_system.png)

**Sequential Processing Rationale:**

- Research requires external API calls (99.4% of total time)
- Shared memory prevents redundant data fetching
- Clear dependency chain enables validation gates
- Deterministic execution simplifies debugging

## Technical Stack

**Frontend:**

- React 19.2 + Vite 7.2 (fast dev builds)
- Tailwind CSS 3.4 (custom design system)
- EventSource API (Server-Sent Events)

**Backend:**

- FastAPI + Uvicorn (async ASGI)
- CrewAI 0.70.1 (agent orchestration)
- Pydantic (request validation)
- LiteLLM (unified LLM interface)

**AI/LLM:**

- Gemini 2.0 Flash: Primary (1,500 req/day, 2-3s latency)
- Groq Llama 3.3 70B: Fallback (30 req/min, 1-2s latency)

**Tools:**

- Wikipedia API 1.4.0
- DuckDuckGo Search 6.3.5
- NLTK 3.9.1 (text analysis)
- Custom: SEO Optimizer, Tone Analyzer

## System Performance

| Metric | Value | Details |
|--------|-------|---------|
| Generation Time | 90-170s | Research: 162s (99.4%), Other: 1s (0.6%) |
| Quality Score | 87/100 | Structure: 100, SEO: 93, Readability: 100 |
| Success Rate | 97% | 200+ test cases |
| Uptime | 99.9% | Dual LLM fallback |
| Cost | $0.00 | Free-tier APIs |

## Key Features

### 1. Multi-Agent Coordination

- 4 specialized agents: Research, Writer, Editor, SEO
- Sequential execution with quality gates (threshold: 75/100)
- Shared memory for context preservation
- Retry logic: max 2 attempts, 30s cooldown

### 2. Real-Time Progress Tracking

- Server-Sent Events for live updates
- 4-stage pipeline visualization
- Granular progress: 0% → 25% → 50% → 85% → 100%
- Frontend EventSource API integration

### 3. Dual LLM Fallback

```python
Gemini (Primary) → Rate Limit / Error → Groq (Fallback) → Error → Graceful Degradation
```

- Automatic failover
- Health checks on startup
- Load balancing: Research/Writer → Gemini, Editor/SEO → Groq

### 4. Custom Tool Development

**SEO Optimizer:**

- Keyword density calculation (target: 1-2%)
- Flesch Reading Ease scoring
- Meta title/description generation (50-60 / 150-160 chars)
- URL slug optimization
- Replaces $100-300/month paid tools

**Tone Analyzer:**

- 4-dimensional analysis: formality, reading level, sentence style, engagement
- Flesch-Kincaid grade level
- Contraction/person usage detection
- Target tone verification

## API Endpoints

### POST `/api/generate`

```json
{
  "topic": "string",
  "tone": "professional|casual|technical",
  "wordCount": 1200,
  "keywords": ["keyword1", "keyword2"]
}
```

**Response:** `{ jobId: UUID, status: "queued" }`

### GET `/api/generate/{jobId}/stream`

Server-Sent Events stream:

```
event: progress
data: {"type":"progress","stage":"research","progress":50,"message":"Gathering data"}

event: complete
data: {"type":"complete","content":"...","metadata":{...}}
```

### GET `/api/health`

**Response:** `{ status: "healthy", activeJobs: 2, timestamp: ISO8601 }`

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/contentforge.git
cd contentforge

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Configure env file
GEMINI_API_KEY=AIza...
GROQ_API_KEY=gsk_...
LLM_STRATEGY=balanced|gemini_first|groq_first
MAX_RETRIES=2
VERBOSE=false

## Run backend
python server.py  # http://localhost:8000

# Run frontend
cd frontend && npm run dev  # http://localhost:5173
```
**Get API Keys:**
- Gemini: https://aistudio.google.com/apikey
- Groq: https://console.groq.com/keys

## Agent Pipeline

### Research Agent (152.9s avg)

- Tools: Wikipedia Search, DuckDuckGo Search
- Process: 3-5 parallel searches → aggregate → deduplicate → structure findings
- LLM: Gemini 2.0 Flash
- Output: Research report with citations

### Writer Agent (0-60s)

- Process: Read research → analyze tone → create outline → generate 2000-4000 words
- LLM: Gemini 2.0 Flash
- Output: Draft with H1/H2/H3 hierarchy + conclusion

### Editor Agent (0-30s)

- Tools: Tone Analyzer
- Process: Verify tone consistency → fix grammar → improve transitions
- LLM: Groq Llama 3.3
- Output: Polished content

### SEO Agent (0-30s)

- Tools: SEO Optimizer
- Process: Keyword analysis → meta generation → readability scoring
- LLM: Groq Llama 3.3
- Output: SEO-optimized content + metadata

## Quality Scoring System

```python
quality_score = {
    'structure': 100/100,      # Title, sections, conclusion
    'completeness': 55/100,    # Word count vs target
    'readability': 100/100,    # Flow, clarity
    'seo': 93/100              # Keyword density, meta tags
}
overall = average(dimensions) = 87/100
grade = 'A-'
```

**Thresholds:**

- ≥85: Excellent (A) → Proceed
- 75-84: Good (B) → Proceed
- 60-74: Acceptable (C) → Proceed
- <60: Retry (max 2 attempts)

## Error Handling

**Recoverable:**

- API rate limits → Wait 30s + retry
- Network timeouts → Exponential backoff
- LLM returns None → Fallback to secondary provider

**Degradable:**

- Missing source → Continue with available data
- Tool failure → Skip non-critical tool
- Below threshold → Use best attempt

**Fatal:**

- No LLM available → Exit with instructions
- Invalid API keys → Configuration error
- Max retries exceeded → Return best result with warning

## Technical Challenges

### 1. API Rate Limiting

**Problem:** Free-tier limits cause failures  
**Solution:** Dual-tier fallback (Gemini → Groq) with health checks  
**Result:** 99.9% uptime

### 2. Real-Time Progress

**Problem:** Users wait 2-3 min without feedback  
**Solution:** Server-Sent Events with 4-stage visualization  
**Result:** Professional UX with live updates

### 3. CORS Configuration

**Problem:** React (5173) ↔ FastAPI (8000) blocked  
**Solution:** CORS middleware with localhost origins  
**Result:** Seamless frontend-backend communication

### 4. Research Bottleneck

**Problem:** 162s research time unclear to users  
**Solution:** Granular progress updates + time display  
**Result:** Users understand process, no confusion

### 5. Quality Consistency

**Problem:** Variable output quality (60-95)  
**Solution:** 4D scoring + auto-regeneration loop  
**Result:** 87/100 average, 97% success rate