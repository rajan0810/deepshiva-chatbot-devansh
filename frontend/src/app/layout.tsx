import type { Metadata } from "next";
import { Merriweather, Lato } from "next/font/google";
import "./globals.css";

const merriweather = Merriweather({
  weight: ["300", "400", "700", "900"],
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
});

const lato = Lato({
  weight: ["100", "300", "400", "700", "900"],
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "DeepShiva - Ayurvedic Healthcare Assistant",
  description: "Holistic health guidance through Ayurveda and Yoga",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${merriweather.variable} ${lato.variable} antialiased bg-stone-50 text-stone-800`}
      >
        {children}
      </body>
    </html>
  );
}