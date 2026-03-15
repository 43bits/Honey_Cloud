// // app/page.tsx
// 'use client';

// import { useState, useEffect, useCallback, lazy, Suspense } from 'react';
// import Header    from '@/components/Header';
// import StatCards from '@/components/StatCards';
// import Charts    from '@/components/Charts';
// import AttackFeed from '@/components/AttackFeed';
// import { fetchAttacks, fetchStats, subscribeToLiveAttacks } from '@/lib/api';
// import type { Attack, Stats } from '@/lib/api';

// // Lazy-load map (Leaflet needs window)
// const AttackMap = lazy(() => import('@/components/AttackMap'));

// const EMPTY: Stats = {
//   total_attacks: 0,
//   by_risk: { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
//   top_attack_types: [],
//   top_ports: [],
//   top_countries: [],
// };

// export default function Dashboard() {
//   const [attacks, setAttacks] = useState<Attack[]>([]);
//   const [stats,   setStats]   = useState<Stats>(EMPTY);
//   const [isLive,  setIsLive]  = useState(false);

//   const refresh = useCallback(async () => {
//     try {
//       const [a, s] = await Promise.all([fetchAttacks(100), fetchStats()]);
//       setAttacks(a);
//       setStats(s);
//     } catch {}
//   }, []);

//   useEffect(() => {
//     refresh();
//     const t = setInterval(refresh, 3000);
//     return () => clearInterval(t);
//   }, [refresh]);

//   useEffect(() => {
//     const unsub = subscribeToLiveAttacks((a) => {
//       setIsLive(true);
//       setAttacks(prev => [a, ...prev].slice(0, 100));
//       setStats(prev => ({
//         ...prev,
//         total_attacks: prev.total_attacks + 1,
//         by_risk: {
//           ...prev.by_risk,
//           [a.risk_level]: (prev.by_risk[a.risk_level] || 0) + 1,
//         },
//       }));
//     });
//     return unsub;
//   }, []);

//   return (
//     <div className="relative z-10 min-h-screen flex flex-col">
//       <Header
//         total={stats.total_attacks}
//         isLive={isLive}
//         criticalCount={stats.by_risk.CRITICAL}
//       />

//       <div className="flex-1 p-3 space-y-3">
//         {/* Stat cards */}
//         <StatCards byRisk={stats.by_risk} total={stats.total_attacks} />

//         {/* Map + Feed side by side */}
//         <div className="grid grid-cols-1 lg:grid-cols-2 gap-3" style={{ height: '380px' }}>
//           {/* Attack Map */}
//           <Suspense fallback={
//             <div className="h-full rounded flex items-center justify-center font-mono text-xs"
//               style={{ border: '1px solid rgba(0,255,231,0.12)', color: 'rgba(0,255,231,0.3)' }}>
//               <span className="blink">loading map_</span>
//             </div>
//           }>
//             <AttackMap attacks={attacks} />
//           </Suspense>

//           {/* Right panel — charts stacked */}
//           <div className="flex flex-col gap-3 overflow-hidden">
//             <Charts
//               topAttackTypes={stats.top_attack_types}
//               topPorts={stats.top_ports}
//               topCountries={stats.top_countries}
//             />
//           </div>
//         </div>

//         {/* Live feed */}
//         <div>
//           <div className="text-[9px] font-mono tracking-widest mb-2"
//             style={{ color: 'rgba(0,255,231,0.35)' }}>
//             LIVE THREAT INTELLIGENCE FEED — {attacks.length} EVENTS CAPTURED
//           </div>
//           <AttackFeed attacks={attacks} />
//         </div>
//       </div>

//       {/* Bottom border glow */}
//       <div className="h-px w-full"
//         style={{ background: 'linear-gradient(90deg, transparent, #00ffe7, transparent)', opacity: 0.2 }} />
//     </div>
//   );
// }
// app/page.tsx
'use client';

import { useState, useEffect, useCallback, lazy, Suspense, useRef } from 'react';
import Header     from '@/components/Header';
import StatCards  from '@/components/StatCards';
import Charts     from '@/components/Charts';
import AttackFeed from '@/components/AttackFeed';
import { fetchAttacks, fetchStats, subscribeToLiveAttacks } from '@/lib/api';
import type { Attack, Stats } from '@/lib/api';

const AttackMap = lazy(() => import('@/components/AttackMap'));

const EMPTY: Stats = {
  total_attacks: 0,
  by_risk:       { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
  top_attack_types: [],
  top_ports:        [],
  top_countries:    [],
};

// Map width as % of the middle row (clamped 40–85%)
const MAP_MIN = 40;
const MAP_MAX = 85;
const MAP_DEFAULT = 65;

export default function Dashboard() {
  const [attacks,  setAttacks]  = useState<Attack[]>([]);
  const [stats,    setStats]    = useState<Stats>(EMPTY);
  const [isLive,   setIsLive]   = useState(false);
  const [mapPct,   setMapPct]   = useState(MAP_DEFAULT);
  const [mapHeight,setMapHeight]= useState(440);

  const draggingW  = useRef(false);
  const draggingH  = useRef(false);
  const rowRef     = useRef<HTMLDivElement>(null);
  const startX     = useRef(0);
  const startPct   = useRef(MAP_DEFAULT);
  const startY     = useRef(0);
  const startH     = useRef(440);

  // ── Data fetching ──────────────────────────────────
  const refresh = useCallback(async () => {
    try {
      const [a, s] = await Promise.all([fetchAttacks(100), fetchStats()]);
      setAttacks(a);
      setStats(s);
    } catch {}
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 3000);
    return () => clearInterval(t);
  }, [refresh]);

  useEffect(() => {
    const unsub = subscribeToLiveAttacks((a) => {
      setIsLive(true);
      setAttacks(prev => [a, ...prev].slice(0, 100));
      setStats(prev => ({
        ...prev,
        total_attacks: prev.total_attacks + 1,
        by_risk: {
          ...prev.by_risk,
          [a.risk_level]: (prev.by_risk[a.risk_level] || 0) + 1,
        },
      }));
    });
    return unsub;
  }, []);

  // ── Horizontal drag (map width) ────────────────────
  const onMouseDownW = (e: React.MouseEvent) => {
    draggingW.current = true;
    startX.current    = e.clientX;
    startPct.current  = mapPct;
    e.preventDefault();
  };

  // ── Vertical drag (map height) ─────────────────────
  const onMouseDownH = (e: React.MouseEvent) => {
    draggingH.current = true;
    startY.current    = e.clientY;
    startH.current    = mapHeight;
    e.preventDefault();
  };

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (draggingW.current && rowRef.current) {
        const rowW = rowRef.current.getBoundingClientRect().width;
        const dx   = e.clientX - startX.current;
        const newPct = startPct.current + (dx / rowW) * 100;
        setMapPct(Math.min(MAP_MAX, Math.max(MAP_MIN, newPct)));
      }
      if (draggingH.current) {
        const dy     = e.clientY - startY.current;
        const newH   = startH.current + dy;
        setMapHeight(Math.min(700, Math.max(280, newH)));
      }
    };
    const onUp = () => {
      draggingW.current = false;
      draggingH.current = false;
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup',   onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup',   onUp);
    };
  }, []);

  const rightPct = 100 - mapPct;

  return (
    <div className="relative z-10 min-h-screen flex flex-col">
      <Header
        total={stats.total_attacks}
        isLive={isLive}
        criticalCount={stats.by_risk.CRITICAL}
      />

      <div className="flex-1 p-3 space-y-3">

        {/* ── Stat cards ── */}
        <StatCards byRisk={stats.by_risk} total={stats.total_attacks} />

        {/* ── Map + Charts row (resizable) ── */}
        <div
          ref={rowRef}
          className="flex gap-0 relative"
          style={{ height: mapHeight }}
        >
          {/* MAP PANEL */}
          <div
            className="relative flex-shrink-0"
            style={{ width: `${mapPct}%` }}
          >
            <Suspense fallback={
              <div className="w-full h-full rounded flex items-center justify-center font-mono text-xs"
                style={{ border: '1px solid rgba(0,255,231,0.12)', color: 'rgba(0,255,231,0.3)' }}>
                <span className="blink">loading map_</span>
              </div>
            }>
              <AttackMap attacks={attacks} />
            </Suspense>
          </div>

          {/* ── VERTICAL DRAG HANDLE (width) ── */}
          <div
            onMouseDown={onMouseDownW}
            className="relative flex-shrink-0 flex items-center justify-center cursor-col-resize select-none z-20"
            style={{ width: '12px' }}
            title="Drag to resize map width"
          >
            {/* visible bar */}
            <div
              className="w-px h-full transition-all"
              style={{ background: 'rgba(0,255,231,0.15)' }}
            />
            {/* grip dots */}
            <div className="absolute flex flex-col gap-1 items-center">
              {[0,1,2,3,4].map(i => (
                <div key={i} className="w-1 h-1 rounded-full"
                  style={{ background: 'rgba(0,255,231,0.4)' }} />
              ))}
            </div>
          </div>

          {/* CHARTS PANEL */}
          <div
            className="flex-1 overflow-hidden"
            style={{ width: `${rightPct}%` }}
          >
            <Charts
              topAttackTypes={stats.top_attack_types}
              topPorts={stats.top_ports}
              topCountries={stats.top_countries}
            />
          </div>
        </div>

        {/* ── HORIZONTAL DRAG HANDLE (height) ── */}
        <div
          onMouseDown={onMouseDownH}
          className="flex items-center justify-center cursor-row-resize select-none h-4 group"
          title="Drag to resize map height"
        >
          <div className="flex gap-1.5 items-center">
            <div className="h-px flex-1 w-16 transition-all"
              style={{ background: 'rgba(0,255,231,0.12)' }} />
            {/* grip dots row */}
            {[0,1,2,3,4,5].map(i => (
              <div key={i} className="w-1 h-1 rounded-full transition-all"
                style={{ background: 'rgba(0,255,231,0.35)' }} />
            ))}
            <div className="h-px flex-1 w-16"
              style={{ background: 'rgba(0,255,231,0.12)' }} />
          </div>
        </div>

        {/* ── Live feed ── */}
        <div>
          <div className="text-[9px] font-mono tracking-widest mb-2"
            style={{ color: 'rgba(0,255,231,0.35)' }}>
            LIVE THREAT INTELLIGENCE FEED — {attacks.length} EVENTS CAPTURED
          </div>
          <AttackFeed attacks={attacks} />
        </div>
      </div>

      <div className="h-px w-full"
        style={{ background: 'linear-gradient(90deg,transparent,#00ffe7,transparent)', opacity: 0.2 }} />
    </div>
  );
}