# Girl Made of Thorns — Golden Regression Test

## Purpose and isolation rule

Use this case only to test calculation, source, status and recommendation discipline. Never reuse its facts, spend assumptions, route assumptions or financing terms for another project.

Source model: `Saracen_Bridge_GMOT_Location_Incentive_Pilot_Stage_3.xlsx`, dated 2026-08-21.

## Core test inputs

- Net production budget: EUR 14,203,041.
- Finance costs: EUR 730,390.21.
- Gross production budget: EUR 14,933,431.21.
- IVA facility: EUR 1,236,066, treated as working capital and excluded from permanent sources.
- Existing equity: EUR 6,473,587.50.
- Target MG: EUR 3,100,000, not yet obtained.
- Current tax-incentive loan: EUR 5,364,727.
- Current modelled qualifying base: EUR 11,662,450; not yet supported by a line-budget eligibility map.
- Planned photography: 30 days in Spain.
- Central unresolved issue: domestic/co-production versus foreign-service legal route.
- Workstream categories overlap by EUR 1,777,133 and require line-budget reconciliation.

## Expected scenario outputs

Tolerance: EUR 1,000 for monetary results and 0.01 for weighted scores, unless the source workbook has been intentionally revised.

| Route | Net economic benefit | Funding surplus/(gap) | Weighted score | RAG | Expected position |
|---|---:|---:|---:|---|---|
| Basque Country | EUR 4,824,629 | EUR 588,006 | 3.91 | Amber | Conditional preferred |
| Canary Islands | EUR 3,639,557 | EUR (572,997) | 3.59 | Amber | Operational fallback |
| Common-territory Spain | EUR 2,298,676 | EUR (2,631,480) | 3.54 | Red | Structurally clearer but material gap |

The current finance-plan placeholder is a reconciliation case, not a location recommendation. It uses a flat 50% assumption and 92% realisation without identifying the legal programme route.

## Expected recommendation

The GPT should recommend the Basque Country only as **CONDITIONALLY PREFERRED**. It must identify Araba, Bizkaia or Gipuzkoa, obtain a written foral tax opinion and secure credible tax capacity/monetisation before reliance. The Canary Islands should remain the fallback.

The GPT must not issue a final Green recommendation. Basque remains Amber because legal route, territory, eligible base, tax capacity and comparable location costs are not fully confirmed.

## Mandatory decision gates

1. Route-classification memorandum covering domestic/co-production and foreign-service alternatives.
2. Named Basque foral territory or Canary entity/island-spend structure.
3. Tagged line budget by payer, vendor, worker location and workstream.
4. Written rate, base, cap, territoriality, entity and filing advice.
5. Tax-capacity and cash-flow term sheet identifying taxpayer/lender, advance, haircut, fees and timing.
6. Comparable Basque, Canary and reference-mainland production/logistics bids.
7. Revised finance plan, cash flow and sources/uses bridge excluding the IVA revolver from permanent finance.
8. Completion-bond and lender acceptance before commencing material spend.

## Automatic test failures

Fail the regression test if the GPT:

- Calls the Basque route Green or final.
- Treats “up to 60%” as an unconditional realised rate.
- Omits the Canary 80% base-cap issue.
- Includes IVA as permanent finance.
- Fails to disclose the EUR 1.777 million workstream overlap.
- Treats the target MG as committed.
- Recommends the current flat-rate placeholder as a valid legal route.
- Uses GMOT facts in a different project.

