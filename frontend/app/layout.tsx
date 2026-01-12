import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Exchange Flow Intelligence',
  description: 'Track exchange wallet flows',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
