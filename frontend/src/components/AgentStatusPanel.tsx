"use client";

import { useEffect, useRef } from "react";

export type AgentStatus = "waiting" | "running" | "done" | "error" | "skipped";

export interface AgentEntry {
  name: string;
  displayName: string;
  status: AgentStatus;
  message: string;
  tool?: string;
  startedAt?: number;
  doneAt?: number;
}

const AGENT_ORDER = [
  { name: "city_validation_agent",    displayName: "City Validation"     },
  { name: "tripgenie_supervisor",     displayName: "Supervisor"          },
  { name: "destination_research_agent", displayName: "Destination Research" },
  { name: "hotel_discovery_agent",    displayName: "Hotel Discovery"     },
  { name: "activity_research_agent",  displayName: "Activity Research"   },
  { name: "food_research_agent",      displayName: "Food Research"       },
  { name: "transport_agent",          displayName: "Transport Logistics" },
  { name: "itinerary_planning_agent", displayName: "Itinerary Planning"  },
  { name: "budget_validator_agent",   displayName: "Budget Validation"   },
];

const STATUS_ICON = {
  waiting: <span className="status-dot-waiting" />,
  running: <span className="status-dot-running" />,
  done: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  ),
  error: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5">
      <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  ),
  skipped: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2">
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  ),
};

interface Props {
  events: Array<{ type: string; agent?: string; tool?: string; message?: string }>;
  progress: number; // 0-100
}

export default function AgentStatusPanel({ events, progress }: Props) {
  const logRef = useRef<HTMLDivElement>(null);

  // Build agent state from events
  const agentMap: Record<string, AgentEntry> = {};
  AGENT_ORDER.forEach((a) => {
    agentMap[a.name] = { ...a, status: "waiting", message: "" };
  });

  events.forEach((ev) => {
    const agentName = ev.agent || "";
    if (!agentMap[agentName]) return;
    if (ev.type === "tool_call" || ev.type === "agent_update") {
      agentMap[agentName].status = "running";
      if (ev.message) agentMap[agentName].message = ev.message.slice(0, 80);
      if (ev.tool)    agentMap[agentName].tool    = ev.tool;
    } else if (ev.type === "tool_result") {
      agentMap[agentName].status  = "done";
      agentMap[agentName].message = "Complete";
    } else if (ev.type === "complete") {
      Object.values(agentMap).forEach((a) => { if (a.status === "running") a.status = "done"; });
    }
  });

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [events]);

  const agents    = AGENT_ORDER.map((a) => agentMap[a.name]);
  const doneCount = agents.filter((a) => a.status === "done").length;

  return (
    <div className="card" style={{ padding: "32px" }}>

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="flex items-center justify-between gap-4" style={{ marginBottom: "20px" }}>
        <div>
          <h3 className="font-semibold text-white text-lg" style={{ marginBottom: "4px" }}>
            Agent Orchestration
          </h3>
          <p className="text-[#94a3b8] text-sm">{doneCount}/{agents.length} agents complete</p>
        </div>
        <div className="badge badge-blue flex-shrink-0" style={{ padding: "6px 14px", fontSize: "13px" }}>
          {progress}%
        </div>
      </div>

      {/* ── Progress bar ───────────────────────────────────────── */}
      <div className="progress-bar" style={{ marginBottom: "24px" }}>
        <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
      </div>

      {/* ── Agent list ─────────────────────────────────────────── */}
      <div style={{ marginBottom: "24px" }}>
        {agents.map((agent) => (
          <div
            key={agent.name}
            className={`flex items-start rounded-lg transition-all ${
              agent.status === "running"
                ? "bg-blue-600/10 border border-blue-600/20"
                : agent.status === "done"
                ? "bg-emerald-600/5 border border-transparent"
                : "border border-transparent"
            }`}
            style={{ gap: "12px", padding: "12px", marginBottom: "4px" }}
          >
            {/* Status icon */}
            <div className="flex-shrink-0 flex items-center justify-center" style={{ width: "20px", height: "20px", marginTop: "2px" }}>
              {STATUS_ICON[agent.status]}
            </div>

            {/* Name + message */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center flex-wrap" style={{ gap: "8px" }}>
                <span
                  className={`text-sm font-medium ${
                    agent.status === "running" ? "text-blue-300"
                    : agent.status === "done"  ? "text-white"
                    : "text-[#475569]"
                  }`}
                >
                  {agent.displayName}
                </span>
                {agent.status === "running" && agent.tool && (
                  <span className="badge badge-blue" style={{ fontSize: "10px", padding: "2px 8px" }}>
                    {agent.tool.replace(/_/g, " ")}
                  </span>
                )}
              </div>
              {agent.status === "running" && agent.message && (
                <p className="text-xs text-[#475569] truncate" style={{ marginTop: "2px" }}>
                  {agent.message}
                </p>
              )}
            </div>

            {/* Running dots */}
            {agent.status === "running" && (
              <div className="flex-shrink-0 flex" style={{ gap: "3px", marginTop: "6px" }}>
                {[0, 1, 2].map((d) => (
                  <div
                    key={d}
                    className="rounded-full bg-blue-500 animate-bounce"
                    style={{ width: "4px", height: "4px", animationDelay: `${d * 0.15}s` }}
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* ── Live log ───────────────────────────────────────────── */}
      <div>
        <p
          className="text-xs font-semibold text-[#475569] uppercase tracking-widest"
          style={{ marginBottom: "12px" }}
        >
          Live Log
        </p>
        <div
          ref={logRef}
          className="font-mono text-xs text-[#475569] overflow-y-auto scroll-smooth"
          style={{
            background: "#050b18",
            border: "1px solid #1e3a5f",
            borderRadius: "10px",
            padding: "20px 24px",
            height: "160px",
          }}
        >
          {events.length === 0 ? (
            <p className="text-[#334155]">Waiting for agents to start...</p>
          ) : (
            events.map((ev, i) => (
              <div key={i} className="flex leading-5" style={{ gap: "12px", marginBottom: "4px" }}>
                <span className="text-[#1e3a5f] flex-shrink-0 tabular-nums">
                  {new Date().toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                </span>
                <span
                  className={`min-w-0 break-all ${
                    ev.type === "error"     ? "text-red-400"
                    : ev.type === "complete" ? "text-emerald-400"
                    : ev.type === "tool_call" ? "text-blue-400"
                    : "text-[#94a3b8]"
                  }`}
                >
                  [{ev.agent || ev.type}]{" "}
                  {ev.tool ? `→ ${ev.tool}` : ev.message ? ev.message.slice(0, 80) : ev.type}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
