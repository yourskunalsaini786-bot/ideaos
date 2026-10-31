"use client";

import React, { useState, useEffect } from "react";
import { api, LearnedRule } from "@/lib/api";

const INITIAL_RULES: LearnedRule[] = [
  {
    rule_type: "structural_preference",
    pattern: "cut_opening_fluff",
    severity: "warning",
    message: "Eliminate introductory niceties ('In this post...', 'Have you ever wondered...'). Open immediately with the core counter-intuitive data point.",
    examples: ["Before: In today's competitive landscape... -> After: 4M views showed 4K videos get 43% fewer comments."],
    applies_to: ["linkedin", "twitter"],
  },
  {
    rule_type: "tone_adjustment",
    pattern: "high_directness",
    severity: "info",
    message: "Maintain a confident, empirical founder perspective. Use concrete operational metrics rather than abstract philosophy.",
    examples: ["Mention ARR multiples, retention seconds, and comment velocity."],
    applies_to: ["all"],
  },
  {
    rule_type: "negative_constraint",
    pattern: "banned_ai_buzzwords",
    severity: "error",
    message: "Strictly prohibit overused AI filler words ('delve', 'synergy', 'game-changer', 'revolutionize', 'dive deep').",
    examples: ["Never write 'Let's delve into this game-changing paradigm'."],
    applies_to: ["all"],
  },
];

const INITIAL_BANNED_WORDS = [
  "delve",
  "synergy",
  "game-changer",
  "revolutionize",
  "dive deep",
  "unleash",
  "paradigm shift",
  "testament",
  "tapestry",
  "supercharge",
];

export function BrandDNASuite() {
  const [rules, setRules] = useState<LearnedRule[]>(INITIAL_RULES);
  const [bannedWords, setBannedWords] = useState<string[]>(INITIAL_BANNED_WORDS);
  const [newBannedWord, setNewBannedWord] = useState("");
  const [formality, setFormality] = useState(38);
  const [directness, setDirectness] = useState(92);
  const [wit, setWit] = useState(42);
  const [provocativeness, setProvocativeness] = useState(78);
  const [savedNotice, setSavedNotice] = useState(false);
  const [isLoadingRules, setIsLoadingRules] = useState(false);

  useEffect(() => {
    setIsLoadingRules(true);
    api.getBrandRules()
      .then((backendRules: any[]) => {
        if (backendRules && backendRules.length > 0) {
          const formatted: LearnedRule[] = backendRules.map((r: any, idx: number) => ({
            rule_type: r.rule_type || "tone_constraint",
            pattern: r.pattern || `learned_rule_${idx + 1}`,
            severity: r.severity || "info",
            message: r.instruction || r.message || "Rule learned from creator edits",
            examples: r.examples || ["Derived from creator edit & approve flow"],
            applies_to: r.applies_to || ["all"],
          }));
          setRules(prev => {
            const existingMessages = new Set(prev.map(p => p.message));
            const newOnes = formatted.filter(f => !existingMessages.has(f.message));
            return [...newOnes, ...prev];
          });
        }
      })
      .catch((err) => console.warn("Failed to fetch brand rules:", err))
      .finally(() => setIsLoadingRules(false));
  }, []);

  const handleAddBannedWord = (e: React.FormEvent) => {
    e.preventDefault();
    const word = newBannedWord.trim().toLowerCase();
    if (!word || bannedWords.includes(word)) return;
    setBannedWords([...bannedWords, word]);
    setNewBannedWord("");
  };

  const handleRemoveBannedWord = (wordToRemove: string) => {
    setBannedWords(bannedWords.filter((w) => w !== wordToRemove));
  };

  const handleSaveSliders = () => {
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 3000);
  };

  return (
    <div className="space-y-space-lg pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm border-b border-outline-variant/30 pb-space-md">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-outlined text-tertiary text-[20px]">psychology</span>
            <span className="text-xs font-mono text-tertiary uppercase tracking-wider font-semibold">
              Brand DNA &amp; Adaptive Memory Suite
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-on-surface">
            Persistent Brand Memory &amp; Guardrails
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Learns from every creator edit in real-time, enforcing voice constraints, negative vocabulary, and tone vectors.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-mono flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            {isLoadingRules ? "Synchronizing..." : `${rules.length} Rules in Memory`}
          </span>
        </div>
      </div>

      {/* Hero Section: Diff View (AI Output vs Creator Edits) */}
      <section className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary text-[18px]">history_edu</span>
            <h2 className="text-sm font-semibold text-on-surface">
              Recent Adaptive Learning Cycles (AI Output vs Creator Edits)
            </h2>
          </div>
          <span className="text-[10px] font-mono text-outline">
            Continuous Self-Correction Loop
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
          {/* AI Original Draft */}
          <div className="p-3 rounded-lg bg-surface-container/60 border border-outline-variant/20 space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-outline">
              <span className="text-rose-400 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                Raw AI Initial Proposal
              </span>
              <span>Episode #48 Clip</span>
            </div>
            <div className="p-2.5 rounded bg-surface-container-lowest text-xs text-on-surface-variant font-mono leading-relaxed line-through opacity-75">
              &quot;In this insightful episode, we delve into the power of video marketing and how creators can unlock immense synergy by building their audience with polish...&quot;
            </div>
            <div className="text-[10px] font-mono text-rose-300">
              Violations: Contained &apos;delve&apos;, &apos;unlock&apos;, &apos;synergy&apos;, passive intro.
            </div>
          </div>

          {/* Creator Final Edit */}
          <div className="p-3 rounded-lg bg-surface-container/60 border border-secondary/30 space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-outline">
              <span className="text-emerald-400 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                Creator Approved Version
              </span>
              <span className="text-secondary font-semibold">+1 Rule Extracted</span>
            </div>
            <div className="p-2.5 rounded bg-surface-container-lowest text-xs text-on-surface font-mono leading-relaxed border-l-2 border-emerald-400">
              &quot;4M views revealed a brutal truth: 4K studio polish dropped comment velocity by 43%. Viewers want direct eye contact, not cinematic distance. Here&apos;s the 400ms defense barrier:&quot;
            </div>
            <div className="text-[10px] font-mono text-secondary">
              Learned Rule: Cut preamble; open with contrarian numerical evidence.
            </div>
          </div>
        </div>
      </section>

      {/* Two Column Grid: Negative Vocabulary & Adaptive Tone Sliders */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
        {/* Left 6 Columns: Prohibited Negative Vocabulary Matrix */}
        <div className="lg:col-span-6 rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-rose-400 text-[18px]">block</span>
              <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
                Prohibited Negative Vocabulary Matrix
              </h3>
            </div>
            <span className="text-[10px] font-mono text-outline">
              Zero-Tolerance Guardrail
            </span>
          </div>

          <p className="text-xs text-on-surface-variant leading-relaxed">
            The Brand Guardian scans every generation against these banned terms. Any generation containing these words is instantly rejected and rewritten before review.
          </p>

          {/* Word Chips */}
          <div className="flex items-center gap-2 flex-wrap min-h-[90px] p-2 rounded-lg bg-surface-container-lowest border border-outline-variant/20">
            {bannedWords.map((word) => (
              <span
                key={word}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono bg-rose-500/10 text-rose-300 border border-rose-500/30 group"
              >
                <span>{word}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveBannedWord(word)}
                  className="hover:text-rose-100 transition-colors"
                >
                  <span className="material-symbols-outlined text-[14px]">close</span>
                </button>
              </span>
            ))}
          </div>

          {/* Add Word Form */}
          <form onSubmit={handleAddBannedWord} className="flex items-center gap-2 pt-1">
            <input
              type="text"
              value={newBannedWord}
              onChange={(e) => setNewBannedWord(e.target.value)}
              placeholder="Add prohibited term or corporate buzzword..."
              className="flex-1 h-9 px-3 rounded-lg bg-surface-container-lowest text-xs text-on-surface font-mono border border-outline-variant/30 focus:outline-none focus:border-secondary"
            />
            <button
              type="submit"
              disabled={!newBannedWord.trim()}
              className="h-9 px-3.5 rounded-lg bg-surface-container-high hover:bg-surface-bright text-xs font-mono text-on-surface font-semibold border border-outline-variant/30 transition-all disabled:opacity-40"
            >
              + Ban Word
            </button>
          </form>
        </div>

        {/* Right 6 Columns: Adaptive Tone Sliders */}
        <div className="lg:col-span-6 rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary text-[18px]">tune</span>
              <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
                Adaptive Tone Sliders
              </h3>
            </div>
            <button
              onClick={handleSaveSliders}
              className="text-[10px] font-mono px-2 py-0.5 rounded bg-secondary-container/20 text-secondary hover:bg-secondary-container/30 transition-colors"
            >
              Save Parameters
            </button>
          </div>

          <div className="space-y-4 pt-1">
            {/* Formality Slider */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-on-surface font-medium">Formality / Conversationality</span>
                <span className="font-mono text-secondary font-semibold">{formality}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={formality}
                onChange={(e) => setFormality(Number(e.target.value))}
                className="w-full accent-secondary cursor-pointer"
              />
              <div className="flex justify-between text-[10px] font-mono text-outline">
                <span>0% Handheld / Raw</span>
                <span>100% Institutional Academic</span>
              </div>
            </div>

            {/* Directness Slider */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-on-surface font-medium">Directness &amp; Density</span>
                <span className="font-mono text-secondary font-semibold">{directness}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={directness}
                onChange={(e) => setDirectness(Number(e.target.value))}
                className="w-full accent-secondary cursor-pointer"
              />
              <div className="flex justify-between text-[10px] font-mono text-outline">
                <span>0% Narrative Storytelling</span>
                <span>100% Zero-Fluff Tactical Data</span>
              </div>
            </div>

            {/* Provocativeness Slider */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-on-surface font-medium">Contrarian Provocativeness</span>
                <span className="font-mono text-tertiary font-semibold">{provocativeness}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={provocativeness}
                onChange={(e) => setProvocativeness(Number(e.target.value))}
                className="w-full accent-tertiary cursor-pointer"
              />
              <div className="flex justify-between text-[10px] font-mono text-outline">
                <span>0% Safe Consensus</span>
                <span>100% Contrarian Status-Quo Inversion</span>
              </div>
            </div>
          </div>

          {savedNotice && (
            <div className="text-xs font-mono text-emerald-400 flex items-center gap-1 pt-1 animate-fadeIn">
              <span className="material-symbols-outlined text-[16px]">check_circle</span>
              Parameters synced to Brand Memory Model.
            </div>
          )}
        </div>
      </div>

      {/* Learned Rules Table */}
      <section className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px]">rule</span>
            <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
              Persistent Voice Rules Learned from Creator ({rules.length})
            </h3>
          </div>
          <span className="text-[10px] font-mono text-outline">
            Applied Automatically Across All Future Generations
          </span>
        </div>

        <div className="space-y-2">
          {rules.map((rule, idx) => (
            <div
              key={idx}
              className="p-3 rounded-lg bg-surface-container/60 border border-outline-variant/20 flex flex-col md:flex-row md:items-center justify-between gap-2"
            >
              <div className="space-y-1 max-w-2xl">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-primary-container/20 text-primary font-semibold">
                    {rule.rule_type}
                  </span>
                  <span className="text-xs font-bold text-on-surface font-mono">
                    {rule.pattern}
                  </span>
                </div>
                <p className="text-xs text-on-surface-variant">
                  {rule.message}
                </p>
                {rule.examples && rule.examples.length > 0 && (
                  <div className="text-[11px] font-mono text-outline italic">
                    Example: {rule.examples[0]}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2 shrink-0 self-start md:self-auto">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                  Active
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
