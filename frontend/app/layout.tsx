import type { Metadata, Viewport } from "next";
import { Inter } from 'next/font/google';
import "./globals.css";
import { Providers } from "@/components/Providers";
import { NetworkProvider } from "@/components/NetworkProvider";

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: "Borsa Takip",
  description: "Borsa Takip Uygulaması",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#4f46e5",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
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
        className={`${inter.className} antialiased bg-slate-50 text-slate-900 min-h-screen flex flex-col`}
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