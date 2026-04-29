"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Activity {
  name: string;
  cost: number;
  category: string;
  description: string;
}

interface Hotel {
  hotel_name: string;
  nightly_price: number;
  amenities_found: string[];
  area: string;
  reason: string;
  source_url: string;
  budget_compliant: boolean;
}

interface DayPlan {
  city: string;
  activities: Activity[];
  hotel: Hotel | null;
  food_highlights: string[];
  day_total_cost: number;
  local_tips: string;
}

interface TripData {
  destinations: string[];
  budget: number;
  days: number;
  itinerary: Record<string, DayPlan>;
  hotels: Hotel[];
  estimated_total_cost: number;
  transport_guide: string;
  citations: string[];
  confidence_score: number;
  budget_breakdown?: {
    accommodation: number;
    activities: number;
    food: number;
    transport: number;
    total: number;
    within_budget: boolean;
  };
}

const TABS = ["Itinerary", "Hotels", "Transport", "Budget"] as const;
type Tab = (typeof TABS)[number];

export default function ResultsPage() {
  const router = useRouter();
  const [trip,      setTrip]      = useState<TripData | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("Itinerary");
  const [loading,   setLoading]   = useState(true);

  useEffect(() => {
    const raw = sessionStorage.getItem("trip_result");
    if (!raw) { router.push("/"); return; }
    try { setTrip(JSON.parse(raw)); }
    catch { router.push("/"); }
    finally { setLoading(false); }
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050b18] flex items-center justify-center">
        <div className="text-center" style={{ gap: "12px" }}>
          <div className="w-10 h-10 rounded-full border-2 border-blue-600 border-t-transparent animate-spin mx-auto" style={{ marginBottom: "12px" }} />
          <p className="text-[#94a3b8] text-sm">Loading your trip...</p>
        </div>
      </div>
    );
  }

  if (!trip) return null;

  const days       = Object.entries(trip.itinerary || {});
  const confidence = Math.round((trip.confidence_score || 0.8) * 100);
  const budgetOk   = trip.estimated_total_cost <= trip.budget;

  return (
    <main className="min-h-screen bg-[#050b18]">
      <div className="fixed inset-0 dot-bg opacity-20 pointer-events-none" />

      {/* ── Nav ──────────────────────────────────────────────────── */}
      <nav className="relative z-10 border-b border-[#1e3a5f]/40">
        <div className="page-container flex items-center justify-between" style={{ paddingTop: "20px", paddingBottom: "20px" }}>
          <button
            onClick={() => router.push("/")}
            className="flex items-center gap-2 text-[#94a3b8] hover:text-white transition-colors text-sm"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            Plan Another
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-accent-gradient flex items-center justify-center">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <span className="font-bold text-sm text-white">TripGenie <span className="text-blue-400">AI</span></span>
          </div>
          <div style={{ width: "112px" }} />
        </div>
      </nav>

      {/* ── Page body ────────────────────────────────────────────── */}
      <div className="relative z-10 page-container" style={{ paddingTop: "48px", paddingBottom: "80px" }}>

        {/* ── Trip header ───────────────────────────────────────── */}
        <div className="animate-slide-up" style={{ marginBottom: "32px" }}>
          <div className="flex flex-wrap items-center" style={{ gap: "8px", marginBottom: "12px" }}>
            <div className={`badge ${budgetOk ? "badge-green" : "badge-yellow"}`}>
              {budgetOk ? "Budget Compliant" : "Slightly Over Budget"}
            </div>
            <div className="badge badge-blue">Confidence {confidence}%</div>
            {trip.destinations.length > 1 && (
              <div className="badge" style={{ background: "rgba(139,92,246,0.12)", color: "#c4b5fd", border: "1px solid rgba(139,92,246,0.25)" }}>
                Multi-City
              </div>
            )}
          </div>

          <h1 className="text-4xl font-bold text-white" style={{ marginBottom: "10px" }}>
            {trip.destinations.join(" → ")}
          </h1>

          <div className="flex flex-wrap items-center text-sm text-[#94a3b8]" style={{ gap: "12px" }}>
            <span>{trip.days} days</span>
            <span>·</span>
            <span>Budget ₹{trip.budget.toLocaleString("en-IN")}</span>
            <span>·</span>
            <span className={budgetOk ? "text-emerald-400" : "text-yellow-400"}>
              Estimated ₹{(trip.estimated_total_cost || 0).toLocaleString("en-IN")}
            </span>
          </div>
        </div>

        {/* ── Summary cards ─────────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 animate-fade-in" style={{ gap: "16px", marginBottom: "32px" }}>
          {[
            { label: "Est. Total", value: `₹${(trip.estimated_total_cost || 0).toLocaleString("en-IN")}`, color: budgetOk ? "text-emerald-400" : "text-yellow-400" },
            { label: "Budget",     value: `₹${trip.budget.toLocaleString("en-IN")}`,                       color: "text-blue-400"   },
            { label: "Days",       value: String(trip.days),                                                color: "text-blue-400"   },
            { label: "Cities",     value: String(trip.destinations.length),                                 color: "text-purple-400" },
          ].map((s) => (
            <div key={s.label} className="card text-center" style={{ padding: "24px 16px" }}>
              <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-xs text-[#475569]" style={{ marginTop: "6px" }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* ── Tabs ──────────────────────────────────────────────── */}
        <div
          className="flex animate-fade-in"
          style={{ gap: "4px", background: "#0d1829", border: "1px solid #1e3a5f", borderRadius: "12px", padding: "6px", marginBottom: "24px" }}
        >
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 text-sm font-medium rounded-lg transition-all ${
                activeTab === tab
                  ? "bg-blue-600 text-white shadow-[0_0_15px_rgba(37,99,235,0.3)]"
                  : "text-[#94a3b8] hover:text-white"
              }`}
              style={{ padding: "10px 16px" }}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* ── Tab Content ───────────────────────────────────────── */}
        <div className="animate-fade-in">

          {/* ITINERARY */}
          {activeTab === "Itinerary" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {days.length === 0 ? (
                <div className="card text-center text-[#94a3b8]" style={{ padding: "48px 32px" }}>
                  No itinerary data available.
                </div>
              ) : (
                days.map(([dayKey, plan]) => (
                  <div key={dayKey} className="card group" style={{ padding: "28px 32px" }}>
                    {/* Day header */}
                    <div className="flex items-start justify-between" style={{ marginBottom: "20px" }}>
                      <div>
                        <div className="flex items-center" style={{ gap: "8px", marginBottom: "4px" }}>
                          <span className="text-blue-400 font-bold text-sm">{dayKey}</span>
                          <span className="text-[#475569]">·</span>
                          <span className="text-white font-semibold">{plan.city}</span>
                        </div>
                        {plan.local_tips && (
                          <p className="text-xs text-[#475569] flex items-center gap-1">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                            {plan.local_tips}
                          </p>
                        )}
                      </div>
                      <div className="text-right flex-shrink-0" style={{ marginLeft: "16px" }}>
                        <div className="text-base font-bold text-white">₹{(plan.day_total_cost || 0).toLocaleString("en-IN")}</div>
                        <div className="text-xs text-[#475569]">day total</div>
                      </div>
                    </div>

                    {/* Activities */}
                    <div style={{ marginBottom: "16px" }}>
                      {plan.activities?.map((act, i) => (
                        <div
                          key={i}
                          className="flex items-start justify-between gap-3"
                          style={{ padding: "10px 0", borderBottom: i < plan.activities.length - 1 ? "1px solid rgba(30,58,95,0.35)" : "none" }}
                        >
                          <div className="flex items-start flex-1 min-w-0" style={{ gap: "10px" }}>
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 flex-shrink-0" style={{ marginTop: "7px" }} />
                            <div>
                              <p className="text-sm text-white font-medium">{act.name}</p>
                              {act.description && <p className="text-xs text-[#475569] line-clamp-1" style={{ marginTop: "2px" }}>{act.description}</p>}
                              {act.category    && <span className="badge badge-blue" style={{ marginTop: "6px", fontSize: "10px" }}>{act.category}</span>}
                            </div>
                          </div>
                          <span className="text-sm font-semibold text-blue-300 flex-shrink-0">
                            {act.cost === 0 ? "Free" : `₹${act.cost.toLocaleString("en-IN")}`}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Food highlights */}
                    {plan.food_highlights && plan.food_highlights.length > 0 && (
                      <div style={{ marginBottom: "16px" }}>
                        <p className="text-xs font-semibold text-[#475569] uppercase tracking-wider" style={{ marginBottom: "8px" }}>
                          Food Picks
                        </p>
                        <div className="flex flex-wrap" style={{ gap: "8px" }}>
                          {plan.food_highlights.map((f, i) => (
                            <span
                              key={i}
                              className="text-amber-300 text-xs"
                              style={{ padding: "5px 12px", background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.2)", borderRadius: "8px" }}
                            >
                              {f}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Hotel */}
                    {plan.hotel && (
                      <div
                        className="flex items-start justify-between rounded-xl"
                        style={{ padding: "16px", background: "#152236", border: "1px solid #1e3a5f", gap: "12px" }}
                      >
                        <div className="flex items-start flex-1 min-w-0" style={{ gap: "10px" }}>
                          <svg className="flex-shrink-0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" style={{ marginTop: "3px" }}>
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
                          </svg>
                          <div>
                            <p className="text-sm font-semibold text-white">{plan.hotel.hotel_name}</p>
                            {plan.hotel.area && <p className="text-xs text-[#94a3b8]" style={{ marginTop: "2px" }}>{plan.hotel.area}</p>}
                            {plan.hotel.amenities_found.length > 0 && (
                              <div className="flex flex-wrap" style={{ gap: "4px", marginTop: "6px" }}>
                                {plan.hotel.amenities_found.map((a) => (
                                  <span key={a} className="badge badge-blue" style={{ fontSize: "10px", padding: "2px 6px" }}>{a}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <div className="text-sm font-bold text-blue-300">₹{(plan.hotel.nightly_price || 0).toLocaleString("en-IN")}</div>
                          <div className="text-xs text-[#475569]">/night</div>
                          {plan.hotel.source_url && (
                            <a href={plan.hotel.source_url} target="_blank" rel="noopener noreferrer"
                              className="text-xs text-blue-500 hover:text-blue-400 block" style={{ marginTop: "4px" }}>
                              Source ↗
                            </a>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* HOTELS */}
          {activeTab === "Hotels" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {(trip.hotels || []).length === 0 ? (
                <div className="card text-center text-[#94a3b8]" style={{ padding: "48px 32px" }}>
                  Hotel details are included in the day-by-day itinerary.
                </div>
              ) : (
                (trip.hotels || []).map((hotel, i) => (
                  <div
                    key={i}
                    className="card"
                    style={{ padding: "28px 32px", borderColor: !hotel.budget_compliant ? "rgba(133,77,14,0.4)" : undefined }}
                  >
                    <div className="flex items-start justify-between" style={{ gap: "24px" }}>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center" style={{ gap: "8px", marginBottom: "6px" }}>
                          <h3 className="font-bold text-white text-lg">{hotel.hotel_name}</h3>
                          {!hotel.budget_compliant && <span className="badge badge-yellow">Over Budget</span>}
                        </div>
                        {hotel.area   && <p className="text-sm text-[#94a3b8]" style={{ marginBottom: "8px" }}>📍 {hotel.area}</p>}
                        {hotel.reason && <p className="text-sm text-[#94a3b8]" style={{ marginBottom: "12px" }}>{hotel.reason}</p>}
                        {hotel.amenities_found.length > 0 && (
                          <div className="flex flex-wrap" style={{ gap: "8px" }}>
                            {hotel.amenities_found.map((a) => (
                              <span key={a} className="badge badge-blue">{a}</span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="text-right flex-shrink-0">
                        <div className="text-2xl font-bold text-blue-300">₹{(hotel.nightly_price || 0).toLocaleString("en-IN")}</div>
                        <div className="text-xs text-[#475569]" style={{ marginBottom: "12px" }}>/night</div>
                        {hotel.source_url && (
                          <a
                            href={hotel.source_url} target="_blank" rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-blue-400 text-xs hover:bg-blue-600/25 transition-colors"
                            style={{ padding: "6px 14px", borderRadius: "8px", background: "rgba(37,99,235,0.15)", border: "1px solid rgba(37,99,235,0.3)" }}
                          >
                            View Source ↗
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* TRANSPORT */}
          {activeTab === "Transport" && (
            <div className="card" style={{ padding: "32px" }}>
              <div className="flex items-center" style={{ gap: "12px", marginBottom: "20px" }}>
                <div className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{ background: "rgba(37,99,235,0.15)", border: "1px solid rgba(37,99,235,0.3)" }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2">
                    <rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
                    <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
                  </svg>
                </div>
                <h3 className="font-semibold text-white text-lg">Transport Guide</h3>
              </div>
              {trip.transport_guide ? (
                <p className="text-[#94a3b8] text-sm leading-relaxed whitespace-pre-line">{trip.transport_guide}</p>
              ) : (
                <p className="text-[#475569] text-sm">Transport information is embedded within the day-by-day itinerary above.</p>
              )}
            </div>
          )}

          {/* BUDGET */}
          {activeTab === "Budget" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {trip.budget_breakdown ? (
                <div className="card" style={{ padding: "32px" }}>
                  <h3 className="font-semibold text-white" style={{ marginBottom: "24px" }}>Budget Breakdown</h3>
                  <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                    {[
                      { label: "Accommodation", value: trip.budget_breakdown.accommodation, color: "bg-blue-500",    icon: "🏨" },
                      { label: "Activities",    value: trip.budget_breakdown.activities,    color: "bg-purple-500", icon: "🎭" },
                      { label: "Food",          value: trip.budget_breakdown.food,          color: "bg-amber-500",  icon: "🍜" },
                      { label: "Transport",     value: trip.budget_breakdown.transport,     color: "bg-emerald-500",icon: "🚗" },
                    ].map((item) => {
                      const pct = trip.budget_breakdown
                        ? Math.round((item.value / trip.budget_breakdown.total) * 100) : 0;
                      return (
                        <div key={item.label}>
                          <div className="flex items-center justify-between" style={{ marginBottom: "8px" }}>
                            <span className="text-sm text-[#94a3b8]">{item.icon} {item.label}</span>
                            <span className="text-sm font-semibold text-white">
                              ₹{item.value.toLocaleString("en-IN")} <span className="text-[#475569] font-normal">({pct}%)</span>
                            </span>
                          </div>
                          <div className="progress-bar">
                            <div className={`h-full rounded-full ${item.color} opacity-80 transition-all`} style={{ width: `${pct}%` }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div
                    className="flex items-center justify-between"
                    style={{ marginTop: "24px", paddingTop: "20px", borderTop: "1px solid #1e3a5f" }}
                  >
                    <span className="font-semibold text-white">Total Estimated</span>
                    <div className="text-right">
                      <span className={`text-xl font-bold ${budgetOk ? "text-emerald-400" : "text-yellow-400"}`}>
                        ₹{trip.estimated_total_cost.toLocaleString("en-IN")}
                      </span>
                      <span className="text-sm text-[#475569]" style={{ marginLeft: "8px" }}>
                        / ₹{trip.budget.toLocaleString("en-IN")} budget
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="card text-center text-[#94a3b8]" style={{ padding: "48px 32px" }}>
                  Budget breakdown was not generated. Check the itinerary for per-day costs.
                </div>
              )}

              {/* Citations */}
              {trip.citations && trip.citations.filter(Boolean).length > 0 && (
                <div className="card" style={{ padding: "32px" }}>
                  <h3 className="font-semibold text-white" style={{ marginBottom: "20px" }}>Sources & Citations</h3>
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {trip.citations.filter(Boolean).slice(0, 10).map((url, i) => (
                      <a
                        key={i}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300 transition-colors truncate"
                      >
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                          <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                        </svg>
                        {url}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
