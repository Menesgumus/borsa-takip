import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers";
import { NetworkProvider } from "@/components/NetworkProvider";

export const metadata: Metadata = {
  title: "Borsa Takip",
  description: "Borsa Takip Uygulaması",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#4f46e5",
  width: "device-width",
  initialScale: 1,
  
  
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <head>
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
      </head>
      <body
        className="font-sans [--font-inter:ui-sans-serif] antialiased bg-slate-50 text-slate-900 min-h-screen flex flex-col"
      >
        <Providers>
          <NetworkProvider>
            {children}
          </NetworkProvider>
        </Providers>
      </body>
    </html>
  );
}
