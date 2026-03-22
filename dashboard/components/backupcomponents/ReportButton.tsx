// components/ReportButton.tsx
'use client';

import { useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Status = 'idle' | 'loading' | 'done' | 'error';

function ActionButton({
  onClick,
  status,
  idleLabel,
  color,
  disabled,
}: {
  onClick: () => void;
  status:  Status;
  idleLabel: string;
  color: string;
  disabled: boolean;
}) {
  const labels: Record<Status, string> = {
    idle:    idleLabel,
    loading: '⟳  GENERATING...',
    done:    '✓  DONE',
    error:   '✗  ERROR',
  };
  const dim = `${color}44`;

  return (
    <button
      onClick={onClick}
      disabled={status === 'loading' || disabled}
      className="relative px-4 py-2 rounded font-mono text-[10px]
        tracking-widest transition-all duration-200
        disabled:opacity-40 disabled:cursor-not-allowed
        hover:scale-[1.02] active:scale-[0.98]"
      style={{
        border:     `1px solid ${status === 'idle' ? dim : color}`,
        color:      status === 'idle' ? color : color,
        background: `${color}08`,
        boxShadow:  status === 'loading' ? `0 0 16px ${dim}` : 'none',
      }}
    >
      {status === 'loading' && (
        <div
          className="absolute bottom-0 left-0 h-0.5 rounded-b"
          style={{
            background: color,
            animation:  'loading-bar 8s linear forwards',
          }}
        />
      )}
      {labels[status]}
    </button>
  );
}

export default function ReportButtons({ hasData }: { hasData: boolean }) {
  const [htmlStatus, setHtmlStatus] = useState<Status>('idle');
  const [pdfStatus,  setPdfStatus]  = useState<Status>('idle');

  const openHTML = async () => {
    setHtmlStatus('loading');
    try {
      // Open in new tab — browser renders it live
      window.open(`${API}/report/html`, '_blank');
      setHtmlStatus('done');
      setTimeout(() => setHtmlStatus('idle'), 3000);
    } catch {
      setHtmlStatus('error');
      setTimeout(() => setHtmlStatus('idle'), 3000);
    }
  };

  const downloadPDF = async () => {
    setPdfStatus('loading');
    try {
      const res  = await fetch(`${API}/report/generate`);
      if (!res.ok) throw new Error();
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = `HoneyCloud_Report_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setPdfStatus('done');
      setTimeout(() => setPdfStatus('idle'), 3000);
    } catch {
      setPdfStatus('error');
      setTimeout(() => setPdfStatus('idle'), 3000);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <ActionButton
        onClick={openHTML}
        status={htmlStatus}
        idleLabel="🌐  VIEW REPORT"
        color="#00ffe7"
        disabled={!hasData}
      />
      <ActionButton
        onClick={downloadPDF}
        status={pdfStatus}
        idleLabel="⬇  DOWNLOAD PDF"
        color="#ff6b00"
        disabled={!hasData}
      />
    </div>
  );
}