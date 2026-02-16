import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono, Playfair_Display, Lora } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })
const playfair = Playfair_Display({ subsets: ["latin", "cyrillic"], variable: "--font-serif" })
const lora = Lora({ subsets: ["latin", "cyrillic"], variable: "--font-body" })

export const metadata: Metadata = {
  title: "Интеллектуальная система управления проектами",
  description: "AI-powered project management system",
  generator: "v0.app",
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ru">
      <body className={`${playfair.variable} ${lora.variable} antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
