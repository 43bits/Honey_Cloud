/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState, useEffect, useCallback } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ScoreBreakdown {
  abuseipdb:     number;
  virustotal:    number;
  ml_model:      number;
  corroboration: number;
}

interface ThreatIntel {
  threat_intel_score: number;
  intel_level:        string;
  intel_color:        string;
  evidence:           string[];
  threat_tags:        string[];
  recommendation:     string;
  data_sources:       string[];
  score_breakdown?:   ScoreBreakdown;
  enriched_at:        string;
  abuseipdb?: {
    available:          boolean;
    abuse_confidence:   number;
    total_reports:      number;
    distinct_reporters: number;
    isp?:               string;
    domain?:            string;
    usage_type?:        string;
    is_whitelisted:     boolean;
    error?:             string;
  };
  virustotal?: {
    available:        boolean;
    malicious_votes:  number;
    suspicious_votes: number;
    harmless_votes:   number;
    total_engines:    number;
    malicious_ratio:  number;
    reputation:       number;
    categories:       string[];
    error?:           string;
  };
}

interface SelectedAttack {
  source_ip:           string;
  attack_type:         string;
  risk_level:          string;
  risk_score?:         number;
  country?:            string;
  threat_intel_score?: number;
  intel_level?:        string;
  [key: string]: any;
}

const LEVEL_META: Record<string, {
  color: string; bg: string; label: string;
}> = {
  CONFIRMED_THREAT: {
    color: '#ff2d2d',
    bg:    'rgba(255,45,45,0.1)',
    label: 'CONFIRMED THREAT',
  },
  HIGH_CONFIDENCE: {
    color: '#ff6b00',
    bg:    'rgba(255,107,0,0.1)',
    label: 'HIGH CONFIDENCE',
  },
  SUSPICIOUS: {
    color: '#ffe600',
    bg:    'rgba(255,230,0,0.08)',
    label: 'SUSPICIOUS',
  },
  LOW_RISK: {
    color: '#00ffe7',
    bg:    'rgba(0,255,231,0.06)',
    label: 'LOW RISK',
  },
  CLEAN: {
    color: '#00ff88',
    bg:    'rgba(0,255,136,0.06)',
    label: 'CLEAN',
  },
  LOCAL: {
    color: '#00ffe7',
    bg:    'rgba(0,255,231,0.04)',
    label: 'LOCAL TRAFFIC',
  },
  UNKNOWN: {
    color: '#888888',
    bg:    'rgba(136,136,136,0.08)',
    label: 'UNKNOWN',
  },
};

const ML_COLOR: Record<string, string> = {
  CRITICAL: '#ff2d2d',
  HIGH:     '#ff6b00',
  MEDIUM:   '#ffe600',
  LOW:      '#00ffe7',
};

const getMeta = (level: string) =>
  LEVEL_META[level] ?? LEVEL_META['UNKNOWN'];

// ── Sub-components ─────────────────────────────────

function ScoreBar({
  score, color, max = 100,
}: {
  score: number; color: string; max?: number;
}) {
  const pct = Math.min(Math.round((score / max) * 100), 100);
  return (
    <div className="flex items-center gap-2">
      <div
        className="flex-1 h-1.5 rounded-full overflow-hidden"
        style={{ background: 'rgba(255,255,255,0.06)' }}>
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width:     `${pct}%`,
            background: color,
            boxShadow: `0 0 6px ${color}55`,
          }}
        />
      </div>
      <span
        className="font-mono text-[10px] font-bold w-7
          text-right flex-shrink-0"
        style={{ color }}>
        {score}
      </span>
    </div>
  );
}

function BreakdownRow({
  label, score, max, color,
}: {
  label: string; score: number; max: number; color: string;
}) {
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span
          className="font-mono text-[9px]"
          style={{ color: 'rgba(0,255,231,0.4)' }}>
          {label}
        </span>
        <span
          className="font-mono text-[9px]"
          style={{ color: 'rgba(0,255,231,0.25)' }}>
          /{max}
        </span>
      </div>
      <ScoreBar score={score} color={color} max={max} />
    </div>
  );
}

function SourceCard({
  title, color, children,
}: {
  title: string; color: string; children: React.ReactNode;
}) {
  return (
    <div
      className="rounded p-3"
      style={{
        background: `${color}07`,
        border:     `1px solid ${color}25`,
      }}>
      <div
        className="font-mono text-[8px] tracking-widest mb-2"
        style={{ color: `${color}80` }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function Stat({
  label, value, color = 'rgba(200,220,255,0.7)',
}: {
  label: string; value: string | number; color?: string;
}) {
  return (
    <div>
      <div
        className="font-mono text-[17px] font-bold leading-none"
        style={{ color }}>
        {value}
      </div>
      <div
        className="font-mono text-[8px] mt-0.5"
        style={{ color: 'rgba(255,255,255,0.28)' }}>
        {label}
      </div>
    </div>
  );
}

function Tag({ text, color }: { text: string; color: string }) {
  return (
    <span
      className="font-mono text-[8px] px-2 py-0.5 rounded"
      style={{
        background: `${color}12`,
        border:     `1px solid ${color}30`,
        color,
      }}>
      {text.replace(/_/g, ' ')}
    </span>
  );
}

function SourceBadge({ source }: { source: string }) {
  const isML = source.includes('ML');
  return (
    <span
      className="font-mono text-[8px] px-2 py-0.5 rounded"
      style={{
        background: isML
          ? 'rgba(0,255,136,0.08)'
          : 'rgba(0,255,231,0.06)',
        border: `1px solid ${isML
          ? 'rgba(0,255,136,0.25)'
          : 'rgba(0,255,231,0.15)'}`,
        color: isML ? '#00ff88' : 'rgba(0,255,231,0.5)',
      }}>
      {source}
    </span>
  );
}

// ── Main component ─────────────────────────────────

export default function ThreatIntelPanel({
  selectedAttack,
}: {
  selectedAttack: SelectedAttack | null;
}) {
  const [intel,   setIntel]   = useState<ThreatIntel | null>(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [error,   setError]   = useState<string | null>(null);

  // ── Refresh summary every 10s — cheap local call ──
  const refreshSummary = useCallback(() => {
    fetch(`${API}/intel/stats/summary`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setSummary(d); })
      .catch(() => {});
  }, []);

  useEffect(() => {
    refreshSummary();
    const t = setInterval(refreshSummary, 10_000);
    return () => clearInterval(t);
  }, [refreshSummary]);

  // ── Reset when a different attack is selected ──────
  useEffect(() => {
    setIntel(null);
    setError(null);
    setLoading(false);

    // Pre-fill only if this attack was already enriched
    if (selectedAttack?.threat_intel_score !== undefined) {
      setIntel({
        threat_intel_score: selectedAttack.threat_intel_score ?? 0,
        intel_level:        selectedAttack.intel_level        ?? 'UNKNOWN',
        intel_color:        selectedAttack.intel_color        ?? '#00ffe7',
        evidence:           selectedAttack.evidence           ?? [],
        threat_tags:        selectedAttack.threat_tags        ?? [],
        recommendation:     selectedAttack.recommendation     ?? '',
        data_sources:       selectedAttack.data_sources       ?? [],
        score_breakdown:    selectedAttack.score_breakdown,
        enriched_at:        selectedAttack.enriched_at        ?? '',
        abuseipdb:          selectedAttack.abuseipdb,
        virustotal:         selectedAttack.virustotal,
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAttack?.source_ip, selectedAttack?.timestamp]);

  // ── Manual fetch — only on button click ───────────
  const handleFetch = async () => {
    if (!selectedAttack || loading || intel) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API}/intel/${selectedAttack.source_ip.trim()}`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setIntel(data);
      // Refresh summary after enrichment
      refreshSummary();
    } catch (e: any) {
      setError(e.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const mlColor = ML_COLOR[selectedAttack?.risk_level ?? 'LOW']
                  ?? '#00ffe7';
  const meta    = intel ? getMeta(intel.intel_level) : null;

  return (
    <div
  className="rounded overflow-hidden flex flex-col"
  style={{
    border:     '1px solid rgba(0,255,231,0.12)',
    background: 'rgba(0,0,0,0.4)',
    height:     '100%',
    minHeight:  '0',
  }}>

      {/* ── Header ── */}
      <div
        className="flex items-center justify-between
          px-4 py-3 flex-shrink-0"
        style={{
          background:   'rgba(0,255,231,0.04)',
          borderBottom: '1px solid rgba(0,255,231,0.08)',
        }}>
        <div className="flex flex-col gap-0.5">
          <span
            className="font-mono text-[9px] tracking-widest"
            style={{ color: 'rgba(0,255,231,0.55)' }}>
            THREAT INTELLIGENCE ENRICHMENT
          </span>
          <span
            className="font-mono text-[8px]"
            style={{ color: 'rgba(0,255,231,0.22)' }}>
            ABUSEIPDB · VIRUSTOTAL · ML (14.2M TRAINED)
          </span>
        </div>

        {/* Show confirmed count if any */}
        {summary?.confirmed_threats > 0 && (
          <span
            className="font-mono text-[9px] px-2 py-0.5 rounded"
            style={{
              color:      '#ff2d2d',
              background: 'rgba(255,45,45,0.1)',
              border:     '1px solid rgba(255,45,45,0.2)',
            }}>
            {summary.confirmed_threats} CONFIRMED
          </span>
        )}
      </div>

      {/* ── Idle — no attack selected ── */}
      {!selectedAttack && (
        <div
          className="flex-1 flex flex-col items-center
            justify-center gap-3 p-6"
          style={{ minHeight: '200px' }}>

          {/* Source badges */}
          <div className="flex flex-wrap gap-2 justify-center">
            {['AbuseIPDB', 'VirusTotal', 'HoneyCloud ML'].map(s => (
              <span
                key={s}
                className="font-mono text-[9px] px-2 py-0.5 rounded"
                style={{
                  background: s.includes('ML')
                    ? 'rgba(0,255,136,0.08)'
                    : 'rgba(0,255,231,0.06)',
                  border: `1px solid ${s.includes('ML')
                    ? 'rgba(0,255,136,0.2)'
                    : 'rgba(0,255,231,0.15)'}`,
                  color: s.includes('ML')
                    ? '#00ff88'
                    : 'rgba(0,255,231,0.45)',
                }}>
                ● {s}
              </span>
            ))}
          </div>

          <div
            className="font-mono text-[10px] blink mt-1"
            style={{ color: 'rgba(0,255,231,0.18)' }}>
            ← SELECT AN ATTACK ROW TO INVESTIGATE
          </div>
        </div>
      )}

      {/* ── Attack selected ── */}
      {selectedAttack && (
        <div className="flex flex-col flex-1 min-h-0">

          {/* Selected attack context bar */}
          <div
            className="px-4 py-2.5 flex items-center
              gap-3 flex-shrink-0"
            style={{
              background:   `${mlColor}08`,
              borderBottom: '1px solid rgba(0,255,231,0.07)',
            }}>
            <div
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{
                background: mlColor,
                boxShadow:  `0 0 6px ${mlColor}`,
              }}
            />
            <span
              className="font-mono text-xs font-bold"
              style={{ color: mlColor }}>
              {selectedAttack.source_ip}
            </span>
            <span
              className="font-mono text-[10px]"
              style={{ color: 'rgba(200,220,255,0.5)' }}>
              {selectedAttack.attack_type}
            </span>
            {selectedAttack.country && (
              <span
                className="font-mono text-[9px]"
                style={{ color: 'rgba(0,255,231,0.35)' }}>
                {selectedAttack.country}
              </span>
            )}
            {/* ML score badge — labelled clearly */}
            <span
              className="font-mono text-[9px] ml-auto
                px-2 py-0.5 rounded flex-shrink-0"
              style={{
                color:      mlColor,
                background: `${mlColor}15`,
                border:     `1px solid ${mlColor}30`,
              }}>
              ML {selectedAttack.risk_level}
              {selectedAttack.risk_score !== undefined
                ? ` · ${selectedAttack.risk_score}` : ''}
            </span>
          </div>

          {/* ── Pre-fetch state — button ── */}
          {!intel && (
            <div
              className="flex-1 flex flex-col items-center
                justify-center gap-4 py-8">

              <div className="text-center">
                <div
                  className="font-mono text-[10px] tracking-widest mb-1"
                  style={{ color: 'rgba(0,255,231,0.35)' }}>
                  EXTERNAL THREAT DATABASE LOOKUP
                </div>
                <div
                  className="font-mono text-[9px]"
                  style={{ color: 'rgba(0,255,231,0.18)' }}>
                  AbuseIPDB + VirusTotal + ML cross-correlation
                </div>
              </div>

              <button
                onClick={handleFetch}
                disabled={loading}
                className="flex items-center gap-2 px-6 py-3
                  rounded font-mono text-[11px] tracking-widest
                  transition-all hover:scale-105 active:scale-95
                  disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: loading
                    ? 'rgba(255,230,0,0.08)'
                    : `${mlColor}15`,
                  border: `1px solid ${
                    loading ? '#ffe600' : mlColor
                  }`,
                  color:     loading ? '#ffe600' : mlColor,
                  boxShadow: `0 0 20px ${
                    loading ? '#ffe60033' : mlColor + '33'
                  }`,
                }}>
                {loading ? (
                  <>
                    <span style={{
                      display:   'inline-block',
                      animation: 'spin 1s linear infinite',
                    }}>
                      ⟳
                    </span>
                    <span>QUERYING INTEL SOURCES...</span>
                  </>
                ) : (
                  <>
                    <span>🔎</span>
                    <span>FETCH THREAT INTEL</span>
                  </>
                )}
              </button>

              <div className="flex gap-3">
                {['AbuseIPDB', 'VirusTotal', 'ML Model'].map(s => (
                  <span
                    key={s}
                    className="font-mono text-[8px]"
                    style={{ color: 'rgba(0,255,231,0.2)' }}>
                    ● {s}
                  </span>
                ))}
              </div>

              {error && (
                <div
                  className="font-mono text-[9px] px-3 py-2 rounded"
                  style={{
                    color:      '#ff2d2d',
                    background: 'rgba(255,45,45,0.08)',
                    border:     '1px solid rgba(255,45,45,0.2)',
                  }}>
                  ✗ {error}
                </div>
              )}
            </div>
          )}

          {/* ── Result ── */}
          {intel && meta && (
            <div className="flex-1 overflow-y-auto p-4 space-y-3">

              {/* Score card */}
              <div
                className="rounded overflow-hidden"
                style={{ border: `1px solid ${meta.color}25` }}>

                {/* Score header */}
                <div
                  className="px-4 py-3 flex items-center
                    justify-between"
                  style={{ background: meta.bg }}>
                  <div>
                    <div
                      className="font-mono text-[9px] tracking-widest"
                      style={{ color: `${meta.color}70` }}>
                      THREAT INTEL SCORE
                    </div>
                    <div
                      className="font-mono text-3xl font-bold mt-0.5"
                      style={{ color: meta.color }}>
                      {intel.threat_intel_score}
                      <span
                        className="text-sm font-normal ml-1"
                        style={{ color: `${meta.color}50` }}>
                        / 100
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div
                      className="font-mono text-[10px] px-2 py-1
                        rounded font-bold tracking-widest"
                      style={{
                        color:      meta.color,
                        background: `${meta.color}15`,
                        border:     `1px solid ${meta.color}40`,
                      }}>
                      {meta.label}
                    </div>
                    <div
                      className="font-mono text-[8px] mt-1"
                      style={{ color: 'rgba(0,255,231,0.2)' }}>
                      reputation-based
                    </div>
                  </div>
                </div>

                {/* Breakdown bars */}
                {intel.score_breakdown && (
                  <div
                    className="px-4 py-3 space-y-2.5"
                    style={{
                      borderTop: `1px solid ${meta.color}12`,
                    }}>
                    <div
                      className="font-mono text-[9px]
                        tracking-widest mb-2"
                      style={{ color: 'rgba(0,255,231,0.28)' }}>
                      SCORE BREAKDOWN
                    </div>
                    <BreakdownRow
                      label="AbuseIPDB community reports"
                      score={intel.score_breakdown.abuseipdb}
                      max={45}
                      color="#ff2d2d"
                    />
                    <BreakdownRow
                      label="VirusTotal engine detections"
                      score={intel.score_breakdown.virustotal}
                      max={40}
                      color="#ff6b00"
                    />
                    <BreakdownRow
                      label="ML model (14.2M trained)"
                      score={intel.score_breakdown.ml_model}
                      max={15}
                      color="#00ff88"
                    />
                    {(intel.score_breakdown.corroboration ?? 0) > 0 && (
                      <BreakdownRow
                        label="Multi-source corroboration"
                        score={intel.score_breakdown.corroboration}
                        max={8}
                        color="#00ffe7"
                      />
                    )}
                  </div>
                )}
              </div>

              {/* Source cards */}
              <div className="grid grid-cols-2 gap-2">

                <SourceCard
                  title="ABUSEIPDB"
                  color={
                    intel.abuseipdb?.available ? '#ff2d2d' : '#444444'
                  }>
                  {intel.abuseipdb?.available ? (
                    <div className="space-y-1.5">
                      <div className="grid grid-cols-2 gap-2">
                        <Stat
                          label="confidence"
                          value={`${intel.abuseipdb.abuse_confidence}%`}
                          color={
                            intel.abuseipdb.abuse_confidence >= 75
                              ? '#ff2d2d'
                              : intel.abuseipdb.abuse_confidence >= 40
                              ? '#ff6b00'
                              : '#ffe600'
                          }
                        />
                        <Stat
                          label="reports"
                          value={intel.abuseipdb.total_reports}
                        />
                      </div>
                      {intel.abuseipdb.isp && (
                        <div
                          className="font-mono text-[8px] truncate"
                          style={{ color: 'rgba(0,255,231,0.3)' }}>
                          {intel.abuseipdb.isp}
                        </div>
                      )}
                      {intel.abuseipdb.usage_type && (
                        <div
                          className="font-mono text-[8px]"
                          style={{ color: 'rgba(0,255,231,0.22)' }}>
                          {intel.abuseipdb.usage_type}
                        </div>
                      )}
                      {intel.abuseipdb.distinct_reporters > 1 && (
                        <div
                          className="font-mono text-[8px]"
                          style={{ color: 'rgba(0,255,231,0.28)' }}>
                          {intel.abuseipdb.distinct_reporters} reporters
                        </div>
                      )}
                      {intel.abuseipdb.is_whitelisted && (
                        <div
                          className="font-mono text-[8px]"
                          style={{ color: '#00ff88' }}>
                          ✓ Whitelisted
                        </div>
                      )}
                    </div>
                  ) : (
                    <div
                      className="font-mono text-[9px]"
                      style={{ color: 'rgba(255,255,255,0.18)' }}>
                      {intel.abuseipdb?.error ?? 'Not available'}
                    </div>
                  )}
                </SourceCard>

                <SourceCard
                  title="VIRUSTOTAL"
                  color={
                    intel.virustotal?.available ? '#ff6b00' : '#444444'
                  }>
                  {intel.virustotal?.available ? (
                    <div className="space-y-1.5">
                      <div className="grid grid-cols-2 gap-2">
                        <Stat
                          label="malicious"
                          value={intel.virustotal.malicious_votes}
                          color={
                            intel.virustotal.malicious_votes >= 10
                              ? '#ff2d2d'
                              : intel.virustotal.malicious_votes >= 3
                              ? '#ff6b00'
                              : 'rgba(200,220,255,0.7)'
                          }
                        />
                        <Stat
                          label={`/${intel.virustotal.total_engines}`}
                          value={`${intel.virustotal.malicious_ratio}%`}
                        />
                      </div>
                      <div className="flex gap-3">
                        <span
                          className="font-mono text-[8px]"
                          style={{ color: 'rgba(255,230,0,0.5)' }}>
                          {intel.virustotal.suspicious_votes} susp
                        </span>
                        <span
                          className="font-mono text-[8px]"
                          style={{ color: 'rgba(0,255,136,0.5)' }}>
                          {intel.virustotal.harmless_votes} clean
                        </span>
                      </div>
                      <div
                        className="font-mono text-[8px]"
                        style={{
                          color: intel.virustotal.reputation < -50
                            ? '#ff2d2d'
                            : intel.virustotal.reputation < 0
                            ? '#ff6b00'
                            : 'rgba(0,255,136,0.6)',
                        }}>
                        rep: {intel.virustotal.reputation}
                      </div>
                      {intel.virustotal.categories.length > 0 && (
                        <div
                          className="font-mono text-[8px] truncate"
                          style={{ color: 'rgba(0,255,231,0.28)' }}>
                          {intel.virustotal.categories[0]}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div
                      className="font-mono text-[9px]"
                      style={{ color: 'rgba(255,255,255,0.18)' }}>
                      {intel.virustotal?.error ?? 'Not available'}
                    </div>
                  )}
                </SourceCard>
              </div>

              {/* Threat tags */}
              {intel.threat_tags.length > 0 && (
                <div>
                  <div
                    className="font-mono text-[9px] tracking-widest mb-2"
                    style={{ color: 'rgba(0,255,231,0.28)' }}>
                    THREAT TAGS
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {intel.threat_tags.map(tag => (
                      <Tag key={tag} text={tag} color="#ff2d2d" />
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence chain */}
              {intel.evidence.length > 0 && (
                <div>
                  <div
                    className="font-mono text-[9px] tracking-widest mb-2"
                    style={{ color: 'rgba(0,255,231,0.28)' }}>
                    EVIDENCE CHAIN
                  </div>
                  <div className="space-y-1.5">
                    {intel.evidence.map((e, i) => (
                      <div key={i} className="flex gap-2 items-start">
                        <span
                          className="font-mono text-[9px] mt-0.5
                            flex-shrink-0 w-5 text-right"
                          style={{ color: 'rgba(0,255,231,0.22)' }}>
                          {String(i + 1).padStart(2, '0')}
                        </span>
                        <span
                          className="font-mono text-[10px]
                            leading-relaxed"
                          style={{ color: 'rgba(180,210,240,0.72)' }}>
                          {e}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendation */}
              <div
                className="rounded p-3"
                style={{
                  background: 'rgba(0,255,136,0.05)',
                  border:     '1px solid rgba(0,255,136,0.15)',
                }}>
                <div
                  className="font-mono text-[9px] tracking-widest mb-1.5"
                  style={{ color: 'rgba(0,255,136,0.5)' }}>
                  🛡 ANALYST RECOMMENDATION
                </div>
                <div
                  className="font-mono text-[10px] leading-relaxed"
                  style={{ color: 'rgba(0,255,136,0.85)' }}>
                  {intel.recommendation}
                </div>
              </div>

              {/* Footer */}
              <div
                className="flex items-center justify-between pt-2"
                style={{
                  borderTop: '1px solid rgba(0,255,231,0.06)',
                }}>
                <div className="flex flex-wrap gap-1.5">
                  {intel.data_sources.map(s => (
                    <SourceBadge key={s} source={s} />
                  ))}
                </div>
                <button
                  onClick={() => {
                    setIntel(null);
                    setError(null);
                  }}
                  className="font-mono text-[9px] hover:underline ml-2
                    flex-shrink-0"
                  style={{ color: 'rgba(0,255,231,0.3)' }}>
                  re-check
                </button>
              </div>

            </div>
          )}
        </div>
      )}
    </div>
  );
}