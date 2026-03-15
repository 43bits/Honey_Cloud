/* eslint-disable @typescript-eslint/no-explicit-any */
// components/AttackMap.tsx
'use client';

import { useEffect, useRef, useState } from 'react';
import type { Attack } from '@/lib/api';

// Server honeypot location (your "home base")
const HOME = { lat: 20.5937, lon: 78.9629, label: 'HoneyCloud Server' }; // India

interface MapAttack extends Attack {
  lat: number;
  lon: number;
  animKey: string;
}

export default function AttackMap({ attacks }: { attacks: Attack[] }) {
  const mapRef       = useRef<any>(null);
  const mapInstance  = useRef<any>(null);
  const linesRef     = useRef<any[]>([]);
  const markersRef   = useRef<any[]>([]);
  const [ready, setReady] = useState(false);

  const riskColor = (risk: string) => {
    if (risk === 'CRITICAL') return '#ff2d2d';
    if (risk === 'HIGH')     return '#ff6b00';
    if (risk === 'MEDIUM')   return '#ffe600';
    return '#00ffe7';
  };

  // Init map (client-side only — Leaflet needs window)
  useEffect(() => {
    if (typeof window === 'undefined' || mapInstance.current) return;

    import('leaflet').then((L) => {
      // Fix default icon paths
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl:       'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl:     'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      });

      const map = L.map(mapRef.current!, {
        center:          [20, 10],
        zoom:            2,
        zoomControl:     true,
        attributionControl: false,
        minZoom:         2,
        maxZoom:         6,
      });

      // Dark tile layer
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
      }).addTo(map);

      // Home marker (honeypot server)
      const homeIcon = L.divIcon({
        html: `<div style="
          width:14px;height:14px;
          background:#00ffe7;
          border:2px solid #fff;
          border-radius:50%;
          box-shadow:0 0 12px #00ffe7, 0 0 24px #00ffe7;
        "></div>`,
        className: '',
        iconSize: [14, 14],
        iconAnchor: [7, 7],
      });

      L.marker([HOME.lat, HOME.lon], { icon: homeIcon })
        .addTo(map)
        .bindTooltip('🛡 HoneyCloud Sentinel', {
          permanent: false,
          className: 'leaflet-tooltip-dark',
        });

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

  // Draw attack lines whenever attacks update
  useEffect(() => {
    if (!ready || !mapInstance.current) return;

    import('leaflet').then((L) => {
      const map = mapInstance.current;

      // Remove old lines and markers beyond last 30
      while (linesRef.current.length > 30) {
        const old = linesRef.current.shift();
        try { map.removeLayer(old); } catch {}
      }
      while (markersRef.current.length > 30) {
        const old = markersRef.current.shift();
        try { map.removeLayer(old); } catch {}
      }

      // Draw the 5 newest attacks that have valid coords
      const fresh = attacks
        .filter(a => a.lat && a.lon && !(a.lat === 0 && a.lon === 0))
        .slice(0, 5);

      fresh.forEach((attack) => {
        const color   = riskColor(attack.risk_level);
        const srcLatLon: [number, number] = [attack.lat, attack.lon];
        const dstLatLon: [number, number] = [HOME.lat, HOME.lon];

        // Animated arc line
        const line = L.polyline([srcLatLon, dstLatLon], {
          color,
          weight:    1.5,
          opacity:   0.7,
          dashArray: '6 4',
        }).addTo(map);

        // Source marker with ping
        const attackIcon = L.divIcon({
          html: `
            <div style="position:relative;width:20px;height:20px;">
              <div style="
                position:absolute;inset:0;
                border-radius:50%;
                background:${color};
                opacity:0.2;
                animation:radar-ping 1.5s ease-out infinite;
              "></div>
              <div style="
                position:absolute;top:5px;left:5px;
                width:10px;height:10px;
                background:${color};
                border-radius:50%;
                box-shadow:0 0 8px ${color};
              "></div>
            </div>`,
          className: '',
          iconSize:  [20, 20],
          iconAnchor:[10, 10],
        });

        const marker = L.marker(srcLatLon, { icon: attackIcon })
          .addTo(map)
          .bindPopup(`
            <div style="
              background:#020810;
              border:1px solid ${color};
              border-radius:4px;
              padding:10px;
              font-family:'Share Tech Mono',monospace;
              font-size:11px;
              color:#00ffe7;
              min-width:180px;
            ">
              <div style="color:${color};font-size:13px;margin-bottom:6px;">
                ${attack.emoji} ${attack.risk_level}
              </div>
              <div>IP: ${attack.source_ip}</div>
              <div>Type: ${attack.attack_type}</div>
              <div>Port: ${attack.port_targeted}</div>
              <div>Country: ${attack.country}</div>
              ${attack.city ? `<div>City: ${attack.city}</div>` : ''}
              <div style="color:#666;margin-top:4px;font-size:10px;">
                ${attack.timestamp}
              </div>
            </div>
          `, { className: 'leaflet-popup-dark' });

        linesRef.current.push(line);
        markersRef.current.push(marker);

        // Fade out line after 8 seconds
        setTimeout(() => {
          try { map.removeLayer(line); } catch {}
        }, 8000);
      });
    });
  }, [attacks, ready]);

  return (
    <div className="relative w-full h-full rounded-lg overflow-hidden border border-cyan-500/20">
      {/* Map container */}
      <div ref={mapRef} className="w-full h-full" style={{ background: '#020810' }} />

      {/* Corner overlays */}
      <div className="absolute top-3 left-3 z-[1000] pointer-events-none">
        <div className="text-[10px] font-mono text-cyan-400/70 tracking-widest">
          GLOBAL THREAT MAP
        </div>
        <div className="text-[9px] font-mono text-cyan-400/40 mt-0.5">
          REAL-TIME ATTACK ORIGINS
        </div>
      </div>

      <div className="absolute top-3 right-3 z-[1000] pointer-events-none flex flex-col gap-1">
        {[
          { label: 'CRITICAL', color: '#ff2d2d' },
          { label: 'HIGH',     color: '#ff6b00' },
          { label: 'MEDIUM',   color: '#ffe600' },
          { label: 'LOW',      color: '#00ffe7' },
        ].map(({ label, color }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ background: color, boxShadow: `0 0 4px ${color}` }} />
            <span className="text-[9px] font-mono" style={{ color }}>{label}</span>
          </div>
        ))}
      </div>

      {/* Bottom status bar */}
      <div className="absolute bottom-3 left-3 right-3 z-[1000] pointer-events-none flex justify-between">
        <div className="text-[9px] font-mono text-cyan-400/40">
          🛡 HONEYPOT: INDIA
        </div>
        <div className="text-[9px] font-mono text-cyan-400/40 blink">
          ● MONITORING
        </div>
      </div>
    </div>
  );
}