import React, { useState, useEffect } from "react";
import { Calendar as CalendarIcon, BarChart3, CheckCircle2, Share2, Eye, Heart, MessageSquare } from "lucide-react";
import { api, CalendarItem } from "../lib/api";

export const CalendarView: React.FC = () => {
  const [items, setItems] = useState<CalendarItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<CalendarItem | null>(null);
  const [metrics, setMetrics] = useState({
    views: 12500,
    likes: 850,
    shares: 140,
    comments: 92,
    retention_rate: 0.78,
  });
  const [perfResult, setPerfResult] = useState<any | null>(null);

  useEffect(() => {
    loadCalendar();
  }, []);

  const loadCalendar = async () => {
    setLoading(true);
    try {
      const data = await api.getCalendarItems();
      setItems(data);
      if (data.length > 0) {
        setSelectedItem(data[0]);
      }
    } catch (err) {
      console.error("Failed to load calendar items:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogPerformance = async () => {
    if (!selectedItem) return;
    try {
      const res = await api.logPerformance({
        content_output_id: (selectedItem as any).content_output_id || selectedItem.id,
        views: metrics.views,
        likes: metrics.likes,
        shares: metrics.shares,
        comments: metrics.comments,
        retention_rate: metrics.retention_rate,
      });
      setPerfResult(res);
    } catch (err: any) {
      alert("Performance logging error: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <CalendarIcon className="w-5 h-5 text-brandPrimary" />
            <span>Content Calendar & Performance Loop</span>
          </h2>
          <p className="text-sm text-gray-400">
            Track multi-platform schedule, log post performance, and feed engagement metrics back into the generation engine.
          </p>
        </div>
        <button
          onClick={loadCalendar}
          className="text-xs px-3 py-1.5 rounded-lg bg-surfaceBorder text-gray-300 hover:text-white transition"
        >
          Refresh Schedule
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar Timeline List (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">
              Scheduled Queue ({items.length} Posts)
            </h3>

            {loading ? (
              <div className="py-12 text-center text-sm text-gray-400">Loading calendar items...</div>
            ) : items.length === 0 ? (
              <div className="py-12 text-center text-sm text-gray-400 space-y-2">
                <p>No posts scheduled yet.</p>
                <p className="text-xs text-gray-500">
                  Select a clip in Clip Studio and approve it to see it appear on your calendar.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {items.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem(item)}
                    className={`p-4 rounded-xl border transition cursor-pointer flex items-center justify-between ${
                      selectedItem?.id === item.id
                        ? "bg-brandPrimary/10 border-brandPrimary"
                        : "bg-background border-surfaceBorder hover:border-gray-700"
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs uppercase font-bold px-2 py-0.5 rounded bg-brandPrimary/20 text-brandPrimary">
                          {item.platform.replace("_", " ")}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 capitalize font-medium">
                          {item.status}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400">
                        Scheduled for:{" "}
                        <span className="text-gray-200 font-medium">
                          {new Date(item.scheduled_at).toLocaleString()}
                        </span>
                      </p>
                    </div>

                    <button className="text-xs px-3 py-1.5 rounded-lg bg-surfaceBorder text-gray-300 hover:text-white">
                      Select
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Performance Feedback Loop Simulator (1 col) */}
        <div className="space-y-6">
          <div className="bg-surface rounded-2xl border border-surfaceBorder p-6 space-y-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-brandAccent" />
              <h3 className="text-base font-bold text-white">Performance Feedback Loop</h3>
            </div>
            <p className="text-xs text-gray-400">
              Enter real engagement stats for the selected post to trigger the continuous learning loop.
            </p>

            {selectedItem ? (
              <div className="space-y-3 pt-2">
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <label className="text-gray-400 block mb-1">Views</label>
                    <input
                      type="number"
                      value={metrics.views}
                      onChange={(e) => setMetrics({ ...metrics, views: Number(e.target.value) })}
                      className="w-full bg-background border border-surfaceBorder rounded-lg p-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-gray-400 block mb-1">Likes</label>
                    <input
                      type="number"
                      value={metrics.likes}
                      onChange={(e) => setMetrics({ ...metrics, likes: Number(e.target.value) })}
                      className="w-full bg-background border border-surfaceBorder rounded-lg p-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-gray-400 block mb-1">Shares</label>
                    <input
                      type="number"
                      value={metrics.shares}
                      onChange={(e) => setMetrics({ ...metrics, shares: Number(e.target.value) })}
                      className="w-full bg-background border border-surfaceBorder rounded-lg p-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-gray-400 block mb-1">Comments</label>
                    <input
                      type="number"
                      value={metrics.comments}
                      onChange={(e) => setMetrics({ ...metrics, comments: Number(e.target.value) })}
                      className="w-full bg-background border border-surfaceBorder rounded-lg p-2 text-white"
                    />
                  </div>
                </div>

                <button
                  onClick={handleLogPerformance}
                  className="w-full mt-3 py-2.5 bg-brandAccent hover:bg-brandAccent/90 rounded-xl text-xs font-semibold text-white shadow-lg shadow-brandAccent/20 transition flex items-center justify-center space-x-2"
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>Update Feedback Model</span>
                </button>

                {perfResult && (
                  <div className="p-3.5 bg-background rounded-xl border border-brandAccent/30 text-xs space-y-1.5 mt-3">
                    <div className="flex items-center justify-between text-brandAccent font-bold">
                      <span>Performance Score:</span>
                      <span>{perfResult.performance_score} / 10</span>
                    </div>
                    <p className="text-gray-300 leading-relaxed text-[11px]">
                      {perfResult.recommendation_impact}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-gray-500 py-6 text-center">Select a scheduled post to log metrics.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
