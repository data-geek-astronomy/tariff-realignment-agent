import streamlit as st
import json
import os
import time
import random
from datetime import datetime, timedelta
import anthropic

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TariffIQ — Tariff Realignment Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── STYLES ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header { font-size: 2.4rem; font-weight: 800; color: #1a1a2e; margin-bottom: 0; }
    .sub-header { font-size: 1rem; color: #555; margin-top: 0; }
    .metric-card { background: #f8f9fa; border-left: 4px solid #0066cc; padding: 1rem; border-radius: 6px; margin: 0.5rem 0; }
    .alert-critical { background: #fff0f0; border-left: 4px solid #cc0000; padding: 1rem; border-radius: 6px; }
    .alert-high { background: #fff8e1; border-left: 4px solid #ff6600; padding: 1rem; border-radius: 6px; }
    .alert-ok { background: #f0fff4; border-left: 4px solid #00aa44; padding: 1rem; border-radius: 6px; }
    .stat-box { text-align: center; background: white; border: 1px solid #e0e0e0; padding: 1.2rem; border-radius: 8px; }
    .stat-number { font-size: 2rem; font-weight: 800; color: #0066cc; }
    .stat-label { font-size: 0.85rem; color: #666; }
    .tag-chip { display: inline-block; background: #e3f2fd; color: #0066cc; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; margin: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">⚡ TariffIQ</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dynamic Tariff Realignment & Landed Cost Intelligence Engine — Powered by Claude + n8n</p>', unsafe_allow_html=True)
st.divider()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔧 Configuration")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.caption("Your key is never stored or logged.")

    st.divider()
    st.subheader("📊 Market Reality")
    st.markdown("""
    **Thomson Reuters 2026 Global Trade Report:**
    - **72%** of trade pros cite tariff volatility as #1 issue ↑ from 41%
    - **68%** name supply chain as top strategic priority ↑ from 35%
    - **39%** absorbing tariff costs (up from 13%)
    - **40%** now exploring AI/blockchain (↑ from 6% in 2024)
    - Only **7%** use dedicated tariff management tools

    *This agent fills that 93% gap.*
    """)
    st.divider()
    st.subheader("🔗 n8n Workflow")
    st.markdown("Deploys as a production n8n agent with:\n- Daily Federal Register monitoring\n- ERP integration\n- Slack/Email alerts\n- Audit log DataTable")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🧮 Landed Cost Simulator", "🤖 AI Tariff Analyst", "📈 Dashboard", "📋 n8n Workflow"])

# ═══════════════════════════════════════════════════════════════════════
# TAB 1 — LANDED COST SIMULATOR
# ═══════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Tariff-Adjusted Landed Cost Calculator")
    st.caption("Model the full financial impact of tariff changes on your product portfolio.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Product Details**")
        product_name = st.text_input("Product Name", value="Laptop — Acer Aspire 5")
        hs_code = st.text_input("HS Code", value="8471.30.0100")
        supplier_country = st.selectbox("Supplier Country", ["China", "Vietnam", "Mexico", "India", "South Korea", "Taiwan", "Thailand"])
        cogs_usd = st.number_input("Cost of Goods Sold (USD)", min_value=1.0, value=650.0, step=10.0)
        current_price = st.number_input("Current Retail Price (USD)", min_value=1.0, value=999.0, step=10.0)
        volume_units = st.number_input("Annual Volume (units)", min_value=1, value=5000, step=100)

    with col2:
        st.markdown("**Tariff & Logistics Parameters**")
        old_tariff_rate = st.slider("Previous Tariff Rate (%)", 0.0, 50.0, 0.0, 0.5) / 100
        new_tariff_rate = st.slider("New Tariff Rate (%)", 0.0, 50.0, 14.5, 0.5) / 100
        freight_rate = st.slider("Freight (% of COGS)", 0.0, 20.0, 8.0, 0.5) / 100
        insurance_rate = st.slider("Insurance (% of COGS)", 0.0, 5.0, 0.5, 0.1) / 100
        customs_fee = st.number_input("Customs Processing Fee (USD/unit)", min_value=0.0, value=25.0, step=5.0)
        target_margin = st.slider("Target Gross Margin (%)", 0.0, 60.0, 25.0, 1.0)

    if st.button("⚡ Calculate Tariff Impact", type="primary", use_container_width=True):
        # ── Calculations ──
        def calc_landed(cogs, tariff, freight, insurance, customs):
            return cogs + (cogs * tariff) + (cogs * freight) + (cogs * insurance) + customs

        old_landed = calc_landed(cogs_usd, old_tariff_rate, freight_rate, insurance_rate, customs_fee)
        new_landed = calc_landed(cogs_usd, new_tariff_rate, freight_rate, insurance_rate, customs_fee)
        delta_per_unit = new_landed - old_landed
        old_margin = ((current_price - old_landed) / current_price) * 100
        new_margin = ((current_price - new_landed) / current_price) * 100
        margin_compression = old_margin - new_margin
        total_annual_exposure = delta_per_unit * volume_units
        breakeven_price = new_landed / (1 - target_margin / 100)
        required_price_increase = max(0, breakeven_price - current_price)

        if total_annual_exposure > 500_000:
            severity = "CRITICAL"
            severity_color = "🔴"
        elif total_annual_exposure > 100_000:
            severity = "HIGH"
            severity_color = "🟠"
        elif total_annual_exposure > 25_000:
            severity = "MEDIUM"
            severity_color = "🟡"
        else:
            severity = "LOW"
            severity_color = "🟢"

        st.divider()
        st.markdown(f"### Results — {severity_color} {severity} Impact")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Old Landed Cost", f"${old_landed:,.2f}", delta=None)
        m2.metric("New Landed Cost", f"${new_landed:,.2f}", delta=f"+${delta_per_unit:,.2f}")
        m3.metric("Margin Compression", f"{new_margin:.1f}%", delta=f"-{margin_compression:.1f}%", delta_color="inverse")
        m4.metric("Annual Exposure", f"${total_annual_exposure:,.0f}", delta=None)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Cost Breakdown (per unit)**")
            breakdown = {
                "COGS": cogs_usd,
                "Tariff (new)": cogs_usd * new_tariff_rate,
                "Freight": cogs_usd * freight_rate,
                "Insurance": cogs_usd * insurance_rate,
                "Customs Fee": customs_fee
            }
            for k, v in breakdown.items():
                pct = (v / new_landed) * 100
                col_label, col_bar, col_val = st.columns([2, 4, 1.5])
                col_label.caption(k)
                col_bar.progress(pct / 100)
                col_val.caption(f"${v:.2f}")

        with col_b:
            st.markdown("**Recommended Actions**")
            if required_price_increase > 0:
                st.markdown(f"""
<div class="alert-critical">
<b>Price Adjustment Required</b><br>
Raise retail price by <b>${required_price_increase:,.2f}</b> (to ${breakeven_price:,.2f}) to maintain {target_margin}% margin.
</div>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div class="alert-high">
<b>Sourcing Alternatives to Evaluate:</b><br>
• Vietnam: ~4% tariff (Section 232 exempt)<br>
• Mexico: 0% under USMCA<br>
• India: ~8.5% vs {new_tariff_rate*100:.1f}% from {supplier_country}
</div>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div class="alert-ok">
<b>Impact Summary:</b><br>
Annual tariff exposure: <b>${total_annual_exposure:,.0f}</b><br>
Break-even retail price: <b>${breakeven_price:,.2f}</b><br>
Severity: <b>{severity}</b>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# TAB 2 — AI TARIFF ANALYST
# ═══════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🤖 AI Tariff & Trade Compliance Analyst")
    st.caption("Ask anything about tariffs, HS codes, sourcing strategy, or trade regulations. Powered by Claude.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm TariffIQ's AI analyst. I can help you with:\n\n"
                           "• **Tariff impact analysis** — give me your HS code and COGS\n"
                           "• **Sourcing strategy** — alternative suppliers and countries\n"
                           "• **Trade classification** — HS code lookups and rulings\n"
                           "• **Regulatory intelligence** — Section 301, 232, USMCA, etc.\n"
                           "• **Cost modeling** — landed cost scenarios\n\n"
                           "What tariff challenge are you facing today?"
            }
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about tariffs, HS codes, sourcing strategy..."):
        if not api_key:
            st.error("Please enter your Anthropic API Key in the sidebar.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            system_prompt = """You are TariffIQ, an expert trade compliance and supply chain analyst with deep expertise in:
- US tariff schedules (HTS), Section 301, Section 232, anti-dumping duties
- USMCA, US-Korea FTA, GSP, and other preferential trade agreements
- HS code classification and CBP rulings
- Landed cost calculation and margin impact modeling
- Global sourcing strategy and supplier diversification
- Federal Register monitoring and regulatory intelligence

Key context from Thomson Reuters 2026 Global Trade Report:
- 72% of trade professionals cite US tariff volatility as their #1 disruption
- 68% cite supply chain management as their dominant strategic priority (up from 35%)
- Only 7% of companies use dedicated tariff management tools — massive gap
- 65% are changing sourcing patterns, 57% renegotiating supplier contracts, 51% nearshoring

Always provide:
1. Specific, actionable recommendations
2. Concrete numbers and percentages where relevant
3. Alternative sourcing options with estimated tariff rates
4. Regulatory citations when applicable
5. Risk assessment (CRITICAL/HIGH/MEDIUM/LOW)

Be direct and tactical. This is a procurement decision support tool."""

            client = anthropic.Anthropic(api_key=api_key)
            full_response = ""
            response_placeholder = st.empty()

            messages_for_api = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=system_prompt,
                messages=messages_for_api
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    if st.button("🗑️ Clear Chat", use_container_width=False):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# TAB 3 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📈 Tariff Intelligence Dashboard")
    st.caption("Live simulation of the n8n agent's monitoring output.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-box"><div class="stat-number">72%</div><div class="stat-label">Trade pros cite tariff volatility as #1 issue</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-box"><div class="stat-number">$2.1T</div><div class="stat-label">US imports subject to active tariff changes</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-box"><div class="stat-number">93%</div><div class="stat-label">SMEs without automated tariff monitoring</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-box"><div class="stat-number">68h</div><div class="stat-label">Avg time to detect regulatory change manually</div></div>', unsafe_allow_html=True)

    st.divider()

    # ── Simulated Recent Scans ──
    st.markdown("### Recent Agent Scans (Simulated)")
    scans = [
        {"date": "2026-06-20 06:00", "hs_codes": "8471.30, 8528.72", "changes": 2, "severity": "CRITICAL", "summary": "New 14.5% tariff on laptops & monitors from China, effective July 1"},
        {"date": "2026-06-19 06:00", "hs_codes": "7318.15", "changes": 1, "severity": "HIGH", "summary": "25% Section 232 tariff extended on steel fasteners from EU"},
        {"date": "2026-06-18 06:00", "hs_codes": "ALL", "changes": 0, "severity": "LOW", "summary": "No actionable tariff changes detected"},
        {"date": "2026-06-17 06:00", "hs_codes": "9013.80", "changes": 1, "severity": "MEDIUM", "summary": "USTR exclusion expiring for optical instruments — 25% tariff resuming"},
        {"date": "2026-06-16 06:00", "hs_codes": "ALL", "changes": 0, "severity": "LOW", "summary": "No actionable tariff changes detected"},
    ]
    for scan in scans:
        color = {"CRITICAL": "#ffcccc", "HIGH": "#fff2cc", "MEDIUM": "#e8f4fd", "LOW": "#f0fff4"}[scan["severity"]]
        icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🔵", "LOW": "🟢"}[scan["severity"]]
        st.markdown(f"""
<div style="background:{color}; padding:0.8rem 1rem; border-radius:6px; margin:0.4rem 0;">
<b>{icon} {scan["date"]}</b> &nbsp;|&nbsp; <b>{scan["severity"]}</b> &nbsp;|&nbsp; {scan["changes"]} changes<br>
<span style="color:#333">{scan["summary"]}</span><br>
<small>HS Codes: <code>{scan["hs_codes"]}</code></small>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── HS Code Watch List ──
    st.markdown("### Active HS Code Watch List")
    watchlist = [
        ("8471.30", "Portable digital computers", "China", "0% → 14.5%", "CRITICAL"),
        ("7318.15", "Steel fasteners", "EU/UK", "25% (active)", "HIGH"),
        ("9013.80", "Optical instruments", "Japan", "Exclusion expiring", "MEDIUM"),
        ("3926.90", "Plastic parts", "Vietnam", "0% (USMCA-like)", "LOW"),
        ("8544.42", "Electric conductors", "Mexico", "0% (USMCA)", "LOW"),
    ]
    cols = st.columns([2, 3, 2, 2, 1.5])
    cols[0].markdown("**HS Code**")
    cols[1].markdown("**Description**")
    cols[2].markdown("**Origin**")
    cols[3].markdown("**Tariff Status**")
    cols[4].markdown("**Risk**")
    for row in watchlist:
        icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[row[4]]
        c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1.5])
        c1.code(row[0])
        c2.caption(row[1])
        c3.caption(row[2])
        c4.caption(row[3])
        c5.markdown(f"{icon} {row[4]}")

# ═══════════════════════════════════════════════════════════════════════
# TAB 4 — WORKFLOW DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📋 n8n Workflow Architecture")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
### Agent Flow Diagram

```
[Schedule Trigger: 6AM Weekdays]  ─────────────────────┐
[Webhook Trigger: /tariff-alert]  ─────────────────────┤
                                                        ▼
                                           [Normalize Trigger Input]
                                                        │
                                                        ▼
                                        ┌──────────────────────────────────┐
                                        │    TARIFF INTELLIGENCE AGENT     │
                                        │  ┌─────────────────────────────┐ │
                                        │  │  Model: GPT-5 (temp=0.1)   │ │
                                        │  └─────────────────────────────┘ │
                                        │  Tools:                          │
                                        │  ├─ Perplexity (Federal Register)│
                                        │  ├─ Landed Cost Calculator (JS)  │
                                        │  └─ ERP Data Fetcher (HTTP)      │
                                        │  Output: Structured JSON Schema  │
                                        └──────────────────────────────────┘
                                                        │
                                                        ▼
                                         [Store Tariff Intelligence Log]
                                            (n8n DataTable — audit trail)
                                                        │
                                                        ▼
                                            [Action Required? IF node]
                                           /                             \\
                                   [TRUE]                                [FALSE]
                                      │                                     │
                              [Build Alert Payload]               [Log No Changes]
                             /                   \\
                [Slack: #procurement-alerts]  [Gmail: procurement@]
```

### Node Configuration Summary

| Node | Type | Purpose |
|------|------|---------|
| Daily Tariff Scan | Schedule Trigger | Fires 6AM Mon–Fri via cron `0 6 * * 1-5` |
| ERP Alert Webhook | Webhook (POST) | `/tariff-alert` endpoint for ERP push events |
| Normalize Input | Set (manual) | Harmonizes both trigger payloads |
| Tariff Intelligence Agent | AI Agent v3.1 | Orchestrates all 3 tools with structured output |
| GPT-5 Tariff Brain | LM (OpenAI) | Low temperature (0.1) for factual analysis |
| Perplexity Tariff Researcher | Perplexity Tool | Sonar-Pro, searches `.gov` domains only |
| Landed Cost Calculator | Code Tool (JS) | Computes full cost breakdown + margin impact |
| ERP Data Fetcher | HTTP Request Tool | Pulls product/BOM data from ERP API |
| Tariff Impact Schema Parser | Structured Output Parser | Enforces consistent JSON schema |
| Store Tariff Log | DataTable (insert) | Permanent audit trail across all executions |
| Action Required? | IF node | Routes on `requires_immediate_action` boolean |
| Alert Procurement Slack | Slack (message/post) | Posts to `#procurement-alerts` with mrkdwn |
| Email Procurement Team | Gmail (message/send) | HTML email with full impact report |
""")

    with col2:
        st.markdown("### Setup Checklist")
        checks = [
            ("OpenAI API Key", "GPT-5 access for AI Agent"),
            ("Perplexity API Key", "Real-time web search (Sonar-Pro)"),
            ("Slack OAuth2 App", "#procurement-alerts channel"),
            ("Gmail OAuth2", "procurement@company.com sender"),
            ("ERP API endpoint", "Product/BOM data (or skip for demo)"),
            ("n8n instance", "Cloud or self-hosted with workflow imported"),
        ]
        for name, desc in checks:
            st.checkbox(name, value=False, help=desc)

        st.divider()
        st.markdown("### Key Design Decisions")
        st.markdown("""
**Why Perplexity over generic web search?**
Domain-filtered to `.gov` sources ensures only official regulatory data reaches the agent.

**Why Code Tool for math?**
Deterministic JS computation avoids LLM hallucination on financial calculations.

**Why DataTable for logs?**
Native n8n storage — zero config, queryable across executions, free on Cloud.

**Why IF not Switch?**
Binary decision: actionable vs. no-action. Switch adds complexity without benefit.

**Why temperature=0.1?**
Trade compliance requires factual precision over creativity.
""")

        st.divider()
        st.markdown("### n8n Deployment")
        st.code("""
# Import workflow JSON to n8n
# File: n8n/workflow.json

# Set credentials in n8n UI:
# Settings → Credentials → New
# 1. OpenAI API
# 2. Perplexity API
# 3. Slack OAuth2 API
# 4. Gmail OAuth2

# Activate workflow → Done!
""", language="bash")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.divider()
st.caption("TariffIQ — Built for production. Data: Thomson Reuters 2026 Global Trade Report | Powered by Claude + n8n | © 2026")
