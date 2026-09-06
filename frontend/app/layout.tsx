import "./globals.css";

export const metadata = {
  title: "Borsa Takip",
  description: "Borsa Takip UygulamasÄ±",
};

import { Providers } from "@/components/Providers";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
