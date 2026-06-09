import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Obrigações Platform",
  description: "Plataforma de gestão de obrigações contratuais",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}