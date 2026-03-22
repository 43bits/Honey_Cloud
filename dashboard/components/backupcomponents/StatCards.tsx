// components/StatCards.tsx
'use client';

interface Props {
  byRisk: { LOW: number; MEDIUM: number; HIGH: number; CRITICAL: number };
  total: number;
}

const levels = [
  { key: 'CRITICAL' as const, color: '#ff2d2d', bg: 'rgba(255,45,45,0.05)',   border: 'rgba(255,45,45,0.25)'  },
  { key: 'HIGH'     as const, color: '#ff6b00', bg: 'rgba(255,107,0,0.05)',   border: 'rgba(255,107,0,0.25)'  },
  { key: 'MEDIUM'   as const, color: '#ffe600', bg: 'rgba(255,230,0,0.05)',   border: 'rgba(255,230,0,0.25)'  },
  { key: 'LOW'      as const, color: '#00ffe7', bg: 'rgba(0,255,231,0.05)',   border: 'rgba(0,255,231,0.25)'  },
];

export default function StatCards({ byRisk, total }: Props) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
      {levels.map(({ key, color, bg, border }) => {
        const count = byRisk[key] || 0;
        const pct   = total > 0 ? Math.round((count / total) * 100) : 0;
        return (
          <div key={key} className="relative p-4 rounded overflow-hidden"
            style={{ background: bg, border: `1px solid ${border}` }}>

            {/* Corner decoration */}
            <div className="absolute top-0 right-0 w-6 h-6 border-t border-r"
              style={{ borderColor: color, opacity: 0.4 }} />
            <div className="absolute bottom-0 left-0 w-6 h-6 border-b border-l"
              style={{ borderColor: color, opacity: 0.4 }} />

            <div className="text-[9px] tracking-[0.25em] mb-2 font-mono"
              style={{ color, opacity: 0.7 }}>{key}</div>

            <div className="text-3xl font-bold tabular-nums font-mono"
              style={{ color, textShadow: `0 0 20px ${color}` }}>
              {count}
            </div>

            <div className="mt-3 h-px w-full" style={{ background: `rgba(${color === '#ff2d2d' ? '255,45,45' : color === '#ff6b00' ? '255,107,0' : color === '#ffe600' ? '255,230,0' : '0,255,231'},0.15)` }}>
              <div className="h-full transition-all duration-700"
                style={{ width: `${pct}%`, background: color, boxShadow: `0 0 6px ${color}` }} />
            </div>

            <div className="text-[9px] font-mono mt-1" style={{ color, opacity: 0.4 }}>
              {pct}% OF TOTAL
            </div>
          </div>
        );
      })}
    </div>
  );
}