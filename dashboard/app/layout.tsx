// app/layout.tsx
import type { Metadata } from 'next';
import { JetBrains_Mono } from 'next/font/google';
import './globals.css';
// app/layout.tsx — add this import
import 'leaflet/dist/leaflet.css';

const mono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
});

export const metadata: Metadata = {
  title: 'HoneyCloud Sentinel',
  description: 'AI-Powered Honeypot Threat Detection',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${mono.variable} font-mono bg-[#080c12] text-slate-100 antialiased`}>
        {children}
      </body>
    </html>
  );
}