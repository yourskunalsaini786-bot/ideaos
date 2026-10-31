"use client";

import React, { useState } from "react";
import { ClipOpportunity } from "@/lib/api";

const DEFAULT_CLIPS: ClipOpportunity[] = [
  {
    clip_id: "clip-1",
    title: "The 400ms Production Defense Barrier: Why Over-Editing Kills Organic Conversion",
    start_time: 252, // 04:12
    end_time: 298,   // 04:58
    duration_seconds: 46,
    hook_strength: 95,
    narrative_score: 92,
    relevance_score: 96,
    viral_potential: 94,
    selection_reason:
      "Features a sharp counter-intuitive reversal in the first 3 seconds, debunking 4K studio polish with empirical data. Mirror neuron trigger projected to drive >80% retention past 15s.",
    key_quote:
      "When a viewer scrolls into a 60fps color-graded cinematic video, their brain instantly tags it as an advertisement and raises defensive shields. Authenticity is an algorithmic distribution moat.",
    suggested_platforms: ["linkedin", "instagram", "youtube", "twitter"],
  },
  {
    clip_id: "clip-2",
    title: "The Illusion of Passive Audience Loyalty: Micro-Cohorts vs 100k Channels",
    start_time: 750, // 12:30
    end_time: 795,   // 13:15
    duration_seconds: 45,
    hook_strength: 90,
    narrative_score: 89,
    relevance_score: 93,
    viral_potential: 91,
    selection_reason:
      "Presents a high-contrast financial comparison between vanity subscriber counts and high-intent niche cohorts. High resonance for founders and monetization strategists.",
    key_quote:
      "A channel with 3,000 highly aligned operators generates 5x the ARR of a vanity channel with 100,000 passive subscribers. Passive audiences click, but high-intent cohorts convert.",
    suggested_platforms: ["linkedin", "twitter", "youtube"],
  },
  {
    clip_id: "clip-3",
    title: "Building an Autonomous Intellectual Flywheel from Long-Form Core Theses",
    start_time: 790, // 13:10
    end_time: 835,   // 13:55
    duration_seconds: 45,
    hook_strength: 86,
    narrative_score: 91,
    relevance_score: 88,
    viral_potential: 88,
    selection_reason:
      "Actionable tactical breakdown on turning raw podcast dialogue into multi-platform atomic content with compounding brand memory.",
    key_quote:
      "When you repurpose your long-form core theses into platform-native atomic content, you're not just clipping—you're building an autonomous intellectual flywheel.",
    suggested_platforms: ["linkedin", "instagram", "twitter"],
  },
];

interface ClipSelectionStudioProps {
  clips?: ClipOpportunity[];
  onSelectClipForRepurpose: (clip: ClipOpportunity) => void;
}

export function ClipSelectionStudio({
  clips,
  onSelectClipForRepurpose,
}: ClipSelectionStudioProps) {
  const [internalClips, setInternalClips] = useState<ClipOpportunity[]>(clips || []);
  const [selectedClipId, setSelectedClipId] = useState<string>(
    clips && clips.length > 0 ? clips[0].clip_id : ""
  );

  const displayClips = internalClips;
  const activeClip = displayClips.find((c) => c.clip_id === selectedClipId) || displayClips[0];

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="space-y-space-lg pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm border-b border-outline-variant/30 pb-space-md">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-outlined text-secondary text-[20px]">movie_edit</span>
            <span className="text-xs font-mono text-secondary uppercase tracking-wider font-semibold">
              AI Clip Selection &amp; Hook Architecture
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-on-surface">
            Explainable Clip Intelligence Studio
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Every clip recommendation includes an explicit AI selection rationale, retention projection, and 9:16 safe-zone framing.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-lg bg-surface-container-high text-on-surface border border-outline-variant/30">
            {displayClips.length} Opportunities Identified
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Avg Viral Score: {displayClips.length > 0 ? Math.round(displayClips.reduce((acc, c) => acc + c.viral_potential, 0) / displayClips.length) : 0}%
          </span>
        </div>
      </div>

      {displayClips.length === 0 ? (
        <div className="p-12 text-center rounded-xl bg-surface-container-low border border-outline-variant/30 space-y-3">
          <div className="w-12 h-12 mx-auto rounded-full bg-secondary-container/15 flex items-center justify-center text-secondary">
            <span className="material-symbols-outlined text-[24px]">movie_filter</span>
          </div>
          <h3 className="text-sm font-semibold text-on-surface">No Media Clips Extracted Yet</h3>
          <p className="text-xs text-outline max-w-sm mx-auto">
            Process a podcast or video in the Ingestion Studio to automatically extract explainable clip opportunities, or load sample clips to test.
          </p>
          <button
            type="button"
            onClick={() => {
              setInternalClips(DEFAULT_CLIPS);
              setSelectedClipId(DEFAULT_CLIPS[0].clip_id);
            }}
            className="px-3.5 py-2 rounded-lg bg-surface-container-high hover:bg-surface-bright text-xs font-mono text-secondary border border-secondary/30 transition-all inline-flex items-center gap-1.5"
          >
            <span className="material-symbols-outlined text-[16px]">play_circle</span>
            <span>Load Sample Clips [Demo Mode]</span>
          </button>
        </div>
      ) : (
        /* Main Grid: Left Explainable Cards, Right 9:16 Inspector */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
        {/* Left 7 Columns: Clip Opportunity Cards */}
        <div className="lg:col-span-7 space-y-space-md">
          {displayClips.map((clip, index) => {
            const isSelected = clip.clip_id === selectedClipId;
            return (
              <div
                key={clip.clip_id || index}
                onClick={() => setSelectedClipId(clip.clip_id)}
                className={`rounded-xl p-space-md border transition-all cursor-pointer relative overflow-hidden ${
                  isSelected
                    ? "bg-surface-container border-secondary/60 shadow-[0_0_24px_-4px_rgba(6,182,212,0.2)]"
                    : "bg-surface-container-low hover:bg-surface-container/70 border-outline-variant/30"
                }`}
              >
                {/* Top Telemetry Row */}
                <div className="flex items-center justify-between text-xs font-mono mb-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-secondary-container/20 text-secondary border border-secondary/30">
                      Clip #{index + 1}
                    </span>
                    <span className="text-outline">
                      {formatTime(clip.start_time)} - {formatTime(clip.end_time)} ({clip.duration_seconds}s)
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 font-bold">
                    <span className="text-emerald-400">{Math.round(clip.viral_potential)}%</span>
                    <span className="text-[10px] text-outline uppercase font-normal">Viral Potential</span>
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-sm font-semibold text-on-surface mb-2 leading-snug">
                  {clip.title}
                </h3>

                {/* Key Quote / Anchor */}
                <div className="p-2.5 rounded-lg bg-surface-container-lowest/80 border border-outline-variant/20 mb-3 text-xs text-on-surface-variant italic leading-relaxed">
                  <span className="text-secondary font-bold mr-1">&ldquo;</span>
                  {clip.key_quote}
                  <span className="text-secondary font-bold ml-1">&rdquo;</span>
                </div>

                {/* EXPLICIT SELECTION RATIONALE (Mandatory Requirement) */}
                <div className="p-2.5 rounded-lg bg-surface-container-high/60 border border-outline-variant/30 mb-3">
                  <div className="flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-secondary font-semibold mb-1">
                    <span className="material-symbols-outlined text-[14px]">psychology</span>
                    <span>AI Selection Rationale</span>
                  </div>
                  <p className="text-xs text-on-surface leading-relaxed">
                    {clip.selection_reason}
                  </p>
                </div>

                {/* Action Footer */}
                <div className="flex items-center justify-between pt-2 border-t border-outline-variant/20">
                  <div className="flex items-center gap-1">
                    {clip.suggested_platforms.map((p) => (
                      <span
                        key={p}
                        className="px-1.5 py-0.5 rounded text-[9px] font-mono uppercase bg-surface-container-highest text-outline"
                      >
                        {p}
                      </span>
                    ))}
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectClipForRepurpose(clip);
                    }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-secondary-container via-primary-container to-tertiary-container text-on-primary text-xs font-semibold hover:opacity-90 active:scale-[0.98] transition-all shadow-sm font-mono"
                  >
                    <span>Repurpose Clip</span>
                    <span className="material-symbols-outlined text-[16px]">transform</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right 5 Columns: 9:16 Vertical Reframe Inspector */}
        <div className="lg:col-span-5 space-y-space-md">
          <div className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-lg sticky top-6">
            <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20 mb-3">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-secondary text-[18px]">crop_portrait</span>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
                  9:16 Reframe Inspector
                </h3>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-container-highest text-secondary font-semibold">
                Auto Face-Lock
              </span>
            </div>

            {/* Vertical 9:16 Video Canvas Mockup */}
            <div className="relative mx-auto w-64 h-[420px] rounded-2xl bg-surface-container-lowest border-2 border-outline-variant/40 overflow-hidden shadow-2xl flex flex-col justify-between p-4">
              {/* Top Meta Overlay */}
              <div className="flex items-center justify-between text-[10px] font-mono text-white/80 z-10">
                <span className="px-1.5 py-0.5 rounded bg-black/60 backdrop-blur-sm">
                  {formatTime(activeClip.start_time)}
                </span>
                <span className="px-1.5 py-0.5 rounded bg-secondary/80 text-surface font-bold backdrop-blur-sm">
                  {Math.round(activeClip.viral_potential)}% Viral
                </span>
              </div>

              {/* Center Face Safe-Zone Box */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-36 h-36 rounded-full border border-secondary/40 border-dashed flex items-center justify-center bg-secondary/5 animate-pulse">
                  <div className="text-center text-[10px] font-mono text-secondary/70">
                    <span className="material-symbols-outlined text-[28px] opacity-70">face</span>
                    <div>Host Center Focus</div>
                  </div>
                </div>
              </div>

              {/* Bottom Dynamic Subtitle Overlay */}
              <div className="z-10 bg-black/75 backdrop-blur-md rounded-xl p-3 border border-white/10 text-center">
                <span className="text-[10px] font-mono text-secondary uppercase tracking-widest block mb-0.5 font-bold">
                  HIGH RETENTION HOOK
                </span>
                <p className="text-xs font-bold text-white leading-tight">
                  &ldquo;{activeClip.key_quote.slice(0, 95)}...&rdquo;
                </p>
              </div>
            </div>

            {/* Hook Architecture Telemetry */}
            <div className="mt-4 p-3 rounded-lg bg-surface-container/60 border border-outline-variant/20 space-y-2">
              <div className="text-[11px] font-mono text-outline uppercase tracking-wider font-semibold">
                Telemetry Diagnostics
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded bg-surface-container-lowest border border-outline-variant/20">
                  <div className="text-[10px] font-mono text-outline">Hook Strength</div>
                  <div className="font-mono font-bold text-secondary">{activeClip.hook_strength}/100</div>
                </div>
                <div className="p-2 rounded bg-surface-container-lowest border border-outline-variant/20">
                  <div className="text-[10px] font-mono text-outline">Narrative Arc</div>
                  <div className="font-mono font-bold text-tertiary">{activeClip.narrative_score}/100</div>
                </div>
              </div>

              <button
                onClick={() => onSelectClipForRepurpose(activeClip)}
                className="w-full mt-2 py-2 rounded-lg bg-gradient-to-r from-secondary-container via-primary-container to-tertiary-container text-on-primary text-xs font-semibold hover:opacity-90 transition-all font-mono shadow-md flex items-center justify-center gap-1.5"
              >
                <span>Repurpose Selected Clip</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      )}
    </div>
  );
}
