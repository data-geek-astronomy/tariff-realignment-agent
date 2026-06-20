# TariffIQ — Dynamic Tariff Realignment & Landed Cost Agent

**Production-grade n8n AI agent** that monitors US tariff changes 24/7, calculates financial impact, and alerts procurement teams before margin damage occurs.

## The Problem (Real Data)

From the **Thomson Reuters 2026 Global Trade Report** (225 senior trade professionals surveyed):

| Metric | 2025 | 2026 | Change |
|--------|------|------|--------|
| Tariff volatility as #1 issue | 41% | **72%** | +76% |
| Supply chain as top priority | 35% | **68%** | +94% |
| Absorbing tariff costs | 13% | **39%** | +200% |
| Using tariff mgmt software | 7% | 7% | flat |
| Exploring AI for trade | 6% | **40%** | +567% |

**93% of companies have no automated tariff monitoring.** This agent fills that gap.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     TariffIQ n8n Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Schedule: 6AM M-F]  ──────────────────────┐                  │
│  [Webhook: /tariff-alert] ──────────────────┤                  │
│                                             ▼                  │
│                                  [Normalize Trigger Input]      │
│                                             │                  │
│                                             ▼                  │
│  ┌──────────────────── AI AGENT ───────────────────────────┐   │
│  │  Model: GPT-5 (temperature=0.1, reasoning=high)         │   │
│  │                                                         │   │
│  │  Tool 1: Perplexity Sonar-Pro                          │   │
│  │    → Scans: federalregister.gov, cbp.gov, ustr.gov     │   │
│  │    → Filter: last 24 hours only                        │   │
│  │                                                         │   │
│  │  Tool 2: Landed Cost Calculator (JS Code Tool)         │   │
│  │    → COGS + Tariff + Freight + Insurance + Customs     │   │
│  │    → Margin impact, break-even, severity rating        │   │
│  │                                                         │   │
│  │  Tool 3: ERP Product Data Fetcher (HTTP Tool)          │   │
│  │    → Pulls live BOM/product data from your ERP         │   │
│  │                                                         │   │
│  │  Output: Structured JSON (tariff changes + impacts)    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                             │                  │
│                                             ▼                  │
│                              [DataTable: tariff_intelligence_log]│
│                                             │                  │
│                                    [IF: Action Required?]       │
│                                   /                    \        │
│                              [TRUE]                  [FALSE]    │
│                                 │                       │       │
│                    [Build Alert Payload]       [Log No Changes] │
│                   /                  \                          │
│        [Slack: #procurement]   [Gmail: cfo+procurement]        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Repo Structure

```
tariff-realignment-agent/
├── n8n/
│   └── workflow.js          # n8n Workflow SDK code (import to n8n)
├── huggingface/
│   ├── app.py               # Streamlit demo app
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Hugging Face Space config
└── README.md                # This file
```

## Deployment

### n8n Workflow
1. Copy `n8n/workflow.js` content
2. In n8n: New Workflow → Code Editor → Paste → Save
3. Set credentials: OpenAI API, Perplexity API, Slack OAuth2, Gmail OAuth2
4. Activate workflow

### Hugging Face Space
1. Create new Space (Streamlit SDK)
2. Upload contents of `huggingface/` folder
3. Set `ANTHROPIC_API_KEY` in Space Secrets
4. Space auto-deploys

## Credentials Required

| Credential | Used By | Purpose |
|-----------|---------|---------|
| OpenAI API | AI Agent Model | GPT-5 reasoning |
| Perplexity API | Tariff Researcher Tool | Real-time .gov search |
| Slack OAuth2 | Alert Node | #procurement-alerts channel |
| Gmail OAuth2 | Alert Node | Email to CFO + procurement |

## Cost Estimate (per month)

| Component | Cost |
|-----------|------|
| n8n Cloud (Starter) | $24/mo |
| OpenAI GPT-5 (~21 runs/mo) | ~$8/mo |
| Perplexity Sonar-Pro | ~$5/mo |
| **Total** | **~$37/mo** |

vs. Enterprise tariff platforms: $2,000–$8,000/month

## References

- [Thomson Reuters 2026 Global Trade Report](https://tax.thomsonreuters.com/blog/2026s-supply-chain-challenge-confronting-complexity-and-disruption-in-global-trade-tri/)
- [FreightWaves: Tariff Volatility 2026](https://www.freightwaves.com/news/tariff-volatility-pushes-global-supply-chains-into-regional-reset-in-2026)
- [SupplyChainBrain: Tariff-Adjusted Landed Cost](https://www.supplychainbrain.com/blogs/1-think-tank/post/44045-tariff-adjusted-landed-cost-as-the-new-sourcing-metric)
