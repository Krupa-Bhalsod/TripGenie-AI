"use client";

import { useEffect, useRef, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import AgentStatusPanel from "@/components/AgentStatusPanel";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function PlanPageInner() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const destination = searchParams.get("destination") || "";
  const budget      = Number(searchParams.get("budget") || 0);
  const days        = Number(searchParams.get("days") || 3);
  const interests   = JSON.parse(searchParams.get("interests") || "[]");
  const amenities   = JSON.parse(searchParams.get("amenities") || "[]");

  const [events,   setEvents]   = useState<any[]>([]);
  const [progress, setProgress] = useState(0);
  const [status,   setStatus]   = useState<"connecting" | "running" | "complete" | "error">("connecting");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (!destination || !budget) { router.push("/"); return; }

    const startStream = async () => {
      setStatus("running");
      try {
        const res = await fetch(`${API_BASE}/trip/plan/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ destination, budget, days, interests, hotel_amenities: amenities }),
        });

        if (!res.ok) throw new Error(`Server error: ${res.status}`);

        const reader = res.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let agentsCompleted = 0;
        const TOTAL_AGENTS = 9;

        while (reader) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const event = JSON.parse(line.slice(6));
              setEvents((prev) => [...prev, event]);
              if (event.type === "tool_result" || event.type === "agent_update") {
                agentsCompleted = Math.min(agentsCompleted + 0.5, TOTAL_AGENTS);
                setProgress(Math.round((agentsCompleted / TOTAL_AGENTS) * 100));
              }
              if (event.type === "complete") { setProgress(100); setStatus("complete"); }
              if (event.type === "error")    { setStatus("error"); setErrorMsg(event.message || "Unknown error"); }
            } catch (_) {}
          }
        }

        if (status !== "complete") { setStatus("complete"); setProgress(100); }
      } catch (err: any) {
        setStatus("error");
        setErrorMsg(err.message || "Connection failed");
      }
    };

    startStream();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (status === "complete") {
      const timer = setTimeout(async () => {
        try {
          const res = await fetch(`${API_BASE}/trip/plan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ destination, budget, days, interests, hotel_amenities: amenities }),
          });
          if (res.ok) {
            const data = await res.json();
            sessionStorage.setItem("trip_result", JSON.stringify(data));
            router.push("/results");
          }
        } catch (_) {}
      }, 2000);
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  const cities = destination.split(",").map((c) => c.trim());

  return (
    <main className="min-h-screen bg-[#050b18]">
      <div className="fixed inset-0 dot-bg opacity-30 pointer-events-none" />

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
            Back
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-accent-gradient flex items-center justify-center">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <span className="font-bold text-sm text-white">TripGenie <span className="text-blue-400">AI</span></span>
          </div>
          <div style={{ width: "80px" }} />
        </div>
      </nav>

      {/* ── Page body ────────────────────────────────────────────── */}
      <div className="relative z-10 content-container" style={{ paddingTop: "48px", paddingBottom: "80px" }}>

        {/* ── Trip Title Block ───────────────────────────────────── */}
        <div style={{ marginBottom: "32px" }}>

          {/* Status indicator */}
          <div className="flex items-center gap-3" style={{ marginBottom: "16px" }}>
            {status === "running" && (
              <div className="flex" style={{ gap: "4px" }}>
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="rounded-full bg-blue-500 animate-bounce"
                    style={{ width: "8px", height: "8px", animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
            )}
            {status === "complete" && (
              <div className="w-6 h-6 rounded-full flex items-center justify-center"
                style={{ background: "rgba(16,185,129,0.2)", border: "1px solid rgba(16,185,129,0.4)" }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
            )}
            {status === "error" && (
              <div className="w-6 h-6 rounded-full flex items-center justify-center"
                style={{ background: "rgba(239,68,68,0.2)", border: "1px solid rgba(239,68,68,0.4)" }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5">
                  <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </div>
            )}
            <span className="text-sm text-[#94a3b8] font-medium">
              {status === "connecting" && "Connecting to agents..."}
              {status === "running"    && "Agents working..."}
              {status === "complete"   && "Planning complete — loading results..."}
              {status === "error"      && "Agent error"}
            </span>
          </div>

          {/* Heading */}
          <h1 className="text-2xl md:text-3xl font-bold text-white leading-tight" style={{ marginBottom: "16px" }}>
            Planning your trip to{" "}
            <span className="gradient-text">
              {cities.length > 1 ? cities.join(" → ") : destination}
            </span>
          </h1>

          {/* Trip metadata pills */}
          <div className="flex flex-wrap" style={{ gap: "8px" }}>
            {[
              {
                icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/></svg>,
                label: `${days} ${days === 1 ? "day" : "days"}`,
              },
              {
                icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>,
                label: `₹${budget.toLocaleString("en-IN")}`,
              },
              ...(interests.length > 0 ? [{ icon: null, label: interests.join(", ") }] : []),
            ].map(({ icon, label }) => (
              <span
                key={label}
                className="flex items-center gap-1.5 text-sm text-[#94a3b8]"
                style={{ padding: "6px 14px", borderRadius: "100px", background: "#152236", border: "1px solid #1e3a5f" }}
              >
                {icon}
                {label}
              </span>
            ))}
          </div>
        </div>

        {/* ── Error state ───────────────────────────────────────── */}
        {status === "error" && (
          <div className="card" style={{ padding: "24px", marginBottom: "24px", borderColor: "rgba(153,27,27,0.4)" }}>
            <div className="flex items-start" style={{ gap: "16px" }}>
              <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ background: "rgba(239,68,68,0.2)" }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-red-300" style={{ marginBottom: "4px" }}>Planning Failed</p>
                <p className="text-sm text-[#94a3b8]" style={{ marginBottom: "12px" }}>{errorMsg}</p>
                <button
                  onClick={() => router.push("/")}
                  className="text-sm text-blue-400 hover:text-blue-300 underline"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Agent Status Panel ────────────────────────────────── */}
        <AgentStatusPanel events={events} progress={progress} />

        {/* ── Planning Context ─────────────────────────────────── */}
        <div className="card" style={{ padding: "28px 32px", marginTop: "24px" }}>
          <p
            className="text-xs font-semibold text-[#475569] uppercase tracking-widest"
            style={{ marginBottom: "20px" }}
          >
            Planning Context
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4" style={{ gap: "16px" }}>
            {[
              { label: "Budget/Night", value: `₹${Math.round((budget / days) * 0.4).toLocaleString("en-IN")}` },
              { label: "Activity/Day", value: `₹${Math.round((budget / days) * 0.3).toLocaleString("en-IN")}` },
              { label: "Food/Day",     value: `₹${Math.round((budget / days) * 0.3).toLocaleString("en-IN")}` },
              { label: "Cities",       value: String(cities.length) },
            ].map((item) => (
              <div
                key={item.label}
                className="text-center rounded-xl"
                style={{ padding: "20px 16px", background: "#152236" }}
              >
                <div className="text-base font-bold text-blue-400">{item.value}</div>
                <div className="text-xs text-[#475569]" style={{ marginTop: "6px" }}>{item.label}</div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </main>
  );
}

export default function PlanPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#050b18] flex items-center justify-center">
          <div className="flex items-center gap-3 text-[#94a3b8]">
            <div className="flex" style={{ gap: "4px" }}>
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="rounded-full bg-blue-500 animate-bounce"
                  style={{ width: "8px", height: "8px", animationDelay: `${i * 0.2}s` }}
                />
              ))}
            </div>
            Loading...
          </div>
        </div>
      }
    >
      <PlanPageInner />
    </Suspense>
  );
}
