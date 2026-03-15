// components/Header.tsx
'use client';

import { useEffect, useState } from 'react';

interface Props {
  total: number;
  isLive: boolean;
  criticalCount: number;
}

export default function Header({ total, isLive, criticalCount }: Props) {
  const [time, setTime] = useState('');

  useEffect(() => {
    const tick = () => setTime(new Date().toUTCString().slice(17, 25) + ' UTC');
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <header className="relative z-10 flex items-center justify-between px-5 py-3 border-b border-cyan-500/20 bg-black/40 backdrop-blur-sm">
      {/* Left — branding */}
      <div className="flex items-center gap-4">
        <div className="relative">
          <div className="w-8 h-8 border border-cyan-500/60 rotate-45 flex items-center justify-center">
            <div className="w-3 h-3 bg-cyan-400 rotate-[-45deg] live-pulse" />
          </div>
        </div>
        <div>
          <div className="text-sm font-bold tracking-[0.3em] text-cyan-300"
               style={{ fontFamily: "'Share Tech Mono', monospace" }}>
            HONEYCLOUD SENTINEL
          </div>
          <div className="text-[9px] tracking-[0.2em] text-cyan-500/50"
               style={{ fontFamily: "'Share Tech Mono', monospace" }}>
            AI-DRIVEN ADAPTIVE HONEYPOT INTELLIGENCE
          </div>
        </div>
      </div>

      {/* Center — stats */}
      <div className="hidden md:flex items-center gap-8">
        <div className="text-center">
          <div className="text-[9px] tracking-widest text-cyan-500/50 font-mono">TOTAL THREATS</div>
          <div className="text-xl font-bold text-cyan-300 font-mono tabular-nums">{total.toLocaleString()}</div>
        </div>
        {criticalCount > 0 && (
          <div className="text-center">
            <div className="text-[9px] tracking-widest text-red-500/70 font-mono">CRITICAL</div>
            <div className="text-xl font-bold text-red-400 font-mono tabular-nums blink">{criticalCount}</div>
          </div>
        )}
      </div>

      {/* Right — status */}
      <div className="flex items-center gap-4">
        <div className="text-[10px] font-mono text-cyan-500/50">{time}</div>
        <div className={`flex items-center gap-2 px-3 py-1.5 border rounded font-mono text-[10px] tracking-widest
          ${isLive
            ? 'border-green-500/40 text-green-400 bg-green-500/5'
            : 'border-cyan-500/20 text-cyan-500/40'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${isLive ? 'bg-green-400 live-pulse' : 'bg-cyan-500/30'}`} />
          {isLive ? 'LIVE' : 'CONNECTING'}
        </div>
      </div>
    </header>
  );
}