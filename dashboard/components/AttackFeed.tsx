'use client';

import { useRef } from 'react';
import type { Attack } from '@/lib/api';
import Charts from './Charts';

interface ExtendedAttack extends Attack {
  mitre_technique_id?:   string;
  mitre_technique_name?: string;
  mitre_tactic?:         string;
  mitre_url?:            string;
  mitre_mapped?:         boolean;
}

const RISK_COLOR: Record<string, string> = {
  CRITICAL: '#ff4444',
  HIGH:     '#f5a623',
  MEDIUM:   '#f0c040',
  LOW:      '#3dd68c',
};

function StatusPill({ risk }: { risk: string }) {
  const color  = RISK_COLOR[risk] || '#3dd68c';
  const labels: Record<string, string> = {
    CRITICAL: 'Critical', HIGH: 'High', MEDIUM: 'Medium', LOW: 'Low',
  };
  return (
    <span style={{
      display:      'inline-flex',
      alignItems:   'center',
      gap:          '4px',
      padding:      '2px 8px',
      borderRadius: '5px',
      background:   `${color}14`,
      border:       `1px solid ${color}28`,
      fontSize:     '10px',
      fontWeight:   500,
      color,
      whiteSpace:   'nowrap',
    }}>
      <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: color, display: 'inline-block', flexShrink: 0 }} />
      {labels[risk] || risk}
    </span>
  );
}

function Row({
  attack, isSelected, onClick,
}: {
  attack: ExtendedAttack; isSelected: boolean; onClick: () => void;
}) {
  const time = attack.timestamp
    ? new Date(attack.timestamp).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
    : '--:--';

  return (
    <div
      onClick={onClick}
      style={{
        display:             'grid',
        gridTemplateColumns: '124px 1fr 92px 62px 76px',
        gap:                 '0',
        padding:             '10px 18px',
        borderBottom:        '1px solid rgba(255,255,255,0.04)',
        alignItems:          'center',
        cursor:              'pointer',
        background:          isSelected ? 'rgba(255,255,255,0.04)' : 'transparent',
        borderLeft:          isSelected ? '2px solid rgba(255,255,255,0.25)' : '2px solid transparent',
        transition:          'background 0.1s',
      }}
      onMouseEnter={e => { if (!isSelected) (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.02)'; }}
      onMouseLeave={e => { if (!isSelected) (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
    >
      {/* IP */}
      <div>
        <div style={{ fontSize: '11px', fontWeight: 600, color: '#ffffff', fontFamily: 'var(--mono)', letterSpacing: '-0.01em' }}>
          {attack.source_ip}
        </div>
        <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.25)', marginTop: '1px', fontFamily: 'var(--mono)' }}>
          :{attack.port_targeted}
        </div>
      </div>

      {/* Type + Country */}
      <div>
        <div style={{ fontSize: '11px', fontWeight: 500, color: 'rgba(255,255,255,0.8)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', paddingRight: '8px' }}>
          {attack.attack_type}
        </div>
        <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', marginTop: '1px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', paddingRight: '8px' }}>
          {attack.country || '—'}
        </div>
      </div>

      {/* MITRE */}
      <div>
        {attack.mitre_technique_id ? (
          <a
            href={attack.mitre_url || 'https://attack.mitre.org'}
            target="_blank"
            rel="noopener noreferrer"
            onClick={e => e.stopPropagation()}
            style={{
              fontSize:       '10px',
              color:          'rgba(255,255,255,0.35)',
              textDecoration: 'none',
              fontFamily:     'var(--mono)',
              display:        'block',
            }}
          >
            {attack.mitre_technique_id}
          </a>
        ) : (
          <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.12)' }}>—</span>
        )}
        {attack.is_anomaly && (
          <div style={{ fontSize: '9px', color: '#f0c040', marginTop: '1px' }}>⚠ anomaly</div>
        )}
      </div>

      {/* Time */}
      <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.25)', fontFamily: 'var(--mono)' }}>
        {time}
      </div>

      {/* Risk */}
      <div>
        <StatusPill risk={attack.risk_level} />
      </div>
    </div>
  );
}

export default function AttackFeed({
  attacks,
  selectedAttack,
  onSelectAttack,
  topAttackTypes,
  topCountries,
}: {
  attacks:        Attack[];
  selectedAttack: Attack | null;
  onSelectAttack: (a: Attack) => void;
  topAttackTypes?: { type: string; count: number }[];
  topCountries?:   { country: string; count: number }[];
}) {
  const scrollRef   = useRef<HTMLDivElement>(null);
  const extended    = attacks as ExtendedAttack[];
  const mitreMapped = extended.filter(a => a.mitre_mapped).length;
  const anomalies   = extended.filter(a => a.is_anomaly).length;

  return (
    <div style={{
      display:       'flex',
      flexDirection: 'column',
      background:    '#1a1a1a',
      borderRadius:  '12px',
      border:        '1px solid rgba(255,255,255,0.07)',
      height:        '100%',
      overflow:      'hidden',
    }}>

      {/* Header */}
      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        padding:        '14px 18px 10px',
        flexShrink:     0,
        borderBottom:   '1px solid rgba(255,255,255,0.06)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#ffffff' }}>Attack Feed</span>
          {extended.length > 0 && (
            <span style={{
              fontSize:     '10px',
              fontWeight:   500,
              padding:      '2px 7px',
              borderRadius: '5px',
              background:   'rgba(255,68,68,0.1)',
              border:       '1px solid rgba(255,68,68,0.2)',
              color:        '#ff4444',
            }}>
              {extended.length}
            </span>
          )}
        </div>

        {/* Filter tabs */}
        <div style={{ display: 'flex', gap: '4px' }}>
          {['All', 'Critical', 'High'].map((f, i) => (
            <button key={f} style={{
              padding:      '3px 10px',
              borderRadius: '6px',
              background:   i === 0 ? 'rgba(255,255,255,0.08)' : 'transparent',
              border:       `1px solid ${i === 0 ? 'rgba(255,255,255,0.14)' : 'rgba(255,255,255,0.06)'}`,
              color:        i === 0 ? '#ffffff' : 'rgba(255,255,255,0.35)',
              fontSize:     '11px',
              fontWeight:   i === 0 ? 500 : 400,
              cursor:       'pointer',
              fontFamily:   'Inter, sans-serif',
            }}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Column headers */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: '124px 1fr 92px 62px 76px',
        padding:             '7px 18px',
        borderBottom:        '1px solid rgba(255,255,255,0.05)',
        flexShrink:          0,
        background:          'rgba(255,255,255,0.015)',
      }}>
        {['Source IP', 'Attack · Country', 'MITRE', 'Time', 'Risk'].map(h => (
          <div key={h} style={{ fontSize: '10px', color: 'rgba(255,255,255,0.25)', fontWeight: 500, letterSpacing: '0.03em' }}>{h}</div>
        ))}
      </div>

      {/* Rows — takes all remaining space */}
      <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
        {extended.length === 0 ? (
          <div style={{ padding: '48px 18px', textAlign: 'center', color: 'rgba(255,255,255,0.15)', fontSize: '12px', fontFamily: 'Inter, sans-serif' }}>
            Awaiting attacks...
          </div>
        ) : (
          extended.map((a, i) => (
            <Row
              key={`${a.source_ip}-${a.timestamp}-${i}`}
              attack={a}
              isSelected={selectedAttack?.source_ip === a.source_ip && selectedAttack?.timestamp === a.timestamp}
              onClick={() => onSelectAttack(a)}
            />
          ))
        )}
      </div>

      {/* Footer — stats + chart info buttons */}
      <div style={{
        padding:     '10px 18px',
        borderTop:   '1px solid rgba(255,255,255,0.05)',
        display:     'flex',
        alignItems:  'center',
        gap:         '12px',
        flexShrink:  0,
        flexWrap:    'wrap',
      }}>
        {/* Quick stats */}
        <div style={{ display: 'flex', gap: '12px', flex: 1 }}>
          {[
            { label: 'events',    value: extended.length },
            { label: 'mapped',    value: mitreMapped     },
            { label: 'anomalies', value: anomalies       },
          ].map(({ label, value }) => (
            <div key={label} style={{ display: 'flex', gap: '4px', alignItems: 'baseline' }}>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#ffffff' }}>{value}</span>
              <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)' }}>{label}</span>
            </div>
          ))}
        </div>

        {/* Info buttons (Charts component) */}
        <Charts
          topAttackTypes={topAttackTypes || []}
          topPorts={[]}
          topCountries={topCountries || []}
        />
      </div>
    </div>
  );
}
