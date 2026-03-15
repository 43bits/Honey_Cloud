// components/PredictionPanel.tsx
'use client';

import { useState, useEffect } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Prediction {
  ready:          boolean;
  reason?:        string;
  predicted?:     string;
  confidence?:    number;
  probabilities?: Record<string, number>;
  recommendation?: string;
  sequence_used?: string[];
}

const riskColor = (attack: string) => {
  if (attack === 'Database Attack')   return '#ff2d2d';
  if (attack === 'SSH Brute Force')   return '#ff6b00';
  if (attack === 'Telnet Attack')     return '#ff2d2d';
  if (attack === 'Web Exploit')       return '#ff6b00';
  if (attack === 'FTP Attack')        return '#ffe600';
  return '#00ffe7';
};

const confidenceLabel = (c: number) => {
  if (c >= 80) return { label: 'HIGH CONFIDENCE',   color: '#ff2d2d' };
  if (c >= 60) return { label: 'MEDIUM CONFIDENCE', color: '#ff6b00' };
  return         { label: 'LOW CONFIDENCE',          color: '#ffe600' };
};

export default function PredictionPanel() {
  const [data,        setData]        = useState<Prediction | null>(null);
  const [loading,     setLoading]     = useState(true);
  const [retraining,  setRetraining]  = useState(false);
  const [lastUpdated, setLastUpdated] = useState('');

  const fetchPrediction = async () => {
    try {
      const res = await fetch(`${API}/predict/next`);
      setData(await res.json());
      setLastUpdated(new Date().toLocaleTimeString('en-GB'));
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => {
    fetchPrediction();
    const t = setInterval(fetchPrediction, 10000);
    return () => clearInterval(t);
  }, []);

  const handleRetrain = async () => {
    setRetraining(true);
    try {
      await fetch(`${API}/predict/train`, { method: 'POST' });
      setTimeout(() => {
        fetchPrediction();
        setRetraining(false);
      }, 5000);
    } catch {
      setRetraining(false);
    }
  };

  return (
    <div
      className="rounded overflow-hidden"
      style={{
        border:     '1px solid rgba(0,255,231,0.12)',
        background: 'rgba(0,0,0,0.4)',
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{
          background:   'rgba(0,255,231,0.04)',
          borderBottom: '1px solid rgba(0,255,231,0.08)',
        }}
      >
        <div>
          <span
            className="font-mono text-[9px] tracking-widest"
            style={{ color: 'rgba(0,255,231,0.5)' }}
          >
            LSTM ATTACK PREDICTION ENGINE
          </span>
          <span
            className="font-mono text-[9px] ml-4"
            style={{ color: 'rgba(0,255,231,0.25)' }}
          >
            NEXT LIKELY ATTACK
          </span>
        </div>
        <div className="flex items-center gap-3">
          {lastUpdated && (
            <span
              className="font-mono text-[9px]"
              style={{ color: 'rgba(0,255,231,0.2)' }}
            >
              {lastUpdated}
            </span>
          )}
          <button
            onClick={handleRetrain}
            disabled={retraining}
            className="font-mono text-[9px] px-3 py-1 rounded
              tracking-widest transition-all hover:scale-105
              disabled:opacity-40"
            style={{
              border:     '1px solid rgba(0,255,231,0.2)',
              color:      'rgba(0,255,231,0.4)',
              background: 'rgba(0,255,231,0.04)',
            }}
          >
            {retraining ? '⟳ TRAINING...' : '↺ RETRAIN'}
          </button>
        </div>
      </div>

      <div className="p-4">
        {loading ? (
          <div
            className="py-8 text-center font-mono text-sm"
            style={{ color: 'rgba(0,255,231,0.2)' }}
          >
            <span className="blink">loading prediction_</span>
          </div>

        ) : !data?.ready ? (
          <div
            className="py-8 text-center font-mono"
            style={{ color: 'rgba(0,255,231,0.2)' }}
          >
            <div className="text-sm blink mb-2">
              model warming up_
            </div>
            <div className="text-[10px]">
              {data?.reason || 'Need more attack data'}
            </div>
            <div className="text-[10px] mt-1">
              Run demo script to generate attacks,
              then click RETRAIN
            </div>
          </div>

        ) : (
          <div className="space-y-4">

            {/* Main prediction */}
            <div className="flex items-center gap-6">
              <div>
                <div
                  className="font-mono text-[9px] tracking-widest mb-1"
                  style={{ color: 'rgba(0,255,231,0.35)' }}
                >
                  PREDICTED NEXT ATTACK
                </div>
                <div
                  className="font-mono text-2xl font-bold"
                  style={{
                    color:      riskColor(data.predicted || ''),
                    textShadow: `0 0 20px ${riskColor(data.predicted || '')}55`,
                  }}
                >
                  {data.predicted}
                </div>
              </div>

              {/* Confidence gauge */}
              <div className="flex-1">
                <div className="flex justify-between mb-1">
                  <span
                    className="font-mono text-[9px] tracking-widest"
                    style={{
                      color: confidenceLabel(data.confidence || 0).color,
                    }}
                  >
                    {confidenceLabel(data.confidence || 0).label}
                  </span>
                  <span
                    className="font-mono text-[9px] font-bold"
                    style={{
                      color: confidenceLabel(data.confidence || 0).color,
                    }}
                  >
                    {data.confidence}%
                  </span>
                </div>
                <div
                  className="h-2 rounded-full"
                  style={{ background: 'rgba(255,255,255,0.05)' }}
                >
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width:     `${data.confidence}%`,
                      background: confidenceLabel(data.confidence || 0).color,
                      boxShadow:  `0 0 8px ${
                        confidenceLabel(data.confidence || 0).color
                      }`,
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Recommendation */}
            {data.recommendation && (
              <div
                className="px-4 py-3 rounded font-mono text-xs"
                style={{
                  background: 'rgba(0,255,136,0.05)',
                  border:     '1px solid rgba(0,255,136,0.15)',
                  color:      'rgba(0,255,136,0.8)',
                  lineHeight: '1.6',
                }}
              >
                <span
                  className="text-[9px] tracking-widest block mb-1"
                  style={{ color: 'rgba(0,255,136,0.4)' }}
                >
                  🛡 PREEMPTIVE ACTION
                </span>
                {data.recommendation}
              </div>
            )}

            {/* Probability bars */}
            {data.probabilities && (
              <div>
                <div
                  className="font-mono text-[9px] tracking-widest mb-2"
                  style={{ color: 'rgba(0,255,231,0.35)' }}
                >
                  ALL CLASS PROBABILITIES
                </div>
                <div className="space-y-1.5">
                  {Object.entries(data.probabilities)
                    .sort((a, b) => b[1] - a[1])
                    .map(([type, prob]) => (
                      <div
                        key={type}
                        className="grid gap-2 items-center"
                        style={{
                          gridTemplateColumns: '160px 1fr 40px',
                        }}
                      >
                        <span
                          className="font-mono text-[10px] truncate"
                          style={{
                            color: type === data.predicted
                              ? riskColor(type)
                              : 'rgba(0,255,231,0.4)',
                          }}
                        >
                          {type === data.predicted ? '▸ ' : '  '}
                          {type}
                        </span>
                        <div
                          className="h-1.5 rounded-full"
                          style={{ background: 'rgba(255,255,255,0.04)' }}
                        >
                          <div
                            className="h-full rounded-full transition-all duration-700"
                            style={{
                              width:     `${prob}%`,
                              background: type === data.predicted
                                ? riskColor(type)
                                : 'rgba(0,255,231,0.3)',
                              boxShadow: type === data.predicted
                                ? `0 0 6px ${riskColor(type)}`
                                : 'none',
                            }}
                          />
                        </div>
                        <span
                          className="font-mono text-[10px] text-right"
                          style={{
                            color: type === data.predicted
                              ? riskColor(type)
                              : 'rgba(0,255,231,0.3)',
                          }}
                        >
                          {prob}%
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Sequence used */}
            {data.sequence_used && (
              <div>
                <div
                  className="font-mono text-[9px] tracking-widest mb-2"
                  style={{ color: 'rgba(0,255,231,0.25)' }}
                >
                  SEQUENCE USED FOR PREDICTION
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {data.sequence_used.map((s, i) => (
                    <span
                      key={i}
                      className="font-mono text-[9px] px-2 py-0.5 rounded"
                      style={{
                        background: 'rgba(0,255,231,0.05)',
                        border:     '1px solid rgba(0,255,231,0.12)',
                        color:      'rgba(0,255,231,0.4)',
                      }}
                    >
                      {i + 1}. {s}
                    </span>
                  ))}
                  <span
                    className="font-mono text-[9px] px-2 py-0.5 rounded
                      blink"
                    style={{
                      background: `${riskColor(data.predicted || '')}15`,
                      border:     `1px solid ${riskColor(data.predicted || '')}40`,
                      color:      riskColor(data.predicted || ''),
                    }}
                  >
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