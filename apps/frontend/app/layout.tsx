import type { Metadata } from 'next'
import { Outfit, Instrument_Sans, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Navigation } from '@/components/Navigation'

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
})

const instrumentSans = Instrument_Sans({
  subsets: ['latin'],
  variable: '--font-instrument',
  display: 'swap',
})

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Aureon | Planetary Procurement Substrate',
  description: 'Intelligent procurement platform for discovering, scoring, and managing government contracting opportunities across jurisdictions.',
  keywords: ['procurement', 'government contracts', 'SAM.gov', 'federal contracts', 'AI', 'opportunity scoring'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${outfit.variable} ${instrumentSans.variable} ${jetbrains.variable}`}>
      <body className="bg-cosmos-950 text-white min-h-screen font-body antialiased">
        <Providers>
          <div className="relative min-h-screen">
            {/* Background mesh gradient */}
            <div className="fixed inset-0 bg-mesh opacity-60 pointer-events-none" />
            <div className="fixed inset-0 bg-gradient-to-b from-cosmos-950 via-transparent to-cosmos-950 pointer-events-none" />
            
            {/* Content */}
            <div className="relative z-10">
              <Navigation />
              <main className="container mx-auto px-4 py-8">
                {children}
              </main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  )
}

