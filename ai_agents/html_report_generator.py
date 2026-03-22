# ai_agents/html_report_generator.py
from datetime import datetime


def generate_html_report(report_text: str, stats: dict, attacks: list) -> str:

    now           = datetime.now().strftime('%B %d, %Y  %H:%M UTC')
    by_risk       = stats.get('by_risk', {})
    total         = stats.get('total_attacks', 0) or 1
    top_types     = stats.get('top_attack_types', [])
    top_countries = stats.get('top_countries', [])

    # ── Risk distribution bars ─────────────────────
    def risk_row(label, count, color):
        pct = round(count / total * 100, 1)
        return f"""
        <div class="risk-row">
          <span class="mono" style="color:{color};font-size:10px;letter-spacing:0.1em;width:72px;flex-shrink:0">{label}</span>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%;background:{color}"></div>
          </div>
          <span class="mono" style="color:{color};font-size:13px;font-weight:600;width:36px;text-align:right;flex-shrink:0">{count}</span>
          <span class="mono" style="color:rgba(255,255,255,0.2);font-size:9px;width:40px;text-align:right;flex-shrink:0">{pct}%</span>
        </div>"""

    # ── Horizontal bar charts ──────────────────────
    bar_colors = ['#38bdf8', '#ef4444', '#f59e0b', '#22c55e', '#a78bfa']

    def hbars(items, key_label, key_count, max_val):
        out = ''
        for i, item in enumerate(items):
            pct   = round(item[key_count] / max_val * 100) if max_val else 0
            color = bar_colors[i % len(bar_colors)]
            label = item[key_label]
            if len(label) > 22:
                label = label[:20] + '…'
            out += f"""
            <div style="margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                <span class="mono" style="font-size:10px;color:rgba(255,255,255,0.45)">{label}</span>
                <span class="mono" style="font-size:10px;color:{color};font-weight:500">{item[key_count]}</span>
              </div>
              <div style="height:3px;background:rgba(255,255,255,0.05);border-radius:2px;overflow:hidden">
                <div style="height:100%;width:{pct}%;background:{color};border-radius:2px"></div>
              </div>
            </div>"""
        return out

    max_type    = max((t['count'] for t in top_types), default=1)
    max_country = max((c['count'] for c in top_countries), default=1)
    type_bars   = hbars(top_types,     'type',    'count', max_type)
    country_bars= hbars(top_countries, 'country', 'count', max_country)

    # ── Risk gauge SVG ─────────────────────────────
    critical_pct = by_risk.get('CRITICAL', 0) / total * 100
    high_pct     = by_risk.get('HIGH', 0)     / total * 100
    danger_score = min(100, critical_pct * 1.5 + high_pct * 0.8)
    gauge_angle  = -90 + (danger_score / 100 * 180)
    gauge_color  = ('#ef4444' if danger_score > 70
                    else '#f59e0b' if danger_score > 40
                    else '#eab308' if danger_score > 20
                    else '#38bdf8')
    gauge_label  = ('CRITICAL' if danger_score > 70
                    else 'HIGH' if danger_score > 40
                    else 'MEDIUM' if danger_score > 20
                    else 'LOW')

    # ── Recent attacks table ───────────────────────
    risk_colors = {
        'CRITICAL': '#ef4444',
        'HIGH':     '#f59e0b',
        'MEDIUM':   '#eab308',
        'LOW':      '#38bdf8',
    }
    rows = ''
    for a in attacks[:20]:
        rc = risk_colors.get(a.get('risk_level', 'LOW'), '#38bdf8')
        anomaly = '<span style="font-size:8px;padding:1px 5px;border:1px solid rgba(234,179,8,0.3);border-radius:2px;color:#eab308;background:rgba(234,179,8,0.06);margin-left:6px;font-family:IBM Plex Mono,monospace">⚠</span>' if a.get('is_anomaly') else ''
        rows += f"""
        <tr>
          <td class="mono" style="color:rgba(255,255,255,0.3);font-size:10px">{str(a.get('timestamp',''))[:16]}</td>
          <td class="mono" style="color:#38bdf8;font-size:10px">{a.get('source_ip','?')}</td>
          <td style="font-size:11px">{a.get('attack_type','?')}{anomaly}</td>
          <td class="mono" style="color:rgba(255,255,255,0.3);font-size:10px">:{a.get('port_targeted','?')}</td>
          <td style="font-size:11px;color:rgba(255,255,255,0.4)">{a.get('country','?')}</td>
          <td><span class="mono" style="font-size:9px;padding:2px 6px;border:1px solid {rc}35;border-radius:2px;color:{rc};background:{rc}0d;letter-spacing:0.06em">{a.get('risk_level','?')}</span></td>
        </tr>"""

    # ── Parse AI report sections ───────────────────
    section_names = [
        'EXECUTIVE SUMMARY',
        'THREAT ANALYSIS',
        'ANOMALY DETECTION FINDINGS',
        'CAMPAIGN ATTRIBUTION',
        'RISK ASSESSMENT',
        'IMMEDIATE RECOMMENDATIONS',
        'INDICATORS OF COMPROMISE',
    ]

    sections_html = ''
    current = None
    buf     = []

    def flush_section(name, lines):
        content = '\n'.join(lines).strip()
        if not content or not name:
            return ''
        is_ioc  = 'INDICATOR' in name
        is_recs = 'RECOMMENDATION' in name
        body    = ''
        if is_ioc:
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    body += f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:rgba(34,197,94,0.8);padding:3px 0;border-bottom:1px solid rgba(34,197,94,0.06)">▸ {line}</div>'
        elif is_recs:
            import re
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                line = re.sub(
                    r'^(\d+\.)\s*',
                    r'<span style="color:#38bdf8;font-family:IBM Plex Mono,monospace;font-weight:600">\1</span> ',
                    line
                )
                body += f'<p style="margin-bottom:8px">{line}</p>'
        else:
            for chunk in content.split('\n\n'):
                chunk = chunk.strip().replace('\n', ' ')
                if chunk:
                    body += f'<p style="margin-bottom:10px">{chunk}</p>'

        icons = {'EXECUTIVE':'01','THREAT':'02','ANOMALY':'03',
                 'CAMPAIGN':'04','RISK':'05','IMMEDIATE':'06','INDICATOR':'07'}
        num = next((v for k, v in icons.items() if k in name), '—')

        return f"""
        <div class="section">
          <div class="section-head">
            <span class="mono" style="color:rgba(56,189,248,0.4);font-size:10px;letter-spacing:0.1em">{num}</span>
            <span class="mono" style="color:rgba(255,255,255,0.5);font-size:9px;letter-spacing:0.16em">{name}</span>
          </div>
          <div class="section-body">{body}</div>
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
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=Inter:wght@400;500;600&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{
  background:#060a12;
  color:rgba(255,255,255,0.65);
  font-family:'Inter',sans-serif;
  font-size:13px;
  line-height:1.7;
}}
/* grid bg */
body::before{{
  content:'';position:fixed;inset:0;
  background-image:linear-gradient(rgba(56,189,248,0.015) 1px,transparent 1px),linear-gradient(90deg,rgba(56,189,248,0.015) 1px,transparent 1px);
  background-size:48px 48px;pointer-events:none;
}}
.mono{{font-family:'IBM Plex Mono',monospace}}
.page{{max-width:1000px;margin:0 auto;padding:0 24px 60px;position:relative}}

/* ── HEADER ── */
.report-header{{
  border-bottom:1px solid rgba(255,255,255,0.06);
  padding:32px 0 24px;
  margin-bottom:24px;
}}
.header-line{{
  height:2px;
  background:linear-gradient(90deg,#38bdf8,rgba(56,189,248,0));
  margin-bottom:24px;
}}
.report-title{{
  font-family:'IBM Plex Mono',monospace;
  font-size:28px;font-weight:600;
  color:#e2e8f0;
  letter-spacing:0.12em;
  line-height:1.1;
}}
.report-sub{{
  font-family:'IBM Plex Mono',monospace;
  font-size:10px;
  color:rgba(255,255,255,0.25);
  letter-spacing:0.18em;
  margin-top:6px;
}}
.meta-row{{
  display:flex;gap:24px;flex-wrap:wrap;margin-top:16px;
}}
.meta-item{{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px;color:rgba(255,255,255,0.2);letter-spacing:0.1em;
}}
.meta-val{{color:rgba(255,255,255,0.4)}}

/* ── STAT GRID ── */
.stat-grid{{
  display:grid;grid-template-columns:repeat(4,1fr);
  gap:1px;background:rgba(255,255,255,0.04);
  margin-bottom:1px;
}}
.stat-cell{{
  background:#060a12;padding:14px 16px;
  position:relative;overflow:hidden;
}}
.stat-cell::after{{
  content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
}}
.stat-label{{font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:0.14em;color:rgba(255,255,255,0.2);margin-bottom:6px}}
.stat-number{{font-family:'IBM Plex Mono',monospace;font-size:28px;font-weight:700;line-height:1}}
.stat-sub{{font-family:'IBM Plex Mono',monospace;font-size:8px;color:rgba(255,255,255,0.15);margin-top:4px}}

/* ── PANEL ── */
.panel{{
  background:#060a12;
  border:1px solid rgba(255,255,255,0.06);
  border-radius:3px;
  overflow:hidden;
  margin-bottom:12px;
}}
.panel-head{{
  display:flex;align-items:center;gap:10px;
  padding:8px 12px;
  border-bottom:1px solid rgba(255,255,255,0.06);
  background:rgba(255,255,255,0.02);
}}
.panel-title{{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px;letter-spacing:0.14em;color:rgba(255,255,255,0.3);
}}
.panel-body{{padding:12px 16px}}

/* ── TWO COL ── */
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}}
@media(max-width:700px){{.two-col{{grid-template-columns:1fr}}.stat-grid{{grid-template-columns:repeat(2,1fr)}}}}

/* ── GAUGE ── */
.gauge-row{{
  display:grid;grid-template-columns:180px 1fr;gap:24px;align-items:center;
  padding:16px;
}}
@media(max-width:600px){{.gauge-row{{grid-template-columns:1fr}}}}
.gauge-label{{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px;letter-spacing:0.12em;
  text-align:center;margin-top:4px;
}}
.risk-row{{
  display:flex;align-items:center;gap:10px;
  margin-bottom:10px;
}}
.bar-track{{
  flex:1;height:3px;
  background:rgba(255,255,255,0.05);
  border-radius:2px;overflow:hidden;
}}
.bar-fill{{height:100%;border-radius:2px}}

/* ── SECTIONS ── */
.section{{
  background:#060a12;
  border:1px solid rgba(255,255,255,0.06);
  border-radius:3px;
  margin-bottom:8px;
  overflow:hidden;
}}
.section-head{{
  display:flex;align-items:center;gap:12px;
  padding:8px 12px;
  border-bottom:1px solid rgba(255,255,255,0.06);
  background:rgba(255,255,255,0.015);
}}
.section-body{{
  padding:14px 16px;
  font-size:12px;
  color:rgba(255,255,255,0.5);
  line-height:1.75;
}}

/* ── TABLE ── */
.attack-table-wrap{{
  background:#060a12;
  border:1px solid rgba(255,255,255,0.06);
  border-radius:3px;
  overflow:hidden;
  margin-bottom:24px;
}}
.table-head{{
  padding:8px 12px;
  border-bottom:1px solid rgba(255,255,255,0.06);
  background:rgba(255,255,255,0.02);
  font-family:'IBM Plex Mono',monospace;
  font-size:9px;letter-spacing:0.14em;
  color:rgba(255,255,255,0.3);
}}
table{{width:100%;border-collapse:collapse}}
thead td{{
  font-family:'IBM Plex Mono',monospace;
  font-size:8px;letter-spacing:0.12em;
  color:rgba(255,255,255,0.2);
  padding:8px 12px;
  border-bottom:1px solid rgba(255,255,255,0.06);
  background:rgba(255,255,255,0.01);
}}
tbody tr{{border-bottom:1px solid rgba(255,255,255,0.03)}}
tbody tr:hover{{background:rgba(255,255,255,0.015)}}
tbody td{{padding:7px 12px;font-size:11px;color:rgba(255,255,255,0.5)}}

/* ── FOOTER ── */
.report-footer{{
  border-top:1px solid rgba(255,255,255,0.06);
  padding-top:16px;margin-top:32px;
  text-align:center;
  font-family:'IBM Plex Mono',monospace;
  font-size:8px;letter-spacing:0.12em;
  color:rgba(255,255,255,0.12);
}}
@media print{{
  body{{background:#060a12 !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
  body::before{{display:none}}
}}
</style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div class="report-header">
    <div class="header-line"></div>
    <div class="report-title">HONEYCLOUD SENTINEL</div>
    <div class="report-sub">THREAT INTELLIGENCE REPORT</div>
    <div class="meta-row">
      <div class="meta-item">GENERATED &nbsp;<span class="meta-val">{now}</span></div>
      <div class="meta-item">EVENTS &nbsp;<span class="meta-val">{stats.get('total_attacks',0)}</span></div>
      <div class="meta-item">CLASSIFICATION &nbsp;<span class="meta-val">CONFIDENTIAL</span></div>
    </div>
  </div>

  <!-- STAT STRIP -->
  <div class="stat-grid" style="margin-bottom:12px">
    <div class="stat-cell" style="border-bottom:2px solid #ef4444">
      <div class="stat-label" style="color:rgba(239,68,68,0.6)">CRITICAL</div>
      <div class="stat-number" style="color:#ef4444">{by_risk.get('CRITICAL',0)}</div>
      <div class="stat-sub">{round(by_risk.get('CRITICAL',0)/total*100,1)}% of total</div>
    </div>
    <div class="stat-cell" style="border-bottom:2px solid #f59e0b">
      <div class="stat-label" style="color:rgba(245,158,11,0.6)">HIGH</div>
      <div class="stat-number" style="color:#f59e0b">{by_risk.get('HIGH',0)}</div>
      <div class="stat-sub">{round(by_risk.get('HIGH',0)/total*100,1)}% of total</div>
    </div>
    <div class="stat-cell" style="border-bottom:2px solid #eab308">
      <div class="stat-label" style="color:rgba(234,179,8,0.6)">MEDIUM</div>
      <div class="stat-number" style="color:#eab308">{by_risk.get('MEDIUM',0)}</div>
      <div class="stat-sub">{round(by_risk.get('MEDIUM',0)/total*100,1)}% of total</div>
    </div>
    <div class="stat-cell" style="border-bottom:2px solid #38bdf8">
      <div class="stat-label" style="color:rgba(56,189,248,0.6)">LOW</div>
      <div class="stat-number" style="color:#38bdf8">{by_risk.get('LOW',0)}</div>
      <div class="stat-sub">{round(by_risk.get('LOW',0)/total*100,1)}% of total</div>
    </div>
  </div>

  <!-- GAUGE + CHARTS -->
  <div class="two-col">

    <!-- Gauge + risk bars -->
    <div class="panel">
      <div class="panel-head"><span class="panel-title">THREAT LEVEL</span></div>
      <div class="gauge-row">
        <div style="text-align:center">
          <svg viewBox="0 0 180 100" width="180" height="100">
            <path d="M 18 90 A 72 72 0 0 1 162 90" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="12" stroke-linecap="round"/>
            <path d="M 18 90 A 72 72 0 0 1 54 28"  fill="none" stroke="#38bdf8" stroke-width="12" stroke-linecap="round" opacity="0.6"/>
            <path d="M 54 28 A 72 72 0 0 1 90 18"  fill="none" stroke="#eab308" stroke-width="12" stroke-linecap="round" opacity="0.6"/>
            <path d="M 90 18 A 72 72 0 0 1 126 28" fill="none" stroke="#f59e0b" stroke-width="12" stroke-linecap="round" opacity="0.6"/>
            <path d="M 126 28 A 72 72 0 0 1 162 90" fill="none" stroke="#ef4444" stroke-width="12" stroke-linecap="round" opacity="0.6"/>
            <line x1="90" y1="90" x2="90" y2="24" stroke="{gauge_color}" stroke-width="2.5" stroke-linecap="round" transform="rotate({gauge_angle},90,90)"/>
            <circle cx="90" cy="90" r="4" fill="{gauge_color}"/>
            <text x="90" y="82" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="10" fill="{gauge_color}" letter-spacing="1">{gauge_label}</text>
          </svg>
          <div class="gauge-label mono" style="color:{gauge_color};font-size:8px;letter-spacing:0.12em">OVERALL RISK</div>
        </div>
        <div>
          {risk_row('CRITICAL', by_risk.get('CRITICAL',0), '#ef4444')}
          {risk_row('HIGH',     by_risk.get('HIGH',0),     '#f59e0b')}
          {risk_row('MEDIUM',   by_risk.get('MEDIUM',0),   '#eab308')}
          {risk_row('LOW',      by_risk.get('LOW',0),      '#38bdf8')}
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div style="display:flex;flex-direction:column;gap:12px">
      <div class="panel">
        <div class="panel-head"><span class="panel-title">ATTACK TYPES</span></div>
        <div class="panel-body">
          {type_bars if type_bars else '<span style="font-size:10px;color:rgba(255,255,255,0.1)">no data</span>'}
        </div>
      </div>
      <div class="panel">
        <div class="panel-head"><span class="panel-title">SOURCE NATIONS</span></div>
        <div class="panel-body">
          {country_bars if country_bars else '<span style="font-size:10px;color:rgba(255,255,255,0.1)">no data</span>'}
        </div>
      </div>
    </div>

  </div>

  <!-- AI REPORT SECTIONS -->
  {sections_html}

  <!-- ATTACK TABLE -->
  <div class="attack-table-wrap">
    <div class="table-head">RECENT ATTACK LOG — LAST 20 EVENTS</div>
    <table>
      <thead><tr>
        <td>TIMESTAMP</td><td>SOURCE IP</td><td>ATTACK TYPE</td>
        <td>PORT</td><td>COUNTRY</td><td>RISK</td>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <!-- FOOTER -->
  <div class="report-footer">
    HONEYCLOUD SENTINEL &nbsp;·&nbsp; CONFIDENTIAL &nbsp;·&nbsp; AI-DRIVEN THREAT INTELLIGENCE &nbsp;·&nbsp; {now}
  </div>

</div>
</body>
</html>"""
