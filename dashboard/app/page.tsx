'use client';

import {
  useState, useEffect, useCallback,
  lazy, Suspense, useRef
} from 'react';
import Header           from '@/components/Header';
import StatCards        from '@/components/StatCards';
import Charts           from '@/components/Charts';
import AttackFeed       from '@/components/AttackFeed';
import MitreHeatmap     from '@/components/MitreHeatmap';
import PredictionPanel  from '@/components/PredictionPanel';
import InvestigationPanel from '@/components/InvestigationPanel';
import { fetchAttacks, fetchStats, subscribeToLiveAttacks } from '@/lib/api';
import type { Attack, Stats } from '@/lib/api';

const AttackMap = lazy(() => import('@/components/AttackMap'));

const EMPTY: Stats = {
  total_attacks:    0,
  by_risk:          { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
  top_attack_types: [],
  top_ports:        [],
  top_countries:    [],
};

const MAP_MIN     = 40;
const MAP_MAX     = 85;
const MAP_DEFAULT = 62;

// ── Section label component ─────────────────────────
function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 mb-2">
      <div className="h-px flex-1"
        style={{ background: 'rgba(0,255,231,0.08)' }} />
      <span className="font-mono text-[9px] tracking-[0.2em] flex-shrink-0"
        style={{ color: 'rgba(0,255,231,0.3)' }}>
        {children}
      </span>
      <div className="h-px flex-1"
        style={{ background: 'rgba(0,255,231,0.08)' }} />
    </div>
  );
}

export default function Dashboard() {
  const [attacks,        setAttacks]        = useState<Attack[]>([]);
  const [stats,          setStats]          = useState<Stats>(EMPTY);
  const [isLive,         setIsLive]         = useState(false);
  const [mapPct,         setMapPct]         = useState(MAP_DEFAULT);
  const [mapHeight,      setMapHeight]      = useState(460);
  const [selectedAttack, setSelectedAttack] = useState<Attack | null>(null);

  const draggingW = useRef(false);
  const draggingH = useRef(false);
  const rowRef    = useRef<HTMLDivElement>(null);
  const startX    = useRef(0);
  const startPct  = useRef(MAP_DEFAULT);
  const startY    = useRef(0);
  const startH    = useRef(460);

  // ── Data fetching ──────────────────────────────────
  const refresh = useCallback(async () => {
    try {
      const [a, s] = await Promise.all([
        fetchAttacks(100), fetchStats()
      ]);
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

  // ── Drag handlers ──────────────────────────────────
  const onMouseDownW = (e: React.MouseEvent) => {
    draggingW.current = true;
    startX.current    = e.clientX;
    startPct.current  = mapPct;
    e.preventDefault();
  };

  const onMouseDownH = (e: React.MouseEvent) => {
    draggingH.current = true;
    startY.current    = e.clientY;
    startH.current    = mapHeight;
    e.preventDefault();
  };

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (draggingW.current && rowRef.current) {
        const rowW   = rowRef.current.getBoundingClientRect().width;
        const dx     = e.clientX - startX.current;
        const newPct = startPct.current + (dx / rowW) * 100;
        setMapPct(Math.min(MAP_MAX, Math.max(MAP_MIN, newPct)));
      }
      if (draggingH.current) {
        const dy   = e.clientY - startY.current;
        const newH = startH.current + dy;
        setMapHeight(Math.min(720, Math.max(300, newH)));
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
    <div className="relative z-10 min-h-screen flex flex-col"
      style={{ background: '#080c14' }}>
      <Header
        total={stats.total_attacks}
        isLive={isLive}
        criticalCount={stats.by_risk.CRITICAL}
      />

      <div className="flex-1 p-3 space-y-4">

        {/* ── Stat cards ── */}
        <StatCards byRisk={stats.by_risk} total={stats.total_attacks} />

        {/* ── Map + Charts ── */}
        <section>
          <SectionLabel>THREAT INTELLIGENCE MAP</SectionLabel>
          <div ref={rowRef} className="flex relative"
            style={{ height: mapHeight, gap: 0 }}>

            {/* Map */}
            <div className="relative flex-shrink-0 rounded-lg overflow-hidden"
              style={{ width: `${mapPct}%` }}>
              <Suspense fallback={
                <div className="w-full h-full rounded-lg flex items-center
                  justify-center font-mono text-xs"
                  style={{
                    border:     '1px solid rgba(0,255,231,0.12)',
                    background: '#020810',
                    color:      'rgba(0,255,231,0.3)',
                  }}>
                  <span className="blink">initializing map_</span>
                </div>
              }>
                <AttackMap
                  attacks={attacks}
                  selectedAttack={selectedAttack}
                />
              </Suspense>
            </div>

            {/* Drag handle */}
            <div onMouseDown={onMouseDownW}
              className="relative flex-shrink-0 flex items-center
                justify-center cursor-col-resize select-none z-20"
              style={{ width: 14 }}>
              <div className="w-px h-full"
                style={{ background: 'rgba(0,255,231,0.1)' }} />
              <div className="absolute flex flex-col gap-1.5 items-center">
                {[0,1,2,3,4].map(i => (
                  <div key={i} className="w-1 h-1 rounded-full"
                    style={{ background: 'rgba(0,255,231,0.35)' }} />
                ))}
              </div>
            </div>

            {/* Charts */}
            <div className="flex-1 overflow-hidden rounded-lg"
              style={{ width: `${rightPct}%` }}>
              <Charts
                topAttackTypes={stats.top_attack_types}
                topPorts={stats.top_ports}
                topCountries={stats.top_countries}
              />
            </div>
          </div>

          {/* Height drag handle */}
          <div onMouseDown={onMouseDownH}
            className="flex items-center justify-center h-5
              cursor-row-resize select-none mt-1"
            title="Drag to resize">
            <div className="flex gap-1.5 items-center">
              <div className="h-px w-12"
                style={{ background: 'rgba(0,255,231,0.1)' }} />
              {[0,1,2,3,4,5].map(i => (
                <div key={i} className="w-1 h-1 rounded-full"
                  style={{ background: 'rgba(0,255,231,0.3)' }} />
              ))}
              <div className="h-px w-12"
                style={{ background: 'rgba(0,255,231,0.1)' }} />
            </div>
          </div>
        </section>

        {/* ── MITRE ── */}
        <section>
          <SectionLabel>MITRE ATT&CK® FRAMEWORK</SectionLabel>
          <MitreHeatmap />
        </section>

        {/* ── Feed + Investigation side by side ── */}
        <section>
          <SectionLabel>
            LIVE FEED &amp; AI INVESTIGATION —
            {' '}{attacks.length} EVENTS · CLICK ROW TO INVESTIGATE
          </SectionLabel>
          <div className="grid gap-3"
            style={{ gridTemplateColumns: '1fr 1fr' }}>
            <AttackFeed
              attacks={attacks}
              selectedAttack={selectedAttack}
              onSelectAttack={setSelectedAttack}
            />
            <InvestigationPanel selectedAttack={selectedAttack} />
          </div>
        </section>

        {/* ── Prediction ── */}
        <section>
          <SectionLabel>LSTM ATTACK PREDICTION ENGINE</SectionLabel>
          <PredictionPanel />
        </section>

      </div>

      <div className="h-px w-full mt-2"
        style={{
          background: 'linear-gradient(90deg,transparent,#00ffe7,transparent)',
          opacity: 0.15,
        }} />
    </div>
  );
}