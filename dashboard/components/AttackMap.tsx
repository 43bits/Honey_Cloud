/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useEffect, useRef, useState } from 'react';
import type { Attack } from '@/lib/api';

const HOME = { lat: 20.5937, lon: 78.9629 };

interface MapAttack extends Attack { lat: number; lon: number; }

const riskColor = (risk: string) => {
  if (risk === 'CRITICAL') return '#ff4444';
  if (risk === 'HIGH')     return '#f5a623';
  if (risk === 'MEDIUM')   return '#f0c040';
  return '#3dd68c';
};

export default function AttackMap({
  attacks, selectedAttack,
}: {
  attacks: Attack[]; selectedAttack?: Attack | null;
}) {
  const mapRef      = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const linesRef    = useRef<any[]>([]);
  const markersRef  = useRef<any[]>([]);
  const [ready,   setReady]   = useState(false);
  const [mapMode, setMapMode] = useState<'live' | 'view'>('live');

  useEffect(() => {
    if (typeof window === 'undefined' || mapInstance.current) return;
    import('leaflet').then((L) => {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      const map = L.map(mapRef.current!, {
        center: [20, 10], zoom: 2,
        zoomControl: false, attributionControl: false,
        minZoom: 2, maxZoom: 6,
      });
      L.control.zoom({ position: 'bottomright' }).addTo(map);
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }).addTo(map);
      const homeIcon = L.divIcon({
        html: `<div style="width:10px;height:10px;background:#ffffff;border:2px solid rgba(255,255,255,0.5);border-radius:50%;"></div>`,
        className: '', iconSize: [10,10], iconAnchor: [5,5],
      });
      L.marker([HOME.lat, HOME.lon], { icon: homeIcon }).addTo(map).bindTooltip('HoneyCloud · India');
      mapInstance.current = map;
      setReady(true);
    });
    return () => { if (mapInstance.current) { mapInstance.current.remove(); mapInstance.current = null; } };
  }, []);

  useEffect(() => {
    if (!ready || !mapInstance.current || mapMode !== 'live') return;
    import('leaflet').then((L) => {
      const map = mapInstance.current;
      while (linesRef.current.length > 30) { try { map.removeLayer(linesRef.current.shift()); } catch {} }
      while (markersRef.current.length > 30) { try { map.removeLayer(markersRef.current.shift()); } catch {} }
      const fresh = (attacks as MapAttack[]).filter(a => a.lat && a.lon && !(a.lat === 0 && a.lon === 0)).slice(0, 8);
      fresh.forEach((attack) => {
        const color = riskColor(attack.risk_level);
        const line = L.polyline([[attack.lat, attack.lon], [HOME.lat, HOME.lon]], { color, weight: 1, opacity: 0.5, dashArray: '5 5' }).addTo(map);
        const icon = L.divIcon({
          html: `<div style="position:relative;width:16px;height:16px;"><div style="position:absolute;inset:0;border-radius:50%;background:${color};opacity:0.12;animation:radar-ping 1.8s ease-out infinite;"></div><div style="position:absolute;top:4px;left:4px;width:8px;height:8px;background:${color};border-radius:50%;opacity:0.9;"></div></div>`,
          className: '', iconSize: [16,16], iconAnchor: [8,8],
        });
        const popup = `<div style="background:#1a1a1a;border-radius:8px;padding:12px 14px;font-family:'Inter',sans-serif;font-size:12px;color:rgba(255,255,255,0.7);min-width:180px;line-height:1.6;"><div style="color:${color};font-size:11px;font-weight:600;margin-bottom:6px;letter-spacing:0.04em">${attack.risk_level}</div><div style="font-weight:500;color:#fff;font-family:'Geist Mono',monospace">${attack.source_ip}</div><div style="color:rgba(255,255,255,0.45);margin-top:2px">${attack.attack_type}</div><div style="color:rgba(255,255,255,0.3);font-size:11px">:${attack.port_targeted} · ${attack.country||'—'}</div>${(attack as any).mitre_technique_id?`<div style="color:rgba(255,255,255,0.3);font-size:11px;margin-top:4px;font-family:'Geist Mono',monospace">${(attack as any).mitre_technique_id}</div>`:''}</div>`;
        const marker = L.marker([attack.lat, attack.lon], { icon }).addTo(map).bindPopup(popup);
        linesRef.current.push(line);
        markersRef.current.push(marker);
        setTimeout(() => { try { map.removeLayer(line); } catch {} }, 10000);
      });
    });
  }, [attacks, ready, mapMode]);

  useEffect(() => {
    if (!ready || !mapInstance.current || mapMode !== 'view' || !selectedAttack) return;
    import('leaflet').then((L) => {
      linesRef.current.forEach(l => { try { mapInstance.current.removeLayer(l); } catch {} });
      markersRef.current.forEach(m => { try { mapInstance.current.removeLayer(m); } catch {} });
      linesRef.current = []; markersRef.current = [];
      const a = selectedAttack as MapAttack;
      if (!a.lat || !a.lon || (a.lat === 0 && a.lon === 0)) return;
      const color = riskColor(a.risk_level);
      mapInstance.current.flyTo([a.lat, a.lon], 4, { duration: 1.2 });
      const line = L.polyline([[a.lat, a.lon], [HOME.lat, HOME.lon]], { color, weight: 1.5, opacity: 0.7, dashArray: '4 4' }).addTo(mapInstance.current);
      const srcIcon = L.divIcon({
        html: `<div style="position:relative;width:22px;height:22px;"><div style="position:absolute;inset:0;border-radius:50%;background:${color};opacity:0.1;animation:radar-ping 1.2s ease-out infinite;"></div><div style="position:absolute;inset:4px;border-radius:50%;background:${color};opacity:0.18;animation:radar-ping 1.2s 0.4s ease-out infinite;"></div><div style="position:absolute;top:7px;left:7px;width:8px;height:8px;background:${color};border-radius:50%;"></div></div>`,
        className: '', iconSize: [22,22], iconAnchor: [11,11],
      });
      const popup = `<div style="background:#1a1a1a;border-radius:8px;padding:12px 14px;font-family:'Inter',sans-serif;font-size:12px;color:rgba(255,255,255,0.7);min-width:200px;line-height:1.6;"><div style="color:${color};font-size:11px;font-weight:600;margin-bottom:8px">▸ SELECTED · ${a.risk_level}</div><div style="font-weight:500;color:#fff;font-family:'Geist Mono',monospace">${a.source_ip}</div><div style="color:rgba(255,255,255,0.45)">${a.attack_type}</div><div style="color:rgba(255,255,255,0.3);font-size:11px">:${a.port_targeted} · ${a.country||'—'}</div><div style="color:rgba(255,255,255,0.25);font-size:11px">${(a as any).city||''}</div>${(a as any).mitre_technique_id?`<div style="color:rgba(255,255,255,0.3);font-size:11px;margin-top:4px;font-family:'Geist Mono',monospace">${(a as any).mitre_technique_id}</div>`:''}</div>`;
      const marker = L.marker([a.lat, a.lon], { icon: srcIcon }).addTo(mapInstance.current).bindPopup(popup).openPopup();
      linesRef.current.push(line); markersRef.current.push(marker);
    });
  }, [selectedAttack, ready, mapMode]);

  useEffect(() => {
    if (!ready || !mapInstance.current) return;
    if (mapMode === 'live') mapInstance.current.flyTo([20,10], 2, { duration: 1 });
  }, [mapMode, ready]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.07)' }}>
      <div ref={mapRef} style={{ width: '100%', height: '100%', background: '#1a1a1a' }} />

      {/* Top-left label */}
      <div style={{ position: 'absolute', top: '14px', left: '14px', zIndex: 1000, pointerEvents: 'none' }}>
        <div style={{ fontSize: '12px', fontWeight: 600, color: 'rgba(255,255,255,0.7)' }}>
          {mapMode === 'live' ? 'Global Threat Map' : 'Attack Origin View'}
        </div>
        <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginTop: '1px' }}>
          {mapMode === 'live' ? 'Real-time attack origins' : selectedAttack ? `${selectedAttack.source_ip} · ${selectedAttack.attack_type}` : 'Select an attack'}
        </div>
      </div>

      {/* Legend */}
      <div style={{
        position: 'absolute', top: '14px', right: '14px', zIndex: 1000, pointerEvents: 'none',
        background: 'rgba(17,17,17,0.85)', borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.08)', padding: '8px 12px',
        display: 'flex', flexDirection: 'column', gap: '5px',
      }}>
        {[
          { label: 'Critical', color: '#ff4444' },
          { label: 'High',     color: '#f5a623' },
          { label: 'Medium',   color: '#f0c040' },
          { label: 'Low',      color: '#3dd68c' },
        ].map(({ label, color }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: color }} />
            <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.45)' }}>{label}</span>
          </div>
        ))}
      </div>

      {/* LIVE/VIEW toggle */}
      <div style={{
        position: 'absolute', bottom: '46px', left: '14px', zIndex: 1000,
        display: 'flex', background: 'rgba(17,17,17,0.9)',
        borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', overflow: 'hidden',
      }}>
        {(['live','view'] as const).map((mode, idx) => (
          <button key={mode} onClick={() => setMapMode(mode)} style={{
            padding: '5px 14px', fontSize: '11px', fontWeight: 500,
            background: mapMode === mode ? 'rgba(255,255,255,0.12)' : 'transparent',
            color: mapMode === mode ? '#ffffff' : 'rgba(255,255,255,0.35)',
            border: 'none', borderRight: idx === 0 ? '1px solid rgba(255,255,255,0.08)' : 'none',
            cursor: 'pointer', fontFamily: 'Inter, sans-serif',
            display: 'flex', alignItems: 'center', gap: '6px',
          }}>
            {mode === 'live' ? (
              <><span style={{ width:'5px', height:'5px', borderRadius:'50%', background: mapMode==='live'?'#3dd68c':'rgba(255,255,255,0.2)', display:'inline-block' }} />Live</>
            ) : <>⊙ View</>}
          </button>
        ))}
      </div>

      {/* Bottom status */}
      <div style={{ position:'absolute', bottom:'14px', left:'14px', right:'14px', zIndex:1000, pointerEvents:'none', display:'flex', justifyContent:'space-between' }}>
        <span style={{ fontSize:'10px', color:'rgba(255,255,255,0.2)', fontFamily:'Inter,sans-serif' }}>Honeypot · India</span>
        <span style={{ fontSize:'10px', color:'rgba(61,214,140,0.5)', fontFamily:'Inter,sans-serif' }}>● Monitoring</span>
      </div>

      {mapMode === 'view' && !selectedAttack && (
        <div style={{ position:'absolute', inset:0, zIndex:999, pointerEvents:'none', display:'flex', alignItems:'center', justifyContent:'center' }}>
          <div style={{ background:'rgba(17,17,17,0.9)', border:'1px solid rgba(255,255,255,0.08)', borderRadius:'8px', padding:'10px 20px', fontSize:'12px', color:'rgba(255,255,255,0.35)' }}>
            Select an attack row to view on map
          </div>
        </div>
      )}
    </div>
  );
}
