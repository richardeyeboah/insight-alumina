import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Insight Alumina — Tarot & Reflection",
  description: "A little stillness. A different perspective. Explore tarot as a space for reflection with Insight Alumina.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
