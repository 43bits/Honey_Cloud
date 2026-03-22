// // components/GlobalHoneypotNetwork.tsx
// 'use client';

// import { useState, useEffect } from 'react';
// import { fetchGeoStats } from '@/lib/api';
// import type { GeoStats } from '@/lib/api';

// // City to region mapping
// const CITY_REGION: Record<string, string> = {
//   'Frankfurt':     'Europe',
//   'Amsterdam':     'Europe',
//   'London':        'Europe',
//   'New York':      'Americas',
//   'Toronto':       'Americas',
//   'San Francisco': 'Americas',
//   'Singapore':     'Asia Pacific',
//   'Bangalore':     'Asia Pacific',
// };

// // City coordinates for the mini dots
// const CITY_COORDS: Record<string, { x: number; y: number }> = {
//   'Frankfurt':     { x: 52,  y: 28 },
//   'Amsterdam':     { x: 50,  y: 25 },
//   'London':        { x: 47,  y: 26 },
//   'New York':      { x: 24,  y: 33 },
//   'Toronto':       { x: 22,  y: 30 },
//   'San Francisco': { x: 10,  y: 35 },
//   'Singapore':     { x: 78,  y: 55 },
//   'Bangalore':     { x: 72,  y: 48 },
// };

// function formatCount(n: number): string {
//   if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
//   if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}K`;
//   return String(n);
// }

// function intensityColor(rank: number, total: number): string {
//   const ratio = 1 - rank / total;
//   if (ratio > 0.75) return '#ff2d2d';
//   if (ratio > 0.50) return '#ff6b00';
//   if (ratio > 0.25) return '#ffe600';
//   return '#00ffe7';
// }

// export default function GlobalHoneypotNetwork() {
//   const [data,    setData]    = useState<GeoStats | null>(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     fetchGeoStats().then(d => {
//       setData(d);
//       setLoading(false);
//     });
//   }, []);

//   if (loading) {
//     return (
//       <div
//         className="rounded p-6 flex items-center justify-center"
//         style={{
//           border:     '1px solid rgba(0,255,231,0.12)',
//           background: 'rgba(0,0,0,0.4)',
//           minHeight:  80,
//         }}
//       >
//         <span
//           className="font-mono text-xs blink"
//           style={{ color: 'rgba(0,255,231,0.3)' }}
//         >
//           loading hornet 40 data_
//         </span>
//       </div>
//     );
//   }

//   if (!data) {
//     return (
//       <div
//         className="rounded p-4 flex items-center justify-between"
//         style={{
//           border:     '1px solid rgba(0,255,231,0.08)',
//           background: 'rgba(0,0,0,0.3)',
//         }}
//       >
//         <span
//           className="font-mono text-[10px]"
//           style={{ color: 'rgba(0,255,231,0.25)' }}
//         >
//           GLOBAL HONEYPOT NETWORK — run process_hornet40.py to enable
//         </span>
//       </div>
//     );
//   }

//   const sorted = Object.entries(data.city_totals)
//     .sort((a, b) => b[1] - a[1]);

//   const maxVal       = sorted[0]?.[1] || 1;
//   const topCity      = sorted[0]?.[0] || '—';
//   const peakHour     = data.peak_hours[topCity] ?? '—';
//   const busiestDay   = Object.keys(data.busiest_days)[0] || '—';

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
//             🌐 GLOBAL HONEYPOT NETWORK
//           </span>
//           <span
//             className="font-mono text-[9px] ml-3"
//             style={{ color: 'rgba(0,255,231,0.25)' }}
//           >
//             HORNET 40 DATASET — 8 LOCATIONS · 40 DAYS
//           </span>
//         </div>
//         <span
//           className="font-mono text-[9px] font-bold"
//           style={{ color: 'rgba(0,255,231,0.4)' }}
//         >
//           {formatCount(data.total_events)} TOTAL EVENTS
//         </span>
//       </div>

//       <div className="p-4">
//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

//           {/* Left — city bars */}
//           <div className="lg:col-span-2 space-y-2">
//             {sorted.map(([city, count], i) => {
//               const pct   = Math.round((count / maxVal) * 100);
//               const color = intensityColor(i, sorted.length);
//               const region = CITY_REGION[city] || 'Unknown';

//               return (
//                 <div key={city} className="flex items-center gap-3">
//                   {/* Rank */}
//                   <span
//                     className="font-mono text-[9px] w-4 text-right flex-shrink-0"
//                     style={{ color: 'rgba(0,255,231,0.2)' }}
//                   >
//                     {i + 1}
//                   </span>

//                   {/* City name */}
//                   <div className="flex-shrink-0" style={{ width: '100px' }}>
//                     <div
//                       className="font-mono text-[10px] font-bold truncate"
//                       style={{ color }}
//                     >
//                       {city}
//                     </div>
//                     <div
//                       className="font-mono text-[8px]"
//                       style={{ color: 'rgba(0,255,231,0.25)' }}
//                     >
//                       {region}
//                     </div>
//                   </div>

//                   {/* Bar */}
//                   <div className="flex-1">
//                     <div
//                       className="h-4 rounded-sm relative overflow-hidden"
//                       style={{ background: 'rgba(255,255,255,0.04)' }}
//                     >
//                       <div
//                         className="h-full rounded-sm transition-all duration-700"
//                         style={{
//                           width:      `${pct}%`,
//                           background: `linear-gradient(90deg, ${color}cc, ${color}44)`,
//                           boxShadow:  `0 0 8px ${color}44`,
//                         }}
//                       />
//                       {/* Peak hour badge inside bar */}
//                       {data.peak_hours[city] !== undefined && (
//                         <span
//                           className="absolute right-1 top-0 bottom-0
//                             flex items-center font-mono text-[8px]"
//                           style={{ color: 'rgba(255,255,255,0.3)' }}
//                         >
//                           peak {String(data.peak_hours[city]).padStart(2,'0')}:00
//                         </span>
//                       )}
//                     </div>
//                   </div>

//                   {/* Count */}
//                   <span
//                     className="font-mono text-[10px] font-bold flex-shrink-0"
//                     style={{ color, width: '42px', textAlign: 'right' }}
//                   >
//                     {formatCount(count)}
//                   </span>
//                 </div>
//               );
//             })}
//           </div>

//           {/* Right — 3 insight cards */}
//           <div className="flex flex-col gap-3">

//             {/* Most targeted */}
//             <div
//               className="rounded p-3 flex-1"
//               style={{
//                 background: 'rgba(255,45,45,0.05)',
//                 border:     '1px solid rgba(255,45,45,0.15)',
//               }}
//             >
//               <div
//                 className="font-mono text-[8px] tracking-widest mb-1"
//                 style={{ color: 'rgba(255,45,45,0.5)' }}
//               >
//                 MOST TARGETED
//               </div>
//               <div
//                 className="font-mono text-lg font-bold"
//                 style={{ color: '#ff2d2d' }}
//               >
//                 {topCity}
//               </div>
//               <div
//                 className="font-mono text-[9px] mt-1"
//                 style={{ color: 'rgba(255,45,45,0.4)' }}
//               >
//                 {formatCount(maxVal)} attacks recorded
//               </div>
//             </div>

//             {/* Peak attack hour */}
//             <div
//               className="rounded p-3 flex-1"
//               style={{
//                 background: 'rgba(255,230,0,0.05)',
//                 border:     '1px solid rgba(255,230,0,0.15)',
//               }}
//             >
//               <div
//                 className="font-mono text-[8px] tracking-widest mb-1"
//                 style={{ color: 'rgba(255,230,0,0.5)' }}
//               >
//                 PEAK ATTACK HOUR
//               </div>
//               <div
//                 className="font-mono text-lg font-bold"
//                 style={{ color: '#ffe600' }}
//               >
//                 {String(peakHour).padStart(2, '0')}:00 UTC
//               </div>
//               <div
//                 className="font-mono text-[9px] mt-1"
//                 style={{ color: 'rgba(255,230,0,0.4)' }}
//               >
//                 attackers prefer night hours
//               </div>
//             </div>

//             {/* Busiest day */}
//             <div
//               className="rounded p-3 flex-1"
//               style={{
//                 background: 'rgba(0,255,136,0.05)',
//                 border:     '1px solid rgba(0,255,136,0.15)',
//               }}
//             >
//               <div
//                 className="font-mono text-[8px] tracking-widest mb-1"
//                 style={{ color: 'rgba(0,255,136,0.5)' }}
//               >
//                 BUSIEST DAY
//               </div>
//               <div
//                 className="font-mono text-lg font-bold"
//                 style={{ color: '#00ff88' }}
//               >
//                 {busiestDay.slice(0, 3).toUpperCase()}
//               </div>
//               <div
//                 className="font-mono text-[9px] mt-1"
//                 style={{ color: 'rgba(0,255,136,0.4)' }}
//               >
//                 automated campaigns start Mondays
//               </div>
//             </div>
//           </div>
//         </div>

//         {/* Bottom region summary */}
//         <div
//           className="mt-4 pt-3 flex flex-wrap gap-6"
//           style={{ borderTop: '1px solid rgba(0,255,231,0.06)' }}
//         >
//           {['Europe', 'Americas', 'Asia Pacific'].map(region => {
//             const regionTotal = sorted
//               .filter(([city]) => CITY_REGION[city] === region)
//               .reduce((sum, [, count]) => sum + count, 0);
//             return (
//               <div key={region} className="flex items-center gap-2">
//                 <span
//                   className="font-mono text-[9px]"
//                   style={{ color: 'rgba(0,255,231,0.35)' }}
//                 >
//                   {region}
//                 </span>
//                 <span
//                   className="font-mono text-[9px] font-bold"
//                   style={{ color: 'rgba(0,255,231,0.6)' }}
//                 >
//                   {formatCount(regionTotal)}
//                 </span>
//               </div>
//             );
//           })}
//           <div className="flex items-center gap-2 ml-auto">
//             <span
//               className="font-mono text-[8px]"
//               style={{ color: 'rgba(0,255,231,0.2)' }}
//             >
//               SOURCE: HORNET 40 DATASET — MENDELEY DATA
//             </span>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }








    {/* ── Global Honeypot Network ── */}
{/* <div>
  <div
    className="text-[9px] font-mono tracking-widest mb-2"
    style={{ color: 'rgba(0,255,231,0.35)' }}
  >
    GLOBAL HONEYPOT NETWORK INTELLIGENCE
  </div>
  <GlobalHoneypotNetwork />
</div> */}