'use client';

import { useRef } from 'react';
import type { Attack } from '@/lib/api';

interface ExtendedAttack extends Attack {
  mitre_technique_id?: string;
  mitre_technique_name?: string;
  mitre_tactic?: string;
  mitre_url?: string;
  mitre_mapped?: boolean;
}

const riskColor = (risk: string) => {
  if (risk === 'CRITICAL') return '#ff2d2d';
  if (risk === 'HIGH') return '#ff6b00';
  if (risk === 'MEDIUM') return '#ffe600';
  return '#00ffe7';
};

const GRID = '55px 100px 110px 1fr 50px 80px 90px 28px';

function AttackRow({
  attack,
  isNew,
}: {
  attack: ExtendedAttack;
  isNew: boolean;
}) {
  const color = riskColor(attack.risk_level);
  const time = new Date(attack.timestamp).toLocaleTimeString('en-GB');

  return (
    <div
      className={[
        'grid gap-2 px-4 py-2 border-b text-xs font-mono',
        'items-center transition-all hover:bg-white/5 cursor-default',
        isNew ? 'attack-new' : '',
      ].join(' ')}
      style={{
        gridTemplateColumns: GRID,
        borderColor: 'rgba(0,255,231,0.06)',
      }}
    >
      {/* 1 — Risk */}
      <span
        style={{
          color,
          textShadow: '0 0 8px ' + color,
          opacity: 0.9,
          fontSize: '10px',
          letterSpacing: '0.05em',
        }}
      >
        {attack.risk_level.slice(0, 4)}
      </span>

      {/* 2 — Time */}
      <span
        className="tabular-nums"
        style={{ color: 'rgba(0,255,231,0.5)', fontSize: '11px' }}
      >
        {time}
      </span>

      {/* 3 — Source IP */}
      <span
        className="tabular-nums font-medium"
        style={{ color: '#00ffe7', fontSize: '11px' }}
      >
        {attack.source_ip}
      </span>

      {/* 4 — Attack type */}
      <span
        className="truncate"
        style={{ color: 'rgba(200,220,255,0.7)', fontSize: '11px' }}
      >
        {attack.attack_type}
      </span>

      {/* 5 — Port */}
      <span style={{ color: 'rgba(0,255,231,0.35)', fontSize: '11px' }}>
        :{attack.port_targeted}
      </span>

      {/* 6 — Country */}
      <span
        className="truncate"
        style={{ color: 'rgba(0,255,231,0.4)', fontSize: '11px' }}
      >
        {attack.country || '—'}
      </span>

      {/* 7 — MITRE ID */}
      {attack.mitre_technique_id ? (
        <a
          href={attack.mitre_url ?? 'https://attack.mitre.org'}
          target="_blank"
          rel="noopener noreferrer"
          title={attack.mitre_technique_name ?? ''}
          className="truncate hover:underline"
          style={{ color: 'rgba(0,255,231,0.55)', fontSize: '11px' }}
          onClick={(e) => e.stopPropagation()}
        >
          {attack.mitre_technique_id}
        </a>
      ) : (
        <span style={{ color: 'rgba(0,255,231,0.2)', fontSize: '11px' }}>
          —
        </span>
      )}

      {/* 8 — Anomaly */}
      <span className="text-center">
        {attack.is_anomaly && (
          <span
            title="Anomaly detected"
            style={{ color: '#ffe600', fontSize: '11px' }}
          >
            ⚠
          </span>
        )}
      </span>
    </div>
  );
}

export default function AttackFeed({
  attacks,
}: {
  attacks: Attack[];
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const extended = attacks as ExtendedAttack[];

  const mitreCount = extended.filter((a) => a.mitre_mapped).length;
  const anomalyCount = extended.filter((a) => a.is_anomaly).length;

  return (
    <div
      className="rounded overflow-hidden"
      style={{
        border: '1px solid rgba(0,255,231,0.12)',
        background: 'rgba(0,0,0,0.4)',
      }}
    >
      {/* Column headers */}
      <div
        className="grid gap-2 px-4 py-2 font-mono uppercase"
        style={{
          gridTemplateColumns: GRID,
          background: 'rgba(0,255,231,0.04)',
          borderBottom: '1px solid rgba(0,255,231,0.10)',
          color: 'rgba(0,255,231,0.35)',
          fontSize: '9px',
          letterSpacing: '0.15em',
        }}
      >
        <span>RISK</span>
        <span>TIME</span>
        <span>SOURCE IP</span>
        <span>ATTACK TYPE</span>
        <span>PORT</span>
        <span>COUNTRY</span>
        <span>MITRE ID</span>
        <span>⚠</span>
      </div>

      {/* Rows */}
      <div
        ref={scrollRef}
        className="overflow-y-auto"
        style={{ maxHeight: '300px' }}
      >
        {extended.length === 0 ? (
          <div
            className="py-14 text-center font-mono"
            style={{ color: 'rgba(0,255,231,0.2)', fontSize: '13px' }}
          >
            <span className="blink">awaiting incoming attacks_</span>
          </div>
        ) : (
          extended.map((a, i) => (
            <AttackRow
              key={a.source_ip + '-' + a.timestamp + '-' + i}
              attack={a}
              isNew={i === 0}
            />
          ))
        )}
      </div>

      {/* Footer */}
      {extended.length > 0 && (
        <div
          className="px-4 py-2 font-mono"
          style={{
            borderTop: '1px solid rgba(0,255,231,0.06)',
            color: 'rgba(0,255,231,0.2)',
            fontSize: '9px',
            letterSpacing: '0.12em',
          }}
        >
          {'SHOWING ' + extended.length + ' EVENTS'}
          {' · '}
          {mitreCount + ' MITRE MAPPED'}
          {' · '}
          {anomalyCount + ' ANOMALIES'}
        </div>
      )}
    </div>
  );
}