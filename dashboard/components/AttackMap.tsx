// /* eslint-disable @typescript-eslint/no-explicit-any */
// // components/AttackMap.tsx
// 'use client';

// import { useEffect, useRef, useState } from 'react';
// import type { Attack } from '@/lib/api';

// // Server honeypot location (your "home base")
// const HOME = { lat: 20.5937, lon: 78.9629, label: 'HoneyCloud Server' }; // India

// interface MapAttack extends Attack {
//   lat: number;
//   lon: number;
//   animKey: string;
// }

// export default function AttackMap({ attacks }: { attacks: Attack[] }) {
//   const mapRef       = useRef<any>(null);
//   const mapInstance  = useRef<any>(null);
//   const linesRef     = useRef<any[]>([]);
//   const markersRef   = useRef<any[]>([]);
//   const [ready, setReady] = useState(false);

//   const riskColor = (risk: string) => {
//     if (risk === 'CRITICAL') return '#ff2d2d';
//     if (risk === 'HIGH')     return '#ff6b00';
//     if (risk === 'MEDIUM')   return '#ffe600';
//     return '#00ffe7';
//   };

//   // Init map (client-side only — Leaflet needs window)
//   useEffect(() => {
//     if (typeof window === 'undefined' || mapInstance.current) return;

//     import('leaflet').then((L) => {
//       // Fix default icon paths
//       // eslint-disable-next-line @typescript-eslint/no-explicit-any
//       delete (L.Icon.Default.prototype as any)._getIconUrl;
//       L.Icon.Default.mergeOptions({
//         iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
//         iconUrl:       'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
//         shadowUrl:     'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
//       });

//       const map = L.map(mapRef.current!, {
//         center:          [20, 10],
//         zoom:            2,
//         zoomControl:     true,
//         attributionControl: false,
//         minZoom:         2,
//         maxZoom:         6,
//       });

//       // Dark tile layer
//       L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
//         maxZoom: 19,
//       }).addTo(map);

//       // Home marker (honeypot server)
//       const homeIcon = L.divIcon({
//         html: `<div style="
//           width:14px;height:14px;
//           background:#00ffe7;
//           border:2px solid #fff;
//           border-radius:50%;
//           box-shadow:0 0 12px #00ffe7, 0 0 24px #00ffe7;
//         "></div>`,
//         className: '',
//         iconSize: [14, 14],
//         iconAnchor: [7, 7],
//       });

//       L.marker([HOME.lat, HOME.lon], { icon: homeIcon })
//         .addTo(map)
//         .bindTooltip('🛡 HoneyCloud Sentinel', {
//           permanent: false,
//           className: 'leaflet-tooltip-dark',
//         });

//       mapInstance.current = map;
//       setReady(true);
//     });

//     return () => {
//       if (mapInstance.current) {
//         mapInstance.current.remove();
//         mapInstance.current = null;
//       }
//     };
//   }, []);

//   // Draw attack lines whenever attacks update
//   useEffect(() => {
//     if (!ready || !mapInstance.current) return;

//     import('leaflet').then((L) => {
//       const map = mapInstance.current;

//       // Remove old lines and markers beyond last 30
//       while (linesRef.current.length > 30) {
//         const old = linesRef.current.shift();
//         try { map.removeLayer(old); } catch {}
//       }
//       while (markersRef.current.length > 30) {
//         const old = markersRef.current.shift();
//         try { map.removeLayer(old); } catch {}
//       }

//       // Draw the 5 newest attacks that have valid coords
//       const fresh = attacks
//         .filter(a => a.lat && a.lon && !(a.lat === 0 && a.lon === 0))
//         .slice(0, 5);

//       fresh.forEach((attack) => {
//         const color   = riskColor(attack.risk_level);
//         const srcLatLon: [number, number] = [attack.lat, attack.lon];
//         const dstLatLon: [number, number] = [HOME.lat, HOME.lon];

//         // Animated arc line
//         const line = L.polyline([srcLatLon, dstLatLon], {
//           color,
//           weight:    1.5,
//           opacity:   0.7,
//           dashArray: '6 4',
//         }).addTo(map);

//         // Source marker with ping
//         const attackIcon = L.divIcon({
//           html: `
//             <div style="position:relative;width:20px;height:20px;">
//               <div style="
//                 position:absolute;inset:0;
//                 border-radius:50%;
//                 background:${color};
//                 opacity:0.2;
//                 animation:radar-ping 1.5s ease-out infinite;
//               "></div>
//               <div style="
//                 position:absolute;top:5px;left:5px;
//                 width:10px;height:10px;
//                 background:${color};
//                 border-radius:50%;
//                 box-shadow:0 0 8px ${color};
//               "></div>
//             </div>`,
//           className: '',
//           iconSize:  [20, 20],
//           iconAnchor:[10, 10],
//         });

//         const marker = L.marker(srcLatLon, { icon: attackIcon })
//           .addTo(map)
//           .bindPopup(`
//             <div style="
//               background:#020810;
//               border:1px solid ${color};
//               border-radius:4px;
//               padding:10px;
//               font-family:'Share Tech Mono',monospace;
//               font-size:11px;
//               color:#00ffe7;
//               min-width:180px;
//             ">
//               <div style="color:${color};font-size:13px;margin-bottom:6px;">
//                 ${attack.emoji} ${attack.risk_level}
//               </div>
//               <div>IP: ${attack.source_ip}</div>
//               <div>Type: ${attack.attack_type}</div>
//               <div>Port: ${attack.port_targeted}</div>
//               <div>Country: ${attack.country}</div>
//               ${attack.city ? `<div>City: ${attack.city}</div>` : ''}
//               <div style="color:#666;margin-top:4px;font-size:10px;">
//                 ${attack.timestamp}
//               </div>
//             </div>
//           `, { className: 'leaflet-popup-dark' });

//         linesRef.current.push(line);
//         markersRef.current.push(marker);

//         // Fade out line after 8 seconds
//         setTimeout(() => {
//           try { map.removeLayer(line); } catch {}
//         }, 8000);
//       });
//     });
//   }, [attacks, ready]);

//   return (
//     <div className="relative w-full h-full rounded-lg overflow-hidden border border-cyan-500/20">
//       {/* Map container */}
//       <div ref={mapRef} className="w-full h-full" style={{ background: '#020810' }} />

//       {/* Corner overlays */}
//       <div className="absolute top-3 left-3 z-[1000] pointer-events-none">
//         <div className="text-[10px] font-mono text-cyan-400/70 tracking-widest">
//           GLOBAL THREAT MAP
//         </div>
//         <div className="text-[9px] font-mono text-cyan-400/40 mt-0.5">
//           REAL-TIME ATTACK ORIGINS
//         </div>
//       </div>

//       <div className="absolute top-3 right-3 z-[1000] pointer-events-none flex flex-col gap-1">
//         {[
//           { label: 'CRITICAL', color: '#ff2d2d' },
//           { label: 'HIGH',     color: '#ff6b00' },
//           { label: 'MEDIUM',   color: '#ffe600' },
//           { label: 'LOW',      color: '#00ffe7' },
//         ].map(({ label, color }) => (
//           <div key={label} className="flex items-center gap-1.5">
//             <div className="w-2 h-2 rounded-full" style={{ background: color, boxShadow: `0 0 4px ${color}` }} />
//             <span className="text-[9px] font-mono" style={{ color }}>{label}</span>
//           </div>
//         ))}
//       </div>

//       {/* Bottom status bar */}
//       <div className="absolute bottom-3 left-3 right-3 z-[1000] pointer-events-none flex justify-between">
//         <div className="text-[9px] font-mono text-cyan-400/40">
//           🛡 HONEYPOT: INDIA
//         </div>
//         <div className="text-[9px] font-mono text-cyan-400/40 blink">
//           ● MONITORING
//         </div>
//       </div>
//     </div>
//   );
// }

/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useEffect, useRef, useState } from 'react';
import type { Attack } from '@/lib/api';

const HOME = { lat: 20.5937, lon: 78.9629 };

interface MapAttack extends Attack {
  lat: number;
  lon: number;
}

const riskColor = (risk: string) => {
  if (risk === 'CRITICAL') return '#ff2d2d';
  if (risk === 'HIGH')     return '#ff6b00';
  if (risk === 'MEDIUM')   return '#ffe600';
  return '#00ffe7';
};

export default function AttackMap({
  attacks,
  selectedAttack,
}: {
  attacks:          Attack[];
  selectedAttack?:  Attack | null;
}) {
  const mapRef      = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const linesRef    = useRef<any[]>([]);
  const markersRef  = useRef<any[]>([]);
  const [ready,   setReady]   = useState(false);
  const [mapMode, setMapMode] = useState<'live' | 'view'>('live');

  // ── Init map ───────────────────────────────────────
  useEffect(() => {
    if (typeof window === 'undefined' || mapInstance.current) return;

    import('leaflet').then((L) => {
      delete (L.Icon.Default.prototype as any)._getIconUrl;

      const map = L.map(mapRef.current!, {
        center:             [20, 10],
        zoom:               2,
        // Move zoom controls to bottom-right
        // so our toggle at bottom-left doesn't clash
        zoomControl:        false,
        attributionControl: false,
        minZoom:            2,
        maxZoom:            6,
      });

      // Re-add zoom at bottom-right
      L.control.zoom({ position: 'bottomright' }).addTo(map);

      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        { maxZoom: 19 }
      ).addTo(map);

      // Home marker
      const homeIcon = L.divIcon({
        html: `<div style="
          width:14px;height:14px;
          background:#00ffe7;border:2px solid #fff;
          border-radius:50%;
          box-shadow:0 0 12px #00ffe7,0 0 24px #00ffe7;">
        </div>`,
        className: '',
        iconSize:   [14, 14],
        iconAnchor: [7,  7],
      });

      L.marker([HOME.lat, HOME.lon], { icon: homeIcon })
        .addTo(map)
        .bindTooltip('🛡 HoneyCloud Sentinel');

      mapInstance.current = map;
      setReady(true);
    });

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  // ── LIVE mode — draw recent attack lines ───────────
  useEffect(() => {
    if (!ready || !mapInstance.current || mapMode !== 'live') return;

    import('leaflet').then((L) => {
      const map = mapInstance.current;

      while (linesRef.current.length > 30) {
        const old = linesRef.current.shift();
        try { map.removeLayer(old); } catch {}
      }
      while (markersRef.current.length > 30) {
        const old = markersRef.current.shift();
        try { map.removeLayer(old); } catch {}
      }

      const fresh = (attacks as MapAttack[])
        .filter(a => a.lat && a.lon && !(a.lat === 0 && a.lon === 0))
        .slice(0, 8);

      fresh.forEach((attack) => {
        const color = riskColor(attack.risk_level);

        const line = L.polyline(
          [[attack.lat, attack.lon], [HOME.lat, HOME.lon]],
          { color, weight: 1.5, opacity: 0.7, dashArray: '6 4' }
        ).addTo(map);

        const icon = L.divIcon({
          html: `
            <div style="position:relative;width:20px;height:20px;">
              <div style="position:absolute;inset:0;border-radius:50%;
                background:${color};opacity:0.2;
                animation:radar-ping 1.5s ease-out infinite;"></div>
              <div style="position:absolute;top:5px;left:5px;
                width:10px;height:10px;background:${color};
                border-radius:50%;box-shadow:0 0 8px ${color};"></div>
            </div>`,
          className: '',
          iconSize:   [20, 20],
          iconAnchor: [10, 10],
        });

        const marker = L.marker([attack.lat, attack.lon], { icon })
          .addTo(map)
          .bindPopup(`
            <div style="background:#020810;border:1px solid ${color};
              border-radius:4px;padding:10px;
              font-family:'Share Tech Mono',monospace;
              font-size:11px;color:#00ffe7;min-width:180px;">
              <div style="color:${color};font-size:13px;margin-bottom:6px;">
                ${attack.emoji} ${attack.risk_level}
              </div>
              <div>IP: ${attack.source_ip}</div>
              <div>Type: ${attack.attack_type}</div>
              <div>Port: ${attack.port_targeted}</div>
              <div>Country: ${attack.country}</div>
              ${(attack as any).city
                ? `<div>City: ${(attack as any).city}</div>` : ''}
            </div>
          `);

        linesRef.current.push(line);
        markersRef.current.push(marker);

        setTimeout(() => {
          try { map.removeLayer(line); } catch {}
        }, 8000);
      });
    });
  }, [attacks, ready, mapMode]);

  // ── VIEW mode — show selected attack ──────────────
  useEffect(() => {
    if (!ready || !mapInstance.current || mapMode !== 'view') return;
    if (!selectedAttack) return;

    import('leaflet').then((L) => {
      linesRef.current.forEach(l => {
        try { mapInstance.current.removeLayer(l); } catch {}
      });
      markersRef.current.forEach(m => {
        try { mapInstance.current.removeLayer(m); } catch {}
      });
      linesRef.current  = [];
      markersRef.current = [];

      const a = selectedAttack as MapAttack;
      if (!a.lat || !a.lon || (a.lat === 0 && a.lon === 0)) return;

      const color = riskColor(a.risk_level);

      mapInstance.current.flyTo([a.lat, a.lon], 4, { duration: 1.2 });

      const line = L.polyline(
        [[a.lat, a.lon], [HOME.lat, HOME.lon]],
        { color, weight: 2, opacity: 0.9, dashArray: '4 3' }
      ).addTo(mapInstance.current);

      const srcIcon = L.divIcon({
        html: `
          <div style="position:relative;width:28px;height:28px;">
            <div style="position:absolute;inset:0;border-radius:50%;
              background:${color};opacity:0.15;
              animation:radar-ping 1s ease-out infinite;"></div>
            <div style="position:absolute;inset:4px;border-radius:50%;
              background:${color};opacity:0.25;
              animation:radar-ping 1s ease-out infinite;
              animation-delay:0.3s;"></div>
            <div style="position:absolute;top:9px;left:9px;
              width:10px;height:10px;background:${color};
              border-radius:50%;
              box-shadow:0 0 12px ${color},0 0 24px ${color};"></div>
          </div>`,
        className: '',
        iconSize:   [28, 28],
        iconAnchor: [14, 14],
      });

      const marker = L.marker([a.lat, a.lon], { icon: srcIcon })
        .addTo(mapInstance.current)
        .bindPopup(`
          <div style="background:#020810;border:1px solid ${color};
            border-radius:4px;padding:12px;
            font-family:'Share Tech Mono',monospace;
            font-size:11px;color:#00ffe7;min-width:200px;">
            <div style="color:${color};font-size:13px;
              font-weight:bold;margin-bottom:8px;">
              ${a.emoji} ${a.risk_level} — SELECTED
            </div>
            <div>IP: ${a.source_ip}</div>
            <div>Attack: ${a.attack_type}</div>
            <div>Port: ${a.port_targeted}</div>
            <div>Country: ${a.country}</div>
            <div>City: ${(a as any).city || '—'}</div>
            <div style="margin-top:6px;color:rgba(0,255,231,0.4)">
              MITRE: ${(a as any).mitre_technique_id || '—'}
            </div>
          </div>
        `)
        .openPopup();

      linesRef.current.push(line);
      markersRef.current.push(marker);
    });
  }, [selectedAttack, ready, mapMode]);

  // Re-center when switching back to live
  useEffect(() => {
    if (!ready || !mapInstance.current) return;
    if (mapMode === 'live') {
      mapInstance.current.flyTo([20, 10], 2, { duration: 1 });
    }
  }, [mapMode, ready]);

  return (
    <div className="relative w-full h-full rounded-lg overflow-hidden"
      style={{ border: '1px solid rgba(0,255,231,0.2)' }}>

      {/* Map */}
      <div ref={mapRef} className="w-full h-full"
        style={{ background: '#020810' }} />

      {/* Top-left — title */}
      <div className="absolute top-3 left-3 z-[1000] pointer-events-none">
        <div className="font-mono text-[10px] tracking-widest"
          style={{ color: 'rgba(0,255,231,0.7)' }}>
          {mapMode === 'live' ? 'GLOBAL THREAT MAP' : 'ATTACK ORIGIN VIEW'}
        </div>
        <div className="font-mono text-[8px] mt-0.5"
          style={{ color: 'rgba(0,255,231,0.35)' }}>
          {mapMode === 'live'
            ? 'REAL-TIME ATTACK ORIGINS'
            : selectedAttack
              ? `${selectedAttack.source_ip} — ${selectedAttack.attack_type}`
              : 'SELECT AN ATTACK FROM THE FEED'}
        </div>
      </div>

      {/* Top-right — legend */}
      <div className="absolute top-3 right-3 z-[1000]
        pointer-events-none flex flex-col gap-1">
        {[
          { label: 'CRITICAL', color: '#ff2d2d' },
          { label: 'HIGH',     color: '#ff6b00' },
          { label: 'MEDIUM',   color: '#ffe600' },
          { label: 'LOW',      color: '#00ffe7' },
        ].map(({ label, color }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full"
              style={{ background: color,
                       boxShadow: `0 0 4px ${color}` }} />
            <span className="font-mono text-[8px]"
              style={{ color }}>{label}</span>
          </div>
        ))}
      </div>

      {/* ── LIVE / VIEW toggle — bottom-left ──────────
          Positioned just above the bottom status bar.
          Does NOT overlap zoom buttons (bottom-right). */}
      <div className="absolute z-[1000] flex rounded overflow-hidden"
        style={{
          bottom:  '36px',
          left:    '10px',
          border:  '1px solid rgba(0,255,231,0.3)',
          boxShadow: '0 0 12px rgba(0,255,231,0.1)',
        }}>
        {(['live', 'view'] as const).map((mode, idx) => (
          <button
            key={mode}
            onClick={() => setMapMode(mode)}
            className="px-3 py-1.5 font-mono text-[10px]
              tracking-widest transition-all"
            style={{
              background: mapMode === mode
                ? 'rgba(0,255,231,0.18)'
                : 'rgba(2,8,16,0.9)',
              color: mapMode === mode
                ? '#00ffe7'
                : 'rgba(0,255,231,0.35)',
              borderRight: idx === 0
                ? '1px solid rgba(0,255,231,0.3)'
                : 'none',
            }}>
            {mode === 'live' ? (
              <span className="flex items-center gap-1.5">
                <span
                  style={{
                    width:        6,
                    height:       6,
                    borderRadius: '50%',
                    background:   mapMode === 'live'
                      ? '#00ffe7'
                      : 'rgba(0,255,231,0.3)',
                    display:      'inline-block',
                    boxShadow:    mapMode === 'live'
                      ? '0 0 6px #00ffe7' : 'none',
                    animation:    mapMode === 'live'
                      ? 'pulse-glow 2s infinite' : 'none',
                  }}
                />
                LIVE
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <span style={{ fontSize: 11 }}>🔍</span>
                VIEW
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Bottom status bar */}
      <div className="absolute bottom-3 left-3 right-3 z-[1000]
        pointer-events-none flex justify-between items-center">
        <div className="font-mono text-[8px]"
          style={{ color: 'rgba(0,255,231,0.35)' }}>
          🛡 HONEYPOT: INDIA
        </div>
        <div className="font-mono text-[8px] blink"
          style={{ color: 'rgba(0,255,231,0.35)' }}>
          ● MONITORING
        </div>
      </div>

      {/* VIEW mode — no attack hint */}
      {mapMode === 'view' && !selectedAttack && (
        <div className="absolute inset-0 flex items-center
          justify-center z-[999] pointer-events-none">
          <div className="font-mono text-[10px] tracking-widest
            text-center px-5 py-2.5 rounded"
            style={{
              background: 'rgba(2,8,16,0.85)',
              border:     '1px solid rgba(0,255,231,0.15)',
              color:      'rgba(0,255,231,0.4)',
            }}>
            SELECT AN ATTACK ROW TO VIEW ON MAP
          </div>
        </div>
      )}
    </div>
  );
}