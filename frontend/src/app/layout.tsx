import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TripGenie AI | Your Agentic Travel Copilot",
  description:
    "AI-powered travel planner with real-time agent orchestration. Get personalized, budget-aware itineraries backed by live web research for any city in the world.",
  keywords: "AI travel planner, budget travel, itinerary generator, agentic AI, trip planning",
  openGraph: {
    title: "TripGenie AI | Your Agentic Travel Copilot",
    description: "AI-powered travel planner with real-time agent orchestration.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${poppins.variable} font-sans bg-[#050b18] text-[#f0f6ff] antialiased`}>
        {children}
      </body>
    </html>
  );
}
