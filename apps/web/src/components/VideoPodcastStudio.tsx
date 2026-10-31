"use client";

import React, { useState } from "react";
import { api, IngestResponse } from "@/lib/api";

const DEMO_TRANSCRIPT = `Speaker A [00:00]: Welcome back to The Founder's Edge. Today we're deconstructing attention arbitrage and why modern brands must become media operations first.
Speaker B [01:15]: The biggest mistake founders make in 2026 is believing that high-polish video equals authority. In fact, our data across 4 million views showed that over-engineered 4K studio productions generated 43% lower comment velocity than raw handheld smartphone clips.
Speaker A [04:12]: Let's dig into that exact number. Why is raw footage outperforming expensive studio productions?
Speaker B [04:25]: It's what we call the 400ms Production Defense Barrier. When a viewer scrolls into a 60fps color-graded cinematic video, their brain instantly tags it as an advertisement and raises defensive shields. But when they see natural motion and direct eye contact, their mirror neurons engage within 200 milliseconds. Authenticity is no longer a soft value—it's an algorithmic distribution moat.
Speaker A [12:30]: This ties directly to micro-community compounding. A channel with 3,000 highly aligned operators generates 5x the ARR of a vanity channel with 100,000 passive subscribers.
Speaker B [13:10]: Exactly. Passive audiences click, but high-intent cohorts convert. When you repurpose your long-form core theses into platform-native atomic content, you're not just clipping—you're building an autonomous intellectual flywheel.`;

interface VideoPodcastStudioProps {
  onIngestComplete: (data: IngestResponse) => void;
  onNavigateToClips: () => void;
}

export function VideoPodcastStudio({
  onIngestComplete,
  onNavigateToClips,
}: VideoPodcastStudioProps) {
  const [inputText, setInputText] = useState("");
  const [mediaTitle, setMediaTitle] = useState("Episode #48: The Attention Arbitrage");
  const [mediaUrl, setMediaUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [ingestedData, setIngestedData] = useState<IngestResponse | null>(null);
  const [activeSegmentIndex, setActiveSegmentIndex] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleIngest = async (contentToIngest: string, titleToUse: string) => {
    setLoading(true);
    try {
      const data = await api.ingestMedia(contentToIngest, titleToUse, "podcast");
      setIngestedData(data);
      onIngestComplete(data);
    } catch (err: any) {
      alert("Ingestion error: " + (err.message || String(err)));
    } finally {
      setLoading(false);
    }
  };

  const loadDemo = () => {
    setInputText(DEMO_TRANSCRIPT);
    setMediaTitle("Episode #48: The Attention Arbitrage: Why Modern Brands Build Media Networks");
    handleIngest(DEMO_TRANSCRIPT, "Episode #48: The Attention Arbitrage: Why Modern Brands Build Media Networks");
  };

  return (
    <div className="space-y-space-lg pb-16">
      {/* Studio Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm border-b border-outline-variant/30 pb-space-md">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-outlined text-secondary text-[20px]">mic</span>
            <span className="text-xs font-mono text-secondary uppercase tracking-wider font-semibold">
              Media Ingestion &amp; Semantic Deconstruction
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-on-surface">
            Video &amp; Podcast Ingestion Studio
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Extract timestamped topics, speaker diarization, and viral cognitive seeds from multi-hour media.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadDemo}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-secondary-container/20 hover:bg-secondary-container/30 text-secondary text-xs font-mono font-medium border border-secondary/30 transition-all"
          >
            <span className="material-symbols-outlined text-[16px]">play_circle</span>
            <span>Load Demo Episode #48</span>
          </button>
        </div>
      </div>

      {/* Ingestion Dropzone & URL Input */}
      {!ingestedData && (
        <div className="rounded-xl bg-surface-container-low p-space-lg border border-outline-variant/30 shadow-lg space-y-space-md">
          <div className="border-2 border-dashed border-outline-variant/50 hover:border-secondary/50 rounded-xl p-8 text-center transition-all bg-surface-container/30">
            <div className="w-12 h-12 mx-auto rounded-full bg-secondary-container/15 flex items-center justify-center text-secondary mb-3 shadow-[0_0_16px_rgba(6,182,212,0.2)]">
              <span className="material-symbols-outlined text-[24px]">cloud_upload</span>
            </div>
            <h3 className="text-sm font-semibold text-on-surface">
              Drop long-form podcast (MP3, WAV) or video (MP4, MOV)
            </h3>
            <p className="text-xs text-outline mt-1 mb-4">
              AI speech model will deconstruct audio waveforms, detect speakers, and generate timestamped segments.
            </p>

            <div className="flex items-center justify-center gap-2 max-w-md mx-auto">
              <input
                type="text"
                value={mediaUrl}
                onChange={(e) => setMediaUrl(e.target.value)}
                placeholder="Or paste YouTube / Spotify episode link..."
                className="flex-1 h-9 px-3 rounded-lg bg-surface-container-lowest text-xs text-on-surface border border-outline-variant/40 focus:outline-none focus:border-secondary font-mono"
              />
              <button
                type="button"
                onClick={() => handleIngest(DEMO_TRANSCRIPT, mediaUrl || mediaTitle)}
                disabled={loading}
                className="h-9 px-4 rounded-lg bg-primary-container text-on-primary text-xs font-semibold hover:opacity-90 transition-all font-mono"
              >
                Ingest URL
              </button>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-on-surface-variant">
              <span className="font-medium">Direct Transcript / Notes Ingestion</span>
              <span className="font-mono text-outline">Markdown or raw speech text</span>
            </div>
            <textarea
              rows={4}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste raw transcript with speaker cues or episode dialogue..."
              className="w-full p-3 rounded-lg bg-surface-container-lowest text-xs text-on-surface border border-outline-variant/30 font-mono focus:outline-none focus:border-secondary"
            />
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => handleIngest(inputText || DEMO_TRANSCRIPT, mediaTitle)}
                disabled={loading}
                className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-secondary-container via-primary-container to-tertiary-container text-on-primary text-xs font-semibold hover:opacity-90 shadow-md transition-all"
              >
                <span className="material-symbols-outlined text-[16px]">psychology</span>
                <span>{loading ? "Deconstructing Media & Extracting Clips..." : "Process Audio & Extract Hooks"}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* When Ingested: Rich Workstation View */}
      {ingestedData && (
        <div className="space-y-space-md animate-fadeIn">
          {/* Active Episode Header & Player Controls */}
          <div className="rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 shadow-md">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 mb-3">
              <div>
                <div className="flex items-center gap-2 text-xs font-mono text-outline mb-1">
                  <span className="px-1.5 py-0.5 rounded bg-surface-container-highest text-secondary font-semibold">
                    PODCAST AUDIO
                  </span>
                  <span>48m 20s Duration</span>
                  <span>•</span>
                  <span>44.1 kHz 2-Channel</span>
                  <span>•</span>
                  <span className="text-emerald-400">Diarization Complete</span>
                </div>
                <h2 className="text-lg font-bold text-on-surface">
                  {ingestedData.title || mediaTitle}
                </h2>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container-high hover:bg-surface-bright text-xs text-on-surface font-mono font-medium border border-outline-variant/30 transition-all"
                >
                  <span className="material-symbols-outlined text-[16px] text-secondary">
                    {isPlaying ? "pause" : "play_arrow"}
                  </span>
                  <span>{isPlaying ? "Pause Waveform" : "Preview Audio"}</span>
                </button>

                <button
                  onClick={onNavigateToClips}
                  className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-gradient-to-r from-secondary-container via-primary-container to-tertiary-container text-on-primary text-xs font-semibold shadow-[0_0_16px_rgba(59,130,246,0.25)] hover:opacity-90 transition-all font-mono"
                >
                  <span>Review {ingestedData.clip_opportunities.length} Selected Clips</span>
                  <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                </button>
              </div>
            </div>

            {/* Audio Waveform Visualization */}
            <div className="p-3 rounded-lg bg-surface-container-lowest border border-outline-variant/20 space-y-2">
              <div className="flex items-center justify-between text-[11px] font-mono text-outline">
                <span className="text-secondary font-medium">04:25 / 48:20 (Scrubbing Clip #1)</span>
                <span className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-secondary" />
                    Speaker A: Alex (Host)
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-tertiary" />
                    Speaker B: Dr. Mercer (Guest)
                  </span>
                </span>
              </div>

              {/* Fake visual waveform bars */}
              <div className="h-10 flex items-end gap-1 px-1 py-1 bg-surface-container rounded cursor-pointer overflow-hidden">
                {[
                  30, 45, 60, 25, 40, 80, 95, 70, 50, 40, 65, 85, 100, 90, 75, 60, 45, 30, 70, 85, 90,
                  60, 40, 55, 75, 90, 85, 65, 40, 50, 70, 90, 95, 80, 60, 50, 40, 75, 90, 85, 60, 45,
                  35, 65, 80, 90, 70, 55, 40, 50, 65, 80, 75, 60, 40, 30, 50, 70, 85, 90, 65, 45, 30,
                  55, 75, 90, 80, 60, 45, 35, 60, 80, 90, 70, 55, 40, 50, 65, 80, 75, 60, 40, 30,
                ].map((val, idx) => {
                  const isHighlighted = idx >= 15 && idx <= 35;
                  return (
                    <div
                      key={idx}
                      className={`flex-1 rounded-sm transition-all ${
                        isHighlighted
                          ? "bg-secondary hover:bg-secondary-fixed shadow-[0_0_8px_rgba(6,182,212,0.4)]"
                          : "bg-surface-container-highest hover:bg-outline"
                      }`}
                      style={{ height: `${val}%` }}
                    />
                  );
                })}
              </div>
            </div>
          </div>

          {/* Two-Column Grid: Live Transcript & Extracted Cognitive Seeds */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
            {/* Left 7 Cols: Transcript Scrubber */}
            <div className="lg:col-span-7 rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-[18px]">subtitles</span>
                  <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
                    Diarized Transcript Segments ({ingestedData.segments.length})
                  </h3>
                </div>
                <span className="text-[10px] font-mono text-outline">Auto-sync with audio track</span>
              </div>

              <div className="space-y-2 max-h-[460px] overflow-y-auto pr-1">
                {ingestedData.segments.map((seg, idx) => {
                  const isSelected = activeSegmentIndex === idx;
                  const isSpeakerA = seg.speaker.includes("A") || seg.speaker.includes("Host");
                  return (
                    <div
                      key={idx}
                      onClick={() => setActiveSegmentIndex(idx)}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        isSelected
                          ? "bg-surface-container border-secondary/50 shadow-sm"
                          : "bg-surface-container/40 hover:bg-surface-container/70 border-outline-variant/20"
                      }`}
                    >
                      <div className="flex items-center justify-between text-[11px] font-mono mb-1.5">
                        <span
                          className={`font-semibold flex items-center gap-1.5 ${
                            isSpeakerA ? "text-secondary" : "text-tertiary"
                          }`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${isSpeakerA ? "bg-secondary" : "bg-tertiary"}`} />
                          {seg.speaker}
                        </span>
                        <span className="text-outline">
                          {Math.floor(seg.start_time / 60)}:{(seg.start_time % 60).toString().padStart(2, "0")} - {Math.floor(seg.end_time / 60)}:{(seg.end_time % 60).toString().padStart(2, "0")}
                        </span>
                      </div>
                      <p className="text-xs text-on-surface leading-relaxed">
                        {seg.text}
                      </p>
                      {seg.topic && (
                        <div className="mt-2 flex items-center gap-1.5">
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-surface-container-highest text-outline">
                            Topic: {seg.topic}
                          </span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right 5 Cols: Extracted Cognitive Seeds */}
            <div className="lg:col-span-5 rounded-xl bg-surface-container-low p-space-md border border-outline-variant/30 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-tertiary text-[18px]">lightbulb</span>
                  <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-on-surface">
                    Extracted Cognitive Seeds
                  </h3>
                </div>
                <span className="text-[10px] font-mono text-tertiary">3 Viral Moments</span>
              </div>

              <div className="space-y-3">
                {ingestedData.clip_opportunities.map((clip, idx) => (
                  <div
                    key={clip.clip_id || idx}
                    className="p-3 rounded-lg bg-surface-container/60 hover:bg-surface-container border border-outline-variant/20 space-y-2 transition-all"
                  >
                    <div className="flex items-center justify-between text-[11px] font-mono">
                      <span className="px-1.5 py-0.5 rounded bg-primary-container/20 text-primary font-semibold">
                        Viral Score: {Math.round(clip.viral_potential)}%
                      </span>
                      <span className="text-outline">
                        {Math.floor(clip.start_time / 60)}:{(clip.start_time % 60).toString().padStart(2, "0")} ({clip.duration_seconds}s)
                      </span>
                    </div>

                    <h4 className="text-xs font-semibold text-on-surface">
                      {clip.title}
                    </h4>

                    <p className="text-[11px] text-on-surface-variant italic border-l-2 border-secondary/40 pl-2">
                      &quot;{clip.key_quote}&quot;
                    </p>

                    <div className="text-[10px] font-mono text-outline">
                      <span className="text-secondary font-medium">Why AI picked it:</span> {clip.selection_reason}
                    </div>

                    <button
                      onClick={onNavigateToClips}
                      className="w-full mt-1 py-1.5 rounded bg-surface-container-highest hover:bg-surface-bright text-[11px] font-mono text-on-surface font-medium flex items-center justify-center gap-1 transition-all"
                    >
                      <span>Inspect in Clip Studio</span>
                      <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
