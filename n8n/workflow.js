import {
  workflow,
  node,
  trigger,
  sticky,
  ifElse,
  languageModel,
  tool,
  outputParser,
  newCredential,
  expr,
  fromAi,
  nodeJson
} from '@n8n/workflow-sdk';

// ─── TRIGGERS ───────────────────────────────────────────────────────────────

const scheduleTrigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.3,
  config: {
    name: 'Daily Tariff Scan (6 AM)',
    parameters: {
      rule: {
        interval: [{ field: 'cronExpression', expression: '0 6 * * 1-5' }]
      }
    }
  },
  output: [{ triggeredAt: '2026-06-20T06:00:00Z' }]
});

const webhookTrigger = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'ERP Alert Webhook',
    parameters: {
      httpMethod: 'POST',
      path: 'tariff-alert',
      responseMode: 'onReceived'
    }
  },
  output: [{ body: { hs_code: '8471.30', product_name: 'Laptop', cogs_usd: 800 } }]
});

// ─── NORMALIZE INPUTS ────────────────────────────────────────────────────────

const normalizeInput = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Normalize Trigger Input',
    parameters: {
      mode: 'manual',
      includeOtherFields: false,
      assignments: {
        assignments: [
          {
            id: 'source',
            name: 'source',
            value: expr('{{ $json.body?.source ?? $json.source ?? "schedule" }}'),
            type: 'string'
          },
          {
            id: 'hs_code',
            name: 'hs_code',
            value: expr('{{ $json.body?.hs_code ?? $json.hs_code ?? "ALL" }}'),
            type: 'string'
          },
          {
            id: 'product_name',
            name: 'product_name',
            value: expr('{{ $json.body?.product_name ?? $json.product_name ?? "All Products" }}'),
            type: 'string'
          },
          {
            id: 'cogs_usd',
            name: 'cogs_usd',
            value: expr('{{ $json.body?.cogs_usd ?? $json.cogs_usd ?? 0 }}'),
            type: 'number'
          },
          {
            id: 'triggered_at',
            name: 'triggered_at',
            value: expr('{{ $now.toISO() }}'),
            type: 'string'
          }
        ]
      }
    }
  },
  output: [{ source: 'schedule', hs_code: 'ALL', product_name: 'All Products', cogs_usd: 0, triggered_at: '2026-06-20T06:00:00Z' }]
});

// ─── AI SUBNODES ─────────────────────────────────────────────────────────────

const openAiModel = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatOpenAi',
  version: 1.3,
  config: {
    name: 'GPT-5 Tariff Brain',
    parameters: {
      model: { __rl: true, mode: 'id', value: 'gpt-5' },
      options: { temperature: 0.1, reasoningEffort: 'high' }
    },
    credentials: { openAiApi: newCredential('OpenAI API') }
  }
});

const perplexityTariffTool = tool({
  type: 'n8n-nodes-base.perplexityTool',
  version: 2,
  config: {
    name: 'Perplexity Tariff Researcher',
    parameters: {
      resource: 'chat',
      operation: 'complete',
      model: 'sonar-pro',
      messages: {
        message: [
          {
            role: 'system',
            content: 'You are a trade compliance expert. Return only factual, cited tariff data from official government sources: Federal Register, USITC, CBP, and USTR.'
          },
          {
            role: 'user',
            content: fromAi('query', 'Tariff research query — include specific HS codes, trade partners, and date range')
          }
        ]
      },
      simplify: false,
      options: {
        searchMode: 'web',
        searchRecency: 'day',
        searchDomainFilter: 'federalregister.gov,usitc.gov,cbp.gov,ustr.gov',
        temperature: 0.1
      }
    },
    credentials: { perplexityApi: newCredential('Perplexity API') }
  }
});

const landedCostCalculatorTool = tool({
  type: '@n8n/n8n-nodes-langchain.toolCode',
  version: 1.3,
  config: {
    name: 'Landed Cost Calculator',
    parameters: {
      description: 'Calculate tariff-adjusted landed cost, margin impact, and break-even price. Provide JSON: { cogs_usd, new_tariff_rate, freight_rate, insurance_rate, customs_fee, current_price, volume_units }',
      language: 'javaScript',
      specifyInputSchema: true,
      schemaType: 'fromJson',
      jsonSchemaExample: JSON.stringify({
        cogs_usd: 800,
        new_tariff_rate: 0.145,
        freight_rate: 0.08,
        insurance_rate: 0.005,
        customs_fee: 25,
        current_price: 1200,
        volume_units: 500
      }),
      jsCode: `const input = JSON.parse(query);
const { cogs_usd=0, new_tariff_rate=0, freight_rate=0.08, insurance_rate=0.005, customs_fee=25, current_price=0, volume_units=1 } = input;

const tariff_amount    = cogs_usd * new_tariff_rate;
const freight_amount   = cogs_usd * freight_rate;
const insurance_amount = cogs_usd * insurance_rate;
const total_landed     = cogs_usd + tariff_amount + freight_amount + insurance_amount + customs_fee;
const gross_margin     = current_price > 0 ? ((current_price - total_landed) / current_price) * 100 : null;
const break_even       = total_landed * 1.15;
const total_exposure   = tariff_amount * volume_units;
const severity         = total_exposure > 500000 ? 'CRITICAL' : total_exposure > 100000 ? 'HIGH' : total_exposure > 25000 ? 'MEDIUM' : 'LOW';

return JSON.stringify({
  cost_breakdown: { cogs_usd: cogs_usd.toFixed(2), tariff_amount: tariff_amount.toFixed(2), freight_amount: freight_amount.toFixed(2), insurance_amount: insurance_amount.toFixed(2), customs_fee: customs_fee.toFixed(2), total_landed_cost: total_landed.toFixed(2) },
  margin_analysis: { gross_margin_pct: gross_margin ? gross_margin.toFixed(2)+'%' : 'N/A', break_even_price: break_even.toFixed(2), suggested_retail: (total_landed * 1.35).toFixed(2) },
  tariff_exposure: { per_unit_impact: tariff_amount.toFixed(2), total_annual_exposure_usd: total_exposure.toFixed(2), impact_severity: severity }
}, null, 2);`
    }
  }
});

const erpDataTool = tool({
  type: 'n8n-nodes-base.httpRequestTool',
  version: 4.4,
  config: {
    name: 'ERP Product Data Fetcher',
    parameters: {
      method: 'GET',
      url: fromAi('url', 'ERP API URL to fetch product or BOM data by HS code'),
      optimizeResponse: true,
      responseType: 'json',
      fieldsToInclude: 'selected',
      fields: 'hs_code,product_name,cogs_usd,supplier_country,current_price,volume_units'
    }
  }
});

const structuredParser = outputParser({
  type: '@n8n/n8n-nodes-langchain.outputParserStructured',
  version: 1.3,
  config: {
    name: 'Tariff Impact Schema Parser',
    parameters: {
      schemaType: 'fromJson',
      jsonSchemaExample: JSON.stringify({
        scan_date: '2026-06-20',
        tariff_changes: [
          {
            hs_code: '8471.30',
            description: 'Portable digital computers',
            previous_rate: 0.0,
            new_rate: 0.145,
            effective_date: '2026-07-01',
            trade_partner: 'China',
            federal_register_citation: 'FR Doc 2026-12345',
            confidence: 'high'
          }
        ],
        summary: 'Brief summary of tariff changes found',
        sources: ['https://federalregister.gov/...'],
        requires_immediate_action: true,
        affected_hs_codes: ['8471.30']
      })
    }
  }
});

// ─── MAIN AI AGENT ───────────────────────────────────────────────────────────

const tariffIntelAgent = node({
  type: '@n8n/n8n-nodes-langchain.agent',
  version: 3.1,
  config: {
    name: 'Tariff Intelligence Agent',
    parameters: {
      promptType: 'define',
      text: expr(
        'Analyze the US tariff landscape for HS code: {{ $json.hs_code }}. ' +
        'Product: {{ $json.product_name }}. COGS: ${{ $json.cogs_usd }}. Today: {{ $now.toFormat("yyyy-MM-dd") }}. ' +
        'Step 1: Use Perplexity Tariff Researcher to search Federal Register, USTR, CBP, USITC for any tariff changes in the last 24h. ' +
        'Step 2: If changes found, use Landed Cost Calculator with freight_rate=0.08, insurance_rate=0.005, customs_fee=25, volume_units=500. ' +
        'Step 3: Return structured JSON with all findings, financial impact, severity, and sourcing recommendations.'
      ),
      hasOutputParser: true,
      options: {
        systemMessage:
          'You are an expert trade compliance and supply chain analyst at a Fortune 500 manufacturer. ' +
          'Tools available: (1) Perplexity Tariff Researcher — real-time .gov regulatory data, ' +
          '(2) Landed Cost Calculator — deterministic JS financial modeling, ' +
          '(3) ERP Product Data Fetcher — live inventory data. ' +
          'Always cite sources. Flag CRITICAL items requiring same-day procurement action.',
        maxIterations: 8,
        returnIntermediateSteps: false
      }
    },
    subnodes: {
      model: openAiModel,
      tools: [perplexityTariffTool, landedCostCalculatorTool, erpDataTool],
      outputParser: structuredParser
    }
  },
  output: [
    {
      output: {
        scan_date: '2026-06-20',
        tariff_changes: [{ hs_code: '8471.30', description: 'Portable computers', previous_rate: 0, new_rate: 0.145, effective_date: '2026-07-01', trade_partner: 'China', confidence: 'high' }],
        summary: 'New 14.5% tariff on laptops from China effective July 1 2026',
        sources: ['https://federalregister.gov/documents/2026/06/18/tariff-update'],
        requires_immediate_action: true,
        affected_hs_codes: ['8471.30']
      }
    }
  ]
});

// ─── STORE AUDIT LOG ─────────────────────────────────────────────────────────

const storeTariffLog = node({
  type: 'n8n-nodes-base.dataTable',
  version: 1.1,
  config: {
    name: 'Store Tariff Intelligence Log',
    parameters: {
      resource: 'row',
      operation: 'insert',
      dataTableId: { __rl: true, mode: 'name', value: 'tariff_intelligence_log' },
      columns: {
        mappingMode: 'defineBelow',
        value: {
          scan_date: nodeJson(tariffIntelAgent, 'output.scan_date'),
          hs_codes_affected: nodeJson(tariffIntelAgent, 'output.affected_hs_codes'),
          summary: nodeJson(tariffIntelAgent, 'output.summary'),
          requires_action: nodeJson(tariffIntelAgent, 'output.requires_immediate_action'),
          changes_count: nodeJson(tariffIntelAgent, 'output.tariff_changes'),
          sources: nodeJson(tariffIntelAgent, 'output.sources'),
          raw_json: expr('{{ JSON.stringify($("Tariff Intelligence Agent").item.json.output) }}')
        },
        schema: [
          { id: 'scan_date', displayName: 'scan_date', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'hs_codes_affected', displayName: 'hs_codes_affected', required: false, defaultMatch: false, display: true, type: 'array', canBeUsedToMatch: false },
          { id: 'summary', displayName: 'summary', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'requires_action', displayName: 'requires_action', required: false, defaultMatch: false, display: true, type: 'boolean', canBeUsedToMatch: false },
          { id: 'changes_count', displayName: 'changes_count', required: false, defaultMatch: false, display: true, type: 'array', canBeUsedToMatch: false },
          { id: 'sources', displayName: 'sources', required: false, defaultMatch: false, display: true, type: 'array', canBeUsedToMatch: false },
          { id: 'raw_json', displayName: 'raw_json', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false }
        ]
      }
    }
  },
  output: [{ id: 1, createdAt: '2026-06-20T06:05:00Z' }]
});

// ─── ROUTE BY SEVERITY (references agent output via nodeJson) ────────────────

const checkActionRequired = ifElse({
  version: 2.2,
  config: {
    name: 'Action Required?',
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
        conditions: [
          {
            leftValue: nodeJson(tariffIntelAgent, 'output.requires_immediate_action'),
            operator: { type: 'boolean', operation: 'true' },
            rightValue: true
          }
        ],
        combinator: 'and'
      }
    }
  }
});

// ─── BUILD ALERT PAYLOAD ─────────────────────────────────────────────────────

const buildAlertPayload = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Build Alert Payload',
    parameters: {
      mode: 'manual',
      includeOtherFields: false,
      assignments: {
        assignments: [
          {
            id: 'slack_text',
            name: 'slack_text',
            value: expr(
              ':rotating_light: *TARIFF ALERT* — {{ $("Tariff Intelligence Agent").item.json.output.scan_date }}\n\n' +
              '*Summary:* {{ $("Tariff Intelligence Agent").item.json.output.summary }}\n' +
              '*Affected HS Codes:* {{ $("Tariff Intelligence Agent").item.json.output.affected_hs_codes?.join(", ") ?? "N/A" }}\n' +
              '*Changes Detected:* {{ $("Tariff Intelligence Agent").item.json.output.tariff_changes?.length ?? 0 }}\n' +
              '*Source:* {{ $("Tariff Intelligence Agent").item.json.output.sources?.[0] ?? "Federal Register" }}\n\n' +
              '_Immediate sourcing alternatives required. Review full report in Procurement portal._'
            ),
            type: 'string'
          },
          {
            id: 'email_subject',
            name: 'email_subject',
            value: expr(
              '[URGENT] Tariff Alert — {{ $("Tariff Intelligence Agent").item.json.output.affected_hs_codes?.join(", ") }} — {{ $("Tariff Intelligence Agent").item.json.output.scan_date }}'
            ),
            type: 'string'
          },
          {
            id: 'email_body',
            name: 'email_body',
            value: expr(
              '<h2>TariffIQ Intelligence Report — {{ $("Tariff Intelligence Agent").item.json.output.scan_date }}</h2>' +
              '<p><strong>Summary:</strong> {{ $("Tariff Intelligence Agent").item.json.output.summary }}</p>' +
              '<p><strong>HS Codes Affected:</strong> {{ $("Tariff Intelligence Agent").item.json.output.affected_hs_codes?.join(", ") }}</p>' +
              '<p><strong>Changes Requiring Action:</strong> {{ $("Tariff Intelligence Agent").item.json.output.tariff_changes?.length ?? 0 }}</p>' +
              '<p><strong>Sources:</strong> {{ $("Tariff Intelligence Agent").item.json.output.sources?.join(", ") }}</p>' +
              '<hr><em>Generated by TariffIQ Agent</em>'
            ),
            type: 'string'
          }
        ]
      }
    }
  },
  output: [
    {
      slack_text: ':rotating_light: TARIFF ALERT',
      email_subject: '[URGENT] Tariff Alert — 8471.30 — 2026-06-20',
      email_body: '<h2>TariffIQ Report</h2>'
    }
  ]
});

// ─── NOTIFICATIONS ────────────────────────────────────────────────────────────

const slackAlert = node({
  type: 'n8n-nodes-base.slack',
  version: 2.5,
  config: {
    name: 'Alert Procurement Slack Channel',
    parameters: {
      resource: 'message',
      operation: 'post',
      authentication: 'oAuth2',
      select: 'channel',
      channelId: { __rl: true, mode: 'name', value: '#procurement-alerts' },
      messageType: 'text',
      text: expr('{{ $json.slack_text }}'),
      otherOptions: { mrkdwn: true, includeLinkToWorkflow: true }
    },
    credentials: { slackOAuth2Api: newCredential('Slack OAuth2') }
  },
  output: [{ ok: true, message_timestamp: '1750000000.000100' }]
});

const emailAlert = node({
  type: 'n8n-nodes-base.gmail',
  version: 2.2,
  config: {
    name: 'Email Procurement Team',
    parameters: {
      resource: 'message',
      operation: 'send',
      sendTo: 'procurement@company.com, cfo@company.com',
      subject: nodeJson(buildAlertPayload, 'email_subject'),
      emailType: 'html',
      message: nodeJson(buildAlertPayload, 'email_body'),
      options: { appendAttribution: false, senderName: 'TariffIQ Agent' }
    },
    credentials: { gmailOAuth2: newCredential('Gmail OAuth2') }
  },
  output: [{ id: 'msg_12345', threadId: 'thread_67890' }]
});

// ─── LOG NO ACTION ────────────────────────────────────────────────────────────

const logNoChanges = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Log No Changes Detected',
    parameters: {
      mode: 'manual',
      includeOtherFields: false,
      assignments: {
        assignments: [
          {
            id: 'status',
            name: 'status',
            value: expr('No actionable tariff changes on {{ $now.toFormat("yyyy-MM-dd") }}. Next scan tomorrow 06:00.'),
            type: 'string'
          }
        ]
      }
    }
  },
  output: [{ status: 'No actionable tariff changes on 2026-06-20.' }]
});

// ─── STICKY NOTE ─────────────────────────────────────────────────────────────

const overviewNote = sticky(
  '## TariffIQ — Dynamic Tariff Realignment Agent\n\n' +
  '**Solves:** 72% of trade pros cite tariff volatility as #1 disruption — yet only 7% have automation\n\n' +
  '**Daily 6AM scan:** Federal Register + CBP + USTR via Perplexity\n' +
  '**On-demand webhook:** POST /tariff-alert from your ERP\n' +
  '**Outputs:** Audit log (DataTable) + Slack alert + Email to CFO\n\n' +
  '**Setup:** Add OpenAI API, Perplexity API, Slack OAuth2, Gmail OAuth2 credentials',
  [scheduleTrigger, webhookTrigger],
  { color: 3 }
);

// ─── WORKFLOW COMPOSITION ────────────────────────────────────────────────────

export default workflow('tariff-realignment-agent', 'TariffIQ — Dynamic Tariff Realignment Agent')
  .add(overviewNote)
  // Schedule trigger path
  .add(scheduleTrigger)
  .to(normalizeInput)
  .to(tariffIntelAgent)
  .to(storeTariffLog)
  .to(
    checkActionRequired
      .onTrue(buildAlertPayload.to(slackAlert).to(emailAlert))
      .onFalse(logNoChanges)
  )
  // Webhook trigger fans into the same normalizeInput node
  .add(webhookTrigger)
  .to(normalizeInput);
