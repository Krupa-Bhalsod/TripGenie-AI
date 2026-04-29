"use client";

const STEPS = [
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
      </svg>
    ),
    title: "Live Research",
    description: "8 agents run targeted searches using your budget, interests, and amenities as hard constraints — not hints.",
    step: "01",
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    ),
    title: "Constraint Filtering",
    description: "Results are filtered post-retrieval. Hotels exceeding your budget are discarded. Luxury chains flagged. Only compliant options proceed.",
    step: "02",
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14.5 10c-.83 0-1.5-.67-1.5-1.5v-5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5z"/><path d="M20.5 10H19V8.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/><path d="M9.5 14c.83 0 1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5S8 21.33 8 20.5v-5c0-.83.67-1.5 1.5-1.5z"/><path d="M3.5 14H5v1.5c0 .83-.67 1.5-1.5 1.5S2 16.33 2 15.5 2.67 14 3.5 14z"/><path d="M14 14.5c0-.83.67-1.5 1.5-1.5h5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5h-5c-.83 0-1.5-.67-1.5-1.5z"/><path d="M15.5 19H14v1.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5-.67-1.5-1.5-1.5z"/><path d="M10 9.5C10 8.67 9.33 8 8.5 8h-5C2.67 8 2 8.67 2 9.5S2.67 11 3.5 11h5c.83 0 1.5-.67 1.5-1.5z"/><path d="M8.5 5H10V3.5C10 2.67 9.33 2 8.5 2S7 2.67 7 3.5 7.67 5 8.5 5z"/>
      </svg>
    ),
    title: "Structured Itinerary",
    description: "Budget validator approves the final plan. Day-by-day itinerary with real hotels, grounded activities, and source citations.",
    step: "03",
  },
];

export default function HowItWorks() {
  return (
    <section className="relative z-10 max-w-6xl mx-auto px-4 py-20">
      <div className="text-center mb-14">
        <div className="badge badge-blue mx-auto mb-4">How It Works</div>
        <h2 className="text-3xl font-bold text-white">
          Not a chatbot. An{" "}
          <span className="gradient-text">agentic pipeline.</span>
        </h2>
        <p className="text-[#94a3b8] mt-3 max-w-xl mx-auto">
          Every recommendation is retrieval-backed and constraint-filtered before it reaches you.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {STEPS.map((step, i) => (
          <div
            key={step.title}
            className="card p-6 relative overflow-hidden group animate-fade-in"
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            {/* Step number bg */}
            <div className="absolute top-4 right-4 text-6xl font-black text-[#0d1829] select-none">
              {step.step}
            </div>

            {/* Icon */}
            <div className="w-10 h-10 rounded-xl bg-blue-600/15 border border-blue-600/30 flex items-center justify-center text-blue-400 mb-4 group-hover:bg-blue-600/25 transition-colors">
              {step.icon}
            </div>

            <h3 className="font-semibold text-white mb-2">{step.title}</h3>
            <p className="text-[#94a3b8] text-sm leading-relaxed">{step.description}</p>
          </div>
        ))}
      </div>

      {/* Agent pipeline visual */}
      <div className="mt-14 card p-6 overflow-x-auto">
        <p className="text-xs font-semibold text-[#475569] uppercase tracking-widest mb-5">Agent Pipeline</p>
        <div className="flex items-center gap-2 min-w-max">
          {[
            "City Validator",
            "Query Builder",
            "Hotel Discovery",
            "Activity Research",
            "Food Research",
            "Transport Agent",
            "Constraint Filter",
            "Itinerary Planner",
            "Budget Validator",
          ].map((agent, i, arr) => (
            <div key={agent} className="flex items-center gap-2">
              <div className="flex flex-col items-center">
                <div className="px-3 py-1.5 rounded-lg bg-[#152236] border border-[#1e3a5f] text-xs text-[#94a3b8] font-medium whitespace-nowrap hover:border-blue-600/40 hover:text-white transition-all">
                  {agent}
                </div>
              </div>
              {i < arr.length - 1 && (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2.5" className="flex-shrink-0 opacity-60">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
