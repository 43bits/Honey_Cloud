/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState, useEffect, useCallback } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ScoreBreakdown { abuseipdb: number; virustotal: number; ml_model: number; corroboration: number; }
interface ThreatIntel {
  threat_intel_score: number; intel_level: string; intel_color: string;
  evidence: string[]; threat_tags: string[]; recommendation: string;
  data_sources: string[]; score_breakdown?: ScoreBreakdown; enriched_at: string;
  abuseipdb?: { available: boolean; abuse_confidence: number; total_reports: number; distinct_reporters: number; isp?: string; usage_type?: string; is_whitelisted: boolean; error?: string; };
  virustotal?: { available: boolean; malicious_votes: number; suspicious_votes: number; harmless_votes: number; total_engines: number; malicious_ratio: number; reputation: number; categories: string[]; error?: string; };
}
interface SelectedAttack { source_ip: string; attack_type: string; risk_level: string; risk_score?: number; country?: string; threat_intel_score?: number; intel_level?: string; [key: string]: any; }

const LEVEL_COLOR: Record<string,string> = {
  CONFIRMED_THREAT:'#ff4444', HIGH_CONFIDENCE:'#f5a623', SUSPICIOUS:'#f0c040', LOW_RISK:'#3dd68c', CLEAN:'#3dd68c', UNKNOWN:'rgba(255,255,255,0.3)',
};
const LEVEL_LABEL: Record<string,string> = {
  CONFIRMED_THREAT:'Confirmed Threat', HIGH_CONFIDENCE:'High Confidence', SUSPICIOUS:'Suspicious', LOW_RISK:'Low Risk', CLEAN:'Clean', UNKNOWN:'Unknown',
};
const ML_COLOR: Record<string,string> = { CRITICAL:'#ff4444', HIGH:'#f5a623', MEDIUM:'#f0c040', LOW:'#3dd68c' };

function ScoreBar({ label, score, max, color }: { label: string; score: number; max: number; color: string; }) {
  const pct = Math.min(Math.round((score/max)*100), 100);
  return (
    <div style={{ marginBottom: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
        <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)' }}>{label}</span>
        <span style={{ fontSize: '11px', fontWeight: 600, color }}>{score}<span style={{ color:'rgba(255,255,255,0.2)', fontWeight:400 }}>/{max}</span></span>
      </div>
      <div style={{ height: '3px', background: 'rgba(255,255,255,0.07)', borderRadius: '2px' }}>
        <div style={{ height:'100%', width:`${pct}%`, background:color, borderRadius:'2px', transition:'width 0.7s ease' }} />
      </div>
    </div>
  );
}

export default function ThreatIntelPanel({ selectedAttack }: { selectedAttack: SelectedAttack | null }) {
  const [intel,   setIntel]   = useState<ThreatIntel | null>(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [error,   setError]   = useState<string | null>(null);

  const refreshSummary = useCallback(() => {
    fetch(`${API}/intel/stats/summary`).then(r => r.ok ? r.json() : null).then(d => { if (d) setSummary(d); }).catch(() => {});
  }, []);

  useEffect(() => { refreshSummary(); const t = setInterval(refreshSummary, 10000); return () => clearInterval(t); }, [refreshSummary]);

  useEffect(() => {
    setIntel(null); setError(null); setLoading(false);
    if (selectedAttack?.threat_intel_score !== undefined) {
      setIntel({
        threat_intel_score: selectedAttack.threat_intel_score ?? 0,
        intel_level:        selectedAttack.intel_level   ?? 'UNKNOWN',
        intel_color:        selectedAttack.intel_color   ?? '#3dd68c',
        evidence:           selectedAttack.evidence      ?? [],
        threat_tags:        selectedAttack.threat_tags   ?? [],
        recommendation:     selectedAttack.recommendation ?? '',
        data_sources:       selectedAttack.data_sources  ?? [],
        score_breakdown:    selectedAttack.score_breakdown,
        enriched_at:        selectedAttack.enriched_at   ?? '',
        abuseipdb:          selectedAttack.abuseipdb,
        virustotal:         selectedAttack.virustotal,
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAttack?.source_ip, selectedAttack?.timestamp]);

  const handleFetch = async () => {
    if (!selectedAttack || loading || intel) return;
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API}/intel/${selectedAttack.source_ip.trim()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setIntel(await res.json());
      refreshSummary();
    } catch (e: any) { setError(e.message || 'Request failed'); }
    finally { setLoading(false); }
  };

  const mlColor    = ML_COLOR[selectedAttack?.risk_level ?? 'LOW'] ?? '#3dd68c';
  const intelColor = intel ? (LEVEL_COLOR[intel.intel_level] ?? '#3dd68c') : '#3dd68c';
  const intelLabel = intel ? (LEVEL_LABEL[intel.intel_level] ?? 'Unknown') : '';

  return (
    <div style={{ background:'#1a1a1a', borderRadius:'12px', border:'1px solid rgba(255,255,255,0.07)', overflow:'hidden', display:'flex', flexDirection:'column', minHeight:'340px' }}>

      {/* Header */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'16px 20px 12px', flexShrink:0 }}>
        <div>
          <div style={{ fontSize:'13px', fontWeight:600, color:'#ffffff' }}>Threat Intelligence</div>
          <div style={{ fontSize:'11px', color:'rgba(255,255,255,0.3)', marginTop:'1px' }}>AbuseIPDB · VirusTotal · ML</div>
        </div>
        {summary?.confirmed_threats > 0 && (
          <span style={{ fontSize:'11px', fontWeight:500, padding:'3px 8px', borderRadius:'6px', background:'rgba(255,68,68,0.1)', border:'1px solid rgba(255,68,68,0.2)', color:'#ff4444' }}>
            {summary.confirmed_threats} confirmed
          </span>
        )}
      </div>

      {/* No attack */}
      {!selectedAttack && (
        <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'24px', gap:'14px' }}>
          <div style={{ display:'flex', gap:'6px', flexWrap:'wrap', justifyContent:'center' }}>
            {['AbuseIPDB', 'VirusTotal', 'HoneyCloud ML'].map(s => (
              <span key={s} style={{ fontSize:'11px', padding:'3px 10px', borderRadius:'6px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.08)', color:'rgba(255,255,255,0.4)' }}>{s}</span>
            ))}
          </div>
          {summary && (
            <div style={{ display:'flex', gap:'20px', marginTop:'4px' }}>
              {[{l:'Enriched',v:summary.total_enriched,c:'#ffffff'},{l:'Confirmed',v:summary.confirmed_threats,c:'#ff4444'},{l:'Suspicious',v:summary.suspicious,c:'#f0c040'}].map(({l,v,c}) => (
                <div key={l} style={{ textAlign:'center' }}>
                  <div style={{ fontSize:'22px', fontWeight:700, color:c, lineHeight:1 }}>{v}</div>
                  <div style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)', marginTop:'2px' }}>{l}</div>
                </div>
              ))}
            </div>
          )}
          <div style={{ fontSize:'12px', color:'rgba(255,255,255,0.15)' }}>← Select an attack to investigate</div>
        </div>
      )}

      {selectedAttack && (
        <div style={{ display:'flex', flexDirection:'column', flex:1 }}>

          {/* Attack bar */}
          <div style={{ padding:'10px 20px', background:`${mlColor}08`, borderTop:'1px solid rgba(255,255,255,0.05)', borderBottom:'1px solid rgba(255,255,255,0.05)', display:'flex', alignItems:'center', gap:'10px', flexShrink:0 }}>
            <div style={{ width:'7px', height:'7px', borderRadius:'50%', background:mlColor, flexShrink:0 }} />
            <span style={{ fontSize:'12px', fontWeight:600, color:mlColor, fontFamily:'var(--mono)' }}>{selectedAttack.source_ip}</span>
            <span style={{ fontSize:'12px', color:'rgba(255,255,255,0.4)', flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{selectedAttack.attack_type}</span>
            <span style={{ fontSize:'11px', padding:'2px 7px', borderRadius:'5px', background:`${mlColor}12`, border:`1px solid ${mlColor}25`, color:mlColor, flexShrink:0, fontWeight:500 }}>
              {selectedAttack.risk_level}{selectedAttack.risk_score !== undefined ? ` · ${selectedAttack.risk_score}` : ''}
            </span>
          </div>

          {/* Pre-fetch */}
          {!intel && (
            <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'16px', padding:'24px' }}>
              <div style={{ textAlign:'center' }}>
                <div style={{ fontSize:'12px', color:'rgba(255,255,255,0.4)', marginBottom:'4px', fontWeight:500 }}>External Threat Database Lookup</div>
                <div style={{ fontSize:'11px', color:'rgba(255,255,255,0.2)' }}>AbuseIPDB + VirusTotal + ML cross-correlation</div>
              </div>
              <button onClick={handleFetch} disabled={loading} style={{
                padding:'10px 28px', borderRadius:'8px',
                background: loading ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.08)',
                border:'1px solid rgba(255,255,255,0.15)',
                color: loading ? 'rgba(255,255,255,0.4)' : '#ffffff',
                fontSize:'12px', fontWeight:500, cursor: loading ? 'not-allowed':'pointer',
                fontFamily:'Inter, sans-serif', transition:'all 0.15s',
                display:'flex', alignItems:'center', gap:'8px',
              }}>
                {loading ? <><span style={{display:'inline-block',animation:'spin 1s linear infinite'}}>⟳</span> Querying...</> : <><span>🔎</span> Fetch Threat Intel</>}
              </button>
              {error && <div style={{ fontSize:'11px', color:'#ff4444' }}>✗ {error}</div>}
            </div>
          )}

          {/* Result */}
          {intel && (
            <div style={{ flex:1, overflowY:'auto', padding:'16px 20px', display:'flex', flexDirection:'column', gap:'14px' }}>

              {/* Score card */}
              <div style={{ background:`${intelColor}0a`, border:`1px solid ${intelColor}20`, borderRadius:'10px', padding:'14px 16px', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                <div>
                  <div style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)', marginBottom:'4px', letterSpacing:'0.04em' }}>THREAT INTEL SCORE</div>
                  <div style={{ fontSize:'32px', fontWeight:700, color:intelColor, lineHeight:1, fontFamily:'Inter,sans-serif' }}>
                    {intel.threat_intel_score}<span style={{ fontSize:'14px', color:'rgba(255,255,255,0.2)', fontWeight:400 }}>/100</span>
                  </div>
                </div>
                <span style={{ fontSize:'11px', fontWeight:500, padding:'4px 10px', borderRadius:'6px', background:`${intelColor}14`, border:`1px solid ${intelColor}30`, color:intelColor }}>
                  {intelLabel}
                </span>
              </div>

              {/* Breakdown */}
              {intel.score_breakdown && (
                <div style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.07)', borderRadius:'10px', padding:'14px 16px' }}>
                  <div style={{ fontSize:'11px', fontWeight:500, color:'rgba(255,255,255,0.4)', marginBottom:'12px', letterSpacing:'0.04em' }}>SCORE BREAKDOWN</div>
                  <ScoreBar label="AbuseIPDB"    score={intel.score_breakdown.abuseipdb}    max={45} color="#ff4444" />
                  <ScoreBar label="VirusTotal"   score={intel.score_breakdown.virustotal}   max={40} color="#f5a623" />
                  <ScoreBar label="ML Model"     score={intel.score_breakdown.ml_model}     max={15} color="#3dd68c" />
                  {(intel.score_breakdown.corroboration??0)>0 && <ScoreBar label="Corroboration" score={intel.score_breakdown.corroboration} max={8} color="#60a5fa" />}
                </div>
              )}

              {/* AbuseIPDB + VT */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'8px' }}>
                {[
                  { title:'AbuseIPDB', color:'#ff4444', data: intel.abuseipdb, render: (d:any) => d?.available ? (
                    <>
                      <div style={{ display:'flex', gap:'12px', marginBottom:'6px' }}>
                        <div><div style={{ fontSize:'20px', fontWeight:700, color: d.abuse_confidence>=75?'#ff4444':'#f5a623', lineHeight:1 }}>{d.abuse_confidence}%</div><div style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)' }}>confidence</div></div>
                        <div><div style={{ fontSize:'20px', fontWeight:700, color:'rgba(255,255,255,0.7)', lineHeight:1 }}>{d.total_reports}</div><div style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)' }}>reports</div></div>
                      </div>
                      {d.isp && <div style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{d.isp}</div>}
                    </>
                  ) : <div style={{ fontSize:'11px', color:'rgba(255,255,255,0.2)' }}>{d?.error??'Not available'}</div> },
                  { title:'VirusTotal', color:'#f5a623', data: intel.virustotal, render: (d:any) => d?.available ? (
                    <>
                      <div style={{ display:'flex', gap:'12px', marginBottom:'6px' }}>
                        <div><div style={{ fontSize:'20px', fontWeight:700, color: d.malicious_votes>=10?'#ff4444':'#f5a623', lineHeight:1 }}>{d.malicious_votes}</div><div style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)' }}>/{d.total_engines}</div></div>
                        <div><div style={{ fontSize:'20px', fontWeight:700, color: d.reputation<-50?'#ff4444':'rgba(255,255,255,0.6)', lineHeight:1 }}>{d.reputation}</div><div style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)' }}>rep</div></div>
                      </div>
                      {d.categories?.[0] && <div style={{ fontSize:'10px', color:'rgba(255,255,255,0.3)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{d.categories[0]}</div>}
                    </>
                  ) : <div style={{ fontSize:'11px', color:'rgba(255,255,255,0.2)' }}>{d?.error??'Not available'}</div> },
                ].map(({ title, color, data: d, render }) => (
                  <div key={title} style={{ background:`${color}07`, border:`1px solid ${color}18`, borderRadius:'10px', padding:'12px 14px' }}>
                    <div style={{ fontSize:'10px', fontWeight:500, color:`${color}80`, letterSpacing:'0.06em', marginBottom:'8px' }}>{title.toUpperCase()}</div>
                    {render(d)}
                  </div>
                ))}
              </div>

              {/* Tags */}
              {intel.threat_tags.length > 0 && (
                <div>
                  <div style={{ fontSize:'11px', fontWeight:500, color:'rgba(255,255,255,0.4)', marginBottom:'8px' }}>THREAT TAGS</div>
                  <div style={{ display:'flex', flexWrap:'wrap', gap:'5px' }}>
                    {intel.threat_tags.map(tag => (
                      <span key={tag} style={{ fontSize:'10px', padding:'2px 8px', borderRadius:'5px', background:'rgba(255,68,68,0.08)', border:'1px solid rgba(255,68,68,0.18)', color:'#ff4444' }}>{tag.replace(/_/g,' ')}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendation */}
              {intel.recommendation && (
                <div style={{ background:'rgba(61,214,140,0.05)', border:'1px solid rgba(61,214,140,0.15)', borderRadius:'10px', padding:'12px 14px' }}>
                  <div style={{ fontSize:'10px', fontWeight:500, color:'rgba(61,214,140,0.5)', marginBottom:'6px', letterSpacing:'0.06em' }}>RECOMMENDATION</div>
                  <div style={{ fontSize:'12px', color:'rgba(61,214,140,0.8)', lineHeight:'1.6' }}>{intel.recommendation}</div>
                </div>
              )}

              {/* Evidence */}
              {intel.evidence.length > 0 && (
                <div>
                  <div style={{ fontSize:'11px', fontWeight:500, color:'rgba(255,255,255,0.3)', marginBottom:'8px' }}>EVIDENCE CHAIN</div>
                  {intel.evidence.map((e, i) => (
                    <div key={i} style={{ display:'flex', gap:'10px', marginBottom:'5px' }}>
                      <span style={{ fontSize:'10px', color:'rgba(255,255,255,0.2)', flexShrink:0, minWidth:'16px', fontFamily:'var(--mono)' }}>{String(i+1).padStart(2,'0')}</span>
                      <span style={{ fontSize:'11px', color:'rgba(255,255,255,0.5)', lineHeight:'1.5' }}>{e}</span>
                    </div>
                  ))}
                </div>
              )}

              <div style={{ display:'flex', justifyContent:'flex-end', paddingTop:'4px' }}>
                <button onClick={() => { setIntel(null); setError(null); }} style={{ fontSize:'11px', color:'rgba(255,255,255,0.25)', background:'none', border:'none', cursor:'pointer', fontFamily:'Inter,sans-serif' }}>Re-check ↺</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
