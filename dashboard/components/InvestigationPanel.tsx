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

const RISK_COLOR: Record<string, string> = {
  CRITICAL: '#ff4444', HIGH: '#f5a623', MEDIUM: '#f0c040', LOW: '#3dd68c',
};

const TABS = [
  { key: 'log_analysis',     label: 'Log Analysis'   },
  { key: 'investigation',    label: 'Threat Context' },
  { key: 'risk_assessment',  label: 'Risk'           },
  { key: 'response_actions', label: 'Response'       },
] as const;

export default function InvestigationPanel({ selectedAttack }: { selectedAttack: Attack | null }) {
  const [report,  setReport]  = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [tab,     setTab]     = useState<typeof TABS[number]['key']>('log_analysis');

  useEffect(() => { setReport(null); setTab('log_analysis'); }, [selectedAttack?.source_ip, selectedAttack?.timestamp]);

  const color = selectedAttack ? (RISK_COLOR[selectedAttack.risk_level] || '#3dd68c') : '#3dd68c';

  const handleInvestigate = async () => {
    if (!selectedAttack || loading || report) return;
    setLoading(true);
    try {
      const res  = await fetch(`${API}/investigate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
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
      if (data.investigation && !data.investigation.skipped) setReport(data.investigation);
    } catch {}
    finally { setLoading(false); }
  };

  return (
    <div style={{ background: '#1a1a1a', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.07)', overflow: 'hidden', display: 'flex', flexDirection: 'column', minHeight: '320px' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px 12px', flexShrink: 0 }}>
        <span style={{ fontSize: '13px', fontWeight: 600, color: '#ffffff' }}>AI Investigation</span>
        {selectedAttack && (
          <span style={{ fontSize: '11px', fontWeight: 500, padding: '3px 8px', borderRadius: '6px', background: `${color}14`, border: `1px solid ${color}30`, color }}>
            {selectedAttack.risk_level}
          </span>
        )}
      </div>

      {!selectedAttack ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '24px', gap: '12px' }}>
          <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.2)', textAlign: 'center' }}>
            Select an attack to investigate
          </div>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', justifyContent: 'center' }}>
            {['Log Analyzer', 'Threat Intel', 'Risk Analyst', 'Responder'].map(a => (
              <span key={a} style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '5px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.3)' }}>{a}</span>
            ))}
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>

          {/* Attack strip */}
          <div style={{ padding: '10px 20px', background: `${color}0a`, borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
            <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: color, flexShrink: 0 }} />
            <span style={{ fontSize: '12px', fontWeight: 600, color, fontFamily: 'var(--mono)' }}>{selectedAttack.source_ip}</span>
            <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{selectedAttack.attack_type}</span>
            {selectedAttack.country && <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.25)', flexShrink: 0 }}>{selectedAttack.country}</span>}
          </div>

          {/* Tabs */}
          {report && (
            <div style={{ display: 'flex', borderBottom: '1px solid rgba(255,255,255,0.07)', flexShrink: 0 }}>
              {TABS.map(t => (
                <button key={t.key} onClick={() => setTab(t.key)} style={{
                  flex: 1, padding: '9px 8px',
                  fontSize: '11px', fontWeight: tab === t.key ? 500 : 400,
                  color: tab === t.key ? '#ffffff' : 'rgba(255,255,255,0.35)',
                  background: tab === t.key ? 'rgba(255,255,255,0.05)' : 'transparent',
                  border: 'none', borderBottom: `2px solid ${tab === t.key ? 'rgba(255,255,255,0.5)' : 'transparent'}`,
                  cursor: 'pointer', fontFamily: 'Inter, sans-serif', transition: 'all 0.15s',
                }}>{t.label}</button>
              ))}
            </div>
          )}

          {/* Body */}
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            {!report && (
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '24px' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.3)', marginBottom: '4px' }}>4-Agent AI Pipeline · Groq Llama 3.3 70B</div>
                  <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.15)' }}>Analyzes logs, threat context, risk, and response</div>
                </div>
                <button onClick={handleInvestigate} disabled={loading} style={{
                  padding: '10px 28px', borderRadius: '8px',
                  background: loading ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  color: loading ? 'rgba(255,255,255,0.4)' : '#ffffff',
                  fontSize: '12px', fontWeight: 500, cursor: loading ? 'not-allowed' : 'pointer',
                  fontFamily: 'Inter, sans-serif', transition: 'all 0.15s',
                  display: 'flex', alignItems: 'center', gap: '8px',
                }}>
                  {loading ? (
                    <><span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⟳</span> Analyzing...</>
                  ) : (
                    <><span>🔍</span> View Insights</>
                  )}
                </button>
              </div>
            )}
            {report && (
              <div style={{ padding: '16px 20px', overflowY: 'auto', height: '100%', fontSize: '12px', lineHeight: '1.7', color: 'rgba(255,255,255,0.55)', whiteSpace: 'pre-wrap', fontFamily: 'Inter, sans-serif' }}>
                {report[tab as keyof Pick<Investigation,'log_analysis'|'investigation'|'risk_assessment'|'response_actions'>]}
              </div>
            )}
          </div>

          {report && (
            <div style={{ padding: '8px 20px', borderTop: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'flex-end', flexShrink: 0 }}>
              <button onClick={() => setReport(null)} style={{ fontSize: '11px', color: 'rgba(255,255,255,0.25)', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'Inter, sans-serif' }}>
                Re-run ↺
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
