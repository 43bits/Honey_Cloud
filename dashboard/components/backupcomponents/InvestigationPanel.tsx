/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState, useEffect } from 'react';
import type { Attack } from '@/lib/api';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Investigation {
  skipped?:         boolean;
  attack_ip:        string;
  attack_type:      string;
  risk_level:       string;
  mitre_id:         string;
  log_analysis:     string;
  investigation:    string;
  risk_assessment:  string;
  response_actions: string;
  generated_at:     string;
  elapsed_seconds:  number;
}

const riskColor = (r: string) => {
  if (r === 'CRITICAL') return '#ff2d2d';
  if (r === 'HIGH')     return '#ff6b00';
  if (r === 'MEDIUM')   return '#ffe600';
  return '#00ffe7';
};

const riskBg = (r: string) => {
  if (r === 'CRITICAL') return 'rgba(255,45,45,0.08)';
  if (r === 'HIGH')     return 'rgba(255,107,0,0.08)';
  if (r === 'MEDIUM')   return 'rgba(255,230,0,0.05)';
  return 'rgba(0,255,231,0.03)';
};

const AGENTS = [
  { key: 'log_analysis',     label: 'LOG ANALYSIS',    icon: '🔬', color: '#00ffe7' },
  { key: 'investigation',    label: 'THREAT CONTEXT',  icon: '🕵️', color: '#ff6b00' },
  { key: 'risk_assessment',  label: 'RISK ASSESSMENT', icon: '🎯', color: '#ff2d2d' },
  { key: 'response_actions', label: 'RESPONSE ACTIONS',icon: '🛡️', color: '#00ff88' },
] as const;

export default function InvestigationPanel({
  selectedAttack,
}: {
  selectedAttack: Attack | null;
}) {
  const [report,  setReport]  = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [tab,     setTab]     = useState<typeof AGENTS[number]['key']>('log_analysis');

  useEffect(() => {
    setReport(null);
    setTab('log_analysis');
  }, [selectedAttack?.source_ip, selectedAttack?.timestamp]);

  const color = selectedAttack
    ? riskColor(selectedAttack.risk_level)
    : 'rgba(0,255,231,0.3)';

  const handleViewInsights = async () => {
    if (!selectedAttack || loading || report) return;
    setLoading(true);

    try {
      const res  = await fetch(`${API}/investigate`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_ip:       selectedAttack.source_ip,
          source_port:     (selectedAttack as any).source_port || 0,
          port_targeted:   selectedAttack.port_targeted || 22,
          protocol:        selectedAttack.protocol      || 'tcp',
          country:         selectedAttack.country       || 'Unknown',
          login_attempts:  (selectedAttack as any).login_attempts  || 50,
          connection_rate: (selectedAttack as any).connection_rate || 20.0,
        }),
      });

      const data = await res.json();

      if (data.investigation && !data.investigation.skipped) {
        setReport(data.investigation);
      } else {
        setReport({
          ...data.investigation,
          skipped: false,
          log_analysis:     data.investigation?.reason || 'Investigation complete',
          investigation:    data.investigation?.reason || '',
          risk_assessment:  data.investigation?.reason || '',
          response_actions: data.investigation?.reason || '',
          attack_ip:        selectedAttack.source_ip,
          attack_type:      selectedAttack.attack_type,
          risk_level:       selectedAttack.risk_level,
          mitre_id:         (selectedAttack as any).mitre_technique_id || '',
          generated_at:     new Date().toISOString(),
          elapsed_seconds:  0,
        });
      }
    } catch (err) {
      console.error('[Investigation] Failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded overflow-hidden flex flex-col"
      style={{
        border:     '1px solid rgba(0,255,231,0.12)',
        background: 'rgba(0,0,0,0.4)',
        minHeight:  '420px',
      }}>

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 flex-shrink-0"
        style={{
          background:   'rgba(0,255,231,0.04)',
          borderBottom: '1px solid rgba(0,255,231,0.08)',
        }}>
        <span className="font-mono text-[9px] tracking-widest"
          style={{ color: 'rgba(0,255,231,0.5)' }}>
          AI THREAT INVESTIGATION
        </span>
        {selectedAttack && (
          <span className="font-mono text-[9px] px-2 py-0.5 rounded"
            style={{
              color,
              background: `${color}15`,
              border:     `1px solid ${color}30`,
            }}>
            {selectedAttack.risk_level}
          </span>
        )}
      </div>

      {!selectedAttack && (
        <div className="flex-1 flex flex-col items-center justify-center gap-3 p-6">
          <div className="font-mono text-[10px] tracking-widest text-center"
            style={{ color: 'rgba(0,255,231,0.2)' }}>
            ← SELECT AN ATTACK FROM THE FEED
          </div>
        </div>
      )}

      {selectedAttack && (
        <div className="flex flex-col flex-1">

          <div className="flex flex-shrink-0"
            style={{ borderBottom: '1px solid rgba(0,255,231,0.08)' }}>
            {AGENTS.map((agent) => (
              <button key={agent.key}
                onClick={() => setTab(agent.key)}
                className="flex items-center gap-1.5 px-3 py-2.5
                  font-mono text-[9px] tracking-widest
                  transition-all hover:bg-white/5 flex-1 justify-center"
                style={{
                  color: tab === agent.key
                    ? agent.color
                    : 'rgba(0,255,231,0.3)',
                  borderBottom: tab === agent.key
                    ? `2px solid ${agent.color}`
                    : '2px solid transparent',
                  background: tab === agent.key
                    ? `${agent.color}08`
                    : 'transparent',
                }}>
                <span style={{ fontSize: '16px' }}>{agent.icon}</span>
                <span className="hidden xl:inline">{agent.label}</span>
              </button>
            ))}
          </div>

          <div className="flex-1 relative" style={{ minHeight: '200px' }}>

            {!report && (
              <div className="absolute inset-0 flex flex-col
                items-center justify-center gap-3">
                <button
                  onClick={handleViewInsights}
                  disabled={loading}
                  className="flex items-center gap-2 px-6 py-3
                    rounded font-mono text-[11px] tracking-widest
                    transition-all hover:scale-105 active:scale-95
                    disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    background: `${color}15`,
                    border:     `1px solid ${color}`,
                    color:      color,
                    boxShadow:  `0 0 20px ${color}33`,
                  }}
                >
                  {loading ? (
                    <>
                      <span style={{
                        display:   'inline-block',
                        animation: 'spin 1s linear infinite',
                      }}>
                        ⟳
                      </span>
                      <span>ANALYZING...</span>
                    </>
                  ) : (
                    <>
                      <span>🔍</span>
                      <span>VIEW INSIGHTS</span>
                    </>
                  )}
                </button>
              </div>
            )}

            {report && (
              <div className="p-4 overflow-y-auto h-full">
                <div className="font-mono text-xs leading-relaxed whitespace-pre-wrap"
                  style={{ color: 'rgba(180,210,240,0.8)' }}>
                  {report[tab as keyof Pick<
  Investigation,
  'log_analysis' | 'investigation' | 'risk_assessment' | 'response_actions'
>]}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}