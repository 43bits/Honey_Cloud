'use client';

import { useRef } from 'react';
import type { Attack } from '@/lib/api';

interface ExtendedAttack extends Attack {
  mitre_technique_id?:   string;
  mitre_technique_name?: string;
  mitre_tactic?:         string;
  mitre_url?:            string;
  mitre_mapped?:         boolean;
}

const riskColor = (risk: string) => {
  if (risk === 'CRITICAL') return '#ff2d2d';
  if (risk === 'HIGH')     return '#ff6b00';
  if (risk === 'MEDIUM')   return '#ffe600';
  return '#00ffe7';
};

const riskBg = (risk: string) => {
  if (risk === 'CRITICAL') return 'rgba(255,45,45,0.08)';
  if (risk === 'HIGH')     return 'rgba(255,107,0,0.08)';
  if (risk === 'MEDIUM')   return 'rgba(255,230,0,0.05)';
  return 'transparent';
};

const GRID = '52px 90px 105px 1fr 48px 75px 85px 24px';

function AttackRow({
  attack,
  isNew,
  isSelected,
  onClick,
}: {
  attack:     ExtendedAttack;
  isNew:      boolean;
  isSelected: boolean;
  onClick:    () => void;
}) {
  const color = riskColor(attack.risk_level);
  const time  = new Date(attack.timestamp).toLocaleTimeString('en-GB');

  return (
    <div
      onClick={onClick}
      className={[
        'grid gap-2 px-3 py-2 border-b text-xs font-mono',
        'items-center transition-all cursor-pointer',
        isNew      ? 'attack-new'    : '',
        isSelected ? 'brightness-125': 'hover:bg-white/5',
      ].join(' ')}
      style={{
        gridTemplateColumns: GRID,
        borderColor: isSelected
          ? `${color}40`
          : 'rgba(0,255,231,0.06)',
        background: isSelected
          ? riskBg(attack.risk_level)
          : 'transparent',
        borderLeft: isSelected
          ? `2px solid ${color}`
          : '2px solid transparent',
      }}
    >
      {/* Risk */}
      <span style={{
        color,
        textShadow:    `0 0 8px ${color}`,
        opacity:       0.9,
        fontSize:      '10px',
        letterSpacing: '0.05em',
      }}>
        {attack.risk_level.slice(0, 4)}
      </span>

      {/* Time */}
      <span className="tabular-nums"
        style={{ color: 'rgba(0,255,231,0.5)', fontSize: '10px' }}>
        {time}
      </span>

      {/* Source IP */}
      <span className="tabular-nums font-medium"
        style={{ color: '#00ffe7', fontSize: '10px' }}>
        {attack.source_ip}
      </span>

      {/* Attack type */}
      <span className="truncate"
        style={{ color: 'rgba(200,220,255,0.7)', fontSize: '10px' }}>
        {attack.attack_type}
      </span>

      {/* Port */}
      <span style={{ color: 'rgba(0,255,231,0.35)', fontSize: '10px' }}>
        :{attack.port_targeted}
      </span>

      {/* Country */}
      <span className="truncate"
        style={{ color: 'rgba(0,255,231,0.4)', fontSize: '10px' }}>
        {attack.country || '—'}
      </span>

      {/* MITRE ID */}
      {attack.mitre_technique_id ? (
        <a
          href={attack.mitre_url ?? 'https://attack.mitre.org'}
          target="_blank"
          rel="noopener noreferrer"
          title={attack.mitre_technique_name ?? ''}
          className="truncate hover:underline"
          style={{ color: 'rgba(0,255,231,0.55)', fontSize: '10px' }}
          onClick={e => e.stopPropagation()}
        >
          {attack.mitre_technique_id}
        </a>
      ) : (
        <span style={{ color: 'rgba(0,255,231,0.2)', fontSize: '10px' }}>—</span>
      )}

      {/* Anomaly */}
      <span className="text-center">
        {attack.is_anomaly && (
          <span title="Anomaly detected"
            style={{ color: '#ffe600', fontSize: '11px' }}>⚠</span>
        )}
      </span>
    </div>
  );
}

export default function AttackFeed({
  attacks,
  selectedAttack,
  onSelectAttack,
}: {
  attacks:         Attack[];
  selectedAttack:  Attack | null;
  onSelectAttack:  (attack: Attack) => void;
}) {
  const scrollRef  = useRef<HTMLDivElement>(null);
  const extended   = attacks as ExtendedAttack[];
  const mitreCount = extended.filter(a => a.mitre_mapped).length;
  const anomCount  = extended.filter(a => a.is_anomaly).length;

  return (
    <div className="rounded overflow-hidden"
      style={{
        border:     '1px solid rgba(0,255,231,0.12)',
        background: 'rgba(0,0,0,0.4)',
      }}>

      {/* Header */}
      <div className="grid gap-2 px-3 py-2 font-mono uppercase"
        style={{
          gridTemplateColumns: GRID,
          background:   'rgba(0,255,231,0.04)',
          borderBottom: '1px solid rgba(0,255,231,0.10)',
          color:        'rgba(0,255,231,0.35)',
          fontSize:     '9px',
          letterSpacing:'0.12em',
        }}>
        <span>RISK</span>
        <span>TIME</span>
        <span>SOURCE IP</span>
        <span>ATTACK TYPE</span>
        <span>PORT</span>
        <span>COUNTRY</span>
        <span>MITRE</span>
        <span>⚠</span>
      </div>

      {/* Rows */}
      <div ref={scrollRef} className="overflow-y-auto"
        style={{ maxHeight: '380px' }}>
        {extended.length === 0 ? (
          <div className="py-14 text-center font-mono"
            style={{ color: 'rgba(0,255,231,0.2)', fontSize: '13px' }}>
            <span className="blink">awaiting incoming attacks_</span>
          </div>
        ) : (
          extended.map((a, i) => (
            <AttackRow
              key={a.source_ip + '-' + a.timestamp + '-' + i}
              attack={a}
              isNew={i === 0}
              isSelected={
                selectedAttack?.source_ip === a.source_ip &&
                selectedAttack?.timestamp === a.timestamp
              }
              onClick={() => onSelectAttack(a)}
            />
          ))
        )}
      </div>

      {/* Footer */}
      {extended.length > 0 && (
        <div className="px-3 py-2 font-mono"
          style={{
            borderTop:     '1px solid rgba(0,255,231,0.06)',
            color:         'rgba(0,255,231,0.2)',
            fontSize:      '9px',
            letterSpacing: '0.1em',
          }}>
          {extended.length} EVENTS
          {' · '}{mitreCount} MITRE MAPPED
          {' · '}{anomCount} ANOMALIES
          {' · '}
          <span style={{ color: 'rgba(0,255,231,0.35)' }}>
            CLICK ROW TO INVESTIGATE →
          </span>
        </div>
      )}
    </div>
  );
}