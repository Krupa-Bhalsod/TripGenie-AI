"use client";

import { useState, KeyboardEvent } from "react";

const INTERESTS = [
  { id: "food",         label: "🍜 Food"         },
  { id: "history",      label: "🏛️ History"       },
  { id: "architecture", label: "🕌 Architecture"  },
  { id: "nature",       label: "🌿 Nature"        },
  { id: "nightlife",    label: "🌃 Nightlife"     },
  { id: "shopping",     label: "🛍️ Shopping"      },
  { id: "adventure",    label: "🧗 Adventure"     },
  { id: "culture",      label: "🎭 Culture"       },
  { id: "art",          label: "🎨 Art"           },
  { id: "beaches",      label: "🏖️ Beaches"       },
];

const AMENITIES = [
  { id: "wifi",       label: "📶 WiFi"       },
  { id: "breakfast",  label: "🍳 Breakfast"  },
  { id: "pool",       label: "🏊 Pool"       },
  { id: "gym",        label: "💪 Gym"        },
  { id: "parking",    label: "🚗 Parking"    },
  { id: "spa",        label: "💆 Spa"        },
  { id: "ac",         label: "❄️ AC"         },
  { id: "restaurant", label: "🍽️ Restaurant" },
];

interface Props {
  onSubmit: (data: {
    destination: string;
    budget: number;
    days: number;
    interests: string[];
    hotel_amenities: string[];
  }) => void;
}

export default function PlannerForm({ onSubmit }: Props) {
  const [cityInput, setCityInput] = useState("");
  const [cities,    setCities]    = useState<string[]>([]);
  const [budget,    setBudget]    = useState(10000);
  const [days,      setDays]      = useState(3);
  const [interests, setInterests] = useState<string[]>([]);
  const [amenities, setAmenities] = useState<string[]>([]);
  const [error,     setError]     = useState("");

  const addCity = () => {
    const trimmed = cityInput.trim();
    if (!trimmed) return;
    if (cities.includes(trimmed)) { setError("City already added."); return; }
    setCities([...cities, trimmed]);
    setCityInput("");
    setError("");
  };

  const removeCity = (city: string) => setCities(cities.filter((c) => c !== city));

  const handleCityKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") { e.preventDefault(); addCity(); }
    if (e.key === "Backspace" && !cityInput && cities.length > 0) setCities(cities.slice(0, -1));
  };

  const toggleInterest = (id: string) =>
    setInterests((prev) => prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]);

  const toggleAmenity = (id: string) =>
    setAmenities((prev) => prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const allCities = cities.length > 0 ? cities : (cityInput.trim() ? [cityInput.trim()] : []);
    if (allCities.length === 0) { setError("Please add at least one city."); return; }
    if (budget <= 0) { setError("Please enter a valid budget."); return; }
    setError("");
    onSubmit({ destination: allCities.join(", "), budget, days, interests, hotel_amenities: amenities });
  };

  /* ── Shared label style ──────────────────────────────────────── */
  const labelClass = "block text-xs font-semibold text-[#94a3b8] uppercase tracking-widest";

  return (
    <form onSubmit={handleSubmit}>

      {/* ── Header ───────────────────────────────────────────────── */}
      <div style={{ marginBottom: "32px", paddingBottom: "24px", borderBottom: "1px solid rgba(30,58,95,0.5)" }}>
        <h2 className="text-2xl font-bold text-white" style={{ marginBottom: "6px" }}>Plan Your Trip</h2>
        <p className="text-[#94a3b8] text-sm">Enter cities only — countries and regions are not supported.</p>
      </div>

      {/* ── Destination ──────────────────────────────────────────── */}
      <div style={{ marginBottom: "24px" }}>
        <label className={labelClass} style={{ marginBottom: "12px", display: "block" }}>
          Destination Cities
        </label>
        <div
          className="input-base flex flex-wrap cursor-text"
          style={{ gap: "8px", padding: "12px 16px", minHeight: "56px" }}
          onClick={() => document.getElementById("city-input")?.focus()}
        >
          {cities.map((city) => (
            <span
              key={city}
              className="inline-flex items-center gap-1.5 text-blue-300 text-sm font-medium"
              style={{ padding: "4px 12px", background: "rgba(37,99,235,0.2)", border: "1px solid rgba(59,130,246,0.4)", borderRadius: "8px" }}
            >
              {city}
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); removeCity(city); }}
                className="text-blue-400 hover:text-white transition-colors leading-none"
              >
                ×
              </button>
            </span>
          ))}
          <input
            id="city-input"
            type="text"
            value={cityInput}
            onChange={(e) => { setCityInput(e.target.value); setError(""); }}
            onKeyDown={handleCityKeyDown}
            onBlur={addCity}
            placeholder={cities.length === 0 ? "Type a city and press Enter (e.g. Jaipur)" : "Add another city..."}
            className="flex-1 bg-transparent outline-none text-white placeholder:text-[#475569] text-sm"
            style={{ minWidth: "180px" }}
          />
        </div>

        {error && (
          <p className="text-red-400 text-xs flex items-center gap-1" style={{ marginTop: "8px" }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {error}
          </p>
        )}
        {cities.length > 1 && (
          <p className="text-blue-400 text-xs flex items-center gap-1" style={{ marginTop: "8px" }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2l9 4.5v9L12 20l-9-4.5v-9L12 2z"/></svg>
            Multi-city mode: agents will optimize visit order
          </p>
        )}
      </div>

      {/* ── Budget + Duration ─────────────────────────────────────── */}
      <div
        className="grid grid-cols-1 sm:grid-cols-2"
        style={{ gap: "24px", marginBottom: "24px" }}
      >
        {/* Budget */}
        <div>
          <label className={labelClass} style={{ marginBottom: "12px", display: "block" }}>Total Budget</label>
          <div className="relative" style={{ marginBottom: "12px" }}>
            <span className="absolute text-[#94a3b8] font-semibold text-sm pointer-events-none"
              style={{ left: "16px", top: "50%", transform: "translateY(-50%)" }}>₹</span>
            <input
              type="number"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              min={500} max={1000000} step={500}
              className="input-base"
              style={{ paddingLeft: "32px" }}
            />
          </div>
          <input
            type="range"
            min={1000} max={200000} step={1000}
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            className="w-full rounded-full appearance-none cursor-pointer"
            style={{ background: `linear-gradient(to right, #2563eb ${(budget/200000)*100}%, #1e3a5f ${(budget/200000)*100}%)` }}
          />
          <div className="flex justify-between text-xs text-[#475569]" style={{ marginTop: "6px" }}>
            <span>₹1K</span>
            <span className="text-blue-400 font-medium">₹{budget.toLocaleString("en-IN")}</span>
            <span>₹2L</span>
          </div>
        </div>

        {/* Duration */}
        <div>
          <label className={labelClass} style={{ marginBottom: "12px", display: "block" }}>Duration</label>
          <div className="flex items-center" style={{ gap: "12px", marginBottom: "8px" }}>
            <button
              type="button"
              onClick={() => setDays(Math.max(1, days - 1))}
              className="w-11 h-11 rounded-lg text-white font-bold hover:border-blue-500 hover:bg-blue-950/50 transition-all flex-shrink-0 flex items-center justify-center"
              style={{ background: "#152236", border: "1px solid #1e3a5f" }}
            >
              −
            </button>
            <div className="flex-1 input-base text-center font-bold text-white text-lg" style={{ padding: "12px 16px" }}>
              {days} <span className="text-[#94a3b8] text-sm font-normal">{days === 1 ? "day" : "days"}</span>
            </div>
            <button
              type="button"
              onClick={() => setDays(Math.min(30, days + 1))}
              className="w-11 h-11 rounded-lg text-white font-bold hover:border-blue-500 hover:bg-blue-950/50 transition-all flex-shrink-0 flex items-center justify-center"
              style={{ background: "#152236", border: "1px solid #1e3a5f" }}
            >
              +
            </button>
          </div>
          <p className="text-xs text-[#475569] text-center">1 to 30 days</p>
        </div>
      </div>

      {/* ── Interests ─────────────────────────────────────────────── */}
      <div style={{ marginBottom: "24px" }}>
        <label className={labelClass} style={{ marginBottom: "12px", display: "block" }}>
          Interests{" "}
          <span className="text-[#475569] normal-case font-normal tracking-normal">(select all that apply)</span>
        </label>
        <div className="flex flex-wrap" style={{ gap: "8px" }}>
          {INTERESTS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => toggleInterest(item.id)}
              className={`chip ${interests.includes(item.id) ? "chip-active-blue" : ""}`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Hotel Amenities ───────────────────────────────────────── */}
      <div style={{ marginBottom: "32px" }}>
        <label className={labelClass} style={{ marginBottom: "12px", display: "block" }}>
          Hotel Amenities{" "}
          <span className="text-[#475569] normal-case font-normal tracking-normal">(required)</span>
        </label>
        <div className="flex flex-wrap" style={{ gap: "8px" }}>
          {AMENITIES.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => toggleAmenity(item.id)}
              className={`chip ${amenities.includes(item.id) ? "chip-active-green" : ""}`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Summary + Submit ──────────────────────────────────────── */}
      <div
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between"
        style={{ gap: "16px", paddingTop: "24px", borderTop: "1px solid rgba(30,58,95,0.5)" }}
      >
        <div className="text-sm text-[#94a3b8] min-w-0">
          {cities.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              <span className="font-semibold text-white">{cities.join(" → ")}</span>
              <span>·</span>
              <span>₹{budget.toLocaleString("en-IN")}</span>
              <span>·</span>
              <span>{days}d</span>
              {interests.length > 0 && <><span>·</span><span>{interests.join(", ")}</span></>}
            </div>
          )}
        </div>
        <button type="submit" className="btn-primary flex-shrink-0">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Launch Agents
        </button>
      </div>

    </form>
  );
}
