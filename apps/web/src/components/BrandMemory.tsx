import React, { useState, useEffect } from "react";
import { Brain, ShieldCheck, AlertCircle, PlusCircle, CheckCircle2 } from "lucide-react";
import { api, LearnedRule } from "../lib/api";

export const BrandMemory: React.FC = () => {
  const [rules, setRules] = useState<LearnedRule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setLoading(true);
    try {
      const data = await api.getBrandRules();
      setRules(data);
    } catch (err) {
      console.error("Failed to load brand rules:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Brain className="w-5 h-5 text-brandPrimary" />
            <span>Persistent Brand Memory & DNA</span>
          </h2>
          <p className="text-sm text-gray-400">
            Rules, vocabulary constraints, and tone preferences automatically learned from your previous edits.
          </p>
        </div>
        <button
          onClick={loadRules}
          className="text-xs px-3 py-1.5 rounded-lg bg-surfaceBorder text-gray-300 hover:text-white transition"
        >
          Refresh Rules
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Brand Voice Core (1 Col) */}
        <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="font-bold text-white text-base">Creator Voice Profile</h3>
          </div>

          <div className="p-3.5 bg-background rounded-xl border border-surfaceBorder space-y-1.5 text-xs">
            <span className="font-semibold text-gray-400 uppercase tracking-wider block text-[10px]">
              Tone & Style
            </span>
            <p className="text-gray-200 leading-relaxed font-medium">
              Authoritative, concise, tactical. Prefers bullet points and direct takeaways over conversational filler.
            </p>
          </div>

          <div className="p-3.5 bg-background rounded-xl border border-surfaceBorder space-y-1.5 text-xs">
            <span className="font-semibold text-gray-400 uppercase tracking-wider block text-[10px]">
              Target Audience
            </span>
            <p className="text-gray-200 leading-relaxed font-medium">
              Founders, tech operators, solopreneurs, and high-velocity digital creators.
            </p>
          </div>

          <div className="p-3.5 bg-background rounded-xl border border-surfaceBorder space-y-1.5 text-xs">
            <span className="font-semibold text-gray-400 uppercase tracking-wider block text-[10px]">
              Universal Prohibited Buzzwords
            </span>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {["synergy", "paradigm shift", "circle back", "utilize"].map((w) => (
                <span
                  key={w}
                  className="px-2 py-0.5 rounded bg-red-950/40 border border-red-500/20 text-red-300 font-mono text-[11px]"
                >
                  {w}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Learned Rules List (2 Cols) */}
        <div className="lg:col-span-2 bg-surface rounded-2xl border border-surfaceBorder p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">
              Rules Extracted from Creator Edits ({rules.length})
            </h3>
            <span className="text-xs text-brandPrimary font-medium">
              Autonomously Updated on Every Approval
            </span>
          </div>

          {loading ? (
            <div className="py-12 text-center text-sm text-gray-400">Loading brand memory rules...</div>
          ) : rules.length === 0 ? (
            <div className="py-12 text-center text-sm text-gray-400 space-y-2">
              <p>No learned rules yet.</p>
              <p className="text-xs text-gray-500">
                Whenever you edit generated copy in the Platform Editor, IdeaOS compares the diff and automatically synthesizes rules to remember your preference.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {rules.map((rule, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-background rounded-xl border border-surfaceBorder space-y-2 hover:border-gray-700 transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                          rule.rule_type === "must_avoid"
                            ? "bg-red-500/10 text-red-400 border border-red-500/20"
                            : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        }`}
                      >
                        {rule.rule_type.replace("_", " ")}
                      </span>
                      {rule.pattern && (
                        <span className="text-xs font-mono px-2 py-0.5 rounded bg-surface border border-surfaceBorder text-gray-200">
                          {rule.pattern}
                        </span>
                      )}
                    </div>

                    <span className="text-[10px] text-gray-400 capitalize">
                      Applies to: {rule.applies_to ? rule.applies_to.join(", ") : "All platforms"}
                    </span>
                  </div>

                  <p className="text-xs text-gray-300 leading-relaxed font-medium">
                    {rule.message}
                  </p>

                  {rule.examples && rule.examples.length > 0 && (
                    <p className="text-[11px] text-gray-500 italic">
                      Triggered by edit: "{rule.examples[0]}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
