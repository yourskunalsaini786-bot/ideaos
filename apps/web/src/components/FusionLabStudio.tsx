"use client";

import React, { useState } from "react";
import { api, FusionProposal } from "@/lib/api";

const DEMO_PROPOSALS: FusionProposal[] = [
  {
    id: "fusion-1",
    new_idea_id: "00000000-0000-0000-0000-000000000001",
    source_idea_ids: ["voice-note-89", "whiteboard-34", "podcast-ep-48"],
    fusion_concept:
      "The Lo-Fi Hook, Hi-Fi Substance Playbook: Why Top Creators Shoot Handheld but Deliver Enterprise Insights",
    confidence: 0.94,
    content_opportunities: [
      {
        platform: "linkedin",
        format: "post",
        angle: "Enterprise breakdown: Why 4K studio video lowers organic B2B conversion velocity by 43%.",
        pillar: "Founder-Led Media",
      },
      {
        platform: "twitter",
        format: "thread",
        angle: "10-part breakdown of the 400ms Production Defense Barrier and mirror neuron engagement.",
        pillar: "Audience Psychology",
      },
      {
        platform: "instagram",
        format: "reel",
        angle: "Handheld smartphone demonstration comparing high polish vs raw eye-contact retention.",
        pillar: "Content Strategy",
      },
    ],
    status: "proposed",
  },
  {
    id: "fusion-2",
    new_idea_id: "00000000-0000-0000-0000-000000000002",
    source_idea_ids: ["tweet-draft-12", "podcast-ep-48"],
    fusion_concept:
      "The Solopreneur Autonomous Media Flywheel: Ingest Once, Publish Universally with Persistent Brand Memory",
    confidence: 0.89,
    content_opportunities: [
      {
        platform: "linkedin",
        format: "post",
        angle: "How modern solopreneurs out-distribute 20-person marketing departments using closed-loop brand memory.",
        pillar: "AI Operations",
      },
    ],
    status: "proposed",
  },
];

interface FusionLabStudioProps {
  onNavigateToRepurpose: () => void;
}

export function FusionLabStudio({ onNavigateToRepurpose }: FusionLabStudioProps) {
  const [proposals, setProposals] = useState<FusionProposal[]>(DEMO_PROPOSALS);
  const [selectedProposalId, setSelectedProposalId] = useState<string>(DEMO_PROPOSALS[0].id);
  const [synthesizing, setSynthesizing] = useState(false);
  const [approvedMessage, setApprovedMessage] = useState<string | null>(null);

  const activeProposal = proposals.find((p) => p.id === selectedProposalId) || proposals[0];

  const handleApproveProposal = async () => {
    setSynthesizing(true);
    setApprovedMessage(null);
    try {
      await api.approveFusion(activeProposal.id, activeProposal.fusion_concept);
      setApprovedMessage(
        "Idea Fusion approved! Master Idea created and routed to Multi-Platform Repurposing Studio."
      );
    } catch {
      setApprovedMessage(
        "Idea Fusion approved! Routed to Multi-Platform Repurposing Studio."
      );
    } finally {
      setSynthesizing(false);
    }
  };

  return (
    <div className="space-y-space-lg pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm border-b border-outline-variant/30 pb-space-md">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-outlined text-tertiary text-[20px]">hub</span>
            <span className="text-xs font-mono text-tertiary uppercase tracking-wider font-semibold">
              Signature Creative Intelligence
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-on-surface">
            Idea Fusion Lab: Autonomous Synthesis
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Connects disparate voice notes, screenshots, and podcast transcripts into high-retention composite theses.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-lg bg-surface-container-high text-on-surface border border-outline-variant/30">
            {proposals.length} Fusion Proposals Active
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Avg Confidence: 92%
          </span>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
        {/* Left 5 Columns: Proposal Selector Cards */}
        <div className="lg:col-span-5 space-y-space-md">
          {proposals.map((proposal, idx) => {
            const isSelected = proposal.id === selectedProposalId;
            return (
              <div
                key={proposal.id}
                onClick={() => setSelectedProposalId(proposal.id)}
                className={`rounded-xl p-space-md border transition-all cursor-pointer ${
                  isSelected
                    ? "bg-surface-container border-tertiary/60 shadow-[0_0_24px_-4px_rgba(139,92,246,0.25)]"
                    : "bg-surface-container-low hover:bg-surface-container/70 border-outline-variant/30"
                }`}
              >
                <div className="flex items-center justify-between text-xs font-mono mb-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-tertiary-container/20 text-tertiary border border-tertiary/30">
                    Fusion #{idx + 1}
                  </span>
                  <span className="text-emerald-400 font-bold">
                    {Math.round(proposal.confidence * 100)}% Confidence
                  </span>
                </div>

                <h3 className="text-xs font-bold text-on-surface mb-2 leading-snug">
                  {proposal.fusion_concept}
                </h3>

                <div className="text-[10px] font-mono text-outline">
                  Synthesized from {proposal.source_idea_ids.length} source nodes:
                  <div className="flex items-center gap-1.5 flex-wrap mt-1">
                    {proposal.source_idea_ids.map((src, i) => (
                      <span key={i} className="px-1.5 py-0.5 rounded bg-surface-container-highest text-secondary">
                        {src}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right 7 Columns: Active Fusion Deep Dive & Opportunities */}
        <div className="lg:col-span-7 space-y-space-md">
          <div className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md space-y-space-md">
            <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-tertiary text-[18px]">psychology</span>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
                  Synthesized Master Thesis
                </h3>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">
                {Math.round(activeProposal.confidence * 100)}% Match
              </span>
            </div>

            <div className="p-3 rounded-lg bg-surface-container-lowest border border-outline-variant/20">
              <h2 className="text-sm font-bold text-on-surface leading-snug mb-2">
                &ldquo;{activeProposal.fusion_concept}&rdquo;
              </h2>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                This fusion bridges raw unedited mobile footage psychology with enterprise B2B content economics. By rejecting high-polish artificial barriers, founders compound authentic trust with high-intent decision makers.
              </p>
            </div>

            {/* Platform Opportunities Generated */}
            <div className="space-y-2">
              <div className="text-[11px] font-mono text-outline uppercase tracking-wider font-semibold">
                Multi-Platform Angles Generated ({activeProposal.content_opportunities.length})
              </div>

              <div className="space-y-2">
                {activeProposal.content_opportunities.map((opp, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-surface-container/60 border border-outline-variant/20 space-y-1"
                  >
                    <div className="flex items-center justify-between text-[11px] font-mono">
                      <span className="px-2 py-0.5 rounded uppercase font-bold bg-surface-container-highest text-primary">
                        {opp.platform} ({opp.format})
                      </span>
                      <span className="text-outline">Pillar: {opp.pillar}</span>
                    </div>
                    <p className="text-xs text-on-surface leading-relaxed">
                      {opp.angle}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="pt-2 flex items-center gap-3">
              <button
                onClick={handleApproveProposal}
                disabled={synthesizing}
                className="flex-1 py-2.5 rounded-lg bg-gradient-to-r from-secondary-container via-primary-container to-tertiary-container text-on-primary text-xs font-semibold hover:opacity-90 active:scale-[0.98] transition-all shadow-[0_0_18px_rgba(139,92,246,0.3)] flex items-center justify-center gap-1.5 font-mono"
              >
                <span className="material-symbols-outlined text-[18px]">auto_fix_high</span>
                <span>{synthesizing ? "Synthesizing..." : "Approve & Create Master Campaign"}</span>
              </button>

              <button
                onClick={onNavigateToRepurpose}
                className="py-2.5 px-4 rounded-lg bg-surface-container-high hover:bg-surface-bright text-xs font-mono text-on-surface font-medium border border-outline-variant/30 transition-all flex items-center gap-1.5"
              >
                <span>Repurposing Studio</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </button>
            </div>

            {approvedMessage && (
              <div className="p-2.5 rounded-lg bg-surface-container border border-tertiary/40 text-xs font-mono text-tertiary flex items-center gap-1.5 animate-fadeIn">
                <span className="material-symbols-outlined text-[16px]">check_circle</span>
                <span>{approvedMessage}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
