import React, { useState } from "react";
import { Sparkles, ArrowRight, CheckCircle2, Lightbulb, Link2 } from "lucide-react";
import { api, FusionProposal } from "../lib/api";

interface FusionLabProps {
  currentIdeaId?: string;
}

export const FusionLab: React.FC<FusionLabProps> = ({ currentIdeaId }) => {
  const [proposals, setProposals] = useState<FusionProposal[]>([]);
  const [loading, setLoading] = useState(false);
  const [approvedMap, setApprovedMap] = useState<Record<string, boolean>>({});

  const handleDiscoverFusions = async () => {
    setLoading(true);
    try {
      // Use existing idea id or trigger sample fusion
      const ideaId = currentIdeaId || "4507d656-97fb-4bdf-9a58-1483a7c12f83";
      const data = await api.suggestFusions(ideaId);
      setProposals(data);
    } catch (err: any) {
      console.error("Fusion suggestion error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (proposal: FusionProposal) => {
    try {
      await api.approveFusion(proposal.id, proposal.fusion_concept.slice(0, 80));
      setApprovedMap({ ...approvedMap, [proposal.id]: true });
    } catch (err: any) {
      alert("Failed to approve fusion: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-brandAccent/10 text-brandAccent border border-brandAccent/20">
              Product Differentiator
            </span>
          </div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2 mt-1">
            <Sparkles className="w-5 h-5 text-brandAccent" />
            <span>Idea Fusion Lab</span>
          </h2>
          <p className="text-sm text-gray-400">
            Automatically discovers non-obvious thematic links between your captured ideas and synthesizes them into novel master content.
          </p>
        </div>

        <button
          onClick={handleDiscoverFusions}
          disabled={loading}
          className="px-5 py-2.5 bg-gradient-to-r from-brandAccent to-purple-600 hover:opacity-90 rounded-xl text-xs font-bold text-white shadow-lg shadow-brandAccent/25 transition flex items-center space-x-2"
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
          <span>Synthesize Cross-Idea Fusions</span>
        </button>
      </div>

      {proposals.length === 0 ? (
        <div className="bg-surface rounded-2xl border border-surfaceBorder p-12 text-center space-y-3">
          <Lightbulb className="w-10 h-10 text-gray-500 mx-auto" />
          <h4 className="font-bold text-white text-base">No Active Fusions Generated</h4>
          <p className="text-xs text-gray-400 max-w-md mx-auto">
            Click "Synthesize Cross-Idea Fusions" to scan your captured ideas library and discover unexpected conceptual connections.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {proposals.map((prop) => (
            <div
              key={prop.id}
              className="bg-surface rounded-2xl border border-surfaceBorder p-6 space-y-4 flex flex-col justify-between hover:border-brandAccent/40 transition shadow-lg"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-brandAccent/10 text-brandAccent border border-brandAccent/20 flex items-center space-x-1">
                    <Link2 className="w-3 h-3" />
                    <span>Thematic Synthesis</span>
                  </span>
                  <span className="text-xs text-emerald-400 font-bold">
                    {Math.round(prop.confidence * 100)}% Confidence
                  </span>
                </div>

                <h3 className="font-bold text-white text-base leading-snug">
                  {prop.fusion_concept}
                </h3>

                {prop.content_opportunities && prop.content_opportunities.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-surfaceBorder">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
                      Content Angles Unlocked:
                    </span>
                    <div className="space-y-1.5">
                      {prop.content_opportunities.map((opp, idx) => (
                        <div key={idx} className="p-2.5 bg-background rounded-lg text-xs space-y-0.5">
                          <div className="flex items-center justify-between font-semibold text-brandAccent uppercase text-[10px]">
                            <span>{opp.platform} {opp.format}</span>
                            <span className="text-gray-400">{opp.pillar}</span>
                          </div>
                          <p className="text-gray-200">{opp.angle}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-surfaceBorder flex items-center justify-between">
                <span className="text-[11px] text-gray-400">
                  Status: <span className="text-white capitalize">{approvedMap[prop.id] ? "Approved" : prop.status}</span>
                </span>

                <button
                  onClick={() => handleApprove(prop)}
                  disabled={approvedMap[prop.id] || prop.status === "approved"}
                  className="px-4 py-2 bg-brandAccent hover:bg-brandAccent/90 rounded-xl text-xs font-bold text-white disabled:opacity-40 transition flex items-center space-x-1.5"
                >
                  {approvedMap[prop.id] || prop.status === "approved" ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Approved into Master Idea</span>
                    </>
                  ) : (
                    <>
                      <span>Approve Synthesis</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
