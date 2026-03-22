'use client';

import { useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
type Status = 'idle' | 'loading' | 'done' | 'error';

function Btn({ onClick, status, label, variant, disabled }: {
  onClick: () => void; status: Status; label: string;
  variant: 'primary' | 'secondary'; disabled: boolean;
}) {
  const labels: Record<Status, string> = { idle: label, loading: '⟳ Generating...', done: '✓ Done', error: '✗ Error' };
  return (
    <button onClick={onClick} disabled={status === 'loading' || disabled} style={{
      padding:      '6px 14px',
      borderRadius: '7px',
      background:   variant === 'primary'
        ? (status === 'idle' ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.06)')
        : 'transparent',
      border:   '1px solid rgba(255,255,255,0.12)',
      color:    disabled ? 'rgba(255,255,255,0.2)' : status === 'idle' ? '#ffffff' : 'rgba(255,255,255,0.5)',
      fontSize: '11px', fontWeight: 500, cursor: status === 'loading' || disabled ? 'not-allowed' : 'pointer',
      fontFamily: 'Inter, sans-serif', transition: 'all 0.15s', whiteSpace: 'nowrap',
    }}>
      {labels[status]}
    </button>
  );
}

export default function ReportButton({ hasData }: { hasData: boolean }) {
  const [htmlStatus, setHtmlStatus] = useState<Status>('idle');
  const [pdfStatus,  setPdfStatus]  = useState<Status>('idle');

  const openHTML = async () => {
    setHtmlStatus('loading');
    try { window.open(`${API}/report/html`, '_blank'); setHtmlStatus('done'); setTimeout(() => setHtmlStatus('idle'), 3000); }
    catch { setHtmlStatus('error'); setTimeout(() => setHtmlStatus('idle'), 3000); }
  };

  const downloadPDF = async () => {
    setPdfStatus('loading');
    try {
      const res = await fetch(`${API}/report/generate`);
      if (!res.ok) throw new Error();
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href = url; a.download = `HoneyCloud_Report_${Date.now()}.pdf`;
      document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
      setPdfStatus('done'); setTimeout(() => setPdfStatus('idle'), 3000);
    } catch { setPdfStatus('error'); setTimeout(() => setPdfStatus('idle'), 3000); }
  };

  return (
    <div style={{ display: 'flex', gap: '6px' }}>
      <Btn onClick={openHTML}    status={htmlStatus} label="View Report" variant="primary"    disabled={!hasData} />
      <Btn onClick={downloadPDF} status={pdfStatus}  label="↓ PDF"       variant="secondary"  disabled={!hasData} />
    </div>
  );
}
