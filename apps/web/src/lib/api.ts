/**
 * Typed API client connecting Next.js to FastAPI backend.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api/v1" : "http://localhost:8000/api/v1");

export interface Segment {
  start_time: number;
  end_time: number;
  speaker: string;
  topic: string;
  text: string;
}

export interface ClipOpportunity {
  clip_id: string;
  title: string;
  start_time: number;
  end_time: number;
  duration_seconds: number;
  hook_strength: number;
  narrative_score: number;
  relevance_score: number;
  viral_potential: number;
  selection_reason: string;
  key_quote: string;
  suggested_platforms: string[];
}

export interface IngestResponse {
  capture_id: string;
  idea_id: string;
  title: string;
  summary: string;
  main_topic: string;
  duration_seconds: number;
  segments: Segment[];
  clip_opportunities: ClipOpportunity[];
}

export interface GeneratedContent {
  idea_id: string;
  platform: string;
  format: string;
  title: string;
  hook: string;
  body: string;
  cta?: string;
  hashtags: string[];
  quality_score: number;
  quality_passed: boolean;
  quality_warnings: string[];
  visual_notes: Array<{ timestamp: string; direction: string }>;
}

export interface LearnedRule {
  rule_type: string;
  pattern: string;
  severity: string;
  message: string;
  examples: string[];
  applies_to: string[];
}

export interface ApprovedContentResponse {
  content_output_id: string;
  calendar_item_id?: string;
  status: string;
  learned_brand_rules: LearnedRule[];
  message: string;
}

export interface CalendarItem {
  id: string;
  platform: string;
  status: string;
  scheduled_at: string;
  metadata?: Record<string, any>;
}

export interface FusionProposal {
  id: string;
  new_idea_id: string;
  source_idea_ids: string[];
  fusion_concept: string;
  confidence: number;
  content_opportunities: Array<{
    platform: string;
    format: string;
    angle: string;
    pillar: string;
  }>;
  status: string;
}

export const api = {
  async uploadMedia(file: File, title?: string, content_pillar = "Repurposing", media_type = "podcast"): Promise<IngestResponse> {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    formData.append("content_pillar", content_pillar);
    formData.append("media_type", media_type);

    const res = await fetch(`${API_BASE_URL}/repurpose/upload-media`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(`Audio upload & transcription failed: ${await res.text()}`);
    const data = await res.json();
    return data;
  },

  async ingestMedia(content: string, title?: string, media_type = "podcast"): Promise<IngestResponse> {
    const res = await fetch(`${API_BASE_URL}/repurpose/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, title, media_type }),
    });
    if (!res.ok) throw new Error(`Ingest failed: ${await res.text()}`);
    const data = await res.json();
    return data;
  },

  async generateContent(payload: {
    idea_id: string;
    clip_title: string;
    key_quote: string;
    selection_reason: string;
    start_time: number;
    end_time: number;
    platform: string;
    format: string;
  }): Promise<GeneratedContent> {
    const res = await fetch(`${API_BASE_URL}/repurpose/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Generate failed: ${await res.text()}`);
    const data = await res.json();
    return data;
  },

  async approveAndLearn(payload: {
    idea_id: string;
    platform: string;
    format: string;
    original_content: string;
    edited_content: string;
    title?: string;
    schedule_time?: string;
  }): Promise<ApprovedContentResponse> {
    const res = await fetch(`${API_BASE_URL}/repurpose/edit-and-approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Approve failed: ${await res.text()}`);
    const data = await res.json();
    return data;
  },

  async getCalendarItems(): Promise<CalendarItem[]> {
    const res = await fetch(`${API_BASE_URL}/calendar`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`Calendar fetch failed: ${await res.text()}`);
    const data = await res.json();
    return data.data || [];
  },

  async logPerformance(payload: {
    content_output_id: string;
    views: number;
    likes: number;
    shares: number;
    comments: number;
    retention_rate?: number;
  }) {
    const res = await fetch(`${API_BASE_URL}/repurpose/performance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Log performance failed: ${await res.text()}`);
    const data = await res.json();
    return data;
  },

  async getFusionProposals(): Promise<FusionProposal[]> {
    const res = await fetch(`${API_BASE_URL}/fusion/proposals`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`Fetch fusion proposals failed: ${await res.text()}`);
    const data = await res.json();
    return Array.isArray(data) ? data : data.data || [];
  },

  async suggestFusions(idea_id: string): Promise<FusionProposal[]> {
    const res = await fetch(`${API_BASE_URL}/fusion/suggest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea_id, max_candidates: 5 }),
    });
    if (!res.ok) throw new Error(`Suggest fusions failed: ${await res.text()}`);
    const data = await res.json();
    return data;
  },

  async approveFusion(proposal_id: string, title?: string) {
    const res = await fetch(`${API_BASE_URL}/fusion/${proposal_id}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ create_master_idea: true, master_idea_title: title }),
    });
    if (!res.ok) throw new Error(`Approve fusion failed: ${await res.text()}`);
    const data = await res.json();
    return data;
  },

  async getBrandRules(): Promise<LearnedRule[]> {
    const res = await fetch(`${API_BASE_URL}/brand/rules`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`Fetch brand rules failed: ${await res.text()}`);
    const data = await res.json();
    return data.data || [];
  },

  async quickCapture(text: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/captures`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: "text",
        source_text: text,
        metadata: { source: "quick_scratchpad", title: text.slice(0, 50) },
      }),
    });
    if (!res.ok) throw new Error(`Quick capture failed: ${await res.text()}`);
    const data = await res.json();
    return data;
  },
};
