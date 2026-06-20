---
title: TariffIQ — Dynamic Tariff Realignment Agent
emoji: ⚡
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: true
license: mit
short_description: AI agent that monitors US tariffs and calculates landed cost impact in real-time
---

# TariffIQ — Dynamic Tariff Realignment & Landed Cost Agent

> Solving a real enterprise pain point: **72% of trade professionals** cite US tariff volatility as their #1 disruption (Thomson Reuters 2026 Global Trade Report), yet only **7%** of companies use dedicated tariff management tools.

## What This Does

TariffIQ is a production-grade AI agent (built on n8n + Claude) that:

1. **Monitors** Federal Register, CBP, and USTR daily for tariff changes
2. **Calculates** full tariff-adjusted landed cost impact per product/HS code
3. **Alerts** procurement teams via Slack + Email when action is required
4. **Logs** every scan for audit trail and compliance records

## Live Demo Features

- **Landed Cost Simulator** — Input any product's COGS, tariff rate, logistics costs → instant margin impact
- **AI Tariff Analyst** — Chat with Claude about HS codes, sourcing strategy, trade regulations
- **Dashboard** — Simulated agent scan history and HS code watch list
- **Workflow Docs** — Full n8n architecture and setup guide

## n8n Agent Architecture

```
Schedule (6AM) / Webhook → Normalize → AI Agent → DataTable Log
                                          ├── Perplexity (Federal Register scan)
                                          ├── Landed Cost Calculator (JS)
                                          └── ERP Data Fetcher (HTTP)
                                              ↓
                                        IF: Action Required?
                                        ├── YES → Slack + Gmail alerts
                                        └── NO  → Silent log
```

## Powered By

- **n8n** — Workflow orchestration
- **Claude (claude-sonnet-4-6)** — AI analyst chat
- **Perplexity Sonar-Pro** — Real-time regulatory data
- **OpenAI GPT-5** — Agent reasoning (in n8n workflow)
- **Thomson Reuters 2026 Global Trade Report** — Research foundation

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set `ANTHROPIC_API_KEY` or enter it in the sidebar.

## Data Sources

- [Thomson Reuters 2026 Supply Chain Report](https://tax.thomsonreuters.com/blog/2026s-supply-chain-challenge-confronting-complexity-and-disruption-in-global-trade-tri/)
- US Federal Register (federalregister.gov)
- CBP (cbp.gov)
- USTR (ustr.gov)
- USITC (usitc.gov)
