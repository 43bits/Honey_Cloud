# ai_agents/threat_report_agent.py
import os
# Find this line at the top of threat_api.py
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(stats: dict, attacks: list) -> str:

    recent = attacks[:20]
    attack_summary = "\n".join([
        f"- {a.get('attack_type','?')} from {a.get('source_ip','?')} "
        f"({a.get('country','?')}) on port {a.get('port_targeted','?')} "
        f"| Risk: {a.get('risk_level','?')} "
        f"| Anomaly: {a.get('is_anomaly', False)} "
        f"| Campaign: {a.get('campaign','?')} "
        f"| Time: {a.get('timestamp','?')}"
        for a in recent
    ])

    by_type       = {}
    by_country    = {}
    anomaly_count = 0

    for a in attacks:
        t = a.get('attack_type', 'Unknown')
        c = a.get('country', 'Unknown')
        by_type[t]    = by_type.get(t, 0) + 1
        by_country[c] = by_country.get(c, 0) + 1
        if a.get('is_anomaly'):
            anomaly_count += 1

    top_types     = sorted(by_type.items(),    key=lambda x: x[1], reverse=True)[:5]
    top_countries = sorted(by_country.items(), key=lambda x: x[1], reverse=True)[:5]

    return f"""You are a senior cybersecurity analyst at a threat intelligence firm.
You have been given honeypot attack data from HoneyCloud Sentinel, an AI-powered
cloud honeypot system. Write a professional, detailed threat intelligence report.

=== ATTACK DATA SUMMARY ===
Total Attacks Captured : {stats.get('total_attacks', 0)}
Critical Threats       : {stats.get('by_risk', {}).get('CRITICAL', 0)}
High Threats           : {stats.get('by_risk', {}).get('HIGH', 0)}
Medium Threats         : {stats.get('by_risk', {}).get('MEDIUM', 0)}
Low Threats            : {stats.get('by_risk', {}).get('LOW', 0)}
Anomalous Attacks      : {anomaly_count}

Top Attack Types:
{chr(10).join(f"  {t}: {c} attacks" for t, c in top_types)}

Top Source Nations:
{chr(10).join(f"  {c}: {n} attacks" for c, n in top_countries)}

Recent Attack Log (last 20):
{attack_summary}

=== INSTRUCTIONS ===
Write a formal threat intelligence report with EXACTLY these 7 sections.
Use professional cybersecurity language. Base all findings on the actual
data above. Do NOT use markdown symbols like ** or ## anywhere.
Do NOT add any text before the first section heading.

EXECUTIVE SUMMARY
2-3 paragraphs covering overall threat landscape, most critical findings,
and immediate risk level for the organization.

THREAT ANALYSIS
Detailed breakdown of attack patterns. Discuss the top attack types,
attacker intent, and which are most dangerous. Reference specific IPs
and countries from the data.

ANOMALY DETECTION FINDINGS
Discuss the {anomaly_count} anomalous attacks flagged by the Isolation
Forest ML model. What makes them unusual? Potential zero-day indicators
or APT activity?

CAMPAIGN ATTRIBUTION
Based on clustering analysis, describe the likely attack campaigns.
Are these opportunistic automated attacks or targeted intrusions?
Evidence of botnet coordination?

RISK ASSESSMENT
State the overall risk level (CRITICAL, HIGH, MEDIUM, or LOW) with
full justification. Which systems are most at risk based on targeted ports?

IMMEDIATE RECOMMENDATIONS
Give exactly 5 numbered, specific, actionable security recommendations
based directly on this attack data.

INDICATORS OF COMPROMISE (IoCs)
List the top source IPs, targeted ports, and attack signatures from
this data that defenders should immediately block or monitor.

Write the complete report now."""


def generate_threat_report(stats: dict, attacks: list) -> str:
    """Call Groq API and return the report text."""

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError(
            "GROQ_API_KEY not found in .env — "
            "get a free key at console.groq.com"
        )

    prompt = build_prompt(stats, attacks)
    print("[AI Agent] Sending request to Groq (llama-3.3-70b)...")

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2500,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior cybersecurity analyst. "
                    "Write formal, professional threat intelligence reports. "
                    "Never use markdown like ** or ##. "
                    "Use plain text with the exact section headings provided. "
                    "Be specific, technical, and base everything on the data given."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    report_text = completion.choices[0].message.content
    print("[AI Agent] Report generated successfully")
    return report_text