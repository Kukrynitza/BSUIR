import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css" ;
import "the-new-css-reset/css/reset.css";
import '@fontsource/noto-sans-kr'
import Header from "@/companents/Header/header";

export default function RootLayout({children}: Readonly<{children: React.ReactNode;}>) {
  return (
    <html lang="en">
      <body>
        <Header/>
        {children}
      </body>
    </html>
  );
}
