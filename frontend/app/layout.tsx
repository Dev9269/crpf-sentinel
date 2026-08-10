import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import { Providers } from "@/app/providers";
import "./globals.css";

const inter = localFont({
  src: "./fonts/Inter-variable.woff2",
  variable: "--font-inter",
  display: "swap",
});

const jetbrains = localFont({
  src: "./fonts/JetBrainsMono-variable.woff2",
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "CRPF SENTINEL — Centralized IT System Log Analysis & Threat Detection Platform",
  description:
    "Centralized Security Operations for CRPF: SIEM-grade Windows Event Log monitoring, threat detection, alerting, and incident response across distributed units.",
  applicationName: "CRPF SENTINEL",
  icons: {
    icon: "/shield.svg",
  },
};

export const viewport: Viewport = {
  themeColor: "#060A12",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable} dark`}>
      <body className="min-h-screen antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
