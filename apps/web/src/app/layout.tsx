import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Insight Alumina | Tarot Readings",
  description: "Explore tarot readings and view appointment availability with Insight Alumina.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
