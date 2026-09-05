import "./globals.css";

export const metadata = {
  title: "Borsa Takip",
  description: "Borsa Takip UygulamasÄ±",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
