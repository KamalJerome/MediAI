# MediAI — Next Panel Presentation Outline (12–15 min)

Use this document to build **Panel Review 2** (successor to `MediAI_PanelReview1.pptx`).  
**Slide count target:** ~14–18 slides total (fits 12–15 minutes at ~45–60 sec/slide).

---

## How to use this file

- Each **section** maps to your rubric.
- **Suggested slides** = one PowerPoint slide each unless noted.
- Fill **[BRACKETS]** with your numbers, screenshots, and dates.
- **Code snippets:** copy from `app.py`, `utils/rag_manager.py`, `utils/safety_checker.py` (keep to 5–12 lines per slide).

---

## 1. Introduction & Problem Recap (1–2 slides)

### Slide A — Title + team
- **Title:** MediAI — Medical Information Assistant (Panel Review 2)
- **Subtitle:** RAG + safety-first chatbot over user documents
- **Names / date / course / panel**

### Slide B — Problem recap
- **Problem:** Patients and learners need **general medical information** and help **understanding their own PDFs** (prescriptions, reports) without replacing clinicians.
- **Risks:** Diagnosis, dosing, emergency advice, and hallucinated “facts” must be constrained.
- **Approach:** Local chat UI + **retrieval-augmented generation (RAG)** + **rule-based safety layer** + **OpenAI** for embeddings and chat.
- **One-line value:** *Inform, explain documents, block unsafe asks.*

**Optional speaker note:** Contrast with Panel Review 1: call out what is **new since last review** (per-chat RAG, lazy load, streaming, citations, UI changes, dependency hardening).

---

## 2. System Design & Architecture (2–3 slides)

### Slide C — High-level architecture (diagram)
**Boxes (left → right):**
- User → **Streamlit (`app.py`)**
- **Safety checker** (`utils/safety_checker.py`) — before LLM
- **Chat manager** — JSON persistence (`data/chats/`)
- **RAG manager** — chunk → embed → **FAISS** (`data/embeddings/<chat_id>/`)
- **OpenAI API** — embeddings + chat completions (streaming)

**Caption:** *Unsafe queries never reach the model; document-grounded answers use retrieved chunks.*

### Slide D — Data flow (one question)
**Numbered flow:**
1. User message → safety check (`has_documents` aware).
2. If safe and docs exist → retrieve top-k chunks → build prompt → **stream** response.
3. If no docs → direct informational prompt (still no diagnosis/prescription in system intent).
4. Persist messages + optional `documents_used` in chat JSON.

### Slide E — Storage model (per-chat isolation)
- **Chats:** `data/chats/<chat_id>.json` — messages, timestamps, `documents_used`.
- **Embeddings:** `data/embeddings/<chat_id>/` — FAISS index + `documents_info.json`.
- **Why:** Each chat has its **own** vector store; no cross-chat document leakage.

---

## 3. Implementation Details (4–5 slides)

### Slide F — Modules developed & integrated

| Module | Role |
|--------|------|
| `app.py` | Streamlit UI: sidebar (new/leave/delete chat, recent chats), sticky upload + `st.chat_input`, streaming display |
| `utils/safety_checker.py` | Regex + keyword safety: emergency, diagnosis, medication, treatment; context when docs uploaded |
| `utils/pdf_processor.py` | PyPDF2 text extraction |
| `utils/rag_manager.py` | Chunking, FAISS, metadata **sources** for citations, `query_stream`, direct OpenAI client |
| `utils/chat_manager.py` | Create/list/load/delete chats, append messages, export |
| `setup.py` / `requirements.txt` | Environment setup and dependencies |

### Slide G — Algorithms implemented (bullet list)
- **Text splitting:** Recursive character chunks (~1000 chars, ~200 overlap) — LangChain `RecursiveCharacterTextSplitter`.
- **Embeddings:** OpenAI embedding model (via LangChain `OpenAIEmbeddings`).
- **Retrieval:** FAISS similarity search, **k = 3** chunks.
- **Generation:** Chat completions with **temperature = 0**; **streaming** token deltas.
- **Safety:** Priority: **emergency** → diagnosis / medication / treatment patterns; optional informational bypass when docs present.
- **Citations:** Chunks stored as `Document` with `metadata["source"]` → unique source list appended to answer.

### Slide H — Code snippet 1 — Safety gate (concept)
**File:** `utils/safety_checker.py`  
**Show:** `is_unsafe_request(..., has_documents=...)` — 1 pattern list + early emergency return (5–8 lines).

### Slide I — Code snippet 2 — RAG + citations + stream hook
**File:** `utils/rag_manager.py`  
**Show:** `get_relevant_chunks_with_sources` OR `_query_rag_manual` append `Sources:` OR `query_stream` yielding deltas (6–10 lines).

### Slide J — Code snippet 3 — Lazy RAG + sticky UI (optional one slide or merge with F)
**Files:** `app.py`  
**Show:** `ensure_rag_manager()` (only load FAISS when upload/query) + comment on sticky CSS selector (4–8 lines total).

---

## 4. Results & Analysis (3–4 slides)

### Slide K — Implementation status (~85% narrative)
**Claim framing (adjust to your truth):**
- **Core pipeline:** ✅ Streamlit app, chat CRUD, PDF → RAG, streaming replies, citations, per-chat stores, safety layer.
- **Polish / optional:** ⚠️ e.g. automated test suite in CI, formal usability study, encryption at rest, multi-user auth, mobile layout — **pick 2–3 honest gaps**.

**Visual:** Simple table: Feature | Status (Done / Partial / Planned).

### Slide L — Performance metrics (fill with your measurements)
**Template — replace [BRACKETS]:**
- **End-to-end latency:** [X]s first token (streaming) / [Y]s full response for typical query.
- **PDF ingest:** [N] pages → [T] seconds (embedding bound).
- **Retrieval:** FAISS local search — “low ms” order of magnitude [Z] ms (if measured).
- **Cost (rough):** OpenAI pricing per 1K tokens — **example session:** [upload + 10 questions] ≈ $[ ] (cite `documentation/API_GUIDE.md` logic).

*If you did not benchmark: say “qualitative: responsive on local machine; formal benchmarks planned.”*

### Slide M — Testing outcomes
- **Manual:** Safe vs unsafe prompts from `EXAMPLES_AND_TESTING.py` / custom list.
- **RAG:** Upload sample PDF → question → answer contains **Sources:** line.
- **Regression fixes:** LangChain import / `langchain.prompts` issues resolved via direct OpenAI for chat; document in one line as engineering note.

**Optional:** Screenshot montage: safety warning, streaming response, sources line, document-added system message.

### Slide N — Demo roadmap (optional 4th slide in this section)
- **Live demo script (60 sec):** New chat → attach PDF → ask grounded question → show **Sources** → ask unsafe question → show block.

---

## 5. Challenges & Solutions (1–2 slides)

### Slide O — Challenge 1: LangChain / Python ecosystem drift
- **Problem:** Import paths, deprecated chains, missing `langchain.prompts` on newer stacks.
- **Solution:** Narrow LangChain to **splitting + embeddings + FAISS**; **direct `openai` client** for chat + streaming; defensive multi-path imports where needed.

### Slide P — Challenge 2: UX vs Streamlit execution model
- **Problem:** Widget order caused input bar to overlap or sit above streaming content; sticky layout + chat lifecycle.
- **Solution:** Sticky CSS targeting upload container; **lazy `RAGManager`** per chat; session state for chat switching and deletes; iterative UI feedback from panel.

*(Add Challenge 3 if second slide: e.g. FAISS “delete document” vs index rebuild — technical debt.)*

---

## 6. Remaining Work (1 slide)

### Slide Q — Remaining work (prioritized)
1. **Robust document removal** — Rebuild or filter FAISS when user deletes a doc (current limitation).
2. **Automated tests** — Pytest for `safety_checker` + RAG smoke tests.
3. **Optional:** Rename chats, export chat UX, more file types (DOCX), re-ranking, admin config UI.
4. **Compliance note:** Not HIPAA-ready as-is (data sent to OpenAI) — document if course requires.

---

## 7. Timeline for Completion (1 slide)

### Slide R — Timeline (example template — edit dates)

| Phase | Tasks | Target |
|-------|--------|--------|
| Week 1 | Tests + doc delete/rebuild strategy | [date] |
| Week 2 | Hardening + demo script + slide updates | [date] |
| Week 3 | Final report + optional deployment note | [date] |

**Milestone:** “Panel Review 3 / final submission” [date].

---

## Appendix — Suggested total slide list (checklist)

1. Title  
2. Problem recap  
3. Architecture diagram  
4. Data flow  
5. Per-chat storage  
6. Modules table  
7. Algorithms  
8. Code: safety  
9. Code: RAG / citations / stream  
10. Code: lazy load / UI (optional)  
11. ~85% status table  
12. Performance / cost  
13. Testing + screenshots  
14. Challenges & solutions  
15. Remaining work  
16. Timeline  

**Optional:** Thank you / Q&A.

---

## Link to previous deck (`MediAI_PanelReview1.pptx`)

When building Review 2, **reuse** from Review 1 only where still accurate; **replace** slides that described:
- Global (non–per-chat) RAG only  
- Sidebar-only document upload  
- Non-streaming replies  
- Any removed features (e.g. theme toggle if it was in old deck)

End of outline.
