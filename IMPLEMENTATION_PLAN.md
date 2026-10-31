# IdeaOS - Implementation Plan

**Version:** 1.0  
**Date:** 2026-10-31  
**Status:** Draft

---

## 1. Strategic Context

### 1.1 Product Mandate
Build a **Content Repurposing Studio with Brand Memory** that satisfies the official Product Space problem statement. The six required capabilities are the core product; IdeaOS universal capture + fusion are differentiators.

### 1.2 Core Workflow (MVP Target)
```
Long-form Media (Video/Podcast) 
    → Ingest & Transcribe 
    → Clip Intelligence (Explainable Selection) 
    → Platform-Specific Content Generation 
    → Brand Guardian (Edit-Learning Memory) 
    → Content Calendar 
    → Publish 
    → Performance Feedback Loop 
    → Improve Future Generations
```

### 1.3 Non-Negotiable Principles
| Principle | Enforcement |
|-----------|-------------|
| **End-to-end functional** | No mock responses; every capability demonstrable |
| **Source attribution preserved** | Original media, timestamps, clips traceable to source |
| **Approval-based** | Creator approves clips, content, calendar items |
| **Secure background processing** | Temporal workflows, presigned URLs, malware scanning |
| **Integration tested** | Each workflow validated via automated tests |
| **Memory learns from edits** | Brand rules evolve from explicit creator corrections |

---

## 2. Phase Structure

| Phase | Focus | Duration | Key Deliverable |
|-------|-------|----------|-----------------|
| **Phase 0** | Foundation & Infrastructure | 2 weeks | Deployable monorepo, auth, DB, object storage |
| **Phase 1** | Long-Form Media Ingestion | 3 weeks | Video/podcast → transcript + segments + keyframes |
| **Phase 2** | Clip Intelligence Agent | 3 weeks | Explainable clip selection with manual adjustment |
| **Phase 3** | Platform-Specific Generation | 3 weeks | 5 platforms × distinct formats from clips |
| **Phase 4** | Brand Guardian + Edit-Learning Memory | 2 weeks | Quality gate + rule extraction from edits |
| **Phase 5** | Content Calendar + Publishing | 2 weeks | Editorial calendar with platform sync |
| **Phase 6** | Performance Feedback Loop | 2 weeks | Metric ingestion → clip ranking → generation improvement |
| **Phase 7** | IdeaOS Differentiation Layer | 3 weeks | Universal capture, Idea Inbox, Fusion, Cross-device |
| **Phase 8** | Integration Hardening & Launch | 2 weeks | E2E tests, load tests, documentation, deploy |

**Total: ~22 weeks (5.5 months) to launch-ready MVP**

---

## 3. Phase Details

### Phase 0: Foundation & Infrastructure (2 weeks)

#### Goals
- Monorepo with all services scaffolded
- Auth, workspace, RBAC working
- Database schema deployed with migrations
- Object storage configured (presigned upload/download)
- CI/CD pipeline with staging environment

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| Initialize monorepo (Turborepo) | Backend Lead | `apps/api`, `apps/web`, `apps/desktop`, `apps/extension`, `apps/ios`, `packages/*` |
| Configure Supabase project | Backend Lead | PostgreSQL + pgvector + Auth + Storage + Realtime |
| Deploy Temporal cluster | DevOps | Temporal UI accessible; test workflow runs |
| Implement Clerk/Auth0 integration | Backend | Login, signup, workspace creation, RBAC enforced |
| Create database migrations | Backend | All 16 tables from DATABASE_SCHEMA.md deployed |
| Configure Cloudflare R2 + CDN | DevOps | Presigned upload/download works; malware scan on complete |
| Set up observability stack | DevOps | Prometheus, Grafana, Loki, Tempo receiving data |
| CI/CD pipeline | DevOps | PR → preview deploy; tag → production deploy |

#### Acceptance Criteria
- [ ] `git clone → turbo run dev` starts all services locally
- [ ] New user can signup, create workspace, invite member
- [ ] Asset upload via presigned URL completes and triggers scan
- [ ] All migrations run cleanly on fresh DB
- [ ] Staging environment accessible at `staging.ideaos.com`

---

### Phase 1: Long-Form Media Ingestion (3 weeks)

#### Goals
- Reliable ingestion of 60+ minute videos and podcasts
- Speaker-diarized transcripts with timestamps
- Topic segmentation and scene detection
- Asynchronous, resumable processing via Temporal

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| **AssetIngestionWorkflow** (Temporal) | Backend | Handles audio, video, documents, URLs; retries; visibility |
| **Transcriber Agent** (WhisperX) | ML Engineer | <10min for 60min; speaker labels; custom vocab; word timestamps |
| **Video Processor** (Keyframes + OCR) | ML Engineer | 1fps extraction; PaddleOCR on frames; slide detection |
| **Topic Segmenter** | ML Engineer | Semantic segmentation (TextTiling + embedding boundaries) |
| **Scene Detector** | ML Engineer | PySceneDetect; shot boundaries; visual chapter markers |
| **Document Parser** | Backend | PDF/DOCX/EPUB/PPTX → structured text + metadata |
| **Web Extractor** | Backend | Readability + Playwright; paywall detection; DOM snapshot |
| **Progress API + WebSocket** | Frontend | Real-time status: uploading → transcribing → segmenting → done |

#### Acceptance Criteria
- [ ] Upload 60min video → transcript with speakers + timestamps in <15min
- [ ] Video yields keyframes (1fps) with OCR text searchable
- [ ] Topics segmented with labels (e.g., "Intro", "Pricing Discussion", "Q&A")
- [ ] Scenes detected with thumbnails; user can jump to scene
- [ ] Failed transcription retries with fallback provider
- [ ] All processing visible in real-time on frontend
- [ ] Original media preserved in R2; transcript stored in DB

---

### Phase 2: Clip Intelligence Agent (3 weeks)

#### Goals
- Identify compelling timestamped segments from long-form media
- Provide explicit explanation for every recommendation
- Allow manual timestamp adjustment and creator approval
- Export actual clips (not just timestamps)

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| **Clip Intelligence Agent** | ML Engineer | Analyzes transcript + topics + scenes + engagement patterns |
| **Clip Scoring Model** | ML Engineer | Scores: hook strength, standalone context, narrative value, audience relevance |
| **Explanation Generator** | ML Engineer | For each clip: "Selected because [reason] — hook at 0:15, complete thought, high relevance to [audience]" |
| **Clip Selection UI** | Frontend | Timeline view; recommended clips highlighted; drag to adjust start/end |
| **Manual Override** | Frontend | Creator can add custom clips; adjust boundaries frame-accurate |
| **Clip Extraction Service** | Backend | FFmpeg serverless; exports MP4/WebM with burned captions option |
| **Clip Approval Workflow** | Backend | POST /clips/{id}/approve → creates approved_clip record |

#### Clip Intelligence Output Schema
```json
{
  "clips": [
    {
      "id": "uuid",
      "source_asset_id": "uuid",
      "start_time": 145.2,
      "end_time": 203.8,
      "duration": 58.6,
      "hook_strength": 0.92,
      "standalone_context": 0.88,
      "narrative_value": 0.85,
      "audience_relevance": 0.91,
      "recommended_platform": "instagram_reel",
      "explanation": "Strong contrarian hook at 2:25 ('Everyone is wrong about X'). Complete standalone argument with evidence. High relevance for technical founders.",
      "transcript_segment": "Full transcript text...",
      "keyframe_thumbnails": ["url1", "url2", "url3"],
      "status": "pending_review"
    }
  ]
}
```

#### Acceptance Criteria
- [ ] From 60min video, generates 8-15 clip recommendations in <60s
- [ ] Each clip has all 5 scores + explicit explanation
- [ ] Creator can adjust timestamps ±1 frame; preview updates instantly
- [ ] Creator approves/rejects each clip; approved clips move to content gen
- [ ] Approved clip exports as MP4 (H.264, 1080p) in <30s
- [ ] Burned captions option works with speaker labels
- [ ] Rejected clips logged with reason for learning

---

### Phase 3: Platform-Specific Content Generation (3 weeks)

#### Goals
- Generate distinctly tailored content for 5 platforms from approved clips
- Preserve source's original message and creator identity
- Support: Instagram Reels, Instagram Carousels, LinkedIn Posts, YouTube Shorts, X Threads, Newsletters

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| **Context Builder** | Backend | Builds context: clip transcript + brand DNA + platform specs + examples |
| **Platform Generators** (6) | ML Engineer | Each generates distinct output, not format conversion |
| **Hook Formula Library** | ML Engineer | 26 formulas; scores variants; platform-appropriate selection |
| **Citation/Attribution System** | Backend | Links back to source clip + original media + timestamp |
| **Content Generation Workflow** | Backend | Parallel generation; Brand Guardian validation; auto-retry |
| **Content Studio UI** | Frontend | Side-by-side preview; edit before approve; version history |

#### Platform-Specific Output Requirements

| Platform | Format | Distinct Requirements |
|----------|--------|----------------------|
| **Instagram Reel** | 9:16 video script | Beat sheet (8-12 beats), visual cues, on-screen text, trending audio suggestion |
| **Instagram Carousel** | 1080x1080 slides | Cover hook, 5-10 slides with progressive disclosure, swipe CTA |
| **LinkedIn Post** | Text + optional image | Hook ≤150 chars, professional narrative, insight→evidence→implication→question |
| **YouTube Shorts** | 9:16 video script | Retention hooks every 3s, visual retention cues, subscribe CTA |
| **X Thread** | 5-8 tweets | Hook tweet standalone, thread flow, numbered/emoji, final CTA + link |
| **Newsletter** | HTML + text | Subject line <50 chars, preheader, sections, single primary CTA |

#### Acceptance Criteria
- [ ] Single clip → 6 platform outputs in <90s (parallel)
- [ ] Each output passes Brand Guardian on first try >80%
- [ ] Outputs are distinctly different (not truncated versions)
- [ ] Source attribution preserved: "From [podcast] at 12:34 — [clip context]"
- [ ] Creator can edit any output; edits feed Brand Memory
- [ ] Hook variants generated (3 per platform) with scores

---

### Phase 4: Brand Guardian + Edit-Learning Memory (2 weeks)

#### Goals
- Multi-layer quality gate before content leaves system
- Learn stable preferences from creator edits (not just ratings)
- Versioned, traceable brand rules used in subsequent generations

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| **Rule Engine** (Deterministic) | Backend | Forbidden words, required phrases, length, format, structure — 100% catch |
| **Style Scorer** (LLM Judge) | ML Engineer | 0-10 score + breakdown (vocab, syntax, tone, formatting); >0.9 human correlation |
| **Fact Checker** | ML Engineer | Verifies claims against source clip spans; flags unsupported |
| **Originality Checker** | ML Engineer | Self-plagiarism (vs user's past outputs) + external sampling |
| **Accessibility Checker** | Backend | Readability, inclusive language, heading structure, alt-text |
| **Brand Guardian Workflow** | Backend | Parallel checks → aggregate verdict → auto-retry (max 2) → human review |
| **Edit Diff Analyzer** | ML Engineer | Compares AI output vs creator edit → extracts rule changes |
| **Brand Rule Extractor** | ML Engineer | From edits: tone shifts, vocab additions/removals, hook style, structure prefs |
| **Versioned Brand Profile** | Backend | Each change creates new version; rollback; diff view; audit trail |

#### Edit-Learning Flow
```
Creator Edits Output
       │
       ▼
┌─────────────────────────────────────┐
│  Compute Semantic Diff              │
│  (AST + embedding diff)             │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Extract Learnings                  │
│  • Tone: "more conversational"      │
│  • Vocab: remove "game-changing"    │
│  • Hook: "lead with question"       │
│  • Structure: "problem→solution"    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Propose Brand Rule Updates         │
│  • Creator reviews + approves       │
│  • Creates new brand version        │
│  • Immediately used in next gen     │
└─────────────────────────────────────┘
```

#### Acceptance Criteria
- [ ] Brand Guardian validates all 6 dimensions in <3s
- [ ] Auto-retry with feedback fixes >60% of failures
- [ ] From 10 edits, extracts ≥5 stable brand rules
- [ ] Rules versioned; creator can see diff + rollback
- [ ] New rules apply to next generation immediately
- [ ] Style score correlation with human rating >0.9

---

### Phase 5: Content Calendar + Publishing (2 weeks)

#### Goals
- Connect source media → clips → platform content → publishing status
- Editable editorial calendar with drag-drop
- Platform publishing integrations (OAuth, webhook sync)

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| **Calendar Data Model** | Backend | Links: source_asset → approved_clips → content_outputs → calendar_items |
| **Calendar UI** | Frontend | Month/week/day views; drag-drop; filter by platform, status, campaign |
| **Auto-Scheduler** | Backend | "Schedule series" → finds optimal slots per platform analytics |
| **Publishing Integrations** | Backend | LinkedIn, X, Instagram (via Buffer/Later), Ghost, Substack, YouTube |
| **OAuth Management** | Backend | Secure token storage; refresh; disconnect; multi-account per platform |
| **Publish Workflow** | Backend | Explicit confirm → async publish → status sync → metrics webhook setup |
| **Campaign Management** | Frontend | Group related outputs; UTM auto-generation; aggregate analytics |

#### Calendar Status Flow
```
captured → developing → ready_for_production → scheduled → published → recycle_or_improve
```

#### Acceptance Criteria
- [ ] Calendar renders 500 items in <100ms
- [ ] Drag-drop reschedules; conflicts detected visually
- [ ] "Publish now" requires explicit confirmation modal
- [ ] Published status syncs back from platform via webhook
- [ ] Campaign view shows aggregate performance
- [ ] Failed publishes retry with backoff; alert on persistent failure

---

### Phase 6: Performance Feedback Loop (2 weeks)

#### Goals
- Ingest actual published content metrics from platforms
- Relate performance to source idea, clip, hook, narrative, format, platform
- Analyze patterns → update clip rankings, content suggestions, hooks
- Working metric ingestion (not placeholder)

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| **Platform Webhook Ingestion** | Backend | Normalized schema for LinkedIn, X, Instagram, YouTube, Ghost, Substack |
| **Metric Collector Agent** | Backend | Near-real-time (<5min); idempotent; enrichment with lineage |
| **Attribution Engine** | ML Engineer | Proportional credit to all source ideas/clips in output |
| **Performance Analytics** | Backend | Per-output + aggregated; cohort analysis; platform breakdown |
| **Pattern Analyzer** | ML Engineer | "Hook type X + platform Y → 2x engagement" → actionable insights |
| **Clip Ranking Updater** | ML Engineer | Re-weights clip scoring model based on published performance |
| **Hook Formula Optimizer** | ML Engineer | Updates hook selection weights per platform from evidence |
| **Feedback Dashboard** | Frontend | Shows: source media → clip → content → metrics → insight |

#### Metric Schema (Normalized)
```json
{
  "event_id": "platform_unique_id",
  "platform": "linkedin",
  "content_output_id": "uuid",
  "calendar_item_id": "uuid",
  "source_clip_id": "uuid",
  "source_asset_id": "uuid",
  "metrics": {
    "impressions": 15420,
    "engagements": 1240,
    "engagement_rate": 0.080,
    "clicks": 340,
    "shares": 89,
    "comments": 45
  },
  "timestamp": "2026-10-31T14:30:00Z",
  "attribution": {
    "ideas": ["uuid1", "uuid2"],
    "hook_formula": "contrarian_statement",
    "narrative_type": "problem_solution",
    "format": "linkedin_post"
  }
}
```

#### Acceptance Criteria
- [ ] Webhooks from 6 platforms ingest without data loss
- [ ] Metrics attributable to source clip + hook + narrative + format
- [ ] Dashboard shows "Clips with contrarian hooks on LinkedIn get 2.3x engagement"
- [ ] Clip Intelligence Agent re-ranks using performance evidence
- [ ] Hook formula weights update monthly from top 20% performers
- [ ] Full provenance: metric → content → clip → source media timestamp

---

### Phase 7: IdeaOS Differentiation Layer (3 weeks)

#### Goals
- Layer universal capture, Idea Inbox, semantic memory, Idea Fusion on top
- Cross-device cloud memory (desktop, browser, iOS, web)
- Preserve approval-based creator workflow

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| **Universal Capture API** | Backend | Single endpoint for voice, image, file, link, text |
| **Desktop App (Tauri)** | Frontend | Global hotkey (⌘⇧Space); menu bar; screen capture + OCR; offline queue |
| **Browser Extension (MV3)** | Frontend | Right-capture selection/page; highlight + annotate; tab batch capture |
| **iOS Share Extension + Widget** | Mobile | Share sheet capture; lock screen widget; Shortcuts integration |
| **Idea Inbox UI** | Frontend | Unified inbox: captures → processing → ideas; bulk actions |
| **Semantic Search** | Backend | Hybrid vector + keyword; NL queries ("ideas about pricing from calls") |
| **Idea Graph** | Frontend | Interactive graph: nodes=ideas, edges=connections; filter by type |
| **Idea Fusion Engine** | ML Engine | Connection types: similar, complementary, continuation, contradictory, common_theme |
| **Cross-Device Sync** | Backend | Real-time via Supabase Realtime; conflict resolution; offline-first |

#### Acceptance Criteria
- [ ] Capture from any device appears in Idea Inbox <30s
- [ ] Semantic search returns relevant results in <100ms
- [ ] Idea Graph shows connections; fusion proposals actionable
- [ ] Offline capture on desktop/iOS syncs on reconnect
- [ ] Brand DNA learned from both repurposing + capture edits
- [ ] Approval workflow consistent: capture→idea→fusion→content→calendar

---

### Phase 8: Integration Hardening & Launch (2 weeks)

#### Goals
- End-to-end integration tests for all 6 core workflows
- Load testing, security audit, documentation
- Production deployment with monitoring

#### Tasks
| Task | Owner | Acceptance Criteria |
|------|-------|---------------------|
| **E2E Test Suite** | QA | Playwright tests for all 6 core workflows; run in CI |
| **Load Testing** | DevOps | k6: 1000 RPS API; 100 concurrent ingestions; 500 WS connections |
| **Security Audit** | Security | Penetration test; RLS verification; secrets scan; dependency audit |
| **Documentation** | All | API docs (OpenAPI); architecture docs; runbooks; user guides |
| **Runbooks** | DevOps | Incident response for: ingestion stall, guardian false positive, publish failure |
| **Production Deploy** | DevOps | Blue-green; smoke tests; rollback <5min |
| **Launch Checklist** | PM | All 6 capabilities demoable; metrics dashboards live; on-call rotation |

#### Acceptance Criteria
- [ ] All 6 core workflows pass E2E tests in CI
- [ ] Load test passes: p95 <500ms API; <15min 60min video ingest
- [ ] Security audit: 0 critical, <5 medium findings
- [ ] Documentation complete for developers and users
- [ ] Production deployed; monitoring alerts configured
- [ ] Demo script: 60min podcast → 6 platform posts → calendar → metrics → learning

---

## 4. Cross-Phase Technical Debt Prevention

| Area | Standard | Enforcement |
|------|----------|-------------|
| **API Contracts** | OpenAPI 3.1 + Zod schemas shared via `packages/types` | CI fails on breaking changes |
| **Database Migrations** | Alembic; backward compatible; tested on staging | No manual SQL in prod |
| **Temporal Workflows** | Deterministic; versioned; replay-safe | Code review checklist |
| **AI Prompts** | Versioned in DB; A/B testable; fallback chains | Prompt registry service |
| **Secrets** | Never in code; Vault + env injection; rotation | TruffleHog in CI |
| **Observability** | Every service: health, metrics, logs, traces | Required for merge |

---

## 5. Resource Requirements

### 5.1 Team Composition
| Role | Count | Phases |
|------|-------|--------|
| Backend Engineers (Python/FastAPI/Temporal) | 3 | All |
| ML Engineers (WhisperX, LLMs, embeddings, ranking) | 2 | 1, 2, 3, 4, 6 |
| Frontend Engineers (Next.js, React, Tauri) | 2 | 0, 2, 3, 5, 7 |
| Mobile Engineer (iOS/SwiftUI) | 1 | 0, 7 |
| DevOps/Platform Engineer | 1 | 0, 8 |
| QA/Automation Engineer | 1 | 3, 8 |
| Product Manager | 1 | All |

### 5.2 Infrastructure (Monthly Estimates)
| Component | Dev/Staging | Production |
|-----------|-------------|------------|
| EKS (3 AZ) | $800 | $3,500 |
| RDS PostgreSQL (Multi-AZ) | $400 | $1,800 |
| ElastiCache Redis | $200 | $900 |
| S3/R2 Storage | $100 | $500 |
| Cloudflare (WAF, CDN, Workers) | $50 | $300 |
| AI APIs (Anthropic, OpenAI, WhisperX) | $500 | $5,000+ |
| GPU Instances (A10G × 4) | $1,200 | $4,800 |
| **Total** | **~$3,250** | **~$16,800** |

---

## 6. Risk Register & Mitigations

| Risk | Phase Impact | Likelihood | Impact | Mitigation |
|------|--------------|------------|--------|------------|
| WhisperX diarization accuracy on noisy audio | 1 | High | Medium | Custom vocab boosting; human review queue for low confidence |
| Clip Intelligence explanations feel generic | 2 | Medium | High | Few-shot with creator-specific examples; explicit "why" template |
| Brand Guardian false positives block good content | 4 | High | High | Tunable strictness; explainable violations; quick override + learn |
| Platform API rate limits / breaking changes | 5 | High | Medium | Abstraction layer; multi-provider; graceful degradation |
| Performance feedback loop too sparse for learning | 6 | Medium | High | Synthetic data bootstrap; minimum 50 publications before ML updates |
| Cross-device sync conflicts | 7 | Medium | Medium | CRDT for local-first; last-write-wins with manual merge option |
| Temporal workflow complexity debug difficulty | All | Medium | High | Comprehensive observability; replay CLI; integration test coverage |

---

## 7. Definition of Done (Per Capability)

### Capability 1: Long-Form Media Ingestion ✓
- [ ] 60min video processes in <15min end-to-end
- [ ] Speaker-diarized transcript with word timestamps
- [ ] Topic segments + scene boundaries + keyframes
- [ ] Failed assets retry automatically; dead-letter visible
- [ ] Original media preserved; processing fully observable

### Capability 2: Explainable Clip Selection ✓
- [ ] 8-15 clips recommended with 5 scores + explanation each
- [ ] Manual timestamp adjustment frame-accurate
- [ ] Approve/reject workflow with reason capture
- [ ] Actual MP4 export with optional burned captions
- [ ] Rejection reasons feed back into clip ranking

### Capability 3: Platform-Specific Content ✓
- [ ] 6 distinct platform outputs from single clip
- [ ] Each output structurally different (not truncation)
- [ ] Hook variants (3/platform) with scores
- [ ] Source attribution in every output
- [ ] Creator edits captured for brand learning

### Capability 4: Edit-Learning Brand Memory ✓
- [ ] Brand Guardian: 6 checks in <3s; auto-retry fixes >60%
- [ ] From edits: extracts ≥5 stable rules per 10 edits
- [ ] Rules versioned with diff + rollback
- [ ] New rules apply immediately to next generation
- [ ] Style score correlates >0.9 with human judgment

### Capability 5: Content Calendar ✓
- [ ] Calendar links source → clip → content → publish status
- [ ] Drag-drop scheduling with conflict detection
- [ ] 6 platform publishing integrations working
- [ ] Explicit confirmation required for publish
- [ ] Campaign view with aggregate metrics

### Capability 6: Performance Feedback Loop ✓
- [ ] Webhooks from 6 platforms ingest normalized metrics
- [ ] Full provenance: metric → content → clip → source timestamp
- [ ] Dashboard shows actionable patterns (hook × platform × format)
- [ ] Clip ranking weights update from performance evidence
- [ ] Hook formula selection optimized monthly from top 20%

---

## 8. Milestone Gates

| Gate | Criteria | Decision |
|------|----------|----------|
| **Gate 1 (End Phase 1)** | 60min video → transcript + topics + scenes working | Proceed to Phase 2 |
| **Gate 2 (End Phase 3)** | Single clip → 6 platform outputs passing Guardian | Proceed to Phase 4 |
| **Gate 3 (End Phase 5)** | Full workflow: media → clips → content → calendar → publish | Proceed to Phase 6 |
| **Gate 4 (End Phase 6)** | Metrics ingested → clip ranking updated → measurable improvement | Proceed to Phase 7 |
| **Gate 5 (End Phase 8)** | All 6 capabilities demoable; load test pass; security clean | **LAUNCH** |

---

## 9. Appendix: File Structure (Monorepo)

```
ideaos/
├── apps/
│   ├── api/                    # FastAPI backend (all services)
│   │   ├── src/
│   │   │   ├── capture/        # Capture service
│   │   │   ├── ingestion/      # Ingestion pipeline + Temporal workflows
│   │   │   ├── intelligence/   # Idea extraction agents
│   │   │   ├── fusion/         # Fusion engine agents
│   │   │   ├── content/        # Generation + Brand Guardian
│   │   │   ├── calendar/       # Calendar + publishing
│   │   │   ├── feedback/       # Feedback loop + metrics
│   │   │   ├── workspace/      # Workspace + auth
│   │   │   └── shared/         # DB, config, utils
│   │   └── tests/
│   ├── web/                    # Next.js 15 web app
│   ├── desktop/                # Tauri 2 desktop app
│   ├── extension/              # Chrome/Firefox MV3 extension
│   └── ios/                    # SwiftUI iOS app + Share Extension
├── packages/
│   ├── types/                  # Shared TypeScript types (OpenAPI generated)
│   ├── ui/                     # Shared React components (shadcn/ui)
│   ├── config/                 # Shared config validation (Zod)
│   ├── sdk/                    # TypeScript/Python SDKs
│   └── prompts/                # Versioned prompt templates
├── infrastructure/
│   ├── terraform/              # AWS/GCP infrastructure
│   ├── kubernetes/             # K8s manifests + Helm charts
│   └── temporal/               # Temporal server config
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── API_SPEC.md
│   ├── AGENT_WORKFLOWS.md
│   └── IMPLEMENTATION_PLAN.md
└── turbo.json
```

---

*End of Implementation Plan*