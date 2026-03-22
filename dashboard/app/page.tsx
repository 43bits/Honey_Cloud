'use client';

import { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import Header             from '@/components/Header';
import StatCards          from '@/components/StatCards';
import AttackFeed         from '@/components/AttackFeed';
import MitreHeatmap       from '@/components/MitreHeatmap';
import PredictionPanel    from '@/components/PredictionPanel';
import InvestigationPanel from '@/components/InvestigationPanel';
import ThreatIntelPanel   from '@/components/ThreatIntelPanel';
import { fetchAttacks, fetchStats, subscribeToLiveAttacks } from '@/lib/api';
import type { Attack, Stats } from '@/lib/api';

const AttackMap = lazy(() => import('@/components/AttackMap'));

const EMPTY: Stats = {
  total_attacks:    0,
  by_risk:          { LOW:0, MEDIUM:0, HIGH:0, CRITICAL:0 },
  top_attack_types: [],
  top_ports:        [],
  top_countries:    [],
};

export default function Dashboard() {
  const [attacks,        setAttacks]        = useState<Attack[]>([]);
  const [stats,          setStats]          = useState<Stats>(EMPTY);
  const [isLive,         setIsLive]         = useState(false);
  const [selectedAttack, setSelectedAttack] = useState<Attack | null>(null);

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
        by_risk: { ...prev.by_risk, [a.risk_level]: (prev.by_risk[a.risk_level]||0) + 1 },
      }));
    });
    return unsub;
  }, []);

  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100vh', background:'#111111', overflow:'hidden' }}>

      {/* Header */}
      <Header total={stats.total_attacks} isLive={isLive} criticalCount={stats.by_risk.CRITICAL} />

      {/* Stat strip */}
      <StatCards byRisk={stats.by_risk} total={stats.total_attacks} />

      {/* 3-column body */}
      <div style={{
        display:    'flex',
        flex:       1,
        overflow:   'hidden',
        gap:        '12px',
        padding:    '12px 16px',
        minHeight:  0,
      }}>

        {/* ── LEFT — Attack Feed (full height, info buttons in footer) ── */}
        <div style={{ width:'360px', flexShrink:0, minHeight:0, overflow:'hidden' }}>
          <AttackFeed
            attacks={attacks}
            selectedAttack={selectedAttack}
            onSelectAttack={setSelectedAttack}
            topAttackTypes={stats.top_attack_types}
            topCountries={stats.top_countries}
          />
        </div>

        {/* ── CENTER — Map + MITRE ── */}
        <div style={{ flex:1, display:'flex', flexDirection:'column', gap:'10px', overflow:'hidden', minHeight:0, minWidth:0 }}>

          {/* Map — 58% height */}
          <div style={{ flex:'0 0 58%', minHeight:0, overflow:'hidden' }}>
            <Suspense fallback={
              <div style={{
                width:'100%', height:'100%', background:'#1a1a1a', borderRadius:'12px',
                border:'1px solid rgba(255,255,255,0.07)', display:'flex', alignItems:'center',
                justifyContent:'center', fontSize:'12px', color:'rgba(255,255,255,0.2)', fontFamily:'Inter,sans-serif',
              }}>
                Initializing map...
              </div>
            }>
              <AttackMap attacks={attacks} selectedAttack={selectedAttack} />
            </Suspense>
          </div>

          {/* MITRE — remaining */}
          <div style={{ flex:1, minHeight:0, overflow:'auto' }}>
            <MitreHeatmap />
          </div>
        </div>

        {/* ── RIGHT — Scrollable panel column ── */}
        <div style={{
          width:        '360px',
          flexShrink:   0,
          overflowY:    'auto',
          overflowX:    'hidden',
          minHeight:    0,
          display:      'flex',
          flexDirection:'column',
          gap:          '10px',
          paddingBottom:'12px',
        }}>
          <div style={{ flexShrink:0, minHeight:'340px' }}>
            <InvestigationPanel selectedAttack={selectedAttack} />
          </div>
          <div style={{ flexShrink:0, minHeight:'360px' }}>
            <ThreatIntelPanel selectedAttack={selectedAttack as any} />
          </div>
          <div style={{ flexShrink:0, minHeight:'220px' }}>
            <PredictionPanel />
          </div>
        </div>

      </div>
    </div>
  );
}
