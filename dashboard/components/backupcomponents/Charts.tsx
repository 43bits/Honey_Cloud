// components/Charts.tsx
'use client';

import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';

interface Props {
  topAttackTypes: { type: string; count: number }[];
  topPorts:       { port: string; count: number }[];
  topCountries:   { country: string; count: number }[];
}

const CYAN   = '#00ffe7';
const colors = ['#00ffe7', '#ff6b00', '#ff2d2d', '#ffe600', '#00ff88'];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const TT = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="font-mono text-[10px] px-3 py-2 rounded"
      style={{ background: '#020810', border: '1px solid rgba(0,255,231,0.2)', color: CYAN }}>
      <div className="opacity-60">{label}</div>
      <div className="font-bold">{payload[0].value}</div>
    </div>
  );
};

export default function Charts({ topAttackTypes, topPorts, topCountries }: Props) {
  const barData = topAttackTypes.map(({ type, count }) => ({
    name: type.replace(' Attack','').replace(' Brute Force',' BF').replace(' Exploit',''),
    count,
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">

      {/* Attack types */}
      <div className="lg:col-span-2 p-4 rounded"
        style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,255,231,0.12)' }}>
        <div className="text-[9px] font-mono tracking-widest mb-4"
          style={{ color: 'rgba(0,255,231,0.4)' }}>ATTACK TYPE FREQUENCY</div>
        {barData.length === 0 ? (
          <div className="h-36 flex items-center justify-center font-mono text-xs"
            style={{ color: 'rgba(0,255,231,0.2)' }}>
            <span className="blink">no data yet_</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={barData} margin={{ top: 0, right: 0, bottom: 0, left: -25 }}>
              <XAxis dataKey="name" tick={{ fontSize: 9, fill: 'rgba(0,255,231,0.4)', fontFamily: 'Share Tech Mono' }} />
              <YAxis tick={{ fontSize: 9, fill: 'rgba(0,255,231,0.3)', fontFamily: 'Share Tech Mono' }} />
              <Tooltip content={<TT />} />
              <Bar dataKey="count" radius={[2,2,0,0]}>
                {barData.map((_, i) => (
                  <Cell key={i} fill={colors[i % colors.length]}
                    style={{ filter: `drop-shadow(0 0 4px ${colors[i % colors.length]})` }} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Top countries */}
      <div className="p-4 rounded"
        style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,255,231,0.12)' }}>
        <div className="text-[9px] font-mono tracking-widest mb-4"
          style={{ color: 'rgba(0,255,231,0.4)' }}>TOP SOURCE NATIONS</div>
        {topCountries.length === 0 ? (
          <div className="h-36 flex items-center justify-center font-mono text-xs"
            style={{ color: 'rgba(0,255,231,0.2)' }}>
            <span className="blink">no data yet_</span>
          </div>
        ) : (
          <div className="space-y-2.5 mt-2">
            {topCountries.map(({ country, count }, i) => {
              const max = topCountries[0].count;
              const pct = Math.round((count / max) * 100);
              return (
                <div key={country}>
                  <div className="flex justify-between text-[10px] font-mono mb-1">
                    <span style={{ color: 'rgba(0,255,231,0.7)' }}>{country}</span>
                    <span style={{ color: colors[i % colors.length] }}>{count}</span>
                  </div>
                  <div className="h-px w-full" style={{ background: 'rgba(0,255,231,0.08)' }}>
                    <div className="h-full transition-all duration-700"
                      style={{
                        width: `${pct}%`,
                        background: colors[i % colors.length],
                        boxShadow: `0 0 6px ${colors[i % colors.length]}`,
                      }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}