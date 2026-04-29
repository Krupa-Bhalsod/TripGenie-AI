"use client";

export default function HeroSection() {
  return (
    <section className="relative z-10 section">
      <div className="content-container text-center">

        {/* ── Badge ───────────────────────────────────────────── */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-600/10 border border-blue-500/20 text-blue-300 text-xs font-semibold mb-5 animate-fade-in">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
          Agentic AI · Real-Time Research · Budget-Aware
        </div>

        {/* ── Headline ─────────────────────────────────────────── */}
        <h1
          className="hero-headline text-5xl md:text-7xl font-extrabold tracking-tight text-white leading-[1.1] animate-slide-up"
          style={{ marginBottom: "28px", maxWidth: "900px", marginLeft: "auto", marginRight: "auto" }}
        >
          Your AI <span className="gradient-text">Travel Copilot</span>
          <br />
          That Actually Plans
        </h1>

        {/* ── Subheadline ──────────────────────────────────────── */}
        <p
          className="text-lg md:text-xl text-[#94a3b8] leading-relaxed animate-fade-in"
          style={{ maxWidth: "680px", marginLeft: "auto", marginRight: "auto", marginBottom: "32px" }}
        >
          8 specialized agents research hotels, activities, and food in real-time —
          grounded in live data, filtered to your exact budget.
        </p>

        {/* ── Stats row ────────────────────────────────────────── */}
        <div
          className="flex flex-wrap items-center justify-center animate-fade-in"
          style={{ gap: "32px", marginBottom: "32px" }}
        >
          {[
            { value: "8",          label: "AI Agents"    },
            { value: "100%",       label: "Budget-Aware" },
            { value: "Live",       label: "Web Research" },
            { value: "Multi-City", label: "Supported"    },
          ].map(({ value, label }) => (
            <div key={label} className="text-center">
              <div className="text-3xl font-bold text-white">{value}</div>
              <div className="text-xs font-semibold text-[#475569] uppercase tracking-wider mt-1">{label}</div>
            </div>
          ))}
        </div>

        {/* ── CTA ──────────────────────────────────────────────── */}
        <div className="animate-fade-in" style={{ marginBottom: "24px" }}>
          <a
            href="#planner"
            className="btn-primary"
            style={{ fontSize: "1rem", padding: "16px 36px", borderRadius: "14px" }}
          >
            Plan My Trip
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </a>
        </div>

        {/* ── Agent pills ──────────────────────────────────────── */}
        <div
          className="flex flex-wrap justify-center animate-fade-in"
          style={{ gap: "8px", maxWidth: "640px", marginLeft: "auto", marginRight: "auto" }}
        >
          {["City Validator", "Hotel Discovery", "Activity Research", "Budget Guard", "Itinerary Planner"].map((agent) => (
            <span
              key={agent}
              className="inline-flex items-center gap-1.5 text-xs text-[#94a3b8]"
              style={{
                padding: "7px 14px",
                borderRadius: "100px",
                background: "#152236",
                border: "1px solid #1e3a5f",
              }}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#475569]" />
              {agent}
            </span>
          ))}
        </div>

      </div>
    </section>
  );
}