// components/AttackFeed.tsx
'use client';

import { useRef, useEffect } from 'react';
import type { Attack } from '@/lib/api';

const riskColor = (risk: string) => {
  if (risk === 'CRITICAL') return '#ff2d2d';
  if (risk === 'HIGH')     return '#ff6b00';
  if (risk === 'MEDIUM')   return '#ffe600';
  return '#00ffe7';
};

function AttackRow({ attack, isNew }: { attack: Attack; isNew: boolean }) {
  const color = riskColor(attack.risk_level);
  const time  = new Date(attack.timestamp).toLocaleTimeString('en-GB');

  return (
    <div className={`grid gap-2 px-4 py-2 border-b text-[11px] font-mono items-center
      transition-all hover:bg-white/5 cursor-default
      ${isNew ? 'attack-new' : ''}`}
      style={{
        gridTemplateColumns: '60px 110px 90px 1fr 55px 70px 30px',
        borderColor: 'rgba(0,255,231,0.06)',
      }}
    >
      <span style={{ color, textShadow: `0 0 8px ${color}`, opacity: 0.9 }}>
        {attack.risk_level.slice(0, 4)}
      </span>
      <span className="text-cyan-400/70 tabular-nums">{time}</span>
      <span className="text-cyan-300/80 tabular-nums">{attack.source_ip}</span>
      <span className="text-cyan-100/60 truncate">{attack.attack_type}</span>
      <span className="text-cyan-500/50">:{attack.port_targeted}</span>
      <span className="text-cyan-500/50 truncate">{attack.country || '—'}</span>
      <span>{attack.is_anomaly ? <span className="text-yellow-400">⚠</span> : ''}</span>
    </div>
  );
}

export default function AttackFeed({ attacks }: { attacks: Attack[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  return (
    <div className="rounded overflow-hidden" style={{ border: '1px solid rgba(0,255,231,0.12)', background: 'rgba(0,0,0,0.4)' }}>

      {/* Header */}
      <div className="grid gap-2 px-4 py-2 text-[9px] font-mono tracking-widest"
        style={{
          gridTemplateColumns: '60px 110px 90px 1fr 55px 70px 30px',
          background: 'rgba(0,255,231,0.04)',
          borderBottom: '1px solid rgba(0,255,231,0.1)',
          color: 'rgba(0,255,231,0.35)',
        }}
      >
        <span>RISK</span>
        <span>TIME</span>
        <span>SOURCE IP</span>
        <span>ATTACK TYPE</span>
        <span>PORT</span>
        <span>COUNTRY</span>
        <span>⚠</span>
      </div>

      {/* Rows */}
      <div ref={scrollRef} className="overflow-y-auto" style={{ maxHeight: '280px' }}>
        {attacks.length === 0 ? (
          <div className="py-12 text-center font-mono text-cyan-500/30 text-sm">
            <span className="blink">awaiting incoming attacks_</span>
          </div>
        ) : (
          attacks.map((a, i) => (
            <AttackRow
              key={`${a.source_ip}-${a.timestamp}-${i}`}
              attack={a}
              isNew={i === 0}
            />
          ))
        )}
      </div>
    </div>
  );
}