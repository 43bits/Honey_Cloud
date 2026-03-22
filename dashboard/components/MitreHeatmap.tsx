'use client';

import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TacticData { tactic_id: string; tactic_name: string; count: number; techniques: { id: string; count: number }[]; }
interface HeatmapData { heatmap: TacticData[]; total_mapped: number; total_attacks: number; }

function cellStyle(count: number, max: number) {
  if (!count) return { bg: 'rgba(255,255,255,0.03)', text: 'rgba(255,255,255,0.2)', border: 'rgba(255,255,255,0.06)' };
  const i = count / max;
  if (i > 0.75) return { bg: 'rgba(255,68,68,0.12)',   text: '#ff4444', border: 'rgba(255,68,68,0.2)'   };
  if (i > 0.50) return { bg: 'rgba(245,166,35,0.1)',   text: '#f5a623', border: 'rgba(245,166,35,0.2)'  };
  if (i > 0.25) return { bg: 'rgba(255,255,255,0.07)', text: '#f0f0f0', border: 'rgba(255,255,255,0.12)' };
  return              { bg: 'rgba(255,255,255,0.04)', text: 'rgba(255,255,255,0.4)', border: 'rgba(255,255,255,0.07)' };
}

export default function MitreHeatmap() {
  const [data,     setData]     = useState<HeatmapData | null>(null);
  const [selected, setSelected] = useState<TacticData | null>(null);

  useEffect(() => {
    const load = () => fetch(`${API}/mitre/heatmap`).then(r => r.json()).then(setData).catch(() => {});
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  if (!data || !data.heatmap.length) {
    return (
      <div style={{ background: '#1a1a1a', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.07)', padding: '24px', textAlign: 'center', color: 'rgba(255,255,255,0.2)', fontSize: '12px' }}>
        Awaiting attacks to map to MITRE ATT&CK...
      </div>
    );
  }

  const maxCount = Math.max(...data.heatmap.map(t => t.count));

  return (
    <div style={{ background: '#1a1a1a', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.07)', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px 12px' }}>
        <div>
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#ffffff' }}>MITRE ATT&CK®</span>
          <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginLeft: '10px' }}>{data.total_mapped}/{data.total_attacks} mapped</span>
        </div>
        <a href="https://attack.mitre.org" target="_blank" rel="noopener noreferrer" style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', textDecoration: 'none' }}>attack.mitre.org ↗</a>
      </div>

      {/* Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '6px', padding: '0 16px 16px' }}>
        {data.heatmap.map(tactic => {
          const s   = cellStyle(tactic.count, maxCount);
          const sel = selected?.tactic_id === tactic.tactic_id;
          return (
            <button key={tactic.tactic_id}
              onClick={() => setSelected(sel ? null : tactic)}
              style={{
                background:   s.bg,
                border:       `1px solid ${sel ? s.text : s.border}`,
                borderRadius: '8px',
                padding:      '10px 12px',
                textAlign:    'left',
                cursor:       'pointer',
                transition:   'all 0.15s',
                outline:      'none',
              }}
            >
              <div style={{ fontSize: '9px', color: 'rgba(255,255,255,0.3)', marginBottom: '4px', fontFamily: 'var(--mono)' }}>{tactic.tactic_id}</div>
              <div style={{ fontSize: '22px', fontWeight: 700, color: s.text, lineHeight: 1, fontFamily: 'Inter, sans-serif' }}>{tactic.count}</div>
              <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.35)', marginTop: '3px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{tactic.tactic_name}</div>
            </button>
          );
        })}
      </div>

      {/* Detail */}
      {selected && (
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)', padding: '14px 20px', background: 'rgba(255,255,255,0.02)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '10px' }}>
            <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', fontFamily: 'var(--mono)' }}>{selected.tactic_id}</span>
            <span style={{ fontSize: '13px', fontWeight: 600, color: '#ffffff' }}>{selected.tactic_name}</span>
            <span style={{ marginLeft: 'auto', fontSize: '20px', fontWeight: 700, color: cellStyle(selected.count, maxCount).text }}>{selected.count}</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {selected.techniques.map(t => (
              <a key={t.id} href={`https://attack.mitre.org/techniques/${t.id.replace('.','/') }/`} target="_blank" rel="noopener noreferrer"
                style={{ fontSize: '11px', padding: '3px 10px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.6)', textDecoration: 'none', fontFamily: 'var(--mono)', display: 'flex', gap: '6px' }}>
                <span>{t.id}</span><span style={{ color: 'rgba(255,255,255,0.25)' }}>×{t.count}</span>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Legend */}
      <div style={{ display: 'flex', gap: '16px', padding: '10px 20px', borderTop: '1px solid rgba(255,255,255,0.05)', alignItems: 'center' }}>
        <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.2)' }}>Intensity</span>
        {[{l:'Low',c:'rgba(255,255,255,0.4)'},{l:'Medium',c:'#f0f0f0'},{l:'High',c:'#f5a623'},{l:'Critical',c:'#ff4444'}].map(({l,c}) => (
          <div key={l} style={{ display:'flex', alignItems:'center', gap:'5px' }}>
            <div style={{ width:'8px', height:'8px', borderRadius:'2px', background:c, opacity:0.7 }} />
            <span style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)' }}>{l}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
