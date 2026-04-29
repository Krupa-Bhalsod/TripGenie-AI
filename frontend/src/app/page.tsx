"use client";

import { useRouter } from "next/navigation";
import PlannerForm from "@/components/PlannerForm";
import HeroSection from "@/components/HeroSection";

export default function Home() {
  const router = useRouter();

  const handlePlanTrip = async (formData: {
    destination: string;
    budget: number;
    days: number;
    interests: string[];
    hotel_amenities: string[];
  }) => {
    const params = new URLSearchParams({
      destination: formData.destination,
      budget: String(formData.budget),
      days: String(formData.days),
      interests: JSON.stringify(formData.interests),
      amenities: JSON.stringify(formData.hotel_amenities),
    });
    router.push(`/plan?${params.toString()}`);
  };

  return (
    <main className="min-h-screen bg-[#050b18] relative overflow-hidden">
      {/* Background dot grid */}
      <div className="fixed inset-0 dot-bg opacity-40 pointer-events-none" />

      {/* Radial glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[900px] h-[600px] pointer-events-none"
        style={{ background: "radial-gradient(ellipse at center, rgba(37,99,235,0.12) 0%, transparent 70%)" }}
      />

      {/* ── Nav ──────────────────────────────────────────────────── */}
      <nav className="relative z-10 border-b border-[#1e3a5f]/30">
        <div className="page-container flex items-center justify-between" style={{ paddingTop: "20px", paddingBottom: "20px" }}>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent-gradient flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight text-white">
              TripGenie<span className="text-blue-400"> AI</span>
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="badge badge-blue hidden sm:inline-flex">Beta</span>
            <a href="https://github.com" className="text-sm text-[#94a3b8] hover:text-white transition-colors">
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────────────────────── */}
      <HeroSection />

      {/* ── Planner Form ─────────────────────────────────────────── */}
      <section id="planner" className="relative z-10" style={{ paddingBottom: "96px" }}>
        <div className="content-container">
          <div className="card glow-border" style={{ padding: "40px 48px" }}>
            <PlannerForm onSubmit={handlePlanTrip} />
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────────────── */}
      <footer
        className="relative z-10 text-center text-[#475569] text-sm border-t border-[#1e3a5f]/50"
        style={{ paddingTop: "32px", paddingBottom: "32px" }}
      >
        <p>TripGenie AI · Powered by Qwen2.5 + Tavily · Built with deepagents</p>
      </footer>
    </main>
  );
}
