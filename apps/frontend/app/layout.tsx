import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TCMS ERP",
  description: "Enterprise education management system authentication foundation",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
