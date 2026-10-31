# IdeaOS Product Requirements Document

**Version:** 1.0  
**Status:** Draft  
**Last Updated:** 2026-10-31

---

## 1. Product Vision & Core Principles

### 1.1 Vision Statement
IdeaOS is the **operating system for ideas** — a unified platform that captures fleeting thoughts from any context, transforms them into structured insights through AI, connects related concepts across time and projects, and generates publish-ready content that sounds authentically like you.

### 1.2 Core Principles

| Principle | Description |
|-----------|-------------|
| **Capture Everywhere** | Zero-friction input from voice, text, image, screen, browser, desktop — no app switching |
| **Intelligence Over Storage** | Raw captures are automatically transcribed, structured, tagged, and linked — not just stored |
| **Fusion, Not Filing** | Ideas connect themselves through semantic similarity, temporal proximity, and explicit relations — no manual tagging required |
| **Your Voice, Amplified** | Brand DNA learns your style, vocabulary, constraints — every output passes a "Brand Guardian" quality gate |
| **Actionable by Default** | Every idea surfaces with next steps: content drafts, calendar slots, collaboration prompts |
| **Privacy-First Architecture** | End-to-end encryption for captures; local-first processing where possible; user owns all data |

### 1.3 North Star Metric
**Weekly Active Ideas (WAI)** — Count of unique ideas that progress from capture → enrichment → connection → output per workspace per week.

---

## 2. User Personas & Use Cases

### 2.1 Primary Personas

#### **Creator Alex** (Content Creator / Solopreneur)
- **Context:** Produces 3-5 pieces of content/week across newsletter, LinkedIn, YouTube, Twitter
- **Pain Points:** Ideas scattered across Notes, Voice Memos, Slack, browser tabs; repurposing is manual; brand voice drifts
- **Goals:** Capture in 5 seconds; auto-generate first drafts; maintain consistent voice; publish from calendar

#### **Strategist Sam** (Product Manager / Founder)
- **Context:** Synthesizes user feedback, competitor intel, team discussions into strategy docs
- **Pain Points:** Insights lost in meeting transcripts; hard to connect feedback to roadmap; context switching kills depth
- **Goals:** Capture meeting highlights; auto-cluster related signals; generate PRDs/strategy docs; track idea evolution

#### **Researcher Riley** (Analyst / Consultant / Academic)
- **Context:** Consumes papers, articles, podcasts, interviews; needs to synthesize into deliverables
- **Pain Points:** Highlight export is fragmented; citation management is manual; synthesis takes weeks
- **Goals:** Ingest long-form sources; extract claims/evidence; build argument maps; export cited drafts

### 2.2 Secondary Personas

#### **Team Lead Taylor** (Engineering/Design Lead)
- **Use Case:** Capture team decisions, technical debt ideas, hiring thoughts; share with team selectively

#### **Investor Ian** (VC / Angel)
- **Use Case:** Capture meeting notes, thesis fragments, portfolio signals; generate thesis memos

---

## 3. Feature Specifications (16 Sections)

### Section 1: Quick Capture Engine
**Epic:** Universal, sub-5-second capture from any context

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **1.1 Voice Capture** | Global hotkey (⌘⇧Space) → records audio → auto-stops on silence → transcribes via Whisper | <3s latency hotkey-to-transcript; 95%+ WER on clear speech |
| **1.2 Text Capture** | Global hotkey (⌘⇧T) → floating input → markdown support → auto-tag from content | <1s hotkey-to-input; preserves formatting |
| **1.3 Image/Screen Capture** | ⌘⇧4 → region select → OCR (Tesseract/PaddleOCR) → text + image stored | OCR confidence >80% on UI text; image + text linked |
| **1.4 Browser Extension** | Right-click → "Capture to IdeaOS" → saves selection + URL + DOM context | Captures selection, source URL, timestamp, page title |
| **1.5 iOS Shortcuts/Share Sheet** | Share sheet action → sends to workspace → background sync | Works offline; syncs on next app open |
| **1.6 Desktop Widget** | Menu bar / system tray widget → one-click capture types | Always visible; <100ms response |

### Section 2: Asset Ingestion Pipeline
**Epic:** Reliable, scalable processing of uploaded media assets

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **2.1 Presigned Upload** | POST /api/assets/presign → returns S3/GCS presigned URL + asset ID | URL expires in 15 min; supports multipart for >100MB |
| **2.2 Asset Completion** | POST /api/assets/complete → triggers processing pipeline | Validates checksum; enqueues transcription job |
| **2.3 Transcription** | WhisperX (speaker diarization) + custom vocabulary | <10min for 60min audio; speaker labels; custom vocab boost |
| **2.4 Video Processing** | Keyframe extraction (1fps) + OCR on frames + audio transcript | Keyframes searchable; OCR on slides/screenshots |
| **2.5 Document Parsing** | PDF (pdfplumber), DOCX, EPUB → structured text + metadata | Preserves headings, tables, images; extracts metadata |
| **2.6 Web Ingestion** | URL → readability extraction + full DOM snapshot | Clean article text; paywall detection; snapshot for reference |

### Section 3: Idea Extraction & Structuring
**Epic:** Transform raw captures into structured, typed idea objects

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **3.1 Entity Extraction** | spaCy + custom NER → people, orgs, products, concepts, metrics | F1 >0.85 on domain entities; configurable per workspace |
| **3.2 Idea Typing** | Classifier: insight, task, question, reference, signal, decision, hypothesis | Accuracy >90%; user-correctable with feedback loop |
| **3.3 Structured Fields** | Auto-populate: title, summary, tags, confidence, source refs, extracted entities | All fields populated within 30s of capture completion |
| **3.4 Claim/Evidence Parsing** | For research sources: extract claims, supporting evidence, citations | Structured claim graph; citation mapping to source spans |
| **3.5 Multi-source Synthesis** | Merge duplicate ideas from different captures (dedup via embedding similarity) | Cosine similarity >0.92 triggers merge suggestion |

### Section 4: Vector Memory & Semantic Search
**Epic:** Embedding-based retrieval and similarity across all ideas

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **4.1 Embedding Generation** | text-embedding-3-large (1536-dim) for ideas; CLIP for images | Batch embed on creation; re-embed on significant edit |
| **4.2 Vector Index** | pgvector (PostgreSQL) with HNSW index; workspace-scoped | p95 <50ms for top-k=10; supports filtered search |
| **4.3 Semantic Search API** | GET /api/ideas?query=&filters= → ranked results with scores | Hybrid search (vector + keyword); rerank with cross-encoder |
| **4.4 Similarity Graph** | Precompute top-50 neighbors per idea; update incrementally | Background job; <5min freshness for new ideas |
| **4.5 Temporal Decay** | Recency-weighted scoring for "recent relevant" queries | Configurable half-life (default 30 days) |

### Section 5: Idea Fusion Engine
**Epic:** Proactive connection discovery and synthesis proposals

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **5.1 Connection Types** | Explicit (user-created), Semantic (embedding), Temporal (co-occurrence), Causal (claim→evidence), Contradiction | All 5 types queryable; weighted in fusion scoring |
| **5.2 Fusion Proposals** | Background agent: "These 3 ideas form a pattern → here's a synthesis" | Generates title, thesis, supporting ideas, suggested output type |
| **5.3 Cluster Detection** | HDBSCAN on embeddings → emergent theme clusters | Min cluster size 3; stability score >0.7; auto-named via LLM |
| **5.4 Contradiction Detection** | NLI model (DeBERTa) on claim pairs → flag contradictions | Precision >0.8 on known contradiction benchmarks |
| **5.5 Fusion Approval** | POST /api/fusion/:id/approve → creates new fused idea + links sources | Immutable audit trail; provenance preserved |

### Section 6: Brand DNA & Voice Profile
**Epic:** Learn and enforce user's unique communication style

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **6.1 Style Analysis** | Analyze 50+ writing samples → vocabulary, sentence structure, tone markers, formatting patterns | Profile converges within 20 samples; explains top 10 distinguishing features |
| **6.2 Brand Rules** | YAML/JSON ruleset: forbidden words, required phrases, length limits, formatting rules, tone constraints | Rules validated at generation time; violations block publish |
| **6.3 Voice Embedding** | Fine-tuned embedding for "sounds like user" scoring | Cosine similarity >0.85 for authentic outputs |
| **6.4 Multi-brand Support** | Per-workspace brand profiles; inheritance from parent | Switch brands in <1s; rules compose correctly |
| **6.5 Brand Evolution** | Monthly re-analysis; drift detection; change log with diffs | Alerts on drift >15%; rollback to previous version |

### Section 7: Content Generation Agent
**Epic:** Generate publish-ready drafts from ideas + brand DNA

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **7.1 Output Templates** | Newsletter, LinkedIn post, Twitter thread, Blog post, Script, PRD, Strategy memo, Slide deck outline | 12+ templates; each with structure, length, hook formulas |
| **7.2 Repurposing Pipeline** | POST /api/content/repurpose → input idea + target formats → parallel generation | 5 formats in <60s; each passes Brand Guardian |
| **7.3 Hook Generation** | 26 hook formulas (question, stat, story, contrarian, etc.) → scored variants | Top-3 hooks per format; A/B test ready |
| **7.4 Citation Integration** | Auto-insert citations from source ideas; format per platform | Accurate source mapping; platform-appropriate citation style |
| **7.5 Iterative Refinement** | Chat-style refinement: "shorter", "more casual", "add example" | <3s per iteration; preserves core thesis |

### Section 8: Brand Guardian (Quality Agent)
**Epic:** Multi-layer quality gate before any content leaves the system

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **8.1 Rule Engine** | Deterministic checks: banned words, length, formatting, required elements | 100% catch rate for deterministic rules |
| **8.2 Style Scoring** | LLM judge: "Does this sound like [brand]?" 1-10 score + specific feedback | Correlation >0.9 with human ratings |
| **8.3 Fact Check** | Claim verification against source ideas + external search (optional) | Flags unverified claims; cites sources |
| **8.4 Plagiarism/Originality** | Similarity check against web index + user's past outputs | Flags >30% similarity to external; self-plagiarism detection |
| **8.5 Accessibility/Inclusivity** | Readability score, inclusive language, alt-text for generated images | WCAG AA readability; inclusive language warnings |

### Section 9: Content Calendar & Scheduling
**Epic:** From idea to published — managed timeline

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **9.1 Calendar View** | Monthly/weekly/daily drag-drop; filter by status, format, brand | <100ms render for 500 items; offline-capable |
| **9.2 Auto-scheduling** | "Schedule this series" → finds optimal slots per platform analytics | Respects platform best-times; avoids conflicts |
| **9.3 Publishing Integrations** | Buffer, Later, Hootsuite, LinkedIn API, Twitter API, Ghost, Substack, Notion | OAuth2; retry with backoff; status sync |
| **9.4 Recurring Series** | "Every Monday newsletter" → auto-generates from idea queue | Queue management; skip/edit individual occurrences |
| **9.5 Campaign Management** | Group related outputs → track collective performance | UTM auto-generation; aggregate analytics |

### Section 10: Feedback Learning Loop
**Epic:** Close the loop between published performance and future generation

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **10.1 Performance Ingestion** | Webhooks from platforms → engagement metrics (views, likes, comments, shares, CTR) | Near-real-time (<5min); normalized schema |
| **10.2 Feedback Events** | POST /api/feedback → explicit (thumbs up/down) + implicit (dwell, scroll, copy) | All event types captured; idempotent |
| **10.3 Performance Attribution** | Link output → originating ideas → capture sources → full provenance | Complete lineage for any metric |
| **10.4 Model Fine-tuning** | Monthly LoRA fine-tune on high-performing outputs (opt-in) | Measurable improvement on style score; privacy-preserving |
| **10.5 Brand Rule Evolution** | Auto-suggest rule changes based on performance patterns | "Posts with X structure get 2x engagement" → rule proposal |

### Section 11: Workspace & Collaboration
**Epic:** Multi-user workspaces with granular permissions

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **11.1 Workspace Roles** | Owner, Admin, Editor, Viewer, Contributor (capture only) | RBAC enforced at API + DB (RLS) |
| **11.2 Shared Ideas** | Ideas can be private, workspace-visible, or public link | Permission checks on all read/write |
| **11.3 Comments & Threads** | Inline comments on ideas/outputs; @mentions; resolution | Real-time via WebSocket; email notifications |
| **11.4 Activity Feed** | Per-idea and workspace-level audit log | Immutable; exportable for compliance |
| **11.5 Invite Links** | Role-scoped invite links with expiry; SSO support (SAML/OIDC) | SCIM provisioning for enterprise |

### Section 12: Desktop Application (Electron/Tauri)
**Epic:** Native desktop experience with global capture

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **12.1 Global Hotkeys** | Register system-wide shortcuts (configurable) | Works when app backgrounded; no conflicts |
| **12.2 Menu Bar / Tray** | Always-available capture menu; recent ideas; sync status | <50ms menu open; shows sync health |
| **12.3 Offline-First** | Local SQLite cache; background sync on reconnect | Full read/write offline; conflict resolution |
| **12.4 Screen Capture** | Region/window/fullscreen → OCR + annotations | 60fps capture; annotation tools |
| **12.5 Auto-updates** | Silent background updates; delta patches | Zero-downtime; rollback on failure |

### Section 13: Browser Extension (Chrome/Firefox/Safari)
**Epic:** Capture from web context with full fidelity

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **13.1 Context Menu** | Right-click selection → capture as idea/reference | Preserves formatting, images, links |
| **13.2 Page Capture** | Full article extraction (readability) + screenshot | Handles paywalls, lazy-load, SPAs |
| **13.3 Highlight & Annotate** | Highlight text → add note → creates linked capture | Highlights persist on revisit |
| **13.4 Tab Management** | "Send tabs to IdeaOS" → batch capture open tabs | Groups by window; preserves tab order |
| **13.5 Identity Sync** | Shares auth with web app; no separate login | Session shared; biometric unlock on mobile |

### Section 14: iOS App & Integrations
**Epic:** Native mobile capture with system integration

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **14.1 Share Sheet** | System share extension → capture any content type | Appears in all apps; background upload |
| **14.2 Shortcuts Integration** | Custom shortcuts actions: "Capture Thought", "Log Insight" | Exposes all capture types; supports variables |
| **14.3 Voice Memos Import** | Auto-import from Voice Memos app (with permission) | Background sync; transcript in <30s |
| **14.4 Widgets** | Lock screen / home screen widgets: quick capture, recent ideas | Deep links to specific capture types |
| **14.5 Offline Mode** | Full capture + queue; sync on WiFi/cellular | No data loss; battery-efficient |

### Section 15: Search & Discovery
**Epic:** Find anything instantly across all modalities

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **15.1 Unified Search** | Single search bar: ideas, captures, assets, outputs, people, tags | Results in <100ms; grouped by type |
| **15.2 Natural Language Queries** | "ideas about pricing from last month's sales calls" → parsed to filters | NL→SQL parsing accuracy >90% |
| **15.3 Visual Search** | "Find screenshots with dashboard UI" → CLIP-based image search | Top-10 precision >0.8 |
| **15.4 Graph Exploration** | Interactive idea graph: nodes=ideas, edges=connections | Force-directed; filter by connection type; export PNG |
| **15.5 Saved Searches/Alerts** | "Alert me when new ideas connect to 'pricing strategy'" | Real-time push; digest option |

### Section 16: Analytics & Insights
**Epic:** Understand your thinking patterns and content performance

| Feature | Spec | Acceptance Criteria |
|---------|------|---------------------|
| **16.1 Capture Analytics** | Volume by type, source, time; capture-to-idea conversion rate | Daily/weekly/monthly views; export CSV |
| **16.2 Idea Health** | Ideas by status (raw, structured, connected, outputted, published) | Funnel visualization; bottleneck identification |
| **16.3 Connection Analytics** | Most connected ideas; cluster evolution; contradiction rate | Graph metrics: centrality, clustering coefficient |
| **16.4 Content Performance** | Per-output and aggregated metrics; attribution to source ideas | Dashboard with platform breakdown; cohort analysis |
| **16.5 Brand Consistency** | Style score trends; rule violation frequency; drift detection | Weekly report; anomaly alerts |

---

## 4. Acceptance Criteria Summary

| Epic | Key Acceptance Criteria |
|------|-------------------------|
| Quick Capture | <5s end-to-end for all capture types; 99.9% reliability |
| Asset Ingestion | 100% asset durability; <15min processing for 60min media |
| Idea Extraction | >90% typing accuracy; <30s structured idea ready |
| Vector Memory | p95 <50ms search; hybrid vector+keyword |
| Idea Fusion | >3 actionable proposals/week per active user; >60% approval rate |
| Brand DNA | Profile from 20 samples; >0.85 voice similarity on outputs |
| Content Generation | 5 formats in <60s; 100% Brand Guardian pass rate |
| Brand Guardian | 100% deterministic rule catch; >0.9 correlation style score |
| Calendar | Drag-drop <100ms; 99.9% publish success via integrations |
| Feedback Loop | Full provenance; monthly fine-tune improves style score 10%+ |
| Workspace | RBAC at DB layer; real-time collab <100ms latency |
| Desktop App | Global hotkeys always work; offline-first; <100MB RAM idle |
| Browser Extension | Capture from any page; <200ms injection |
| iOS App | Share sheet in all apps; offline queue; <5% battery/day |
| Search | <100ms unified; NL query >90% accuracy |
| Analytics | Real-time dashboards; exportable; actionable insights |

---

## 5. Success Metrics (KPIs)

### 5.1 Activation Metrics
- **Time to First Idea:** <2 min from signup to first structured idea
- **Capture Adoption:** >80% of users capture within 24h
- **Multi-modal Usage:** >60% users use ≥3 capture types in week 1

### 5.2 Engagement Metrics
- **Weekly Active Ideas (WAI):** Target >10 per active workspace
- **Fusion Approval Rate:** >60% of proposals approved
- **Content Generation Rate:** >3 outputs/week per active user
- **Search Usage:** >5 searches/day per active user

### 5.3 Quality Metrics
- **Brand Guardian Pass Rate:** >95% first-pass
- **Style Score:** >8.5/10 average on generated content
- **User Correction Rate:** <10% of generated fields edited

### 5.4 Retention Metrics
- **Day 7 Retention:** >45%
- **Day 30 Retention:** >30%
- **Net Revenue Retention:** >120% (expansion > churn)

### 5.5 Business Metrics
- **ARPU:** $25/mo (Pro), $100/mo (Team), $500/mo (Enterprise)
- **CAC Payback:** <6 months
- **Gross Margin:** >80% (software + AI inference)

---

## 6. Constraints & Assumptions

### 6.1 Technical Constraints
- **Latency:** P95 <200ms for all user-facing API calls
- **Availability:** 99.9% uptime SLA (multi-AZ deployment)
- **Data Residency:** EU/US regions; customer choice
- **Scale:** Support 100K workspaces, 10M ideas, 1M daily captures

### 6.2 Regulatory Constraints
- GDPR, CCPA compliance; right to deletion/export
- SOC 2 Type II within 12 months
- HIPAA-ready architecture (BAA on Enterprise)

### 6.3 Assumptions
- LLM API costs decrease 2x/year (budget: $0.02/1K tokens blended)
- Embedding costs negligible at scale (batch, cached)
- Users willing to connect calendars/publishing accounts
- 80/20 rule: 20% of features drive 80% of value

---

## 7. Out of Scope (v1.0)

- Native Android app (PWA + shortcuts only)
- Video editing / rendering pipeline
- Real-time collaborative editing (Google Docs style)
- Marketplace for templates/agents
- White-label / OEM offering
- On-premise deployment

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM hallucination in idea extraction | High | High | Human-in-loop verification; confidence scoring; feedback loop |
| Brand Guardian false positives | Medium | High | Tunable strictness; explainable rejections; quick override |
| Vector search latency at scale | Medium | Medium | HNSW tuning; read replicas; caching layer |
| Privacy concerns with cloud AI | Medium | High | Local-first option; encrypted processing; data processing agreements |
| Platform API changes (publishing) | High | Medium | Abstraction layer; multi-provider; graceful degradation |
| User adoption of new paradigms | High | High | Progressive disclosure; import from existing tools; strong onboarding |

---

## 9. Appendix: Glossary

| Term | Definition |
|------|------------|
| **Capture** | Raw input (voice, text, image, file, URL) before processing |
| **Asset** | Stored media file (audio, video, document) with metadata |
| **Idea** | Structured, typed knowledge unit extracted from captures |
| **Fusion** | Synthesis of multiple ideas into a new, higher-level idea |
| **Brand DNA** | Learned representation of user's communication style |
| **Brand Guardian** | Multi-layer quality gate for generated content |
| **WAI** | Weekly Active Ideas — north star metric |
| **Provenance** | Complete lineage: capture → asset → idea → fusion → output → feedback |