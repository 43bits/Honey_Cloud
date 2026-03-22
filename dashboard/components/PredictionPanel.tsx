'use client';

import { useState, useEffect } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Prediction {
  ready: boolean; reason?: string; predicted?: string; confidence?: number;
  probabilities?: Record<string,number>; recommendation?: string; sequence_used?: string[];
}

const RISK_COLOR = (a: string) => {
  if (['Database Attack','Telnet Attack','SSH Brute Force'].includes(a)) return '#ff4444';
  if (['Web Exploit','FTP Attack'].includes(a)) return '#f5a623';
  return '#3dd68c';
};

export default function PredictionPanel() {
  const [data,       setData]       = useState<Prediction | null>(null);
  const [loading,    setLoading]    = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [lastUpdate, setLastUpdate] = useState('');

  const fetchPrediction = async () => {
    try {
      const res = await fetch(`${API}/predict/next`);
      setData(await res.json());
      setLastUpdate(new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }));
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { fetchPrediction(); const t = setInterval(fetchPrediction, 10000); return () => clearInterval(t); }, []);

  const handleRetrain = async () => {
    setRetraining(true);
    try { await fetch(`${API}/predict/train`, { method:'POST' }); setTimeout(() => { fetchPrediction(); setRetraining(false); }, 5000); }
    catch { setRetraining(false); }
  };

  return (
    <div style={{ background:'#1a1a1a', borderRadius:'12px', border:'1px solid rgba(255,255,255,0.07)', overflow:'hidden', minHeight:'200px' }}>

      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'16px 20px 12px' }}>
        <div>
          <span style={{ fontSize:'13px', fontWeight:600, color:'#ffffff' }}>LSTM Prediction</span>
          {lastUpdate && <span style={{ fontSize:'11px', color:'rgba(255,255,255,0.25)', marginLeft:'10px' }}>{lastUpdate}</span>}
        </div>
        <button onClick={handleRetrain} disabled={retraining} style={{
          padding:'4px 12px', borderRadius:'6px', background:'rgba(255,255,255,0.06)', border:'1px solid rgba(255,255,255,0.1)',
          color: retraining ? 'rgba(255,255,255,0.3)' : 'rgba(255,255,255,0.6)', fontSize:'11px', fontWeight:500,
          cursor: retraining ? 'not-allowed':'pointer', fontFamily:'Inter,sans-serif',
        }}>
          {retraining ? '⟳ Training...' : '↺ Retrain'}
        </button>
      </div>

      <div style={{ padding:'0 20px 20px' }}>
        {loading && <div style={{ textAlign:'center', padding:'20px 0', fontSize:'12px', color:'rgba(255,255,255,0.2)' }}>Loading prediction...</div>}

        {!loading && !data?.ready && (
          <div style={{ textAlign:'center', padding:'20px 0' }}>
            <div style={{ fontSize:'13px', color:'rgba(255,255,255,0.25)', marginBottom:'6px' }}>Model warming up</div>
            <div style={{ fontSize:'11px', color:'rgba(255,255,255,0.15)' }}>{data?.reason || 'Need at least 3 attacks'}</div>
          </div>
        )}

        {!loading && data?.ready && (
          <div style={{ display:'flex', flexDirection:'column', gap:'14px' }}>

            {/* Main */}
            <div style={{ display:'flex', alignItems:'center', gap:'16px' }}>
              <div>
                <div style={{ fontSize:'11px', color:'rgba(255,255,255,0.3)', marginBottom:'4px', fontWeight:500 }}>Next Predicted</div>
                <div style={{ fontSize:'20px', fontWeight:700, color:RISK_COLOR(data.predicted||''), lineHeight:1, fontFamily:'Inter,sans-serif' }}>{data.predicted}</div>
              </div>
              <div style={{ flex:1 }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'5px' }}>
                  <span style={{ fontSize:'11px', color:'rgba(255,255,255,0.3)' }}>Confidence</span>
                  <span style={{ fontSize:'12px', fontWeight:600, color:RISK_COLOR(data.predicted||'') }}>{data.confidence}%</span>
                </div>
                <div style={{ height:'4px', background:'rgba(255,255,255,0.07)', borderRadius:'2px' }}>
                  <div style={{ height:'100%', width:`${data.confidence}%`, background:RISK_COLOR(data.predicted||''), borderRadius:'2px', transition:'width 0.7s ease' }} />
                </div>
              </div>
            </div>

            {/* Recommendation */}
            {data.recommendation && (
              <div style={{ background:'rgba(61,214,140,0.05)', border:'1px solid rgba(61,214,140,0.12)', borderRadius:'8px', padding:'10px 14px' }}>
                <div style={{ fontSize:'10px', color:'rgba(61,214,140,0.4)', marginBottom:'4px', fontWeight:500 }}>PREEMPTIVE ACTION</div>
                <div style={{ fontSize:'11px', color:'rgba(61,214,140,0.7)', lineHeight:'1.6' }}>{data.recommendation}</div>
              </div>
            )}

            {/* Probabilities */}
            {data.probabilities && (
              <div>
                <div style={{ fontSize:'11px', fontWeight:500, color:'rgba(255,255,255,0.35)', marginBottom:'10px' }}>Class Probabilities</div>
                <div style={{ display:'flex', flexDirection:'column', gap:'7px' }}>
                  {Object.entries(data.probabilities).sort((a,b)=>b[1]-a[1]).map(([type, prob]) => {
                    const isPred = type === data.predicted;
                    const c      = isPred ? RISK_COLOR(type) : 'rgba(255,255,255,0.2)';
                    return (
                      <div key={type} style={{ display:'grid', gridTemplateColumns:'1fr 1fr 36px', gap:'10px', alignItems:'center' }}>
                        <span style={{ fontSize:'11px', color: isPred ? RISK_COLOR(type) : 'rgba(255,255,255,0.4)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', fontWeight: isPred ? 500 : 400 }}>
                          {isPred ? '▸ ' : ''}{type}
                        </span>
                        <div style={{ height:'3px', background:'rgba(255,255,255,0.06)', borderRadius:'2px' }}>
                          <div style={{ height:'100%', width:`${prob}%`, background:c, borderRadius:'2px', transition:'width 0.7s' }} />
                        </div>
                        <span style={{ fontSize:'11px', color:c, textAlign:'right', fontWeight: isPred?500:400 }}>{prob}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Sequence */}
            {data.sequence_used && (
              <div>
                <div style={{ fontSize:'11px', fontWeight:500, color:'rgba(255,255,255,0.25)', marginBottom:'7px' }}>Sequence Used</div>
                <div style={{ display:'flex', flexWrap:'wrap', gap:'4px' }}>
                  {data.sequence_used.map((s, i) => (
                    <span key={i} style={{ fontSize:'10px', padding:'2px 7px', borderRadius:'5px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.08)', color:'rgba(255,255,255,0.4)' }}>
                      {i+1}. {s}
                    </span>
                  ))}
                  <span style={{ fontSize:'10px', padding:'2px 7px', borderRadius:'5px', background:`${RISK_COLOR(data.predicted||'')}0f`, border:`1px solid ${RISK_COLOR(data.predicted||'')}25`, color:RISK_COLOR(data.predicted||'') }}>
                    → {data.predicted}?
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
