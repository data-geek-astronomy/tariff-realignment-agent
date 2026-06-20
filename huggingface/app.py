import streamlit as st
import anthropic

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TariffIQ — Tariff Realignment Agent",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── STYLES ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem; font-weight: 800; color: #0a1628;
        letter-spacing: -0.5px; margin-bottom: 0;
    }
    .sub-header {
        font-size: 0.95rem; color: #4a5568; margin-top: 0.2rem;
    }
    .alert-critical {
        background: #fef2f2; border-left: 4px solid #b91c1c;
        padding: 1rem 1.2rem; border-radius: 4px; margin: 0.6rem 0;
        color: #1a1a1a;
    }
    .alert-critical b { color: #991b1b; }
    .alert-high {
        background: #fffbeb; border-left: 4px solid #d97706;
        padding: 1rem 1.2rem; border-radius: 4px; margin: 0.6rem 0;
        color: #1a1a1a;
    }
    .alert-high b { color: #92400e; }
    .alert-ok {
        background: #f0fdf4; border-left: 4px solid #16a34a;
        padding: 1rem 1.2rem; border-radius: 4px; margin: 0.6rem 0;
        color: #1a1a1a;
    }
    .alert-ok b { color: #14532d; }
    .stat-box {
        text-align: center; background: #ffffff;
        border: 1px solid #e2e8f0; padding: 1.4rem 1rem;
        border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .stat-number { font-size: 2rem; font-weight: 800; color: #0d47a1; }
    .stat-label { font-size: 0.8rem; color: #4a5568; margin-top: 0.3rem; }
    .scan-row {
        background: #f8fafc; border: 1px solid #e2e8f0;
        padding: 0.75rem 1rem; border-radius: 4px; margin: 0.35rem 0;
        color: #1a202c;
    }
    .scan-critical { border-left: 4px solid #b91c1c; }
    .scan-high     { border-left: 4px solid #d97706; }
    .scan-medium   { border-left: 4px solid #2563eb; }
    .scan-low      { border-left: 4px solid #16a34a; }
    .badge {
        display: inline-block; padding: 2px 10px; border-radius: 3px;
        font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-critical { background: #fecaca; color: #7f1d1d; }
    .badge-high     { background: #fde68a; color: #78350f; }
    .badge-medium   { background: #bfdbfe; color: #1e3a5f; }
    .badge-low      { background: #bbf7d0; color: #14532d; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">TariffIQ</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dynamic Tariff Realignment &amp; Landed Cost Intelligence Engine &mdash; Powered by Claude + n8n</p>', unsafe_allow_html=True)
st.divider()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.caption("Your key is never stored or logged.")

    st.divider()
    st.subheader("Market Reality")
    st.markdown("""
**Thomson Reuters 2026 Global Trade Report:**
- **72%** of trade pros cite tariff volatility as the #1 issue, up from 41%
- **68%** name supply chain as top strategic priority, up from 35%
- **39%** are absorbing tariff costs directly, up from 13%
- **40%** now exploring AI for trade management, up from 6% in 2024
- Only **7%** use dedicated tariff management tools

*TariffIQ fills that 93% gap.*
""")
    st.divider()
    st.subheader("n8n Workflow")
    st.markdown("""
Deploys as a production n8n agent:
- Daily Federal Register monitoring
- ERP BOM integration via webhook
- Slack and Gmail procurement alerts
- Permanent DataTable audit log
""")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Landed Cost Simulator",
    "AI Tariff Analyst",
    "Dashboard",
    "Workflow Architecture"
])

# ═══════════════════════════════════════════════════════════════════════
# TAB 1 — LANDED COST SIMULATOR
# ═══════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Tariff-Adjusted Landed Cost Calculator")
    st.caption("Model the full financial impact of tariff changes on your product portfolio.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Product Details**")
        product_name   = st.text_input("Product Name", value="Laptop — Acer Aspire 5")
        hs_code        = st.text_input("HS Code", value="8471.30.0100")
        supplier_country = st.selectbox("Supplier Country", ["China", "Vietnam", "Mexico", "India", "South Korea", "Taiwan", "Thailand"])
        cogs_usd       = st.number_input("Cost of Goods Sold (USD)", min_value=1.0, value=650.0, step=10.0)
        current_price  = st.number_input("Current Retail Price (USD)", min_value=1.0, value=999.0, step=10.0)
        volume_units   = st.number_input("Annual Volume (units)", min_value=1, value=5000, step=100)

    with col2:
        st.markdown("**Tariff & Logistics Parameters**")
        old_tariff_rate = st.slider("Previous Tariff Rate (%)", 0.0, 50.0, 0.0, 0.5) / 100
        new_tariff_rate = st.slider("New Tariff Rate (%)", 0.0, 50.0, 14.5, 0.5) / 100
        freight_rate    = st.slider("Freight (% of COGS)", 0.0, 20.0, 8.0, 0.5) / 100
        insurance_rate  = st.slider("Insurance (% of COGS)", 0.0, 5.0, 0.5, 0.1) / 100
        customs_fee     = st.number_input("Customs Processing Fee (USD/unit)", min_value=0.0, value=25.0, step=5.0)
        target_margin   = st.slider("Target Gross Margin (%)", 0.0, 60.0, 25.0, 1.0)

    if st.button("Calculate Tariff Impact", type="primary", use_container_width=True):

        def calc_landed(cogs, tariff, freight, insurance, customs):
            return cogs + (cogs * tariff) + (cogs * freight) + (cogs * insurance) + customs

        old_landed             = calc_landed(cogs_usd, old_tariff_rate, freight_rate, insurance_rate, customs_fee)
        new_landed             = calc_landed(cogs_usd, new_tariff_rate, freight_rate, insurance_rate, customs_fee)
        delta_per_unit         = new_landed - old_landed
        old_margin             = ((current_price - old_landed) / current_price) * 100
        new_margin             = ((current_price - new_landed) / current_price) * 100
        margin_compression     = old_margin - new_margin
        total_annual_exposure  = delta_per_unit * volume_units
        breakeven_price        = new_landed / (1 - target_margin / 100)
        required_price_increase = max(0, breakeven_price - current_price)

        if total_annual_exposure > 500_000:
            severity = "CRITICAL"
        elif total_annual_exposure > 100_000:
            severity = "HIGH"
        elif total_annual_exposure > 25_000:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        severity_label = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}[severity]

        st.divider()
        st.markdown(f"### Analysis Results &mdash; {severity_label} Impact", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Previous Landed Cost", f"${old_landed:,.2f}")
        m2.metric("New Landed Cost",      f"${new_landed:,.2f}", delta=f"+${delta_per_unit:,.2f}")
        m3.metric("Gross Margin (new)",   f"{new_margin:.1f}%",  delta=f"-{margin_compression:.1f}%", delta_color="inverse")
        m4.metric("Annual Exposure",      f"${total_annual_exposure:,.0f}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Cost Breakdown per Unit**")
            breakdown = {
                "COGS":         cogs_usd,
                "Tariff":       cogs_usd * new_tariff_rate,
                "Freight":      cogs_usd * freight_rate,
                "Insurance":    cogs_usd * insurance_rate,
                "Customs Fee":  customs_fee,
            }
            for k, v in breakdown.items():
                pct = (v / new_landed) * 100
                c_label, c_bar, c_val = st.columns([2, 4, 1.5])
                c_label.caption(k)
                c_bar.progress(pct / 100)
                c_val.caption(f"${v:.2f}")

        with col_b:
            st.markdown("**Recommended Actions**")
            if required_price_increase > 0:
                st.markdown(f"""
<div class="alert-critical">
<b>Price Adjustment Required</b><br>
Raise retail price by <b>${required_price_increase:,.2f}</b> (to <b>${breakeven_price:,.2f}</b>)
to maintain a {target_margin:.0f}% gross margin.
</div>""", unsafe_allow_html=True)

            st.markdown(f"""
<div class="alert-high">
<b>Sourcing Alternatives to Evaluate</b><br>
Vietnam: approx. 4% tariff (Section 232 exempt)<br>
Mexico: 0% under USMCA<br>
India: approx. 8.5% vs {new_tariff_rate*100:.1f}% from {supplier_country}
</div>""", unsafe_allow_html=True)

            st.markdown(f"""
<div class="alert-ok">
<b>Impact Summary</b><br>
Annual tariff exposure: <b>${total_annual_exposure:,.0f}</b><br>
Break-even retail price: <b>${breakeven_price:,.2f}</b><br>
Severity classification: <b>{severity}</b>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# TAB 2 — AI TARIFF ANALYST
# ═══════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("AI Tariff & Trade Compliance Analyst")
    st.caption("Ask anything about tariffs, HS codes, sourcing strategy, or trade regulations. Powered by Claude.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello. I am TariffIQ's trade compliance analyst. I can assist with:\n\n"
                    "- **Tariff impact analysis** — provide your HS code and COGS for a full breakdown\n"
                    "- **Sourcing strategy** — alternative suppliers, countries, and preferential trade agreements\n"
                    "- **Trade classification** — HS code lookups and CBP binding rulings\n"
                    "- **Regulatory intelligence** — Section 301, Section 232, USMCA, GSP, anti-dumping duties\n"
                    "- **Cost modeling** — landed cost scenarios under different tariff regimes\n\n"
                    "What tariff challenge is your team facing today?"
                )
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
            system_prompt = """You are TariffIQ, a senior trade compliance and supply chain analyst. You have deep expertise in:
- US Harmonized Tariff Schedule (HTS), Section 301, Section 232, anti-dumping and countervailing duties
- USMCA, US-Korea FTA, GSP, and other preferential trade agreements
- HS code classification methodology and CBP binding rulings
- Landed cost calculation: COGS + tariff + freight + insurance + customs fees
- Global sourcing strategy, nearshoring, and supplier diversification
- Federal Register monitoring and USTR/CBP/USITC regulatory intelligence

Key context from Thomson Reuters 2026 Global Trade Report:
- 72% of trade professionals cite US tariff volatility as their #1 operational disruption
- 68% cite supply chain management as their dominant strategic priority (up from 35%)
- Only 7% of companies use dedicated tariff management tools — a major market gap
- 65% are changing sourcing patterns, 57% renegotiating supplier contracts, 51% nearshoring

Always provide:
1. Specific, actionable recommendations with concrete numbers
2. Alternative sourcing options with estimated tariff rates by country
3. Regulatory citations (HS chapter, FR doc numbers, trade agreement articles) where applicable
4. Risk classification: CRITICAL / HIGH / MEDIUM / LOW
5. Clear next steps for a procurement or finance team

Be direct, precise, and professional. This is a decision-support tool for procurement and trade compliance teams."""

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

    if st.button("Clear Conversation", use_container_width=False):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# TAB 3 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Tariff Intelligence Dashboard")
    st.caption("Simulated output from the n8n agent's daily monitoring runs.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-box"><div class="stat-number">72%</div><div class="stat-label">Trade professionals citing tariff volatility as their #1 operational issue</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-box"><div class="stat-number">$2.1T</div><div class="stat-label">US imports subject to active tariff adjustments in 2026</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-box"><div class="stat-number">93%</div><div class="stat-label">Companies without automated tariff monitoring in place</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-box"><div class="stat-number">68h</div><div class="stat-label">Average time to detect a regulatory tariff change manually</div></div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### Recent Agent Scans")
    scans = [
        {"date": "2026-06-20  06:00", "hs_codes": "8471.30, 8528.72", "changes": 2, "severity": "CRITICAL", "summary": "New 14.5% tariff on laptops and monitors from China, effective July 1"},
        {"date": "2026-06-19  06:00", "hs_codes": "7318.15",          "changes": 1, "severity": "HIGH",     "summary": "25% Section 232 tariff extended on steel fasteners from EU"},
        {"date": "2026-06-18  06:00", "hs_codes": "ALL",              "changes": 0, "severity": "LOW",      "summary": "No actionable tariff changes detected"},
        {"date": "2026-06-17  06:00", "hs_codes": "9013.80",          "changes": 1, "severity": "MEDIUM",   "summary": "USTR exclusion expiring for optical instruments — 25% tariff resuming"},
        {"date": "2026-06-16  06:00", "hs_codes": "ALL",              "changes": 0, "severity": "LOW",      "summary": "No actionable tariff changes detected"},
    ]
    badge_class = {"CRITICAL": "badge-critical", "HIGH": "badge-high", "MEDIUM": "badge-medium", "LOW": "badge-low"}
    scan_class  = {"CRITICAL": "scan-critical",  "HIGH": "scan-high",  "MEDIUM": "scan-medium",  "LOW": "scan-low"}

    for scan in scans:
        bc = badge_class[scan["severity"]]
        sc = scan_class[scan["severity"]]
        st.markdown(f"""
<div class="scan-row {sc}">
  <span style="font-weight:600; color:#1a202c;">{scan["date"]}</span>
  &nbsp;&nbsp;
  <span class="badge {bc}">{scan["severity"]}</span>
  &nbsp;&nbsp;
  <span style="color:#374151;">{scan["changes"]} change(s)</span>
  <br>
  <span style="color:#1f2937;">{scan["summary"]}</span>
  <br>
  <span style="color:#6b7280; font-size:0.82rem;">HS Codes: <code style="color:#374151;">{scan["hs_codes"]}</code></span>
</div>""", unsafe_allow_html=True)

    st.divider()

    st.markdown("### Active HS Code Watch List")
    header_cols = st.columns([2, 3, 2, 2, 1.5])
    header_cols[0].markdown("**HS Code**")
    header_cols[1].markdown("**Description**")
    header_cols[2].markdown("**Origin**")
    header_cols[3].markdown("**Tariff Status**")
    header_cols[4].markdown("**Risk**")

    watchlist = [
        ("8471.30", "Portable digital computers", "China",   "0% to 14.5%",       "CRITICAL"),
        ("7318.15", "Steel fasteners",            "EU / UK", "25% (active)",       "HIGH"),
        ("9013.80", "Optical instruments",        "Japan",   "Exclusion expiring", "MEDIUM"),
        ("3926.90", "Plastic parts",              "Vietnam", "0% (exemption)",     "LOW"),
        ("8544.42", "Electric conductors",        "Mexico",  "0% (USMCA)",         "LOW"),
    ]
    severity_text_color = {"CRITICAL": "#7f1d1d", "HIGH": "#78350f", "MEDIUM": "#1e3a5f", "LOW": "#14532d"}
    for row in watchlist:
        c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1.5])
        c1.code(row[0])
        c2.caption(row[1])
        c3.caption(row[2])
        c4.caption(row[3])
        color = severity_text_color[row[4]]
        c5.markdown(f'<span style="color:{color}; font-weight:600;">{row[4]}</span>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# TAB 4 — WORKFLOW ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("n8n Workflow Architecture")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
### Agent Flow

```
[Schedule Trigger: 6AM Mon–Fri]  ──────────────┐
[Webhook Trigger: POST /tariff-alert]  ─────────┤
                                                 ▼
                                    [Normalize Trigger Input]
                                                 │
                                                 ▼
                        ┌────────────────────────────────────────┐
                        │       TARIFF INTELLIGENCE AGENT        │
                        │  Model: GPT-5  (temperature = 0.1)     │
                        │                                        │
                        │  Tool 1: Perplexity Tariff Researcher  │
                        │    Search: federalregister.gov         │
                        │            cbp.gov / ustr.gov          │
                        │            usitc.gov                   │
                        │  Tool 2: Landed Cost Calculator (JS)   │
                        │    Output: margin, break-even,         │
                        │            severity, annual exposure   │
                        │  Tool 3: ERP Product Data Fetcher      │
                        │    HTTP GET: live BOM / COGS data      │
                        │                                        │
                        │  Output Parser: Structured JSON        │
                        └────────────────────────────────────────┘
                                                 │
                                                 ▼
                                [Store Tariff Intelligence Log]
                                   n8n DataTable — permanent audit trail
                                                 │
                                                 ▼
                                    [IF: Action Required?]
                                   /                        \
                              [TRUE]                      [FALSE]
                                 │                            │
                        [Build Alert Payload]        [Log No Changes]
                       /                   \
          [Slack: #procurement-alerts]   [Gmail: CFO + Procurement]
```

### Node Reference

| Node | Type | Purpose |
|------|------|---------|
| Daily Tariff Scan | Schedule Trigger | Cron `0 6 * * 1-5` — weekday 6 AM |
| ERP Alert Webhook | Webhook (POST) | On-demand trigger from ERP systems |
| Normalize Input | Set | Harmonizes both trigger payloads |
| Tariff Intelligence Agent | AI Agent v3.1 | Orchestrates all tools, returns structured JSON |
| GPT-5 Tariff Brain | Language Model | Temperature 0.1, reasoning=high |
| Perplexity Tariff Researcher | Perplexity Tool | Sonar-Pro, government domains only |
| Landed Cost Calculator | Code Tool (JS) | Deterministic cost and margin math |
| ERP Product Data Fetcher | HTTP Request Tool | BOM and COGS data from ERP API |
| Tariff Impact Schema Parser | Structured Output Parser | Enforces consistent JSON schema |
| Store Tariff Log | DataTable (insert) | Permanent audit trail |
| Action Required? | IF node | Routes on `requires_immediate_action` |
| Alert Procurement Slack | Slack | Posts to #procurement-alerts |
| Email Procurement Team | Gmail | HTML report to CFO and procurement |
""")

    with col2:
        st.markdown("### Setup Checklist")
        checks = [
            ("OpenAI API Key",      "GPT-5 model for the AI Agent node"),
            ("Perplexity API Key",  "Sonar-Pro for real-time regulatory search"),
            ("Slack OAuth2",        "#procurement-alerts channel"),
            ("Gmail OAuth2",        "Sender account for procurement emails"),
            ("ERP API endpoint",    "Product and BOM data source"),
            ("n8n instance",        "Cloud or self-hosted"),
        ]
        for name, desc in checks:
            st.checkbox(name, value=False, help=desc)

        st.divider()
        st.markdown("### Design Rationale")
        st.markdown("""
**Perplexity over generic web search**
Domain-filtered to `.gov` sources ensures the agent only acts on official regulatory data, not press articles.

**Code Tool for cost math**
Deterministic JavaScript eliminates any risk of LLM hallucination on financial figures.

**DataTable for audit log**
Native n8n storage — zero external config, queryable across all executions, included in n8n Cloud.

**Temperature = 0.1**
Trade compliance is a factual domain. Low temperature produces consistent, citable outputs.

**IF over Switch**
The routing decision is binary: actionable or not. A Switch node adds unnecessary complexity.
""")

        st.divider()
        st.markdown("### Cost Estimate")
        st.markdown("""
| Component | Monthly Cost |
|-----------|-------------|
| n8n Cloud Starter | $24 |
| OpenAI GPT-5 (~21 runs) | ~$8 |
| Perplexity Sonar-Pro | ~$5 |
| **Total** | **~$37/mo** |

Enterprise tariff platforms: $2,000–$8,000/month.
""")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.divider()
st.caption("TariffIQ — Production-grade tariff intelligence. Data: Thomson Reuters 2026 Global Trade Report | Powered by Claude + n8n | 2026")
