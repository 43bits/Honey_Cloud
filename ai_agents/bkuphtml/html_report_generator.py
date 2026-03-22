# ai_agents/html_report_generator.py
from datetime import datetime


def generate_html_report(report_text: str, stats: dict, attacks: list) -> str:

    now        = datetime.now().strftime('%B %d, %Y  %H:%M UTC')
    by_risk    = stats.get('by_risk', {})
    total      = stats.get('total_attacks', 0) or 1
    top_types  = stats.get('top_attack_types', [])
    top_countries = stats.get('top_countries', [])

    # ── Risk bar data ──────────────────────────────
    def risk_bar(label, count, color):
        pct = round(count / total * 100, 1)
        return f"""
        <div class="risk-row">
          <span class="risk-label" style="color:{color}">{label}</span>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%;background:{color};
              box-shadow:0 0 8px {color}"></div>
          </div>
          <span class="risk-count" style="color:{color}">{count}</span>
          <span class="risk-pct" style="color:{color}66">{pct}%</span>
        </div>"""

    # ── Attack type chart bars ─────────────────────
    max_count  = max((t['count'] for t in top_types), default=1)
    type_bars  = ""
    bar_colors = ['#00ffe7','#ff6b00','#ff2d2d','#ffe600','#00ff88']
    for i, t in enumerate(top_types):
        pct   = round(t['count'] / max_count * 100)
        color = bar_colors[i % len(bar_colors)]
        type_bars += f"""
        <div class="chart-row">
          <span class="chart-label">{t['type']}</span>
          <div class="chart-track">
            <div class="chart-bar" style="width:{pct}%;background:{color};
              box-shadow:0 0 6px {color}66"></div>
          </div>
          <span class="chart-val" style="color:{color}">{t['count']}</span>
        </div>"""

    # ── Country rows ───────────────────────────────
    max_c      = max((c['count'] for c in top_countries), default=1)
    country_rows = ""
    for i, c in enumerate(top_countries):
        pct   = round(c['count'] / max_c * 100)
        color = bar_colors[i % len(bar_colors)]
        country_rows += f"""
        <div class="chart-row">
          <span class="chart-label">{c['country']}</span>
          <div class="chart-track">
            <div class="chart-bar" style="width:{pct}%;background:{color};
              box-shadow:0 0 6px {color}66"></div>
          </div>
          <span class="chart-val" style="color:{color}">{c['count']}</span>
        </div>"""

    # ── Risk gauge angle ───────────────────────────
    critical_pct = by_risk.get('CRITICAL', 0) / total * 100
    high_pct     = by_risk.get('HIGH', 0)     / total * 100
    danger_score = min(100, critical_pct * 1.5 + high_pct * 0.8)
    gauge_angle  = -90 + (danger_score / 100 * 180)
    gauge_color  = ('#ff2d2d' if danger_score > 70
                    else '#ff6b00' if danger_score > 40
                    else '#ffe600' if danger_score > 20
                    else '#00ffe7')
    gauge_label  = ('CRITICAL' if danger_score > 70
                    else 'HIGH' if danger_score > 40
                    else 'MEDIUM' if danger_score > 20
                    else 'LOW')

    # ── Recent attacks table rows ──────────────────
    risk_colors = {
        'CRITICAL': '#ff2d2d',
        'HIGH':     '#ff6b00',
        'MEDIUM':   '#ffe600',
        'LOW':      '#00ffe7',
    }
    table_rows = ""
    for a in attacks[:20]:
        rc = risk_colors.get(a.get('risk_level','LOW'), '#00ffe7')
        anomaly_badge = (
            '<span class="anomaly-badge">⚠ ANOMALY</span>'
            if a.get('is_anomaly') else ''
        )
        table_rows += f"""
        <tr>
          <td class="mono" style="color:#8899bb">
            {str(a.get('timestamp',''))[:16]}
          </td>
          <td class="mono" style="color:#00ffe7">
            {a.get('source_ip','?')}
          </td>
          <td>{a.get('attack_type','?')} {anomaly_badge}</td>
          <td class="mono" style="color:#8899bb">
            :{a.get('port_targeted','?')}
          </td>
          <td style="color:#8899bb">{a.get('country','?')}</td>
          <td>
            <span class="risk-badge"
              style="color:{rc};border-color:{rc}44;background:{rc}11">
              {a.get('risk_level','?')}
            </span>
          </td>
        </tr>"""

    # ── Format report text into sections ──────────
    section_names = [
        'EXECUTIVE SUMMARY',
        'THREAT ANALYSIS',
        'ANOMALY DETECTION FINDINGS',
        'CAMPAIGN ATTRIBUTION',
        'RISK ASSESSMENT',
        'IMMEDIATE RECOMMENDATIONS',
        'INDICATORS OF COMPROMISE',
    ]

    sections_html = ""
    current       = None
    buf           = []

    def flush_section(name, lines):
        content = '\n'.join(lines).strip()
        if not content or not name:
            return ''
        is_ioc  = 'INDICATOR' in name
        is_recs = 'RECOMMENDATION' in name
        paras   = ''
        if is_ioc:
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    paras += f'<div class="ioc-line">▸ {line}</div>'
        elif is_recs:
            import re
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                line = re.sub(
                    r'^(\d+\.)\s*',
                    r'<span class="rec-num">\1</span> ',
                    line
                )
                paras += f'<p class="rec-line">{line}</p>'
        else:
            for chunk in content.split('\n\n'):
                chunk = chunk.strip().replace('\n', ' ')
                if chunk:
                    paras += f'<p>{chunk}</p>'

        icon_map = {
            'EXECUTIVE':    '📋',
            'THREAT':       '🔍',
            'ANOMALY':      '⚠️',
            'CAMPAIGN':     '🕵️',
            'RISK':         '🎯',
            'IMMEDIATE':    '🛡️',
            'INDICATORS':   '🔒',
        }
        icon = next(
            (v for k, v in icon_map.items() if k in name), '📄'
        )
        return f"""
        <div class="section">
          <div class="section-header">
            <span class="section-icon">{icon}</span>
            <span class="section-title">{name}</span>
          </div>
          <div class="section-body">{paras}</div>
        </div>"""

    for line in report_text.split('\n'):
        matched = False
        for sname in section_names:
            if sname in line.upper():
                if current:
                    sections_html += flush_section(current, buf)
                current = sname
                buf     = []
                matched = True
                break
        if not matched:
            buf.append(line)
    if current:
        sections_html += flush_section(current, buf)

    # ── Full HTML ──────────────────────────────────
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>HoneyCloud Sentinel — Threat Intelligence Report</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

  *{{ box-sizing:border-box; margin:0; padding:0; }}

  body{{
    background:#080c14;
    color:#c8d8f0;
    font-family:'Rajdhani',sans-serif;
    font-size:15px;
    line-height:1.7;
  }}

  /* Scanlines */
  body::before{{
    content:'';
    position:fixed;inset:0;
    background:repeating-linear-gradient(
      0deg,transparent,transparent 2px,
      rgba(0,255,231,.012) 2px,rgba(0,255,231,.012) 4px
    );
    pointer-events:none;z-index:9999;
  }}

  .mono{{ font-family:'Share Tech Mono',monospace; }}

  /* ── PAGE WRAPPER ── */
  .page{{
    max-width:1100px;
    margin:0 auto;
    padding:0 24px 60px;
  }}

  /* ── HEADER ── */
  .report-header{{
    border-bottom:1px solid rgba(0,255,231,.15);
    padding:32px 0 24px;
    margin-bottom:32px;
    position:relative;
  }}
  .header-top-bar{{
    position:absolute;top:0;left:-24px;right:-24px;
    height:3px;
    background:linear-gradient(90deg,transparent,#00ffe7,transparent);
  }}
  .header-badge{{
    display:inline-flex;align-items:center;gap:10px;
    background:rgba(0,255,231,.06);
    border:1px solid rgba(0,255,231,.2);
    border-radius:4px;
    padding:8px 16px;
    margin-bottom:20px;
  }}
  .badge-dot{{
    width:8px;height:8px;border-radius:50%;
    background:#00ffe7;
    box-shadow:0 0 8px #00ffe7;
    animation:pulse 2s ease-in-out infinite;
  }}
  @keyframes pulse{{
    0%,100%{{opacity:1;}} 50%{{opacity:.4;}}
  }}
  .badge-text{{
    font-family:'Share Tech Mono',monospace;
    font-size:11px;
    color:#00ffe7;
    letter-spacing:.15em;
  }}
  .report-title{{
    font-size:38px;font-weight:700;
    color:#00ffe7;
    letter-spacing:.08em;
    text-shadow:0 0 30px rgba(0,255,231,.4);
    line-height:1.1;
  }}
  .report-subtitle{{
    font-size:16px;color:rgba(0,255,231,.5);
    letter-spacing:.12em;margin-top:6px;
  }}
  .report-meta{{
    margin-top:16px;
    display:flex;gap:32px;flex-wrap:wrap;
  }}
  .meta-item{{
    font-family:'Share Tech Mono',monospace;
    font-size:11px;color:#4a6080;
    letter-spacing:.1em;
  }}
  .meta-val{{color:#7090b0;}}

  /* ── STAT GRID ── */
  .stat-grid{{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:12px;
    margin-bottom:24px;
  }}
  @media(max-width:700px){{
    .stat-grid{{grid-template-columns:repeat(2,1fr);}}
  }}
  .stat-card{{
    padding:18px 16px;
    border-radius:6px;
    position:relative;overflow:hidden;
  }}
  .stat-card::before{{
    content:'';
    position:absolute;top:0;left:0;right:0;height:2px;
  }}
  .stat-label{{
    font-family:'Share Tech Mono',monospace;
    font-size:9px;letter-spacing:.2em;
    margin-bottom:8px;
  }}
  .stat-number{{
    font-size:36px;font-weight:700;
    font-family:'Share Tech Mono',monospace;
    line-height:1;
  }}
  .stat-pct{{
    font-size:11px;margin-top:6px;opacity:.5;
    font-family:'Share Tech Mono',monospace;
  }}

  /* ── GAUGE ── */
  .gauge-section{{
    display:grid;grid-template-columns:220px 1fr;
    gap:24px;align-items:center;
    background:rgba(0,0,0,.3);
    border:1px solid rgba(0,255,231,.08);
    border-radius:8px;padding:24px;
    margin-bottom:24px;
  }}
  @media(max-width:600px){{
    .gauge-section{{grid-template-columns:1fr;}}
  }}
  .gauge-wrap{{text-align:center;}}
  .gauge-svg{{width:200px;height:110px;}}
  .gauge-label{{
    font-family:'Share Tech Mono',monospace;
    font-size:11px;letter-spacing:.15em;
    margin-top:4px;
  }}
  .risk-rows{{flex:1;}}
  .risk-row{{
    display:grid;
    grid-template-columns:90px 1fr 50px 50px;
    gap:10px;align-items:center;
    margin-bottom:10px;
  }}
  .risk-label{{
    font-family:'Share Tech Mono',monospace;
    font-size:11px;letter-spacing:.1em;
  }}
  .bar-track{{
    height:6px;background:rgba(255,255,255,.05);
    border-radius:3px;overflow:hidden;
  }}
  .bar-fill{{height:100%;border-radius:3px;transition:width .8s ease;}}
  .risk-count{{
    font-family:'Share Tech Mono',monospace;
    font-size:12px;font-weight:700;text-align:right;
  }}
  .risk-pct{{
    font-family:'Share Tech Mono',monospace;
    font-size:10px;text-align:right;
  }}

  /* ── CHARTS ROW ── */
  .charts-row{{
    display:grid;grid-template-columns:1fr 1fr;
    gap:16px;margin-bottom:24px;
  }}
  @media(max-width:700px){{
    .charts-row{{grid-template-columns:1fr;}}
  }}
  .chart-card{{
    background:rgba(0,0,0,.3);
    border:1px solid rgba(0,255,231,.08);
    border-radius:8px;padding:20px;
  }}
  .chart-title{{
    font-family:'Share Tech Mono',monospace;
    font-size:9px;letter-spacing:.2em;
    color:rgba(0,255,231,.4);
    margin-bottom:16px;
  }}
  .chart-row{{
    display:grid;
    grid-template-columns:130px 1fr 40px;
    gap:10px;align-items:center;
    margin-bottom:10px;
  }}
  .chart-label{{
    font-size:12px;color:#8899bb;
    white-space:nowrap;overflow:hidden;
    text-overflow:ellipsis;
  }}
  .chart-track{{
    height:5px;background:rgba(255,255,255,.05);
    border-radius:3px;overflow:hidden;
  }}
  .chart-bar{{
    height:100%;border-radius:3px;
  }}
  .chart-val{{
    font-family:'Share Tech Mono',monospace;
    font-size:11px;font-weight:700;text-align:right;
  }}

  /* ── SECTIONS ── */
  .section{{
    background:rgba(0,0,0,.25);
    border:1px solid rgba(0,255,231,.07);
    border-radius:8px;
    margin-bottom:16px;
    overflow:hidden;
  }}
  .section-header{{
    display:flex;align-items:center;gap:12px;
    padding:14px 20px;
    background:rgba(0,255,231,.04);
    border-bottom:1px solid rgba(0,255,231,.08);
  }}
  .section-icon{{font-size:16px;}}
  .section-title{{
    font-family:'Share Tech Mono',monospace;
    font-size:11px;letter-spacing:.18em;
    color:#00ffe7;
  }}
  .section-body{{
    padding:20px;
    color:#a0b8d0;
    font-size:14px;line-height:1.75;
  }}
  .section-body p{{margin-bottom:12px;}}
  .section-body p:last-child{{margin-bottom:0;}}

  .ioc-line{{
    font-family:'Share Tech Mono',monospace;
    font-size:12px;color:#00ff88;
    padding:4px 0;border-bottom:1px solid rgba(0,255,136,.08);
  }}
  .ioc-line:last-child{{border-bottom:none;}}

  .rec-num{{
    color:#00ffe7;font-weight:700;
    font-family:'Share Tech Mono',monospace;
  }}
  .rec-line{{margin-bottom:10px !important;}}

  .anomaly-badge{{
    display:inline-block;
    font-size:9px;padding:1px 6px;
    background:rgba(255,230,0,.1);
    border:1px solid rgba(255,230,0,.3);
    border-radius:3px;color:#ffe600;
    font-family:'Share Tech Mono',monospace;
    vertical-align:middle;margin-left:6px;
  }}
  .risk-badge{{
    display:inline-block;
    font-size:10px;padding:2px 8px;
    border:1px solid;border-radius:3px;
    font-family:'Share Tech Mono',monospace;
    letter-spacing:.08em;
  }}

  /* ── ATTACK TABLE ── */
  .table-section{{
    background:rgba(0,0,0,.3);
    border:1px solid rgba(0,255,231,.08);
    border-radius:8px;
    margin-bottom:24px;
    overflow:hidden;
  }}
  .table-header{{
    padding:14px 20px;
    background:rgba(0,255,231,.04);
    border-bottom:1px solid rgba(0,255,231,.08);
    font-family:'Share Tech Mono',monospace;
    font-size:9px;letter-spacing:.2em;
    color:rgba(0,255,231,.4);
  }}
  table{{width:100%;border-collapse:collapse;}}
  thead td{{
    font-family:'Share Tech Mono',monospace;
    font-size:9px;letter-spacing:.15em;
    color:rgba(0,255,231,.4);
    padding:10px 16px;
    background:rgba(0,255,231,.03);
    border-bottom:1px solid rgba(0,255,231,.08);
  }}
  tbody tr{{
    border-bottom:1px solid rgba(0,255,231,.04);
    transition:background .15s;
  }}
  tbody tr:hover{{background:rgba(0,255,231,.03);}}
  tbody tr:last-child{{border-bottom:none;}}
  tbody td{{
    padding:9px 16px;
    font-size:12px;
  }}

  /* ── FOOTER ── */
  .report-footer{{
    margin-top:40px;
    padding-top:20px;
    border-top:1px solid rgba(0,255,231,.1);
    text-align:center;
    font-family:'Share Tech Mono',monospace;
    font-size:10px;
    color:#2a3a50;
    letter-spacing:.12em;
  }}

  /* ── PRINT ── */
  @media print{{
    body{{background:#080c14 !important;
         -webkit-print-color-adjust:exact;
         print-color-adjust:exact;}}
    body::before{{display:none;}}
    .no-print{{display:none;}}
  }}
</style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div class="report-header">
    <div class="header-top-bar"></div>
    <div class="header-badge">
      <div class="badge-dot"></div>
      <span class="badge-text">CLASSIFIED — THREAT INTELLIGENCE REPORT</span>
    </div>
    <div class="report-title">HONEYCLOUD SENTINEL</div>
    <div class="report-subtitle">AI-DRIVEN ADAPTIVE HONEYPOT INTELLIGENCE PLATFORM</div>
    <div class="report-meta">
      <div class="meta-item">GENERATED &nbsp;<span class="meta-val">{now}</span></div>
      <div class="meta-item">TOTAL EVENTS &nbsp;
        <span class="meta-val">{stats.get('total_attacks',0)}</span>
      </div>
      <div class="meta-item">CLASSIFICATION &nbsp;
        <span class="meta-val">CONFIDENTIAL</span>
      </div>
    </div>
  </div>

  <!-- STAT CARDS -->
  <div class="stat-grid">
    <div class="stat-card" style="background:rgba(255,45,45,.05);
      border:1px solid rgba(255,45,45,.2);">
      <div class="stat-card" style="position:absolute;top:0;left:0;right:0;
        height:2px;background:#ff2d2d;"></div>
      <div class="stat-label" style="color:#ff2d2d">CRITICAL</div>
      <div class="stat-number" style="color:#ff2d2d;
        text-shadow:0 0 20px rgba(255,45,45,.5)">
        {by_risk.get('CRITICAL',0)}
      </div>
      <div class="stat-pct" style="color:#ff2d2d">
        {round(by_risk.get('CRITICAL',0)/total*100,1)}% of total
      </div>
    </div>
    <div class="stat-card" style="background:rgba(255,107,0,.05);
      border:1px solid rgba(255,107,0,.2);">
      <div class="stat-label" style="color:#ff6b00">HIGH</div>
      <div class="stat-number" style="color:#ff6b00;
        text-shadow:0 0 20px rgba(255,107,0,.5)">
        {by_risk.get('HIGH',0)}
      </div>
      <div class="stat-pct" style="color:#ff6b00">
        {round(by_risk.get('HIGH',0)/total*100,1)}% of total
      </div>
    </div>
    <div class="stat-card" style="background:rgba(255,230,0,.05);
      border:1px solid rgba(255,230,0,.2);">
      <div class="stat-label" style="color:#ffe600">MEDIUM</div>
      <div class="stat-number" style="color:#ffe600;
        text-shadow:0 0 20px rgba(255,230,0,.5)">
        {by_risk.get('MEDIUM',0)}
      </div>
      <div class="stat-pct" style="color:#ffe600">
        {round(by_risk.get('MEDIUM',0)/total*100,1)}% of total
      </div>
    </div>
    <div class="stat-card" style="background:rgba(0,255,231,.05);
      border:1px solid rgba(0,255,231,.2);">
      <div class="stat-label" style="color:#00ffe7">LOW</div>
      <div class="stat-number" style="color:#00ffe7;
        text-shadow:0 0 20px rgba(0,255,231,.5)">
        {by_risk.get('LOW',0)}
      </div>
      <div class="stat-pct" style="color:#00ffe7">
        {round(by_risk.get('LOW',0)/total*100,1)}% of total
      </div>
    </div>
  </div>

  <!-- GAUGE + RISK BARS -->
  <div class="gauge-section">
    <div class="gauge-wrap">
      <svg class="gauge-svg" viewBox="0 0 200 110">
        <!-- Track -->
        <path d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none" stroke="rgba(255,255,255,.06)"
          stroke-width="14" stroke-linecap="round"/>
        <!-- Low -->
        <path d="M 20 100 A 80 80 0 0 1 60 30"
          fill="none" stroke="#00ffe7" stroke-width="14"
          stroke-linecap="round" opacity=".7"/>
        <!-- Medium -->
        <path d="M 60 30 A 80 80 0 0 1 100 20"
          fill="none" stroke="#ffe600" stroke-width="14"
          stroke-linecap="round" opacity=".7"/>
        <!-- High -->
        <path d="M 100 20 A 80 80 0 0 1 140 30"
          fill="none" stroke="#ff6b00" stroke-width="14"
          stroke-linecap="round" opacity=".7"/>
        <!-- Critical -->
        <path d="M 140 30 A 80 80 0 0 1 180 100"
          fill="none" stroke="#ff2d2d" stroke-width="14"
          stroke-linecap="round" opacity=".7"/>
        <!-- Needle -->
        <line x1="100" y1="100"
          x2="100" y2="28"
          stroke="{gauge_color}"
          stroke-width="2.5"
          stroke-linecap="round"
          transform="rotate({gauge_angle},100,100)"/>
        <circle cx="100" cy="100" r="5"
          fill="{gauge_color}"
          style="filter:drop-shadow(0 0 6px {gauge_color})"/>
        <!-- Center label -->
        <text x="100" y="92" text-anchor="middle"
          font-family="Share Tech Mono,monospace"
          font-size="11" fill="{gauge_color}"
          letter-spacing="2">{gauge_label}</text>
      </svg>
      <div class="gauge-label" style="color:{gauge_color}">
        OVERALL THREAT LEVEL
      </div>
    </div>
    <div class="risk-rows">
      {risk_bar('CRITICAL', by_risk.get('CRITICAL',0), '#ff2d2d')}
      {risk_bar('HIGH',     by_risk.get('HIGH',0),     '#ff6b00')}
      {risk_bar('MEDIUM',   by_risk.get('MEDIUM',0),   '#ffe600')}
      {risk_bar('LOW',      by_risk.get('LOW',0),      '#00ffe7')}
    </div>
  </div>

  <!-- CHARTS ROW -->
  <div class="charts-row">
    <div class="chart-card">
      <div class="chart-title">TOP ATTACK TYPES</div>
      {type_bars if type_bars else
       '<p style="color:#2a3a50;font-size:12px">No data</p>'}
    </div>
    <div class="chart-card">
      <div class="chart-title">TOP SOURCE NATIONS</div>
      {country_rows if country_rows else
       '<p style="color:#2a3a50;font-size:12px">No data</p>'}
    </div>
  </div>

  <!-- AI REPORT SECTIONS -->
  {sections_html}

  <!-- ATTACK TABLE -->
  <div class="table-section">
    <div class="table-header">RECENT ATTACK LOG — LAST 20 EVENTS</div>
    <table>
      <thead>
        <tr>
          <td>TIMESTAMP</td><td>SOURCE IP</td><td>ATTACK TYPE</td>
          <td>PORT</td><td>COUNTRY</td><td>RISK</td>
        </tr>
      </thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>

  <!-- FOOTER -->
  <div class="report-footer">
    HONEYCLOUD SENTINEL &nbsp;·&nbsp; CONFIDENTIAL &nbsp;·&nbsp;
    AI-DRIVEN THREAT INTELLIGENCE &nbsp;·&nbsp; {now}
  </div>

</div>
</body>
</html>"""