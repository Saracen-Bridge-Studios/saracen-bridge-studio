# Inputs and evidence

Use the exact Field ID from `assets/field_map.json`, rather than matching repeated placeholders such as RATE or AMOUNT. Read its surrounding context and input type. The same placeholder can refer to an incentive rate, interest rate, fee or profit allocation.

| Status | Meaning | Required entry |
|---|---|---|
| Confirmed | Supported fact or explicit current user decision | Value and traceable source; identify whether it is a fact, instruction or executed contractual term |
| Proposed | Model assumption, scenario, draft, soft commitment or unverified term | Value, source and Notes explaining the limitation |
| Unknown | Missing, unresolved or conflicting information | Leave Value empty; explain the required answer and suggested owner in Notes |
| Not applicable | Expressly inapplicable field or unused row | Exact Value `Not applicable`; reason in Notes; cite the user's decision or supporting source when available |

Source citations must identify the document, date/version and page, clause, sheet/cell or current user instruction. Add short source identifiers to Evidence; do not rely on a filename containing FINAL or on recalled history. Verify the cited source was actually read. A non-empty source string passes the technical gate but does not prove its accuracy or authority.

Enter Amount as a plain number in the agreement's budget currency. Enter Rate points as 4 for 4%, never 0.04 or 4%. Enter Number as a positive whole number; waterfall tier references must be 1–10. Enter text as one line without square brackets. Unknown is not zero. Proposed financing is not committed financing. Mark unused rows Not applicable only with a reason.

For financing gather legal provider, amount, currency/FX basis, instrument, status, conditions, draw dates, interest basis/term, fees, security, repayment source and priority. Distinguish permanent sources from receivable advances and working capital. For fees gather percentage/amount, precise base, payer, milestones, funding source, tax, caps, included/excluded categories and offsets. For participation gather the pool share, participant share of that original pool, and distribution tier. Never assume one percentage establishes all three.

For revisions, retrieve the current project workbook, preserve confirmed values unless instructed or contradicted by current evidence, and give the new draft a new filename. Keep a change summary in the completion report. Never reuse another production's populated workbook as an intake template.
