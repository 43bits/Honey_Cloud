'use client';

import { useState, useRef } from 'react';

interface Props {
  topAttackTypes: { type: string; count: number }[];
  topPorts:       { port: string; count: number }[];
  topCountries:   { country: string; count: number }[];
}

const RISK_COLORS = ['#ff4444', '#f5a623', '#f0c040', '#3dd68c', '#60a5fa'];

function InfoPopover({
  title,
  items,
  keyLabel,
  valueLabel,
}: {
  title:      string;
  items:      { label: string; count: number }[];
  keyLabel:   string;
  valueLabel: string;
}) {
  const max = Math.max(...items.map(i => i.count), 1);

  return (
    <div style={{
      position:     'absolute',
      bottom:       'calc(100% + 10px)',
      left:         '50%',
      transform:    'translateX(-50%)',
      zIndex:       200,
      width:        '220px',
      background:   '#1a1a1a',
      border:       '1px solid rgba(255,255,255,0.12)',
      borderRadius: '10px',
      boxShadow:    '0 16px 40px rgba(0,0,0,0.6)',
      overflow:     'hidden',
      pointerEvents:'none',
      animation:    'fadeSlideIn 0.15s ease-out',
    }}>
      {/* Arrow */}
      <div style={{
        position:    'absolute',
        bottom:      '-5px',
        left:        '50%',
        transform:   'translateX(-50%) rotate(45deg)',
        width:       '9px',
        height:      '9px',
        background:  '#1a1a1a',
        border:      '1px solid rgba(255,255,255,0.12)',
        borderTop:   'none',
        borderLeft:  'none',
      }} />

      <div style={{ padding: '12px 14px 4px' }}>
        <div style={{ fontSize: '11px', fontWeight: 600, color: '#ffffff', marginBottom: '10px' }}>{title}</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'auto auto', gap: '0 8px', marginBottom: '4px' }}>
          <span style={{ fontSize: '9px', color: 'rgba(255,255,255,0.3)', letterSpacing: '0.08em' }}>{keyLabel.toUpperCase()}</span>
          <span style={{ fontSize: '9px', color: 'rgba(255,255,255,0.3)', letterSpacing: '0.08em', textAlign: 'right' }}>{valueLabel.toUpperCase()}</span>
        </div>
      </div>

      <div style={{ padding: '0 14px 12px' }}>
        {items.slice(0, 6).map((item, i) => {
          const pct = Math.round((item.count / max) * 100);
          return (
            <div key={item.label} style={{ marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '3px' }}>
                <span style={{
                  fontSize:     '11px',
                  color:        'rgba(255,255,255,0.65)',
                  overflow:     'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace:   'nowrap',
                  maxWidth:     '140px',
                }}>
                  {item.label}
                </span>
                <span style={{ fontSize: '11px', fontWeight: 600, color: RISK_COLORS[i % RISK_COLORS.length], flexShrink: 0 }}>
                  {item.count}
                </span>
              </div>
              <div style={{ height: '3px', background: 'rgba(255,255,255,0.07)', borderRadius: '2px', overflow: 'hidden' }}>
                <div style={{
                  height:       '100%',
                  width:        `${pct}%`,
                  background:   RISK_COLORS[i % RISK_COLORS.length],
                  borderRadius: '2px',
                  opacity:      0.75,
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function InfoButton({
  icon,
  label,
  title,
  items,
  keyLabel,
  valueLabel,
  disabled,
}: {
  icon:       string;
  label:      string;
  title:      string;
  items:      { label: string; count: number }[];
  keyLabel:   string;
  valueLabel: string;
  disabled:   boolean;
}) {
  const [hover, setHover] = useState(false);

  return (
    <div
      style={{ position: 'relative', display: 'inline-flex' }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      <button style={{
        display:      'flex',
        alignItems:   'center',
        gap:          '5px',
        padding:      '5px 10px',
        borderRadius: '7px',
        background:   hover && !disabled ? 'rgba(255,255,255,0.07)' : 'rgba(255,255,255,0.04)',
        border:       '1px solid rgba(255,255,255,0.1)',
        color:        disabled ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.55)',
        fontSize:     '11px',
        fontWeight:   500,
        cursor:       disabled ? 'default' : 'pointer',
        fontFamily:   'Inter, sans-serif',
        transition:   'all 0.15s',
        whiteSpace:   'nowrap',
      }}>
        <span style={{ fontSize: '13px' }}>{icon}</span>
        {label}
        <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.25)', marginLeft: '1px' }}>ℹ</span>
      </button>

      {hover && !disabled && items.length > 0 && (
        <InfoPopover
          title={title}
          items={items}
          keyLabel={keyLabel}
          valueLabel={valueLabel}
        />
      )}
    </div>
  );
}

export default function Charts({ topAttackTypes, topCountries }: Props) {
  const attackItems  = topAttackTypes.map(t => ({
    label: t.type.replace(' Attack','').replace(' Brute Force',' BF').replace(' Exploit',''),
    count: t.count,
  }));

  const countryItems = topCountries.map(c => ({
    label: c.country,
    count: c.count,
  }));

  return (
    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
      <InfoButton
        icon="⚔️"
        label="Attack Types"
        title="Attack Distribution"
        items={attackItems}
        keyLabel="Type"
        valueLabel="Count"
        disabled={attackItems.length === 0}
      />
      <InfoButton
        icon="🌍"
        label="Source Nations"
        title="Top Source Nations"
        items={countryItems}
        keyLabel="Country"
        valueLabel="Count"
        disabled={countryItems.length === 0}
      />
    </div>
  );
}
