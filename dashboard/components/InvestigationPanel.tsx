// // components/InvestigationPanel.tsx
// 'use client';

// import { useState, useEffect } from 'react';

// const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// interface Investigation {
//   key:              string;
//   attack_ip:        string;
//   attack_type:      string;
//   risk_level:       string;
//   mitre_id:         string;
//   log_analysis:     string;
//   investigation:    string;
//   risk_assessment:  string;
//   response_actions: string;
//   generated_at:     string;
//   elapsed_seconds:  number;
// }

// const riskColor = (r: string) => {
//   if (r === 'CRITICAL') return '#ff2d2d';
//   if (r === 'HIGH')     return '#ff6b00';
//   if (r === 'MEDIUM')   return '#ffe600';
//   return '#00ffe7';
// };

// const AGENTS = [
//   { key: 'log_analysis',     label: 'LOG ANALYSIS',      icon: '🔬', color: '#00ffe7' },
//   { key: 'investigation',    label: 'THREAT CONTEXT',     icon: '🕵️', color: '#ff6b00' },
//   { key: 'risk_assessment',  label: 'RISK ASSESSMENT',    icon: '🎯', color: '#ff2d2d' },
//   { key: 'response_actions', label: 'RESPONSE ACTIONS',   icon: '🛡️', color: '#00ff88' },
// ] as const;

// function InvestigationCard({
//   inv,
//   isOpen,
//   onToggle,
// }: {
//   inv:      Investigation;
//   isOpen:   boolean;
//   onToggle: () => void;
// }) {
//   const color      = riskColor(inv.risk_level);
//   const [tab, setTab] = useState<typeof AGENTS[number]['key']>('log_analysis');

//   return (
//     <div
//       className="rounded overflow-hidden mb-3"
//       style={{ border: `1px solid ${color}22` }}
//     >
//       {/* Card header — click to expand */}
//       <button
//         onClick={onToggle}
//         className="w-full flex items-center justify-between px-4 py-3
//           transition-all hover:bg-white/5 text-left"
//         style={{ background: `${color}08` }}
//       >
//         <div className="flex items-center gap-3">
//           {/* Risk indicator */}
//           <div
//             className="w-2 h-2 rounded-full flex-shrink-0"
//             style={{ background: color, boxShadow: `0 0 6px ${color}` }}
//           />

//           {/* IP + type */}
//           <div>
//             <span
//               className="font-mono text-xs font-bold"
//               style={{ color }}
//             >
//               {inv.attack_ip}
//             </span>
//             <span
//               className="font-mono text-xs ml-3"
//               style={{ color: 'rgba(200,220,255,0.6)' }}
//             >
//               {inv.attack_type}
//             </span>
//           </div>
//         </div>

//         <div className="flex items-center gap-4">
//           {/* MITRE badge */}
//           <span
//             className="font-mono text-[10px] px-2 py-0.5 rounded"
//             style={{
//               color,
//               background: `${color}15`,
//               border:     `1px solid ${color}30`,
//             }}
//           >
//             {inv.mitre_id}
//           </span>

//           {/* Time */}
//           <span
//             className="font-mono text-[9px]"
//             style={{ color: 'rgba(0,255,231,0.3)' }}
//           >
//             {inv.generated_at.slice(11, 16)}
//           </span>

//           {/* Elapsed */}
//           <span
//             className="font-mono text-[9px]"
//             style={{ color: 'rgba(0,255,231,0.2)' }}
//           >
//             {inv.elapsed_seconds}s
//           </span>

//           {/* Chevron */}
//           <span
//             className="font-mono text-xs transition-transform"
//             style={{
//               color:     'rgba(0,255,231,0.3)',
//               transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
//             }}
//           >
//             ▼
//           </span>
//         </div>
//       </button>

//       {/* Expanded content */}
//       {isOpen && (
//         <div className="sweep-in">
//           {/* Agent tabs */}
//           <div
//             className="flex border-b"
//             style={{ borderColor: 'rgba(0,255,231,0.08)' }}
//           >
//             {AGENTS.map((agent) => (
//               <button
//                 key={agent.key}
//                 onClick={() => setTab(agent.key)}
//                 className="flex items-center gap-2 px-4 py-2.5
//                   font-mono text-[9px] tracking-widest transition-all
//                   hover:bg-white/5"
//                 style={{
//                   color: tab === agent.key
//                     ? agent.color
//                     : 'rgba(0,255,231,0.3)',
//                   borderBottom: tab === agent.key
//                     ? `2px solid ${agent.color}`
//                     : '2px solid transparent',
//                   background: tab === agent.key
//                     ? `${agent.color}08`
//                     : 'transparent',
//                 }}
//               >
//                 <span className="text-l leading-none">{agent.icon}</span>
//                 <span className="hidden sm:inline">{agent.label}</span>
//               </button>
//             ))}
//           </div>

//           {/* Tab content */}
//           <div className="p-4">
//             {AGENTS.map((agent) => (
//               tab === agent.key && (
//                 <div key={agent.key}>
//                   <div
//                     className="font-mono text-[9px] tracking-widest mb-3"
//                     style={{ color: `${agent.color}60` }}
//                   >
//                     {agent.icon} AGENT {AGENTS.indexOf(agent) + 1}
//                     {' — '}{agent.label}
//                   </div>
//                   <div
//                     className="font-mono text-xs leading-relaxed
//                       whitespace-pre-wrap"
//                     style={{ color: 'rgba(180,210,240,0.8)' }}
//                   >
//                     {inv[agent.key]}
//                   </div>
//                 </div>
//               )
//             ))}
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }

// export default function InvestigationPanel() {
//   const [investigations, setInvestigations] = useState<Investigation[]>([]);
//   const [openKey,        setOpenKey]        = useState<string | null>(null);
//   const [loading,        setLoading]        = useState(true);

//   useEffect(() => {
//     const load = async () => {
//       try {
//         const res  = await fetch(`${API}/investigations?limit=10`);
//         const data = await res.json();
//         setInvestigations(data.investigations || []);
//       } catch {}
//       finally { setLoading(false); }
//     };

//     load();
//     const t = setInterval(load, 8000);  // refresh every 8s
//     return () => clearInterval(t);
//   }, []);

//   return (
//     <div
//       className="rounded overflow-hidden"
//       style={{
//         border:     '1px solid rgba(0,255,231,0.12)',
//         background: 'rgba(0,0,0,0.4)',
//       }}
//     >
//       {/* Header */}
//       <div
//         className="flex items-center justify-between px-4 py-3"
//         style={{
//           background:   'rgba(0,255,231,0.04)',
//           borderBottom: '1px solid rgba(0,255,231,0.08)',
//         }}
//       >
//         <div>
//           <span
//             className="font-mono text-[9px] tracking-widest"
//             style={{ color: 'rgba(0,255,231,0.5)' }}
//           >
//             AI THREAT INTELLIGENCE AGENT
//           </span>
//           <span
//             className="font-mono text-[9px] ml-4"
//             style={{ color: 'rgba(0,255,231,0.25)' }}
//           >
//             AUTO-INVESTIGATES HIGH + CRITICAL ATTACKS
//           </span>
//         </div>
//         <div
//           className="font-mono text-[9px]"
//           style={{ color: 'rgba(0,255,231,0.3)' }}
//         >
//           {investigations.length} REPORTS
//         </div>
//       </div>

//       {/* Content */}
//       <div className="p-3">
//         {loading ? (
//           <div
//             className="py-10 text-center font-mono text-sm"
//             style={{ color: 'rgba(0,255,231,0.2)' }}
//           >
//             <span className="blink">loading investigations_</span>
//           </div>
//         ) : investigations.length === 0 ? (
//           <div
//             className="py-10 text-center font-mono text-sm"
//             style={{ color: 'rgba(0,255,231,0.2)' }}
//           >
//             <div className="blink mb-2">awaiting high-risk attacks_</div>
//             <div
//               className="text-[10px]"
//               style={{ color: 'rgba(0,255,231,0.15)' }}
//             >
//               Investigations auto-trigger for HIGH and CRITICAL threats
//             </div>
//           </div>
//         ) : (
//           investigations.map((inv) => (
//             <InvestigationCard
//               key={inv.key}
//               inv={inv}
//               isOpen={openKey === inv.key}
//               onToggle={() =>
//                 setOpenKey(openKey === inv.key ? null : inv.key)
//               }
//             />
//           ))
//         )}
//       </div>

//       {/* Agent pipeline legend */}
//       <div
//         className="px-4 py-3 flex flex-wrap gap-4"
//         style={{ borderTop: '1px solid rgba(0,255,231,0.06)' }}
//       >
//         {AGENTS.map((a, i) => (
//           <div key={a.key} className="flex items-center gap-2">
//             <span
//               className="font-mono text-[9px] w-4 h-4 rounded-full
//                 flex items-center justify-center"
//               style={{
//                 background: `${a.color}20`,
//                 border:     `1px solid ${a.color}40`,
//                 color:      a.color,
//               }}
//             >
//               {i + 1}
//             </span>
//             <span
//               className="font-mono text-[9px]"
//               style={{ color: 'rgba(255,255,255,0.25)' }}
//             >
//               {a.label}
//             </span>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// }

'use client';

import { useState, useEffect } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Investigation {
  key:              string;
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

interface AttackItem {
  source_ip:           string;
  attack_type:         string;
  risk_level:          string;
  mitre_technique_id?: string;
  timestamp:           string;
  country?:            string;
  port_targeted?:      number;
}

const riskColor = (r: string) => {
  if (r === 'CRITICAL') return '#ff2d2d';
  if (r === 'HIGH')     return '#ff6b00';
  if (r === 'MEDIUM')   return '#ffe600';
  return '#00ffe7';
};

const AGENTS = [
  { key: 'log_analysis',     label: 'LOG ANALYSIS',    icon: '🔬', color: '#00ffe7' },
  { key: 'investigation',    label: 'THREAT CONTEXT',  icon: '🕵️', color: '#ff6b00' },
  { key: 'risk_assessment',  label: 'RISK ASSESSMENT', icon: '🎯', color: '#ff2d2d' },
  { key: 'response_actions', label: 'RESPONSE ACTIONS',icon: '🛡️', color: '#00ff88' },
] as const;

const BLUR_PREVIEW: Record<typeof AGENTS[number]['key'], string> = {
  log_analysis: `Analyzing attack log indicators...

- Source IP flagged for repeated connection attempts
- Target port matches known exploitation vector
- Connection rate exceeds normal threshold by 340%
- Protocol fingerprint consistent with automated tooling
- Geographic origin correlates with known threat cluster
- Anomaly score indicates deviation from baseline traffic
- Payload signature matches credential stuffing pattern`,

  investigation: `Based on the provided indicators, here is the investigation result:

The likely threat actor type is a cybercriminal, given the nature of the attack being a brute force attempt to gain access to a system. The attack campaign characteristics suggest that this is part of a larger Credential Stuffing Campaign, where automated tools try a large number of username and password combinations.

The probable attacker objective is credential theft. This could be a precursor to further malicious activities such as ransomware staging, data exfiltration, or lateral movement within the network.`,

  risk_assessment: `Risk assessment for current attack vector:

- Immediate systems at risk: SSH daemon, authentication service
- Potential business impact: unauthorized access, data breach
- Assets that could be compromised: user credentials, system access
- Likelihood of escalation: HIGH — pattern consistent with persistent threat
- Severity rating: CRITICAL — requires immediate response

If attack succeeds, attacker gains foothold for lateral movement across internal network segments.`,

  response_actions: `Immediate response actions required:

1. Block source IP range at perimeter firewall immediately
2. Enable SSH rate limiting — max 3 attempts per minute per IP
3. Force password reset for all accounts targeted during window
4. Review auth logs for any successful logins from similar IP ranges
5. Deploy honeytokens on SSH service to detect future attempts`,
};

function InvestigationCard({
  attack,
  isOpen,
  onToggle,
}: {
  attack:   AttackItem;
  isOpen:   boolean;
  onToggle: () => void;
}) {
  const [report,  setReport]  = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState<typeof AGENTS[number]['key']>('log_analysis');

  const color = riskColor(attack.risk_level);
  const time  = new Date(attack.timestamp).toLocaleTimeString('en-GB');

  const handleViewInsights = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (loading || report) return;
    setLoading(true);
    try {
      const res  = await fetch(`${API}/investigate`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_ip:     attack.source_ip,
          port_targeted: attack.port_targeted || 22,
          protocol:      'tcp',
          country:       attack.country || 'Unknown',
        }),
      });
      const data = await res.json();
      if (data.investigation && !data.investigation.skipped) {
        setReport(data.investigation);
      }
    } catch (err) {
      console.error('Investigation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="rounded overflow-hidden mb-2"
      style={{ border: `1px solid ${color}22` }}
    >
      {/* ── Clickable row header ── */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between
          px-4 py-3 transition-all hover:bg-white/5 text-left"
        style={{ background: `${color}08` }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ background: color, boxShadow: `0 0 6px ${color}` }}
          />
          <span className="font-mono text-xs font-bold" style={{ color }}>
            {attack.source_ip}
          </span>
          <span
            className="font-mono text-xs"
            style={{ color: 'rgba(200,220,255,0.6)' }}
          >
            {attack.attack_type}
          </span>
        </div>

        <div className="flex items-center gap-3">
          {attack.mitre_technique_id && (
            <span
              className="font-mono text-[10px] px-2 py-0.5 rounded"
              style={{
                color,
                background: `${color}15`,
                border:     `1px solid ${color}30`,
              }}
            >
              {attack.mitre_technique_id}
            </span>
          )}
          <span
            className="font-mono text-[9px]"
            style={{ color: 'rgba(0,255,231,0.3)' }}
          >
            {time}
          </span>
          <span
            className="font-mono text-xs"
            style={{
              color:     'rgba(0,255,231,0.3)',
              transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
              display:   'inline-block',
              transition:'transform 0.2s',
            }}
          >
            ▼
          </span>
        </div>
      </button>

      {/* ── Expanded panel ── */}
      {isOpen && (
        <div className="sweep-in">

          {/* Agent tab bar — always visible when expanded */}
          <div
            className="flex border-b"
            style={{ borderColor: 'rgba(0,255,231,0.08)' }}
          >
            {AGENTS.map((agent) => (
              <button
                key={agent.key}
                onClick={() => setTab(agent.key)}
                className="flex items-center gap-2 px-4 py-2.5
                  font-mono text-[9px] tracking-widest
                  transition-all hover:bg-white/5"
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
                }}
              >
                <span>{agent.icon}</span>
                <span className="hidden sm:inline">{agent.label}</span>
              </button>
            ))}
          </div>

          {/* Tab content area */}
         {/* Tab content area */}
          <div className="relative" style={{ minHeight: '180px' }}>

            {/* Before investigation — blank + button */}
            {!report && (
              <div
                className="absolute inset-0 flex flex-col
                  items-center justify-center gap-3"
              >
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
                <span
                  className="font-mono text-[9px] tracking-widest"
                  style={{ color: 'rgba(0,255,231,0.25)' }}
                >
                  CLICK TO RUN AI INVESTIGATION
                </span>
              </div>
            )}

            {/* After investigation — show real text */}
            {report && (
              <div className="p-4">
                <div
                  className="font-mono text-[9px] tracking-widest mb-3"
                  style={{ color: 'rgba(0,255,231,0.3)' }}
                >
                  {AGENTS.find(a => a.key === tab)?.icon}
                  {' AGENT '}{AGENTS.findIndex(a => a.key === tab) + 1}
                  {' — '}{AGENTS.find(a => a.key === tab)?.label}
                  <span
                    className="ml-3"
                    style={{ color: 'rgba(0,255,231,0.15)' }}
                  >
                    {report.elapsed_seconds}s
                  </span>
                </div>
                <div
                  className="font-mono text-xs leading-relaxed
                    whitespace-pre-wrap"
                  style={{ color: 'rgba(180,210,240,0.8)' }}
                >
                  {report[tab as keyof Investigation] as string}
                </div>
              </div>
            )}
          </div>

          {/* Elapsed time footer — only after report */}
          {report && (
            <div
              className="px-4 pb-3 font-mono text-[9px]"
              style={{ color: 'rgba(0,255,231,0.2)' }}
            >
              Generated in {report.elapsed_seconds}s
              &nbsp;·&nbsp;
              {report.generated_at}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function InvestigationPanel() {
  const [attacks, setAttacks] = useState<AttackItem[]>([]);
  const [openKey, setOpenKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res  = await fetch(`${API}/attacks?limit=50`);
        const data = await res.json();
        const highRisk = (data.attacks || [])
          .filter((a: AttackItem) =>
            a.risk_level === 'HIGH' || a.risk_level === 'CRITICAL'
          )
          .slice(0, 10);
        setAttacks(highRisk);
      } catch {}
      finally { setLoading(false); }
    };

    load();
    const t = setInterval(load, 8000);
    return () => clearInterval(t);
  }, []);

  const getKey = (a: AttackItem, i: number) =>
    `${a.source_ip}-${a.timestamp}-${i}`;

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
            AI THREAT INTELLIGENCE AGENT
          </span>
          <span
            className="font-mono text-[9px] ml-4"
            style={{ color: 'rgba(0,255,231,0.25)' }}
          >
            CLICK ROW → VIEW INSIGHTS TO INVESTIGATE
          </span>
        </div>
        <div
          className="font-mono text-[9px]"
          style={{ color: 'rgba(0,255,231,0.3)' }}
        >
          {attacks.length} HIGH/CRITICAL ATTACKS
        </div>
      </div>

      {/* List */}
      <div className="p-3">
        {loading ? (
          <div
            className="py-10 text-center font-mono text-sm"
            style={{ color: 'rgba(0,255,231,0.2)' }}
          >
            <span className="blink">loading attacks_</span>
          </div>
        ) : attacks.length === 0 ? (
          <div
            className="py-10 text-center font-mono"
            style={{ color: 'rgba(0,255,231,0.2)' }}
          >
            <div className="blink mb-2 text-sm">
              awaiting high-risk attacks_
            </div>
            <div
              className="text-[10px]"
              style={{ color: 'rgba(0,255,231,0.15)' }}
            >
              Only HIGH and CRITICAL attacks appear here
            </div>
          </div>
        ) : (
          attacks.map((attack, i) => {
            const key = getKey(attack, i);
            return (
              <InvestigationCard
                key={key}
                attack={attack}
                isOpen={openKey === key}
                onToggle={() =>
                  setOpenKey(openKey === key ? null : key)
                }
              />
            );
          })
        )}
      </div>

      {/* Legend */}
      <div
        className="px-4 py-3 flex flex-wrap gap-4"
        style={{ borderTop: '1px solid rgba(0,255,231,0.06)' }}
      >
        {AGENTS.map((a, i) => (
          <div key={a.key} className="flex items-center gap-2">
            <span
              className="font-mono text-[9px] w-4 h-4 rounded-full
                flex items-center justify-center"
              style={{
                background: `${a.color}20`,
                border:     `1px solid ${a.color}40`,
                color:      a.color,
              }}
            >
              {i + 1}
            </span>
            <span
              className="font-mono text-[9px]"
              style={{ color: 'rgba(255,255,255,0.25)' }}
            >
              {a.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}