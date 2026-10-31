import React, { useState } from "react";
import { Film, Play, Sparkles, CheckCircle2, ArrowRight, Clock, Flame, Info } from "lucide-react";
import { api, IngestResponse, ClipOpportunity } from "../lib/api";

interface ClipStudioProps {
  onSelectClipForRepurposing: (clip: ClipOpportunity, ingestData: IngestResponse) => void;
}

export const ClipStudio: React.FC<ClipStudioProps> = ({ onSelectClipForRepurposing }) => {
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("IdeaOS Founder Podcast #12");
  const [loading, setLoading] = useState(false);
  const [ingestData, setIngestData] = useState<IngestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadSample = () => {
    setTitle("Building the Autonomous Content Studio");
    setContent(
      "Welcome to episode 12 of IdeaOS Deep Dives. Today we break down how creators waste 80% of their creative output.\n" +
      "The fundamental mistake is treating repurposing as mechanical clipping rather than brand synthesis. " +
      "If you hand off a 60-minute interview to an agency, they slice random 30-second soundbites without standalone context. " +
      "The result? Viewers swipe away within 3 seconds because the clip lacked an immediate hook.\n" +
      "The breakthrough happens when you extract clips based on explicit reasoning: strong contrarian thesis at 0:15, " +
      "actionable resolution by 0:50, and zero unnecessary backstory. " +
      "When your AI studio preserves brand memory, every edit you make trains future generations so your tone never drifts."
    );
  };

  const handleIngest = async () => {
    if (!content.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.ingestMedia(content, title);
      setIngestData(data);
    } catch (err: any) {
      setError(err.message || "Failed to ingest media");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero / Input Section */}
      <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center space-x-2">
              <Film className="w-5 h-5 text-brandPrimary" />
              <span>Long-Form Media Ingestion</span>
            </h2>
            <p className="text-sm text-gray-400">
              Upload long video transcripts, podcast audio, or interviews for AI segmenting & explainable clip selection.
            </p>
          </div>
          <button
            onClick={loadSample}
            type="button"
            className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-surfaceBorder text-gray-300 hover:text-white transition flex items-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-brandAccent" />
            <span>Load Demo Recording</span>
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Recording Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-background border border-surfaceBorder rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brandPrimary transition"
              placeholder="e.g. Founder Interview Ep 42"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">
              Full Transcript or Video Notes
            </label>
            <textarea
              rows={5}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full bg-background border border-surfaceBorder rounded-xl p-4 text-sm text-white focus:outline-none focus:border-brandPrimary transition leading-relaxed"
              placeholder="Paste podcast transcript, interview transcription, or speech..."
            />
          </div>

          {error && (
            <div className="p-3 bg-red-900/30 border border-red-800 rounded-xl text-red-300 text-xs">
              {error}
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={handleIngest}
              disabled={loading || !content.trim()}
              className="px-6 py-2.5 bg-gradient-to-r from-brandPrimary to-brandAccent rounded-xl text-sm font-semibold text-white shadow-lg shadow-brandPrimary/25 hover:opacity-95 transition disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Extracting Intelligence...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Analyze & Extract Clips</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Ingested Results */}
      {ingestData && (
        <div className="space-y-6">
          {/* Timeline Overview */}
          <div className="bg-surface rounded-2xl border border-surfaceBorder p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Ingestion Complete
                </span>
                <h3 className="text-lg font-bold text-white mt-2">{ingestData.title}</h3>
                <p className="text-sm text-gray-400 mt-1 max-w-3xl">{ingestData.summary}</p>
              </div>
              <div className="text-right">
                <span className="text-xs text-gray-400">Total Duration</span>
                <p className="text-lg font-bold text-white flex items-center justify-end space-x-1">
                  <Clock className="w-4 h-4 text-brandPrimary" />
                  <span>{Math.round(ingestData.duration_seconds)}s</span>
                </p>
              </div>
            </div>

            {/* Segments Scrubbing Timeline */}
            <div className="mt-6">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
                Timestamped Content Segments ({ingestData.segments.length})
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {ingestData.segments.map((seg, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 bg-background rounded-xl border border-surfaceBorder text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-gray-400">
                      <span className="font-semibold text-brandPrimary">
                        {seg.start_time}s - {seg.end_time}s
                      </span>
                      <span className="px-2 py-0.5 rounded bg-surface text-gray-300">
                        {seg.speaker}
                      </span>
                    </div>
                    <p className="font-medium text-white truncate">{seg.topic}</p>
                    <p className="text-gray-400 line-clamp-2 leading-relaxed">{seg.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Explainable Clip Opportunities */}
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <Flame className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-bold text-white">
                Intelligent Clip Selection with Selection Reasons
              </h3>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {ingestData.clip_opportunities.map((clip, idx) => (
                <div
                  key={idx}
                  className="bg-surface rounded-2xl border border-surfaceBorder p-5 flex flex-col justify-between hover:border-brandPrimary/50 transition shadow-lg group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-brandPrimary/10 text-brandPrimary border border-brandPrimary/20">
                        {clip.start_time}s - {clip.end_time}s ({clip.duration_seconds}s)
                      </span>
                      <div className="flex items-center space-x-1 text-xs text-amber-400 font-semibold">
                        <Flame className="w-3.5 h-3.5" />
                        <span>{Math.round(clip.viral_potential * 100)}% Viral Score</span>
                      </div>
                    </div>

                    <h4 className="font-bold text-white text-base leading-snug group-hover:text-brandPrimary transition">
                      {clip.title}
                    </h4>

                    {/* Key Quote */}
                    <div className="p-3 bg-background rounded-xl border border-surfaceBorder/80">
                      <span className="text-[10px] font-semibold uppercase text-gray-500 block mb-1">
                        Memorable Hook
                      </span>
                      <p className="text-xs italic text-gray-200 leading-relaxed">
                        "{clip.key_quote}"
                      </p>
                    </div>

                    {/* MANDATORY HACKATHON REQUIREMENT: Selection Rationale */}
                    <div className="p-3 bg-brandPrimary/5 border border-brandPrimary/20 rounded-xl space-y-1">
                      <div className="flex items-center space-x-1.5 text-brandPrimary text-xs font-semibold">
                        <Info className="w-3.5 h-3.5 flex-shrink-0" />
                        <span>Why this clip was selected</span>
                      </div>
                      <p className="text-xs text-gray-300 leading-relaxed">
                        {clip.selection_reason}
                      </p>
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-surfaceBorder flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      {clip.suggested_platforms.map((p, i) => (
                        <span
                          key={i}
                          className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-surfaceBorder text-gray-300"
                        >
                          {p.split("_")[0]}
                        </span>
                      ))}
                    </div>

                    <button
                      onClick={() => onSelectClipForRepurposing(clip, ingestData)}
                      className="px-3.5 py-1.5 bg-brandPrimary hover:bg-brandPrimary/90 rounded-lg text-xs font-semibold text-white flex items-center space-x-1.5 shadow transition"
                    >
                      <span>Repurpose</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
