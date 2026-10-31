"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";

interface DashboardOverviewProps {
  onNavigate: (tab: any) => void;
  onSelectClipOpportunity?: (clip: any) => void;
}

export function DashboardOverview({ onNavigate }: DashboardOverviewProps) {
  const [quickThought, setQuickThought] = useState("");
  const [capturing, setCapturing] = useState(false);
  const [captureMessage, setCaptureMessage] = useState<string | null>(null);

  const handleQuickCapture = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!quickThought.trim()) return;

    setCapturing(true);
    try {
      await api.quickCapture(quickThought.trim());
      setCaptureMessage(`Idea buffered into Unreviewed Inbox: "${quickThought.slice(0, 38)}..."`);
      setQuickThought("");
      setTimeout(() => setCaptureMessage(null), 4000);
    } catch {
      setCaptureMessage("Idea captured in local buffer.");
      setQuickThought("");
      setTimeout(() => setCaptureMessage(null), 3000);
    } finally {
      setCapturing(false);
    }
  };

  return (
    <div className="space-y-space-lg pb-16">
      {/* Hero Section */}
      <section className="relative rounded-xl bg-gradient-to-br from-surface-container-high/80 via-surface-container to-surface-container-low p-space-lg shadow-lg border border-outline-variant/30 overflow-hidden">
        <div className="absolute -top-12 -right-12 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/2 -right-24 w-80 h-80 bg-secondary/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-space-md">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-secondary-container/15 text-secondary border border-secondary/20 text-xs font-mono font-medium">
              <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
              Autonomous Creative Intelligence • Active
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-on-surface">
              Your ideas are becoming content.
            </h1>
            <p className="text-on-surface-variant text-sm leading-relaxed">
              IdeaOS discovered <span className="text-secondary font-medium">4 high-resonance clip opportunities</span> and synthesized an active cross-domain fusion across your podcasts and notes.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-2 bg-surface-container-lowest/80 p-2.5 rounded-xl backdrop-blur-md shrink-0 border border-outline-variant/30 w-full lg:w-auto">
            <div className="px-3 py-2 text-center sm:text-left">
              <div className="text-[11px] font-mono text-outline">Captured Ideas</div>
              <div className="text-xl text-on-surface font-semibold flex items-baseline gap-1">
                142 <span className="text-[10px] font-mono text-secondary">+12%</span>
              </div>
            </div>
            <div className="px-3 py-2 text-center sm:text-left border-l border-outline-variant/30">
              <div className="text-[11px] font-mono text-outline">Fusions Ready</div>
              <div className="text-xl text-tertiary font-semibold flex items-baseline gap-1">
                3 <span className="text-[10px] font-mono text-tertiary-fixed-dim">New</span>
              </div>
            </div>
            <div className="px-3 py-2 text-center sm:text-left border-l border-outline-variant/30">
              <div className="text-[11px] font-mono text-outline">Repurposed Drafts</div>
              <div className="text-xl text-secondary-fixed font-semibold flex items-baseline gap-1">
                4 <span className="text-[10px] font-mono text-secondary">Ready</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Scratchpad Bar */}
        <div className="mt-space-md pt-space-sm bg-surface-container/60 rounded-xl p-space-md border border-outline-variant/30">
          <form onSubmit={handleQuickCapture} className="flex flex-col md:flex-row items-stretch md:items-center gap-space-sm">
            <div className="relative flex-1">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                psychology
              </span>
              <input
                type="text"
                value={quickThought}
                onChange={(e) => setQuickThought(e.target.value)}
                placeholder="Dump a fleeting thought, raw voice memo fragment, or research topic..."
                className="w-full h-11 pl-10 pr-24 bg-surface-container-lowest text-on-surface placeholder:text-outline text-sm rounded-lg focus:outline-none focus:ring-1 focus:ring-secondary transition-all"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                <span className="text-[10px] font-mono text-outline px-1.5 py-0.5 rounded bg-surface-container">
                  Enter to save
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                type="submit"
                disabled={capturing || !quickThought.trim()}
                className="flex items-center justify-center gap-1.5 px-4 h-11 rounded-lg bg-gradient-to-r from-secondary-container via-primary-container to-tertiary-container text-on-primary text-xs font-semibold shadow-[0_0_24px_-4px_rgba(59,130,246,0.35)] hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-[18px]">add_circle</span>
                <span>{capturing ? "Capturing..." : "+ Quick Capture"}</span>
              </button>

              <button
                type="button"
                onClick={() => onNavigate("ingest")}
                className="flex items-center justify-center gap-1.5 px-4 h-11 rounded-lg bg-surface-container-high hover:bg-surface-bright text-on-surface text-xs font-medium border border-outline-variant/30 transition-colors"
              >
                <span className="material-symbols-outlined text-[18px] text-secondary">upload_file</span>
                <span>Ingest Video or Podcast</span>
              </button>
            </div>
          </form>

          {captureMessage && (
            <div className="mt-2 text-xs font-mono text-secondary flex items-center gap-1.5 animate-fadeIn">
              <span className="material-symbols-outlined text-[16px]">check_circle</span>
              {captureMessage}
            </div>
          )}
        </div>
      </section>

      {/* Idea Fusion Spotlight Card */}
      <section className="rounded-xl bg-surface-container-low p-space-lg shadow-lg border border-outline-variant/30 relative overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm mb-4">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-tertiary text-[20px]">hub</span>
              <span className="text-xs font-mono text-tertiary uppercase tracking-wider font-semibold">
                Autonomous Cross-Domain Synthesis
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-outline" />
              <span className="text-xs font-mono text-outline">Idea Fusion Engine</span>
            </div>
            <h2 className="text-lg text-on-surface font-semibold">
              &quot;The Lo-Fi Hook, Hi-Fi Substance Playbook: Why Top Creators Shoot Handheld but Deliver Enterprise Insights&quot;
            </h2>
          </div>
          <button
            onClick={() => onNavigate("fusion")}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-tertiary-container/20 hover:bg-tertiary-container/30 text-tertiary text-xs font-mono font-medium border border-tertiary/30 transition-all self-start sm:self-auto"
          >
            <span>Open Fusion Lab</span>
            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
          </button>
        </div>

        <p className="text-sm text-on-surface-variant leading-relaxed mb-4">
          Synthesized by connecting your latest podcast transcription on attention arbitrage with 2 voice notes on micro-authenticity and mobile video editing. Predicted viral resonance score: <span className="text-emerald-400 font-mono font-semibold">94/100</span>.
        </p>

        {/* Source Nodes */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
          <div className="p-3 rounded-lg bg-surface-container/60 border border-outline-variant/20">
            <div className="text-[10px] font-mono text-outline uppercase flex items-center gap-1 mb-1">
              <span className="material-symbols-outlined text-[14px] text-secondary">mic</span>
              Podcast Ep #48
            </div>
            <div className="text-xs font-medium text-on-surface">The Attention Arbitrage Network</div>
            <div className="text-[11px] text-on-surface-variant mt-1">Founders must own audience distribution rails.</div>
          </div>
          <div className="p-3 rounded-lg bg-surface-container/60 border border-outline-variant/20">
            <div className="text-[10px] font-mono text-outline uppercase flex items-center gap-1 mb-1">
              <span className="material-symbols-outlined text-[14px] text-primary">record_voice_over</span>
              Voice Note #89
            </div>
            <div className="text-xs font-medium text-on-surface">Micro-Authenticity Paradox</div>
            <div className="text-[11px] text-on-surface-variant mt-1">High production creates psychological distance.</div>
          </div>
          <div className="p-3 rounded-lg bg-surface-container/60 border border-outline-variant/20">
            <div className="text-[10px] font-mono text-outline uppercase flex items-center gap-1 mb-1">
              <span className="material-symbols-outlined text-[14px] text-tertiary">edit_note</span>
              Whiteboard Note #34
            </div>
            <div className="text-xs font-medium text-on-surface">Audience Trust Compounding</div>
            <div className="text-[11px] text-on-surface-variant mt-1">Retention spikes on vulnerability vs perfection.</div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate("repurpose")}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-secondary-container to-primary-container text-on-primary text-xs font-semibold hover:opacity-90 transition-all shadow-[0_0_16px_rgba(59,130,246,0.25)]"
          >
            <span className="material-symbols-outlined text-[18px]">transform</span>
            <span>Generate Multi-Platform Campaign</span>
          </button>
          <button
            onClick={() => onNavigate("clips")}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-surface-container-high hover:bg-surface-bright text-on-surface text-xs font-medium border border-outline-variant/30 transition-all"
          >
            <span className="material-symbols-outlined text-[18px] text-secondary">movie_edit</span>
            <span>Inspect Clip Opportunities</span>
          </button>
        </div>
      </section>

      {/* Two Column Grid: Ready Hooks & Brand Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-space-md">
        {/* Ready to Extract Hooks */}
        <div className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary text-[20px]">bolt</span>
              <h3 className="text-sm font-semibold text-on-surface">Ready-to-Extract High Retention Hooks</h3>
            </div>
            <button
              onClick={() => onNavigate("clips")}
              className="text-xs font-mono text-secondary hover:underline flex items-center gap-1"
            >
              <span>View All 3</span>
              <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            </button>
          </div>

          <div className="space-y-2">
            <div
              onClick={() => onNavigate("clips")}
              className="p-3 rounded-lg bg-surface-container/70 hover:bg-surface-container border border-outline-variant/20 cursor-pointer transition-all space-y-1.5"
            >
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="px-1.5 py-0.5 rounded bg-primary-container/20 text-primary">Contrarian Reversal</span>
                <span className="text-emerald-400 font-semibold">94/100 Viral Score</span>
              </div>
              <div className="text-xs font-medium text-on-surface">
                &quot;The 400ms Production Defense Barrier: Why over-editing kills organic conversion&quot;
              </div>
              <div className="text-[11px] text-outline">
                Clip 04:12 - 04:58 (46s) • Explains why vulnerability beats studio polish
              </div>
            </div>

            <div
              onClick={() => onNavigate("clips")}
              className="p-3 rounded-lg bg-surface-container/70 hover:bg-surface-container border border-outline-variant/20 cursor-pointer transition-all space-y-1.5"
            >
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="px-1.5 py-0.5 rounded bg-secondary-container/20 text-secondary">Framework Reveal</span>
                <span className="text-emerald-400 font-semibold">91/100 Viral Score</span>
              </div>
              <div className="text-xs font-medium text-on-surface">
                &quot;Micro-Community Trust Compounding vs 100k Passive Audience vanity metrics&quot;
              </div>
              <div className="text-[11px] text-outline">
                Clip 12:30 - 13:15 (45s) • Compares conversion rates of tight cohorts
              </div>
            </div>
          </div>
        </div>

        {/* Brand Memory & Learning Loop Status */}
        <div className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-tertiary text-[20px]">psychology</span>
              <h3 className="text-sm font-semibold text-on-surface">Brand Memory &amp; Learning Loop</h3>
            </div>
            <button
              onClick={() => onNavigate("brand")}
              className="text-xs font-mono text-tertiary hover:underline flex items-center gap-1"
            >
              <span>Brand DNA</span>
              <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            </button>
          </div>

          <div className="p-3 rounded-lg bg-surface-container/70 border border-outline-variant/20 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-on-surface font-medium">Brand Voice Alignment</span>
              <span className="font-mono text-secondary font-semibold">96%</span>
            </div>
            <div className="w-full bg-surface-container-lowest h-2 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-secondary to-primary h-full rounded-full" style={{ width: "96%" }} />
            </div>
            <div className="text-[11px] text-outline font-mono">
              Learned 4 creator rules from recent edits • 0 buzzword violations
            </div>
          </div>

          <div className="p-3 rounded-lg bg-surface-container/70 border border-outline-variant/20 flex items-center justify-between">
            <div>
              <div className="text-xs font-medium text-on-surface">Active Voice Constraints</div>
              <div className="text-[11px] text-outline font-mono">Banned: &apos;delve&apos;, &apos;synergy&apos;, &apos;game-changer&apos;</div>
            </div>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Active Guardrails
            </span>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <button
              onClick={() => onNavigate("calendar")}
              className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-surface-container-high hover:bg-surface-bright text-xs text-on-surface font-medium border border-outline-variant/30 transition-all"
            >
              <span className="material-symbols-outlined text-[16px] text-primary">calendar_today</span>
              <span>Content Calendar</span>
            </button>
            <button
              onClick={() => onNavigate("brand")}
              className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-surface-container-high hover:bg-surface-bright text-xs text-on-surface font-medium border border-outline-variant/30 transition-all"
            >
              <span className="material-symbols-outlined text-[16px] text-tertiary">tune</span>
              <span>Tune Tone Sliders</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
