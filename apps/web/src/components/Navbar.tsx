import React from "react";
import { Sparkles, Calendar, Brain, Cpu, Film } from "lucide-react";

interface NavbarProps {
  activeTab: "studio" | "editor" | "calendar" | "brand" | "fusion";
  setActiveTab: (tab: "studio" | "editor" | "calendar" | "brand" | "fusion") => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="border-b border-surfaceBorder bg-surface/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brandPrimary to-brandAccent flex items-center justify-center shadow-lg shadow-brandPrimary/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">IdeaOS</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-brandPrimary/10 text-brandPrimary border border-brandPrimary/20 font-medium">
                Studio 2.0
              </span>
            </div>
            <p className="text-xs text-gray-400">Content Intelligence & Persistent Brand Memory</p>
          </div>
        </div>

        <nav className="flex items-center space-x-1 bg-background/60 p-1 rounded-xl border border-surfaceBorder">
          <button
            onClick={() => setActiveTab("studio")}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition ${
              activeTab === "studio"
                ? "bg-brandPrimary text-white shadow-sm"
                : "text-gray-400 hover:text-white hover:bg-surface"
            }`}
          >
            <Film className="w-4 h-4" />
            <span>Clip Studio</span>
          </button>

          <button
            onClick={() => setActiveTab("editor")}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition ${
              activeTab === "editor"
                ? "bg-brandPrimary text-white shadow-sm"
                : "text-gray-400 hover:text-white hover:bg-surface"
            }`}
          >
            <Cpu className="w-4 h-4" />
            <span>Platform Editor</span>
          </button>

          <button
            onClick={() => setActiveTab("calendar")}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition ${
              activeTab === "calendar"
                ? "bg-brandPrimary text-white shadow-sm"
                : "text-gray-400 hover:text-white hover:bg-surface"
            }`}
          >
            <Calendar className="w-4 h-4" />
            <span>Calendar</span>
          </button>

          <button
            onClick={() => setActiveTab("brand")}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition ${
              activeTab === "brand"
                ? "bg-brandPrimary text-white shadow-sm"
                : "text-gray-400 hover:text-white hover:bg-surface"
            }`}
          >
            <Brain className="w-4 h-4" />
            <span>Brand Memory</span>
          </button>

          <button
            onClick={() => setActiveTab("fusion")}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition ${
              activeTab === "fusion"
                ? "bg-brandPrimary text-white shadow-sm"
                : "text-gray-400 hover:text-white hover:bg-surface"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Idea Fusion</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
