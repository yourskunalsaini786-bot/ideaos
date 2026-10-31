import React, { useState, useEffect } from "react";
import { Cpu, Sparkles, CheckCircle2, ShieldCheck, Calendar, ArrowRight, AlertTriangle, RefreshCw } from "lucide-react";
import { api, ClipOpportunity, IngestResponse, GeneratedContent, ApprovedContentResponse } from "../lib/api";

interface PlatformEditorProps {
  selectedClip: ClipOpportunity | null;
  ingestData: IngestResponse | null;
  onNavigateToCalendar: () => void;
}

export const PlatformEditor: React.FC<PlatformEditorProps> = ({
  selectedClip,
  ingestData,
  onNavigateToCalendar,
}) => {
  const [platform, setPlatform] = useState<"linkedin_post" | "instagram_reel" | "youtube_shorts" | "x_thread">("linkedin_post");
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState<GeneratedContent | null>(null);
  const [editedBody, setEditedBody] = useState("");
  const [approvalResult, setApprovalResult] = useState<ApprovedContentResponse | null>(null);
  const [scheduleDate, setScheduleDate] = useState<string>(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().slice(0, 16);
  });

  // Auto-generate content when a clip is selected or platform changes
  useEffect(() => {
    if (selectedClip && ingestData) {
      handleGenerate();
    }
  }, [selectedClip, platform]);

  const handleGenerate = async () => {
    if (!selectedClip || !ingestData) return;
    setLoading(true);
    setApprovalResult(null);
    try {
      const formatMap: Record<string, string> = {
        linkedin_post: "post",
        instagram_reel: "reel",
        youtube_shorts: "shorts",
        x_thread: "thread",
      };

      const result = await api.generateContent({
        idea_id: ingestData.idea_id,
        clip_title: selectedClip.title,
        key_quote: selectedClip.key_quote,
        selection_reason: selectedClip.selection_reason,
        start_time: selectedClip.start_time,
        end_time: selectedClip.end_time,
        platform,
        format: formatMap[platform] || "post",
      });
      setGenerated(result);
      setEditedBody(result.body);
    } catch (err: any) {
      console.error("Failed to generate content:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveAndLearn = async () => {
    if (!generated || !ingestData) return;
    try {
      const res = await api.approveAndLearn({
        idea_id: ingestData.idea_id,
        platform,
        format: generated.format,
        original_content: generated.body,
        edited_content: editedBody,
        title: generated.title,
        schedule_time: new Date(scheduleDate).toISOString(),
      });
      setApprovalResult(res);
    } catch (err: any) {
      alert("Approval error: " + err.message);
    }
  };

  if (!selectedClip || !ingestData) {
    return (
      <div className="bg-surface rounded-2xl border border-surfaceBorder p-12 text-center space-y-4">
        <Cpu className="w-12 h-12 text-gray-500 mx-auto" />
        <h3 className="text-lg font-bold text-white">No Clip Selected</h3>
        <p className="text-sm text-gray-400 max-w-md mx-auto">
          Please select a clip from the Clip Studio first to adapt and customize it for specific platforms with persistent brand voice.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Platform Switcher */}
      <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-brandPrimary/10 text-brandPrimary border border-brandPrimary/20">
            Repurposing Clip: {selectedClip.start_time}s - {selectedClip.end_time}s
          </span>
          <h2 className="text-lg font-bold text-white mt-1">{selectedClip.title}</h2>
        </div>

        {/* Platform tabs */}
        <div className="flex items-center space-x-1.5 bg-background p-1.5 rounded-xl border border-surfaceBorder">
          {[
            { id: "linkedin_post", label: "LinkedIn" },
            { id: "instagram_reel", label: "Instagram Reel" },
            { id: "youtube_shorts", label: "Shorts" },
            { id: "x_thread", label: "X Thread" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setPlatform(tab.id as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                platform === tab.id
                  ? "bg-brandPrimary text-white shadow"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="bg-surface rounded-2xl border border-surfaceBorder p-12 text-center space-y-3">
          <div className="w-8 h-8 border-2 border-brandPrimary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-gray-300 font-medium">
            Generating {platform.replace("_", " ")} copy with Brand Guardian check...
          </p>
        </div>
      ) : generated ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Copy Editor (2 Cols) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300">
                  Generated Copy (Editable)
                </h3>
                <button
                  onClick={handleGenerate}
                  className="text-xs text-gray-400 hover:text-white flex items-center space-x-1 transition"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Regenerate</span>
                </button>
              </div>

              {/* Hook Preview */}
              <div className="p-3 bg-background rounded-xl border border-surfaceBorder">
                <span className="text-[10px] font-semibold text-brandPrimary uppercase tracking-wider block mb-1">
                  Feed Hook / First Line
                </span>
                <p className="text-xs font-medium text-white">{generated.hook}</p>
              </div>

              {/* Editable Body */}
              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1">
                  Post Copy (Creator Edits train Brand Memory)
                </label>
                <textarea
                  rows={9}
                  value={editedBody}
                  onChange={(e) => setEditedBody(e.target.value)}
                  className="w-full bg-background border border-surfaceBorder rounded-xl p-4 text-sm text-white focus:outline-none focus:border-brandPrimary transition font-sans leading-relaxed"
                />
              </div>

              {/* Hashtags & CTA */}
              <div className="flex flex-wrap gap-1.5 pt-2">
                {generated.hashtags.map((tag, i) => (
                  <span
                    key={i}
                    className="text-xs px-2.5 py-1 rounded-lg bg-surfaceBorder text-gray-300"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Approval / Scheduling Action Bar */}
            <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center space-x-3">
                <Calendar className="w-5 h-5 text-brandPrimary" />
                <div>
                  <span className="text-xs text-gray-400 block">Schedule Slot</span>
                  <input
                    type="datetime-local"
                    value={scheduleDate}
                    onChange={(e) => setScheduleDate(e.target.value)}
                    className="bg-background border border-surfaceBorder text-xs text-white rounded-lg px-2.5 py-1.5 focus:outline-none"
                  />
                </div>
              </div>

              <button
                onClick={handleApproveAndLearn}
                className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 rounded-xl text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 transition flex items-center space-x-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Approve & Train Brand Memory</span>
              </button>
            </div>

            {/* Confirmation & Learned Rules Notification */}
            {approvalResult && (
              <div className="p-5 bg-emerald-950/40 border border-emerald-500/30 rounded-2xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-emerald-400 font-semibold text-sm">
                    <CheckCircle2 className="w-5 h-5" />
                    <span>Content Approved & Scheduled on Calendar!</span>
                  </div>
                  <button
                    onClick={onNavigateToCalendar}
                    className="text-xs font-semibold text-emerald-300 hover:underline flex items-center space-x-1"
                  >
                    <span>View on Calendar</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {approvalResult.learned_brand_rules.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-emerald-500/20 text-xs text-gray-200 space-y-1">
                    <span className="font-bold text-emerald-300">
                      🧠 Brand Memory Learned from Your Edits:
                    </span>
                    <ul className="list-disc list-inside space-y-0.5 text-gray-300">
                      {approvalResult.learned_brand_rules.map((rule, idx) => (
                        <li key={idx}>
                          <span className="font-semibold capitalize">{rule.rule_type.replace("_", " ")}:</span>{" "}
                          {rule.message}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Brand Guardian & On-Screen Visual Notes (1 Col) */}
          <div className="space-y-6">
            {/* Brand Guardian Score Card */}
            <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400" />
                  <h4 className="font-bold text-white text-sm">Brand Guardian Gate</h4>
                </div>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {generated.quality_score.toFixed(1)} / 10
                </span>
              </div>

              <div className="p-3 bg-background rounded-xl border border-surfaceBorder text-xs space-y-1">
                <p className="text-gray-300 font-medium">Brand Voice Compliance: High</p>
                <p className="text-gray-400">
                  Aligns with creator's direct, tactical tone. Checked against active vocabulary constraints.
                </p>
              </div>

              {generated.quality_warnings.length > 0 ? (
                <div className="p-3 bg-amber-950/40 border border-amber-500/30 rounded-xl space-y-1">
                  <span className="text-xs font-semibold text-amber-400 flex items-center space-x-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Quality Warnings</span>
                  </span>
                  <ul className="text-xs text-amber-200 list-disc list-inside">
                    {generated.quality_warnings.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div className="flex items-center space-x-1.5 text-xs text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>No prohibited words or tone drift detected</span>
                </div>
              )}
            </div>

            {/* Visual Direction Notes */}
            {generated.visual_notes.length > 0 && (
              <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 space-y-3">
                <h4 className="font-bold text-white text-sm">On-Screen Visual Directions</h4>
                <div className="space-y-2">
                  {generated.visual_notes.map((note, i) => (
                    <div key={i} className="p-2.5 bg-background rounded-lg text-xs space-y-0.5">
                      <span className="font-semibold text-brandPrimary">{note.timestamp}</span>
                      <p className="text-gray-300">{note.direction}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
