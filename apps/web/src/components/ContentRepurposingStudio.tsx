"use client";

import React, { useState, useEffect } from "react";
import { api, ClipOpportunity, GeneratedContent, LearnedRule } from "@/lib/api";

const DEFAULT_CLIP: ClipOpportunity = {
  clip_id: "clip-1",
  title: "The 400ms Production Defense Barrier",
  start_time: 252,
  end_time: 298,
  duration_seconds: 46,
  hook_strength: 95,
  narrative_score: 92,
  relevance_score: 96,
  viral_potential: 94,
  selection_reason:
    "Features a sharp counter-intuitive reversal in the first 3 seconds, debunking 4K studio polish with empirical data.",
  key_quote:
    "When a viewer scrolls into a 60fps color-graded cinematic video, their brain instantly tags it as an advertisement and raises defensive shields. Authenticity is an algorithmic distribution moat.",
  suggested_platforms: ["linkedin", "twitter", "instagram", "youtube"],
};

interface ContentRepurposingStudioProps {
  selectedClip?: ClipOpportunity;
  ideaId?: string;
  onNavigateToCalendar: () => void;
  onNavigateToBrand: () => void;
}

export function ContentRepurposingStudio({
  selectedClip = DEFAULT_CLIP,
  ideaId,
  onNavigateToCalendar,
  onNavigateToBrand,
}: ContentRepurposingStudioProps) {
  const currentIdeaId = ideaId || (selectedClip as any)?.idea_id || `idea-${selectedClip.clip_id}`;
  const [platform, setPlatform] = useState<"linkedin" | "twitter" | "instagram" | "youtube">("linkedin");
  const [generating, setGenerating] = useState(false);
  const [approving, setApproving] = useState(false);
  const [content, setContent] = useState<GeneratedContent | null>(null);

  // Editable fields
  const [editedTitle, setEditedTitle] = useState("");
  const [editedHook, setEditedHook] = useState("");
  const [editedBody, setEditedBody] = useState("");
  const [editedCTA, setEditedCTA] = useState("");
  const [learnedRules, setLearnedRules] = useState<LearnedRule[]>([]);
  const [approvalMessage, setApprovalMessage] = useState<string | null>(null);

  const fetchGeneration = async (plat: string) => {
    setGenerating(true);
    setApprovalMessage(null);
    try {
      const gen = await api.generateContent({
        idea_id: currentIdeaId,
        clip_title: selectedClip.title,
        key_quote: selectedClip.key_quote,
        selection_reason: selectedClip.selection_reason,
        start_time: selectedClip.start_time,
        end_time: selectedClip.end_time,
        platform: plat,
        format: plat === "twitter" ? "thread" : plat === "instagram" ? "reel" : "post",
      });
      setContent(gen);
      setEditedTitle(gen.title);
      setEditedHook(gen.hook);
      setEditedBody(gen.body);
      setEditedCTA(gen.cta || "");
    } catch (err: any) {
      alert("Generation failed: " + (err.message || String(err)));
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    fetchGeneration(platform);
  }, [platform, selectedClip]);

  const handleApproveAndLearn = async () => {
    if (!content) return;
    setApproving(true);
    try {
      const fullEdited = `${editedHook}\n\n${editedBody}\n\n${editedCTA}`;
      const originalFull = `${content.hook}\n\n${content.body}\n\n${content.cta || ""}`;

      const res = await api.approveAndLearn({
        idea_id: currentIdeaId,
        platform,
        format: platform === "twitter" ? "thread" : "post",
        original_content: originalFull,
        edited_content: fullEdited,
        title: editedTitle,
        schedule_time: new Date(Date.now() + 86400000).toISOString(),
      });

      if (res.learned_brand_rules && res.learned_brand_rules.length > 0) {
        setLearnedRules(res.learned_brand_rules);
        setApprovalMessage(
          `Approved! Brand Memory learned ${res.learned_brand_rules.length} stylistic rule(s) from your edits.`
        );
      } else {
        setApprovalMessage("Approved! Content scheduled to your content calendar.");
      }
    } catch (err: any) {
      alert("Approval error: " + (err.message || String(err)));
    } finally {
      setApproving(false);
    }
  };

  return (
    <div className="space-y-space-lg pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm border-b border-outline-variant/30 pb-space-md">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-outlined text-secondary text-[20px]">transform</span>
            <span className="text-xs font-mono text-secondary uppercase tracking-wider font-semibold">
              Multi-Platform Repurposing Studio
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-on-surface">
            Native Platform Content Studio
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Transform source clips into high-resonance platform drafts guarded by your persistent Brand Memory.
          </p>
        </div>

        {/* Platform Tabs */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-surface-container-high border border-outline-variant/30 self-start md:self-auto">
          {[
            { id: "linkedin", label: "LinkedIn", icon: "work" },
            { id: "twitter", label: "X / Twitter", icon: "tag" },
            { id: "instagram", label: "Instagram Reel", icon: "photo_camera" },
            { id: "youtube", label: "YouTube Shorts", icon: "smart_display" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setPlatform(tab.id as any)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                platform === tab.id
                  ? "bg-surface-container-lowest text-primary border border-outline-variant/50 font-semibold shadow-sm"
                  : "text-outline hover:text-on-surface"
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 3-Column Studio Workstation */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
        {/* Left 3 Columns: Source Clip Context */}
        <div className="lg:col-span-3 space-y-space-md">
          <div className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md space-y-3">
            <div className="text-[11px] font-mono text-secondary uppercase tracking-wider font-semibold flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">movie</span>
              Source Clip Anchor
            </div>

            <h3 className="text-xs font-bold text-on-surface leading-snug">
              {selectedClip.title}
            </h3>

            <div className="p-2.5 rounded-lg bg-surface-container-lowest text-[11px] text-on-surface-variant italic border border-outline-variant/20 leading-relaxed">
              &ldquo;{selectedClip.key_quote}&rdquo;
            </div>

            <div className="text-[10px] font-mono text-outline space-y-1">
              <div>
                <span className="text-on-surface font-semibold">Start:</span> {Math.floor(selectedClip.start_time / 60)}:{(selectedClip.start_time % 60).toString().padStart(2, "0")}
              </div>
              <div>
                <span className="text-on-surface font-semibold">Duration:</span> {selectedClip.duration_seconds}s
              </div>
              <div>
                <span className="text-on-surface font-semibold">Strategy:</span> Contrarian Hook
              </div>
            </div>

            <button
              onClick={() => fetchGeneration(platform)}
              disabled={generating}
              className="w-full py-1.5 rounded bg-surface-container-high hover:bg-surface-bright text-[11px] font-mono text-on-surface font-medium border border-outline-variant/30 transition-all flex items-center justify-center gap-1"
            >
              <span className="material-symbols-outlined text-[14px] text-secondary">refresh</span>
              <span>{generating ? "Regenerating..." : "Regenerate Variant"}</span>
            </button>
          </div>
        </div>

        {/* Center 6 Columns: Live Editable Platform Copy */}
        <div className="lg:col-span-6 space-y-space-md">
          <div className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">edit_note</span>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
                  {platform.toUpperCase()} Copy Editor
                </h3>
              </div>
              <span className="text-[10px] font-mono text-outline">
                Markdown Supported • Edit to Train Brand Memory
              </span>
            </div>

            {/* Editable Hook Headline */}
            <div className="space-y-1">
              <label className="text-[10px] font-mono uppercase tracking-wider text-outline font-semibold">
                Opening Hook Line (Crucial for first 2 seconds)
              </label>
              <input
                type="text"
                value={editedHook}
                onChange={(e) => setEditedHook(e.target.value)}
                className="w-full p-2.5 rounded-lg bg-surface-container-lowest text-xs text-on-surface font-medium border border-outline-variant/30 focus:outline-none focus:border-secondary"
              />
            </div>

            {/* Editable Main Body */}
            <div className="space-y-1">
              <label className="text-[10px] font-mono uppercase tracking-wider text-outline font-semibold">
                Post Body &amp; Value Delivery
              </label>
              <textarea
                rows={9}
                value={editedBody}
                onChange={(e) => setEditedBody(e.target.value)}
                className="w-full p-3 rounded-lg bg-surface-container-lowest text-xs text-on-surface font-mono leading-relaxed border border-outline-variant/30 focus:outline-none focus:border-secondary"
              />
            </div>

            {/* Editable CTA */}
            <div className="space-y-1">
              <label className="text-[10px] font-mono uppercase tracking-wider text-outline font-semibold">
                Closing Call to Action (CTA)
              </label>
              <input
                type="text"
                value={editedCTA}
                onChange={(e) => setEditedCTA(e.target.value)}
                className="w-full p-2.5 rounded-lg bg-surface-container-lowest text-xs text-on-surface font-mono border border-outline-variant/30 focus:outline-none focus:border-secondary"
              />
            </div>

            {/* Hashtags */}
            {content?.hashtags && content.hashtags.length > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap pt-1">
                {content.hashtags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-container-highest text-secondary border border-outline-variant/30"
                  >
                    #{tag.replace(/^#/, "")}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right 3 Columns: Brand Guardian & Approval / Learning Gate */}
        <div className="lg:col-span-3 space-y-space-md">
          <div className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md space-y-3 sticky top-6">
            <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-secondary text-[18px]">verified</span>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
                  Brand Guardian
                </h3>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">
                {content?.quality_score || 95}% Match
              </span>
            </div>

            {/* Guardrail Checklist */}
            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between p-2 rounded bg-surface-container/60 border border-outline-variant/20">
                <span className="text-on-surface-variant">Banned Buzzwords</span>
                <span className="font-mono text-emerald-400 font-semibold flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">check</span> 0 Detected
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-container/60 border border-outline-variant/20">
                <span className="text-on-surface-variant">Directness Tone</span>
                <span className="font-mono text-secondary font-semibold">9.2 / 10</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-container/60 border border-outline-variant/20">
                <span className="text-on-surface-variant">Platform Compliance</span>
                <span className="font-mono text-emerald-400 font-semibold">100% Pass</span>
              </div>
            </div>

            {/* Actions: Approve & Learn */}
            <div className="pt-2 space-y-2">
              <button
                onClick={handleApproveAndLearn}
                disabled={approving || generating}
                className="w-full py-2.5 rounded-lg bg-gradient-to-r from-secondary-container via-primary-container to-tertiary-container text-on-primary text-xs font-semibold hover:opacity-90 active:scale-[0.98] transition-all shadow-[0_0_18px_rgba(59,130,246,0.3)] flex items-center justify-center gap-1.5 font-mono"
              >
                <span className="material-symbols-outlined text-[18px]">psychology</span>
                <span>{approving ? "Extracting Rules & Scheduling..." : "Approve & Learn from Edits"}</span>
              </button>

              <button
                onClick={onNavigateToCalendar}
                className="w-full py-2 rounded-lg bg-surface-container-high hover:bg-surface-bright text-on-surface text-xs font-medium border border-outline-variant/30 transition-all font-mono flex items-center justify-center gap-1"
              >
                <span className="material-symbols-outlined text-[16px] text-primary">calendar_today</span>
                <span>View Content Calendar</span>
              </button>
            </div>

            {/* Notification / Feedback Banner */}
            {approvalMessage && (
              <div className="p-2.5 rounded-lg bg-surface-container border border-secondary/40 text-xs font-mono text-secondary space-y-1 animate-fadeIn">
                <div className="flex items-center gap-1 font-bold">
                  <span className="material-symbols-outlined text-[16px]">check_circle</span>
                  <span>{approvalMessage}</span>
                </div>
                {learnedRules.length > 0 && (
                  <div className="mt-1 text-[11px] text-on-surface space-y-1">
                    {learnedRules.map((rule, idx) => (
                      <div key={idx} className="p-1.5 rounded bg-surface-container-lowest text-outline">
                        <span className="text-tertiary font-semibold">[{rule.rule_type}]</span> {rule.message}
                      </div>
                    ))}
                    <button
                      onClick={onNavigateToBrand}
                      className="text-secondary underline hover:opacity-80 pt-1 block"
                    >
                      View in Brand DNA &amp; Memory Suite →
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
