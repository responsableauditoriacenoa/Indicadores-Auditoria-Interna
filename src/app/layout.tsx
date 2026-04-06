import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Dashboard de Auditoría Interna",
  description: "KPIs Gerenciales para Seguimiento de Auditoría",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>
        <ThemeProvider>
          <Navbar />
          <main className="container">
            {children}
          </main>
        </ThemeProvider>
      </body>
    </html>
  );
}
