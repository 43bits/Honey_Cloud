'use client';

import { useEffect, useState } from 'react';
import ReportButton from './ReportButton';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Props {
  total:         number;
  isLive:        boolean;
  criticalCount: number;
}

export default function Header({ total, isLive, criticalCount }: Props) {
  const [time,      setTime]      = useState('');
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [n8nStatus, setN8nStatus] = useState<any>(null);

  useEffect(() => {
    const tick = () => setTime(new Date().toUTCString().slice(17, 25) + ' UTC');
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const load = () =>
      fetch(`${API}/n8n/status`).then(r => r.json()).then(setN8nStatus).catch(() => {});
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  return (
    <header style={{
      height:       '56px',
      display:      'flex',
      alignItems:   'center',
      padding:      '0 24px',
      background:   '#111111',
      borderBottom: '1px solid rgba(255,255,255,0.07)',
      flexShrink:   0,
      gap:          '0',
    }}>

      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginRight: '32px', flexShrink: 0 }}>
        <div style={{
          width: '28px', height: '28px', borderRadius: '8px',
          background: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 2L14 5.5V10.5L8 14L2 10.5V5.5L8 2Z" fill="#111111" stroke="#111111" strokeWidth="0.5"/>
          </svg>
        </div>
        <span style={{ fontSize: '15px', fontWeight: 700, color: '#f0f0f0', letterSpacing: '-0.02em' }}>
          HoneyCloud<span style={{ color: 'rgba(255,255,255,0.35)', fontWeight: 400 }}>.</span>
        </span>
      </div>

      {/* Nav links — Transcope style */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '4px', flex: 1 }}>
        {[
          { label: 'Overview', active: true  },
          { label: 'Attacks',  active: false },
          { label: 'Intel',    active: false },
          { label: 'MITRE',    active: false },
          { label: 'Reports',  active: false },
        ].map(({ label, active }) => (
          <button key={label} style={{
            padding:      '5px 14px',
            borderRadius: '6px',
            background:   active ? 'rgba(255,255,255,0.1)' : 'transparent',
            border:       'none',
            color:        active ? '#ffffff' : 'rgba(255,255,255,0.4)',
            fontSize:     '13px',
            fontWeight:   active ? 500 : 400,
            cursor:       'pointer',
            fontFamily:   'Inter, sans-serif',
            transition:   'all 0.15s',
          }}>
            {label}
          </button>
        ))}
      </nav>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>

        {/* Stats pills */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          padding: '4px 12px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '8px',
          border: '1px solid rgba(255,255,255,0.07)',
        }}>
          <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', fontWeight: 400 }}>Total</span>
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#ffffff' }}>{total.toLocaleString()}</span>
          {criticalCount > 0 && (
            <>
              <div style={{ width: '1px', height: '12px', background: 'rgba(255,255,255,0.12)' }} />
              <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>Critical</span>
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#ff4444' }}>{criticalCount}</span>
            </>
          )}
        </div>

        {/* n8n status */}
        {n8nStatus && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            padding: '4px 10px',
            background: n8nStatus.n8n_running ? 'rgba(61,214,140,0.08)' : 'rgba(255,68,68,0.08)',
            border: `1px solid ${n8nStatus.n8n_running ? 'rgba(61,214,140,0.2)' : 'rgba(255,68,68,0.2)'}`,
            borderRadius: '8px',
          }}>
            <div style={{
              width: '5px', height: '5px', borderRadius: '50%',
              background: n8nStatus.n8n_running ? '#3dd68c' : '#ff4444',
            }} />
            <span style={{ fontSize: '11px', fontWeight: 500, color: n8nStatus.n8n_running ? '#3dd68c' : '#ff4444' }}>
              n8n {n8nStatus.n8n_running ? 'Active' : 'Offline'}
              {n8nStatus.n8n_processed > 0 ? ` · ${n8nStatus.n8n_processed}` : ''}
            </span>
          </div>
        )}

        {/* Live pill */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          padding: '4px 10px',
          background: isLive ? 'rgba(255,255,255,0.05)' : 'transparent',
          border: `1px solid ${isLive ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.06)'}`,
          borderRadius: '8px',
        }}>
          <div style={{
            width: '6px', height: '6px', borderRadius: '50%',
            background: isLive ? '#3dd68c' : 'rgba(255,255,255,0.2)',
          }} />
          <span style={{ fontSize: '11px', color: isLive ? '#f0f0f0' : 'rgba(255,255,255,0.3)', fontWeight: 500 }}>
            {isLive ? 'Live' : 'Connecting'}
          </span>
        </div>

        {/* Time */}
        <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.25)', fontFamily: 'var(--mono)', whiteSpace: 'nowrap' }}>
          {time}
        </span>

        {/* Divider */}
        <div style={{ width: '1px', height: '20px', background: 'rgba(255,255,255,0.08)' }} />

        <ReportButton hasData={total > 0} />
      </div>
    </header>
  );
}
