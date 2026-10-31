"use client";

import React from "react";

export type StudioTab =
  | "dashboard"
  | "ingest"
  | "clips"
  | "repurpose"
  | "brand"
  | "calendar"
  | "fusion";

interface SidebarProps {
  currentTab: StudioTab;
  onSelectTab: (tab: StudioTab) => void;
  onQuickCaptureClick?: () => void;
  captureCount?: number;
  clipsCount?: number;
  fusionsCount?: number;
}

export function Sidebar({
  currentTab,
  onSelectTab,
  onQuickCaptureClick,
  captureCount = 142,
  clipsCount = 3,
  fusionsCount = 3,
}: SidebarProps) {
  const navSections = [
    {
      label: "WORKSPACE",
      items: [
        {
          id: "dashboard" as StudioTab,
          name: "Overview",
          icon: "dashboard",
          badge: null,
        },
      ],
    },
    {
      label: "CREATIVE INTELLIGENCE",
      items: [
        {
          id: "fusion" as StudioTab,
          name: "Idea Fusion Lab",
          icon: "hub",
          badge: `${fusionsCount} new`,
          badgeColor: "bg-tertiary-container/30 text-tertiary",
        },
      ],
    },
    {
      label: "MEDIA REPURPOSING",
      items: [
        {
          id: "ingest" as StudioTab,
          name: "Video & Podcast Ingest",
          icon: "mic",
          badge: "Live",
          badgeColor: "bg-secondary-container/20 text-secondary",
        },
        {
          id: "clips" as StudioTab,
          name: "Clip Selection Studio",
          icon: "movie_edit",
          badge: `${clipsCount}`,
          badgeColor: "bg-primary-container/20 text-primary",
        },
        {
          id: "repurpose" as StudioTab,
          name: "Multi-Platform Repurpose",
          icon: "transform",
          badge: "AI",
          badgeColor: "bg-secondary-container/20 text-secondary",
        },
      ],
    },
    {
      label: "PERSISTENT MEMORY",
      items: [
        {
          id: "brand" as StudioTab,
          name: "Brand DNA & Memory",
          icon: "psychology",
          badge: "Learning",
          badgeColor: "bg-tertiary-container/20 text-tertiary",
        },
        {
          id: "calendar" as StudioTab,
          name: "Content Calendar & Feedback",
          icon: "calendar_today",
          badge: null,
        },
      ],
    },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-surface-container-low z-50 flex flex-col border-r border-outline-variant/30 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-space-lg bg-surface-container-low shrink-0 border-b border-outline-variant/20">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-secondary-container via-primary-container to-tertiary-container flex items-center justify-center shadow-[0_0_12px_rgba(6,182,212,0.3)]">
            <span className="material-symbols-outlined text-surface font-bold text-[18px]">
              hub
            </span>
          </div>
          <div>
            <span className="font-semibold text-lg tracking-tight text-on-surface">
              IdeaOS
            </span>
            <span className="text-[10px] block font-mono text-secondary uppercase tracking-widest -mt-1 font-medium">
              Studio Pro
            </span>
          </div>
        </div>
        <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-surface-container-highest text-outline">
          v2.4
        </span>
      </div>

      {/* Quick Capture Button */}
      <div className="px-space-md py-space-sm shrink-0">
        <button
          onClick={onQuickCaptureClick}
          className="w-full flex items-center justify-between px-space-md py-2.5 rounded-lg bg-gradient-to-r from-secondary-container via-primary-container to-tertiary-container text-on-primary text-sm font-semibold hover:opacity-95 active:scale-[0.98] transition-all shadow-[0_0_20px_-4px_rgba(59,130,246,0.35)]"
          type="button"
        >
          <span className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">
              add_circle
            </span>
            <span>+ Quick Capture</span>
          </span>
          <kbd className="text-[10px] font-mono bg-surface-container-lowest/40 px-1.5 py-0.5 rounded text-on-primary">
            ⌘N
          </kbd>
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-space-md py-space-xs space-y-space-md">
        {navSections.map((section) => (
          <div key={section.label} className="space-y-1">
            <div className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-outline font-semibold">
              {section.label}
            </div>
            {section.items.map((item) => {
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? "bg-surface-container-high text-on-surface shadow-sm border border-outline-variant/40 text-primary font-semibold"
                      : "text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
                  }`}
                >
                  <span className="flex items-center gap-2.5">
                    <span
                      className={`material-symbols-outlined text-[18px] ${
                        isActive ? "text-primary" : "text-outline"
                      }`}
                    >
                      {item.icon}
                    </span>
                    <span>{item.name}</span>
                  </span>
                  {item.badge && (
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-medium ${
                        item.badgeColor || "bg-surface-container text-outline"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer Profile & Memory Status */}
      <div className="p-3 bg-surface-container-lowest/80 border-t border-outline-variant/20 shrink-0">
        <div className="flex items-center justify-between text-[11px] font-mono text-outline mb-1">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Brand Sync: 99.4%
          </span>
          <span className="text-secondary">Synced</span>
        </div>
        <div className="flex items-center gap-2 pt-1">
          <div className="w-7 h-7 rounded-full bg-surface-container-highest flex items-center justify-center font-bold text-xs text-primary">
            KS
          </div>
          <div className="truncate">
            <div className="text-xs font-medium text-on-surface truncate">
              Kunal Saini
            </div>
            <div className="text-[10px] font-mono text-outline truncate">
              creator@ideaos.studio
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
