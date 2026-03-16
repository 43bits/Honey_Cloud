# ai_agents/threat_intelligence_agent.py
import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Base agent caller ──────────────────────────────

def run_agent(system_prompt: str, user_prompt: str,
              max_tokens: int = 400) -> str:
    """Single agent call to Groq."""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=0.1,
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Agent error: {str(e)}"


# ── Agent 1: Log Analyzer ──────────────────────────

def agent_log_analyzer(attack: dict) -> str:
    """Extracts and structures all attack indicators."""

    system = """You are a cybersecurity log analyst.
Your job is to extract and structure attack indicators from raw log data.
Be concise. Use bullet points. No markdown headers.
Focus only on facts present in the data."""

    user = f"""Analyze this honeypot attack log and extract all indicators:

Source IP:     {attack.get('source_ip', 'unknown')}
Port Targeted: {attack.get('port_targeted', 'unknown')}
Protocol:      {attack.get('protocol', 'unknown')}
Attack Type:   {attack.get('attack_type', 'unknown')}
Country:       {attack.get('country', 'unknown')}
City:          {attack.get('city', 'unknown')}
Risk Level:    {attack.get('risk_level', 'unknown')}
Risk Score:    {attack.get('risk_score', 0)}/100
Is Anomaly:    {attack.get('is_anomaly', False)}
Anomaly Score: {attack.get('anomaly_score', 0)}
Campaign:      {attack.get('campaign', 'unknown')}
MITRE ID:      {attack.get('mitre_technique_id', 'unknown')}
MITRE Tactic:  {attack.get('mitre_tactic', 'unknown')}
Timestamp:     {attack.get('timestamp', 'unknown')}

Extract:
- Key indicators of compromise (IoCs)
- Attack characteristics
- Anomaly indicators if present
- Geographic threat context"""

    return run_agent(system, user, max_tokens=300)


# ── Agent 2: Threat Investigator ───────────────────

def agent_threat_investigator(attack: dict, log_analysis: str) -> str:
    """Investigates the threat context and likely campaign."""

    system = """You are a threat intelligence investigator.
You identify threat actors, campaigns, and attack patterns.
Be specific and actionable. No markdown. Use plain text with bullet points."""

    user = f"""Investigate this attack based on indicators:

ATTACK DATA:
Type: {attack.get('attack_type', 'unknown')}
IP:   {attack.get('source_ip', 'unknown')}
Country: {attack.get('country', 'unknown')}
MITRE Technique: {attack.get('mitre_technique_id', '?')} — {attack.get('mitre_technique_name', '?')}
MITRE Tactic: {attack.get('mitre_tactic', 'unknown')}
Campaign Cluster: {attack.get('campaign', 'unknown')}
Anomaly: {attack.get('is_anomaly', False)}

LOG ANALYSIS:
{log_analysis}

Investigate:
- Likely threat actor type (nation-state, cybercriminal, hacktivist, script kiddie)
- Attack campaign characteristics
- Probable attacker objective (credential theft, ransomware staging, espionage, etc.)
- Whether this matches known attack patterns
- Confidence level in your assessment"""

    return run_agent(system, user, max_tokens=350)


# ── Agent 3: Risk Analyst ──────────────────────────

def agent_risk_analyst(attack: dict, investigation: str) -> str:
    """Assesses specific risk to the organization."""

    system = """You are a cybersecurity risk analyst.
You assess the specific impact and risk of attacks on infrastructure.
Be direct and quantify risk where possible. Plain text, bullet points."""

    user = f"""Assess the risk of this attack:

ATTACK:
Type:       {attack.get('attack_type', 'unknown')}
Port:       {attack.get('port_targeted', 'unknown')}
Risk Score: {attack.get('risk_score', 0)}/100
Risk Level: {attack.get('risk_level', 'unknown')}
Anomaly:    {attack.get('is_anomaly', False)}

INVESTIGATION FINDINGS:
{investigation}

Assess:
- What systems are at immediate risk
- Potential business impact if attack succeeds
- Data or assets that could be compromised
- Likelihood of escalation to full breach
- Overall severity rating with justification"""

    return run_agent(system, user, max_tokens=300)


# ── Agent 4: Response Recommender ─────────────────

def agent_response_recommender(attack: dict, risk_assessment: str) -> str:
    """Generates specific immediate response actions."""

    system = """You are an incident response specialist.
You give specific, actionable, immediate response recommendations.
Number each action. Be specific — include actual commands or configs where relevant.
Plain text only."""

    user = f"""Generate immediate response actions for this attack:

ATTACK:
Type:       {attack.get('attack_type', 'unknown')}
Source IP:  {attack.get('source_ip', 'unknown')}
Port:       {attack.get('port_targeted', 'unknown')}
Country:    {attack.get('country', 'unknown')}
Risk Level: {attack.get('risk_level', 'unknown')}
MITRE:      {attack.get('mitre_technique_id', '?')}

RISK ASSESSMENT:
{risk_assessment}

Provide exactly 5 numbered immediate actions.
Each action must be specific and executable by a security engineer right now.
Include actual commands, firewall rules, or config changes where applicable."""

    return run_agent(system, user, max_tokens=400)


# ── Orchestrator ──────────────────────────────────

    
    
    

# def run_threat_intelligence_pipeline(attack: dict,
#                                       force: bool = False) -> dict:
#     """
#     Runs all 4 agents in sequence on a single attack.
#     force=True bypasses the risk level threshold check.
#     """
#     risk_level = attack.get('risk_level', 'LOW')

#     # Only skip if not forced AND below threshold
#     if not force and risk_level not in ('HIGH', 'CRITICAL'):
#         return {
#             'skipped': True,
#             'reason':  f'Risk level {risk_level} below threshold',
#         }

#     print(f"\n[TI Agent] Investigating {risk_level} attack from "
#           f"{attack.get('source_ip','?')}...")

#     start = time.time()

#     print("[TI Agent] Agent 1: Analyzing log indicators...")
#     log_analysis = agent_log_analyzer(attack)

#     print("[TI Agent] Agent 2: Investigating threat context...")
#     investigation = agent_threat_investigator(attack, log_analysis)

#     print("[TI Agent] Agent 3: Assessing risk...")
#     risk_assessment = agent_risk_analyst(attack, investigation)

#     print("[TI Agent] Agent 4: Generating response actions...")
#     response_actions = agent_response_recommender(attack, risk_assessment)

#     elapsed = round(time.time() - start, 1)
#     print(f"[TI Agent] Complete in {elapsed}s")

#     return {
#         'skipped':          False,
#         'attack_ip':        attack.get('source_ip', 'unknown'),
#         'attack_type':      attack.get('attack_type', 'unknown'),
#         'risk_level':       risk_level,
#         'mitre_id':         attack.get('mitre_technique_id', 'unknown'),
#         'log_analysis':     log_analysis,
#         'investigation':    investigation,
#         'risk_assessment':  risk_assessment,
#         'response_actions': response_actions,
#         'generated_at':     time.strftime('%Y-%m-%d %H:%M:%S'),
#         'elapsed_seconds':  elapsed,
#     }


def run_threat_intelligence_pipeline(attack: dict,
                                      force: bool = False) -> dict:
    """
    Runs all 4 agents in sequence.
    force=True bypasses risk level threshold (for manual investigations).
    """
    risk_level = attack.get('risk_level', 'LOW')

    # Skip only if not forced AND below threshold
    if not force and risk_level not in ('HIGH', 'CRITICAL'):
        return {
            'skipped': True,
            'reason':  f'Risk level {risk_level} below threshold '
                       f'(need HIGH or CRITICAL)',
        }

    print(f"\n[TI Agent] Investigating {risk_level} attack "
          f"from {attack.get('source_ip','?')}...")

    start = time.time()

    print("[TI Agent] Agent 1: Analyzing log indicators...")
    log_analysis = agent_log_analyzer(attack)

    print("[TI Agent] Agent 2: Investigating threat context...")
    investigation = agent_threat_investigator(attack, log_analysis)

    print("[TI Agent] Agent 3: Assessing risk...")
    risk_assessment = agent_risk_analyst(attack, investigation)

    print("[TI Agent] Agent 4: Generating response actions...")
    response_actions = agent_response_recommender(attack, risk_assessment)

    elapsed = round(time.time() - start, 1)
    print(f"[TI Agent] Complete in {elapsed}s")

    return {
        'skipped':          False,
        'attack_ip':        attack.get('source_ip', 'unknown'),
        'attack_type':      attack.get('attack_type', 'unknown'),
        'risk_level':       risk_level,
        'mitre_id':         attack.get('mitre_technique_id', 'unknown'),
        'log_analysis':     log_analysis,
        'investigation':    investigation,
        'risk_assessment':  risk_assessment,
        'response_actions': response_actions,
        'generated_at':     time.strftime('%Y-%m-%d %H:%M:%S'),
        'elapsed_seconds':  elapsed,
    }
