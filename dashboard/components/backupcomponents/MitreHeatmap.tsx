// components/MitreHeatmap.tsx
'use client';

import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TacticData {
  tactic_id:   string;
  tactic_name: string;
  count:        number;
  techniques:  { id: string; count: number }[];
}

interface HeatmapData {
  heatmap:       TacticData[];
  total_mapped:  number;
  total_attacks: number;
}

// Heat intensity color based on count
function heatColor(count: number, max: number): string {
  if (max === 0) return 'rgba(0,255,231,0.05)';
  const intensity = count / max;
  if (intensity > 0.75) return 'rgba(255,45,45,0.7)';
  if (intensity > 0.50) return 'rgba(255,107,0,0.6)';
  if (intensity > 0.25) return 'rgba(255,230,0,0.5)';
  return 'rgba(0,255,231,0.25)';
}

function heatBorder(count: number, max: number): string {
  if (max === 0) return 'rgba(0,255,231,0.1)';
  const intensity = count / max;
  if (intensity > 0.75) return 'rgba(255,45,45,0.6)';
  if (intensity > 0.50) return 'rgba(255,107,0,0.5)';
  if (intensity > 0.25) return 'rgba(255,230,0,0.4)';
  return 'rgba(0,255,231,0.2)';
}

export default function MitreHeatmap() {
  const [data,     setData]     = useState<HeatmapData | null>(null);
  const [selected, setSelected] = useState<TacticData | null>(null);

  useEffect(() => {
    const load = () =>
      fetch(`${API}/mitre/heatmap`)
        .then(r => r.json())
        .then(setData)
        .catch(() => {});

    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  if (!data || data.heatmap.length === 0) {
    return (
      <div className="rounded p-6 flex items-center justify-center"
        style={{ border: '1px solid rgba(0,255,231,0.12)',
                 background: 'rgba(0,0,0,0.4)',
                 minHeight: 120 }}>
        <span className="font-mono text-xs blink"
          style={{ color: 'rgba(0,255,231,0.3)' }}>
          awaiting attacks to map to MITRE ATT&CK_
        </span>
      </div>
    );
  }

  const maxCount = Math.max(...data.heatmap.map(t => t.count));

  return (
    <div className="rounded overflow-hidden"
      style={{ border: '1px solid rgba(0,255,231,0.12)',
               background: 'rgba(0,0,0,0.4)' }}>

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3"
        style={{ background: 'rgba(0,255,231,0.04)',
                 borderBottom: '1px solid rgba(0,255,231,0.08)' }}>
        <div>
          <span className="font-mono text-[9px] tracking-widest"
            style={{ color: 'rgba(0,255,231,0.5)' }}>
            MITRE ATT&CK® FRAMEWORK HEATMAP
          </span>
          <span className="font-mono text-[9px] ml-4"
            style={{ color: 'rgba(0,255,231,0.25)' }}>
            {data.total_mapped} / {data.total_attacks} ATTACKS MAPPED
          </span>
        </div>
        <a href="https://attack.mitre.org" target="_blank"
          rel="noopener noreferrer"
          className="font-mono text-[9px] tracking-widest transition-opacity hover:opacity-100"
          style={{ color: 'rgba(0,255,231,0.3)' }}>
          attack.mitre.org ↗
        </a>
      </div>

      {/* Heatmap grid */}
      <div className="p-4">
        <div className="grid gap-2"
          style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))' }}>
          {data.heatmap.map((tactic) => (
            <button
              key={tactic.tactic_id}
              onClick={() =>
                setSelected(selected?.tactic_id === tactic.tactic_id
                  ? null : tactic)
              }
              className="rounded p-3 text-left transition-all duration-200
                hover:scale-[1.03] cursor-pointer"
              style={{
                background: heatColor(tactic.count, maxCount),
                border:     `1px solid ${heatBorder(tactic.count, maxCount)}`,
                boxShadow:  selected?.tactic_id === tactic.tactic_id
                  ? `0 0 16px ${heatBorder(tactic.count, maxCount)}`
                  : 'none',
              }}
            >
              <div className="font-mono text-[8px] tracking-widest mb-1"
                style={{ color: 'rgba(255,255,255,0.4)' }}>
                {tactic.tactic_id}
              </div>
              <div className="font-mono text-[10px] font-bold mb-2"
                style={{ color: 'rgba(255,255,255,0.85)' }}>
                {tactic.tactic_name}
              </div>
              <div className="font-mono text-lg font-bold"
                style={{ color: 'white',
                         textShadow: '0 0 10px rgba(255,255,255,0.3)' }}>
                {tactic.count}
              </div>
              <div className="font-mono text-[8px] mt-1"
                style={{ color: 'rgba(255,255,255,0.3)' }}>
                {tactic.techniques.length} technique
                {tactic.techniques.length !== 1 ? 's' : ''}
              </div>
            </button>
          ))}
        </div>

        {/* Detail panel — shows on click */}
        {selected && (
          <div className="mt-4 rounded p-4 sweep-in"
            style={{ background: 'rgba(0,255,231,0.04)',
                     border: '1px solid rgba(0,255,231,0.15)' }}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <span className="font-mono text-[9px] tracking-widest"
                  style={{ color: 'rgba(0,255,231,0.5)' }}>
                  {selected.tactic_id}
                </span>
                <div className="font-mono text-sm font-bold text-cyan-300 mt-0.5">
                  {selected.tactic_name}
                </div>
              </div>
              <div className="font-mono text-2xl font-bold"
                style={{ color: heatBorder(selected.count, maxCount) }}>
                {selected.count}
              </div>
            </div>

            <div className="font-mono text-[9px] tracking-widest mb-2"
              style={{ color: 'rgba(0,255,231,0.35)' }}>
              TECHNIQUES OBSERVED
            </div>
            <div className="flex flex-wrap gap-2">
              {selected.techniques.map(t => (
                <a key={t.id}
                  href={`https://attack.mitre.org/techniques/${t.id.replace('.','/')}/`}
                  target="_blank" rel="noopener noreferrer"
                  className="flex items-center gap-2 px-3 py-1.5 rounded
                    transition-all hover:scale-[1.04]"
                  style={{ background: 'rgba(0,255,231,0.08)',
                           border: '1px solid rgba(0,255,231,0.2)' }}>
                  <span className="font-mono text-[10px] text-cyan-400">
                    {t.id}
                  </span>
                  <span className="font-mono text-[10px]"
                    style={{ color: 'rgba(255,255,255,0.4)' }}>
                    ×{t.count}
                  </span>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="flex items-center gap-4 mt-4 pt-3"
          style={{ borderTop: '1px solid rgba(0,255,231,0.06)' }}>
          <span className="font-mono text-[8px] tracking-widest"
            style={{ color: 'rgba(0,255,231,0.25)' }}>FREQUENCY</span>
          {[
            { label: 'LOW',    color: 'rgba(0,255,231,0.25)' },
            { label: 'MEDIUM', color: 'rgba(255,230,0,0.5)'  },
            { label: 'HIGH',   color: 'rgba(255,107,0,0.6)'  },
            { label: 'CRITICAL',color:'rgba(255,45,45,0.7)'  },
          ].map(({ label, color }) => (
            <div key={label} className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm"
                style={{ background: color }} />
              <span className="font-mono text-[8px]"
                style={{ color: 'rgba(255,255,255,0.3)' }}>
                {label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}