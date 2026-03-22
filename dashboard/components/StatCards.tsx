'use client';

interface Props {
  byRisk: { LOW: number; MEDIUM: number; HIGH: number; CRITICAL: number };
  total:  number;
}

const LEVELS = [
  { key: 'CRITICAL' as const, color: '#ff4444', label: 'Critical' },
  { key: 'HIGH'     as const, color: '#f5a623', label: 'High'     },
  { key: 'MEDIUM'   as const, color: '#f0c040', label: 'Medium'   },
  { key: 'LOW'      as const, color: '#3dd68c', label: 'Low'      },
];

export default function StatCards({ byRisk, total }: Props) {
  return (
    <div style={{
      display:             'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap:                 '8px',
      padding:             '12px 16px',
      background:          '#111111',
      borderBottom:        '1px solid rgba(255,255,255,0.07)',
      flexShrink:          0,
    }}>
      {LEVELS.map(({ key, color, label }) => {
        const count = byRisk[key] || 0;
        const pct   = total > 0 ? Math.round((count / total) * 100) : 0;

        return (
          <div key={key} style={{
            background:   '#1a1a1a',
            borderRadius: '10px',
            padding:      '14px 16px',
            border:       '1px solid rgba(255,255,255,0.06)',
            display:      'flex',
            alignItems:   'center',
            gap:          '14px',
          }}>
            {/* Color dot */}
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: color, flexShrink: 0 }} />

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '7px' }}>
                <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.45)', fontWeight: 400 }}>{label}</span>
                <span style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff', fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em' }}>{count}</span>
              </div>
              {/* Bar — white filled like Transcope */}
              <div style={{ height: '3px', background: 'rgba(255,255,255,0.08)', borderRadius: '2px' }}>
                <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: '2px', transition: 'width 0.6s ease', opacity: 0.8 }} />
              </div>
              <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.2)', marginTop: '4px' }}>{pct}% of {total}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
