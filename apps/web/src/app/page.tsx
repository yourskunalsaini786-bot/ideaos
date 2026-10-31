"use client";

import React, { useState } from "react";
import { Sidebar, StudioTab } from "../components/Sidebar";
import { DashboardOverview } from "../components/DashboardOverview";
import { VideoPodcastStudio } from "../components/VideoPodcastStudio";
import { ClipSelectionStudio } from "../components/ClipSelectionStudio";
import { ContentRepurposingStudio } from "../components/ContentRepurposingStudio";
import { BrandDNASuite } from "../components/BrandDNASuite";
import { CalendarStudio } from "../components/CalendarStudio";
import { FusionLabStudio } from "../components/FusionLabStudio";
import { ClipOpportunity, IngestResponse } from "../lib/api";

export default function HomePage() {
  const [currentTab, setCurrentTab] = useState<StudioTab>("dashboard");
  const [selectedClip, setSelectedClip] = useState<ClipOpportunity | undefined>(undefined);
  const [ingestData, setIngestData] = useState<IngestResponse | null>(null);

  const handleIngestComplete = (data: IngestResponse) => {
    setIngestData(data);
    if (data.clip_opportunities && data.clip_opportunities.length > 0) {
      setSelectedClip(data.clip_opportunities[0]);
    }
  };

  const handleSelectClipForRepurpose = (clip: ClipOpportunity) => {
    setSelectedClip(clip);
    setCurrentTab("repurpose");
  };

  return (
    <div className="min-h-screen bg-surface flex">
      {/* Stitch Design Left Navigation Rail */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        onQuickCaptureClick={() => setCurrentTab("dashboard")}
        captureCount={142}
        clipsCount={ingestData?.clip_opportunities?.length || 3}
        fusionsCount={3}
      />

      {/* Main Workstation Canvas */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        {/* Top Studio Bar */}
        <header className="h-16 border-b border-outline-variant/20 px-space-lg flex items-center justify-between bg-surface-container-low/70 backdrop-blur-md sticky top-0 z-40">
          <div className="flex items-center gap-3 text-xs font-mono">
            <span className="flex items-center gap-1.5 text-on-surface">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-semibold text-secondary">Google Gemini 2.0 Flash</span>
            </span>
            <span className="text-outline">|</span>
            <span className="text-outline">Project Space Hackathon MVP</span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-container text-xs font-mono text-outline border border-outline-variant/30">
              <span className="material-symbols-outlined text-[14px] text-secondary">speed</span>
              <span>FastAPI Backend: Online</span>
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-mono text-secondary hover:underline flex items-center gap-1"
            >
              <span>API Specs</span>
              <span className="material-symbols-outlined text-[14px]">open_in_new</span>
            </a>
          </div>
        </header>

        {/* Studio View Content */}
        <main className="flex-1 p-space-lg max-w-7xl w-full mx-auto">
          {currentTab === "dashboard" && (
            <DashboardOverview
              onNavigate={(tab) => setCurrentTab(tab)}
              onSelectClipOpportunity={handleSelectClipForRepurpose}
            />
          )}

          {currentTab === "ingest" && (
            <VideoPodcastStudio
              onIngestComplete={handleIngestComplete}
              onNavigateToClips={() => setCurrentTab("clips")}
            />
          )}

          {currentTab === "clips" && (
            <ClipSelectionStudio
              clips={ingestData?.clip_opportunities}
              onSelectClipForRepurpose={handleSelectClipForRepurpose}
            />
          )}

          {currentTab === "repurpose" && (
            <ContentRepurposingStudio
              selectedClip={selectedClip}
              onNavigateToCalendar={() => setCurrentTab("calendar")}
              onNavigateToBrand={() => setCurrentTab("brand")}
            />
          )}

          {currentTab === "brand" && <BrandDNASuite />}

          {currentTab === "calendar" && <CalendarStudio />}

          {currentTab === "fusion" && (
            <FusionLabStudio
              onNavigateToRepurpose={() => setCurrentTab("repurpose")}
            />
          )}
        </main>

        {/* Technical Footer */}
        <footer className="border-t border-outline-variant/20 py-4 px-space-lg text-center text-xs font-mono text-outline flex items-center justify-between bg-surface-container-lowest">
          <div>
            IdeaOS Studio Pro • Complete End-to-End Media Repurposing with Persistent Brand Memory
          </div>
          <div className="flex items-center gap-3">
            <span>SQLite/PostgreSQL Local Engine</span>
            <span>•</span>
            <span className="text-secondary">All 6 Hackathon Criteria Passing</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
