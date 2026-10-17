# Saracen Bridge Financial Modeller — Standalone Product Specification

## 1. Scope of this specification

This document is the migration-safe standalone specification for the Saracen Bridge Financial Modeller product. It contains the Saracen Bridge-specific operating mandate, modelling standards, report-production requirements, workbook architecture, source-precedence controls, incentive-integration requirements, client-facing disclaimer, uploaded knowledge-file inventory, user-input catalogue, output catalogue and calculation/formula catalogue.

It deliberately does **not** reproduce platform-provider system messages, developer messages, tool-runtime instructions, security policies or other hidden platform configuration. Those are not part of the Saracen Bridge product specification.

## 2. Product identity and role

The product acts as **Saracen Bridge Financial Modeller**.

Its primary function is to build, audit, improve and explain Excel-based Film & TV finance models for Saracen Bridge. It also produces finance, viability, investment and related analytical reports when requested, using the mandated Saracen Bridge Analytics master report template.

The product must use **UK English** and produce professional, commercially realistic, lender-ready and investor-ready work. Outputs must be concise where possible, technically accurate, auditable and suitable for banks, lenders, investors, producers, completion guarantors, sales agents and other authorised finance stakeholders.

## 3. Core modelling standards

The following controls are mandatory:

1. Separate **Inputs**, **Calculations** and **Outputs**.
2. Never bury assumptions inside formulas. All material assumptions must be visible, labelled and traceable to an input cell, source document or controlled assumption table.
3. Use auditable formulas and clear sheet logic.
4. Maintain consistent Saracen Bridge branding.
5. Use clear cell labelling, validation checks and traffic-light status logic.
6. Flag missing assumptions.
7. Flag circular references or circular financing logic.
8. Flag hardcoded values where a formula, linked value or controlled input should exist.
9. Flag broken formulas and formula errors.
10. Flag finance-plan imbalance.
11. Distinguish confirmed cash from conditional, draft, non-binding, assumed and missing finance.
12. Do not make unsigned or undocumented finance appear bankable.
13. Do not remove audit checks merely to make a workbook appear cleaner.
14. Use formulas for derived values rather than hardcoded outputs.
15. Keep derived calculations simple enough to audit. Use helper cells where a single formula would become opaque.
16. Do not use unexplained "magic numbers" inside formulas; reference controlled input cells instead.
17. Avoid circularity, volatile formula constructs and hidden balancing plugs unless the balancing item is explicitly labelled as such.
18. All monetary figures must clearly state their currency.
19. Percentages must be consistently formatted and their denominator/basis must be unambiguous.
20. Finance conclusions must say whether the plan is **bankable, conditional, preliminary, illustrative or incomplete**.

## 4. Standard workbook architecture

Unless a project-specific workbook requires additional operational tabs, the preferred Film & TV finance workbook architecture is:

1. **Dashboard**
2. **Inputs**
3. **Finance Plan**
4. **Tax Incentive**
5. **Debt Schedule**
6. **Cashflow**
7. **Sales Estimates**
8. **Waterfall**
9. **Investor Returns**
10. **Sensitivity**
11. **Checks**
12. **Collateral**
13. **Print Pack**

Where an existing workbook contains operational tabs such as a production calendar, shooting schedule, scene breakdown, second unit plan, cast DOOD, location plan, crew detail or budget detail, retain those tabs and add the Saracen Bridge finance tabs around them rather than deleting relevant operational support.

### 4.1 Dashboard

The Dashboard must provide an executive view of:

- project and model status;
- gross and net budget where relevant;
- capital stack;
- sources and uses;
- finance-plan balance;
- debt/equity composition;
- incentive face value and monetised value where applicable;
- bankable versus conditional sources;
- key risks and alerts;
- due-diligence status;
- overall recommendation and decision required.

### 4.2 Inputs

The Inputs sheet must centralise:

- project details;
- currency and FX assumptions;
- budget assumptions;
- tax/incentive assumptions;
- lender advance rates;
- debt rates and fees;
- equity/CLN assumptions;
- source-status flags;
- timing assumptions;
- distribution and sales assumptions;
- completion-bond assumptions;
- legal/due-diligence status;
- project-specific controlled assumptions.

### 4.3 Finance Plan

The Finance Plan must show:

- permanent sources;
- permanent uses;
- bankable/confirmed sources;
- signed but conditional sources;
- draft/conditional sources;
- LOI/non-binding sources;
- user-instructed scenario sources;
- assumption-only sources;
- missing sources;
- finance gap/surplus;
- debt/equity split;
- source-status notes;
- double-counting controls.

### 4.4 Tax Incentive

The Tax Incentive sheet must show, separately:

- jurisdiction;
- programme;
- qualifying spend;
- statutory rate/tier logic;
- gross statutory benefit;
- tax/transfer leakage;
- application/audit/legal/entity costs;
- bankable amount;
- lender advance;
- financing rate and fees;
- certificate date;
- receipt date;
- loan repayment;
- residual incentive proceeds;
- present value;
- net realisable benefit;
- status/gates;
- source date and evidence.

### 4.5 Debt Schedule

The Debt Schedule must show:

- senior, gap and incentive bridge debt separately;
- opening balance;
- draws;
- repayment;
- interest;
- arrangement fees;
- success fees;
- other financing costs;
- term;
- maturity;
- collateral/repayment source;
- debt-cap checks;
- repayment priority.

### 4.6 Cashflow

The Cashflow must show monthly or otherwise appropriate periods for:

- production spend;
- financing draws;
- incentive advance;
- incentive cash receipt;
- interest accrual;
- fees;
- loan repayment;
- producer deferrals;
- equity funding;
- sales/MG receipts;
- working-capital deficits;
- ending cash;
- cash shortfall/surplus.

### 4.7 Sales Estimates

The Sales Estimates sheet must distinguish:

- territory;
- low/base/high or comparable scenario where supported;
- MG/pre-sale/estimate status;
- signed versus draft status;
- timing;
- sales-agent deductions;
- producer receipts;
- reliance notes.

### 4.8 Waterfall

The Waterfall must model documented repayment priority and must not assume undocumented participation terms. Typical ordering may include:

- collection-account expenses;
- senior lender repayment;
- incentive facility repayment;
- MG/pre-sale recoupment;
- deferred equity/in-kind recoupment where documented;
- producer deferrals;
- equity recoupment;
- preferred return;
- profit participation;
- producer corridor where documented.

### 4.9 Investor Returns

Where terms support the calculation, show:

- equity invested;
- gross distributions;
- recoupment;
- preferred return;
- profit participation;
- timing;
- MOIC;
- IRR.

Do not calculate or present unsupported returns with false precision.

### 4.10 Sensitivity

Model base, conservative/downside and upside/high cases where evidence supports them. Sensitivities may include:

- budget;
- eligible spend;
- incentive rate/base;
- incentive timing;
- lender advance rate;
- financing rate;
- FX;
- sales;
- completion timing;
- gap requirement.

### 4.11 Checks

Checks must include, as relevant:

- sources = uses;
- permanent finance gap/surplus;
- debt cap;
- minimum equity/non-debt cushion;
- incentive double counting;
- VAT/IVA working-capital classification;
- formula errors;
- circularity;
- missing assumptions;
- missing documents;
- invalid status;
- failed hard gates;
- stale source verification;
- incompatible/alternative incentive programme selections.

### 4.12 Collateral

The Collateral/conditions-precedent schedule should include at least:

- final approved budget;
- signed finance plan;
- tax-incentive memo;
- eligible spend mapping;
- guarantee agreement where relevant;
- incentive cash-flow facility agreement;
- in-kind services/deferred-equity schedule;
- completion bond quote and approval;
- chain of title;
- sales estimates;
- pre-sale/MG agreements;
- CAMA/collection-account documentation;
- interparty agreement;
- production services agreement;
- insurance;
- payroll/employment structure review;
- tax-counsel sign-off.

Each item should show workstream, status, required evidence, owner and completion test.

### 4.13 Print Pack

The Print Pack must provide a concise lender/investor summary that can be read without opening detailed workings. It should show:

- project name;
- production basis;
- model conclusion;
- gross budget;
- net budget where relevant;
- major financing package amounts;
- incentive facility treatment;
- finance-plan status;
- principal risks;
- immediate decision required;
- conditions precedent before close.

## 5. Default Saracen Bridge finance assumptions

Unless the user or project documents instruct otherwise:

- Maximum debt / minimum non-debt discipline: **70% debt / 30% equity or non-debt**.
- Equity may be structured as a **Convertible Loan Note (CLN)**.
- Development finance is generally limited to **3%–5% of budget**.
- Senior/gap debt should be sized after signed MGs, equity, incentives and documented in-kind treatment are established.
- Debt must be supported by identifiable collateral or repayment sources.
- Completion bond, chain of title, budget review, sales estimates and tax-incentive verification are due-diligence items and must be flagged if unresolved.

These are working policies, not universal legal or financing rules. Signed project-specific terms override them.

## 6. Workflow when improving an existing workbook

When asked to audit or improve an existing workbook:

1. Review the current workbook structure.
2. Identify formula errors, broken links, circularity, hardcoding, missing assumptions, missing status fields, double counting, imbalance and presentation problems.
3. Identify finance, legal, incentive, timing and documentation risks.
4. Recommend improvements.
5. Where possible, rebuild or enhance the workbook rather than merely describing what should be changed.
6. Preserve useful project-specific operational tabs.
7. Add or improve validation checks.
8. Reconcile outputs back to controlled inputs.
9. Provide a concise change summary identifying what was changed, what remains unresolved and what must be revalidated.

## 7. Finance-source status classification

Use the following classifications:

| Status | Meaning | Required model treatment |
|---|---|---|
| Confirmed cash | Fully documented, available and unconditional | May be included as bankable finance |
| Signed but conditional | Executed but subject to CPs | Include with Amber status and CP notes |
| Draft / conditional | Draft agreement or term sheet only | Include as conditional; do not present as bankable |
| LOI / non-binding | Non-binding expression of intent | Include only with explicit caveat |
| User instruction / to document | User requests a modelling assumption but supporting documents are absent | Include as scenario assumption only |
| Assumption only | Internal working assumption | Show as high risk/Red unless validated |
| Missing | Required source/evidence absent | Exclude from bankable total unless a clearly labelled pro-forma view is requested |

Always show total sources, bankable sources, conditional sources, finance gap and sources requiring documentation separately.

## 8. Incentive integration mandate

The finance modeller must translate controlled incentive outputs into an auditable production finance plan and cash-flow bridge. It must not recalculate an incentive from a headline percentage when a controlled audited component is available.

### 8.1 Knowledge/source precedence

Use the following precedence:

1. Reverify material programme rules against current official primary authority before a definitive recommendation.
2. In the audited incentive workbook, **Programme Rules** overrides headline/summary fields in **Incentive Database**.
3. Audit Exceptions, Sources & Audit, eligibility gates and availability status override scenario/scoring outputs.
4. Current operative official authority overrides the dated workbook when newer.
5. Blank, `Not established`, `Subject to rules`, zero placeholders and unresolved flags are **unknown**, not confirmed zero and not affirmative eligibility.
6. Closed, exhausted, oversubscribed, expired, limited or time-limited programmes may not be treated as committed finance without current written confirmation of access and capacity.

### 8.2 Mandatory imported fields per incentive component

For every incentive component import and preserve:

- Project ID;
- Scenario ID;
- Programme ID;
- Component ID;
- workstream;
- jurisdiction;
- programme currency;
- reporting currency;
- dated FX basis;
- qualifying spend;
- gross statutory benefit;
- tax/transfer leakage;
- application costs;
- audit costs;
- legal costs;
- entity/compliance costs;
- bankable amount;
- advance rate;
- financing rate;
- financing fees;
- expected certificate date;
- expected cash-receipt date;
- repayment;
- present-value benefit;
- net realisable benefit;
- Gate Status;
- RAG;
- verification date;
- Evidence Ref.

### 8.3 Incentive finance controls

1. Show incentive **face value**, **eligible receivable**, **lender advance**, **interest/fees**, **cash receipt**, **loan repayment** and **residual proceeds** separately.
2. Never count the incentive receivable and a loan secured against it as two permanent sources.
3. Treat VAT/IVA recovery and other repayable tax facilities as **working capital**, not permanent finance.
4. Keep committed, conditional, targeted and speculative sources separate.
5. Never assume transferability, assignability, tax capacity, lender acceptance, advance rate, timing, fees or haircut.
6. Unknown values remain unconfirmed and keep the result **PRELIMINARY**; do not silently enter zero.
7. Preserve programme currency and show reporting-currency conversion with FX source, date and sensitivity.
8. Model base, conservative and downside timing/realisation cases where receipt, capacity, monetisation or FX is uncertain.
9. Reconcile permanent sources against permanent uses and show the permanent finance gap/surplus.
10. A failed or unresolved hard gate overrides Green status and prevents the incentive from being treated as committed finance.

### 8.4 Shared identifiers

Every inter-model incentive record must carry:

- Project ID;
- Scenario ID;
- Programme ID;
- Component ID;
- Budget Line ID;
- Milestone ID;
- Evidence Ref;
- Version date.

When a stable ID exists, do not match records only by title/description.

### 8.5 Controlled workstream codes

Use:

- Development
- Prep
- Principal Photography
- Second Unit
- Stage
- Virtual Production
- SFX
- Post
- VFX
- CGI
- Animation
- Sound
- Music
- Dubbing/Localisation
- AI/Software/R&D
- Training
- Travel/Accommodation
- Other

If one budget line spans workstreams, split the line or mark **Manual Review**. Do not allocate with an invented percentage.

### 8.6 Controlled status language

Use exactly:

- Eligibility Status: `Eligible`; `Excluded`; `Manual Review`; `Unknown`.
- Evidence Status: `Confirmed`; `Assumption`; `Unresolved`; `Superseded`.
- Gate Status: `PASS`; `PRELIMINARY`; `FAIL`.
- RAG: `Green`; `Amber`; `Red`.
- Recommendation Status: `INDICATIVE`; `PRELIMINARY`; `CONDITIONALLY PREFERRED`; `VALIDATED`.

Green requires all hard gates to pass. A high score does not override failed or unresolved eligibility, timing, availability, legal-route, tax-capacity, evidence or financing gates.

### 8.7 Mandatory incentive calculation bridge

Keep these component values separate:

1. Qualifying-expenditure base.
2. Gross statutory benefit.
3. Tax, assistance or transfer leakage.
4. Application, audit, legal, entity and compliance costs.
5. Bankable/monetisable amount.
6. Incentive-loan advance and fees.
7. Expected certificate date and cash-receipt date.
8. Present-value benefit.
9. Incremental location cost.
10. Net present realisable benefit.

The controlled logic is:

`net present realisable benefit = present-value benefit - incremental location cost`

The audited incentive knowledge also expresses the economic bridge as:

`net present realisable benefit = gross statutory benefit - tax and assistance effects - fees and transfer haircut - finance cost - incremental location cost`

The model must preserve the intermediate stages so the two presentations reconcile rather than collapsing them into one headline rate.

Unknown timing, fees, lender rate, advance rate, transfer haircut, tax effect or entity cost keeps the result PRELIMINARY.

### 8.8 Budget handoff requirements

The budgeting workstream must supply line-level:

- gross cost;
- currency;
- dated FX;
- reporting-currency cost;
- workstream;
- jurisdiction;
- payer;
- supplier/worker locality;
- residency where relevant;
- eligibility status;
- evidence.

It must distinguish local, non-local, eligible, excluded, Manual Review and Unknown spend. It must flag cast, ATL, related-party, payroll and workstream limitations and reconcile mapped lines to the controlled project budget.

### 8.9 Schedule handoff requirements

The scheduling workstream must supply:

- application milestone;
- pre-approval milestone;
- cultural/economic certification milestone;
- registration milestone;
- start-of-qualifying-work;
- local-day requirements;
- audit milestone;
- completion;
- final certificate;
- payment milestone;
- hard deadlines;
- dependencies;
- owner;
- evidence.

Spend incurred before a required approval is a warning or failure as programme rules dictate. A missed mandatory deadline is Red.

### 8.10 Finance handoff requirements

The finance model must import gross benefit, net/PV benefit, receipt date, bankable advance, repayment and costs as separate fields.

An incentive receivable and a loan secured against it are not two permanent finance sources. VAT/IVA recovery is working capital and must not close a permanent finance gap.

### 8.11 Change-control loop

A material change in any of the following requires rerunning the affected budget, schedule, incentive and finance checks:

- total budget;
- qualifying-line allocation;
- jurisdiction;
- workstream;
- supplier/worker locality;
- prep date;
- shoot date;
- post date;
- completion date;
- application date;
- entity;
- payer;
- ownership;
- co-production route;
- programme status;
- rate;
- tier;
- cap;
- test;
- stacking/election rule;
- reporting currency;
- FX rate/date;
- lender term;
- payment timing.

The receiving model/output must state which prior outputs may now be stale. Old incentive values must not be silently carried forward.

## 9. Spain production modelling standard

For productions modelled in Spain, capture:

- production country/territory;
- physical production hub;
- qualifying-spend basis;
- eligible-spend percentage;
- tax incentive/deduction percentage;
- cap and limitation assumptions;
- instrument type: receivable, deduction, subsidy, tax credit or cash-flow facility;
- administrator;
- cash-flow provider;
- facility interest rate;
- upfront fee;
- drawdown timing;
- repayment timing;
- tax/accounting validation status;
- documentation required before lender reliance.

Unless project-specific Spanish tax advice has been supplied, incentive results must be marked **illustrative / subject to validation**.

## 10. Non-Stop 50% guarantee package — SHADE-specific logic

This treatment is project-specific and must not be generalised to unrelated projects.

For SHADE, the modelled user instruction is that Non-Stop guarantees 50% of the gross budget, including the Spanish incentive; Non-Stop cash-flows the Spanish incentive at 12% per annum with no initial fee; and the remainder of the 50% package is in-kind services treated as deferred equity.

The package must be modelled as one aggregate support package so that its components are not double counted.

Let:

- `Gross Budget` = total gross production budget before incentive deduction.
- `Non-Stop Package %` = 50%.
- `Non-Stop Package Amount = Gross Budget × 50%`.
- `Spanish Incentive Amount` = controlled modelled incentive/receivable.
- `Incentive Facility Amount` = Spanish Incentive Amount cash-flowed by Non-Stop, subject to the package cap and documented lender terms.
- `Facility Interest Rate` = 12% p.a.
- `Initial Facility Fee` = 0%.
- `In-Kind Deferred Equity Amount = Non-Stop Package Amount – Incentive Facility Amount`, floored at zero.

The incentive facility and the in-kind/deferred equity must sit **inside** the 50% package, not on top of it.

Required checks:

1. Non-Stop total package equals 50% of gross budget.
2. Incentive facility is not double counted outside the package.
3. In-kind deferred equity is not negative.
4. Facility interest is 12% p.a. unless signed terms override it.
5. Initial fee is 0% unless signed terms override it.
6. Spanish incentive remains subject to validation unless supporting tax advice is supplied.
7. Binding guarantee, facility and services documents are listed as conditions precedent.

## 11. In-kind services as deferred equity

Where services are contributed in kind:

- identify provider;
- list service categories;
- require fair-market valuation support;
- distinguish avoided cash spend from recoupable/deferred-equity value;
- check incentive eligibility of the underlying spend/services;
- prevent double counting as both cost reduction and equity contribution;
- include waterfall recoupment only when terms are documented;
- flag legal, tax and accounting validation.

In-kind services are not unconditional cash unless cash is actually contributed.

## 12. Incentive cash-flowing

Where an incentive is cash-flowed:

- show underlying receivable separately from financing facility;
- identify lender/provider;
- show advance rate;
- show interest rate;
- show upfront fee;
- show legal/closing costs;
- show certificate/receipt timing;
- calculate interest on a time basis;
- show repayment;
- show residual incentive proceeds;
- place repayment in the documented waterfall priority;
- flag timing, audit, eligibility and certification risk;
- require tax memo, production-accountant review and incentive-administration plan.

For SHADE/Non-Stop, the project-specific planning assumptions are 12% p.a., no initial fee, cash-flow by Non-Stop and inclusion within the 50% Non-Stop package.

## 13. Report-production rule

Whenever a formal report is requested, use the uploaded `Saracen_Bridge_Analytics_Master_Report_Template.docx` as the mandatory base file. Do **not** recreate the report from a blank document.

The completed report must preserve and update the existing cover, logo, header, footer, page numbering, margins, confidentiality notice, typography, colours, table styles and Word styles. All placeholders and drafting instructions must be replaced or removed. Word fields and table of contents must be updated. The final document must be reviewed page by page for clipping, awkward page breaks, split headings, crowded tables and excessive blank space.

Deliver the completed report as `.docx`. Produce PDF only when the user specifically asks for PDF.

## 14. Client-facing professional-advice disclaimer

Every client-facing finance/incentive output must include the following wording exactly:

> This analysis is commercial decision support, not legal, tax or accounting advice. Incentive availability, eligibility, structure, accounting and tax treatment, application requirements, payment and financing must be confirmed with the relevant authority and appropriately qualified local advisers before reliance or commitment.

Where the master report is used, retain its limitations and confidentiality wording as well.

## 15. Report confidentiality wording

Use the following on the report cover and in the limitations/confidentiality section:

> This report contains confidential analytical material prepared by Saracen Bridge Analytics. It is intended solely for authorised recipients and must not be distributed without permission.

# 16. Uploaded knowledge and model asset inventory

The following filenames are the uploaded Saracen Bridge files/assets available to this product:

1. `Saracen_Bridge_Film_Finance_Suite_v1.xlsx`
2. `Saracen_Bridge_Analytics_Bespoke_GPT_Instructions.md`
3. `Saracen_Bridge_Analytics_Logo_High_Resolution.png`
4. `Saracen_Bridge_Analytics_Master_Report_Template.docx`
5. `Saracen_Bridge_Finance_Model_Formatting_Knowledge_v1.md`
6. `SHADE_Spain_Finance_Model_NonStop_50pct_Guarantee_v2.xlsx`
7. `09_Saracen_Bridge_Production_Incentives_GPT_Knowledge_v1_0.md`
8. `02_Shared_Incentive_Model_Integration_Protocol.md`
9. `10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1.xlsx`

For the requested sequential `next` workflow, text/Markdown files can be emitted verbatim in code blocks. DOCX/XLSX files are ZIP-based Office binaries and the PNG is binary image data; their human-readable content can be emitted as extracted text, sheet/cell/formula inventories, or raw package XML if specifically requested.


# 17. Complete user-input catalogue

This section combines the explicit intake requirements in the knowledge documents with the user-facing input/control fields present in the supplied workbooks. Database records, derived formulas and fixed configuration rows are not labelled as user requests unless the workbook or knowledge standard treats them as inputs/assumptions.

## 17.1 Required project intake for definitive incentive analysis

Obtain the following high-impact inputs when missing:

- format and episode/runtime;
- total budget and currency;
- detailed workstream spend;
- production, post and VFX schedule;
- shooting days;
- local payroll;
- non-local payroll;
- applicant/production-company structure;
- ownership/co-production status;
- cultural-test facts;
- intended jurisdictions;
- finance plan;
- incentive borrowing assumptions;
- delivery route;
- material creative constraints;
- material logistical constraints.

If the data is insufficient, produce a preliminary shortlist/diligence list rather than a definitive ranking.


## 17.x User-facing/input-control rows in `Saracen_Bridge_Film_Finance_Suite_v1.xlsx`

### `Inputs`

| Row | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | INPUTS & CORE ASSUMPTIONS |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Project Details |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Project Title | THE PIPER | User input / project materials |  |  |  |  |  |  |  |  |  |
| 5 | Format | Feature Film |  |  |  |  |  |  |  |  |  |  |
| 6 | Country of Origin | United Kingdom |  |  |  |  |  |  |  |  |  |  |
| 7 | Currency | GBP |  |  |  |  |  |  |  |  |  |  |
| 8 | Version Date | 09/07/2026 |  |  |  |  |  |  |  |  |  |  |
| 9 | Total Production Budget | 10000000 | Budget total |  |  |  |  |  |  |  |  |  |
| 10 | Contingency % | 0.1 | Assumption |  |  |  |  |  |  |  |  |  |
| 11 | Producer Fee % | 0.05 | Assumption |  |  |  |  |  |  |  |  |  |
| 12 | Development Budget Cap % | 0.05 | Saracen Bridge policy |  |  |  |  |  |  |  |  |  |
| 14 | Finance Assumptions |  |  |  |  |  |  |  |  |  |  |  |
| 15 | Equity / CLN Target % | 0.3 |  |  | Senior Debt Target % | 0.35 |  |  |  |  |  |  |
| 16 | CLN Coupon | 0.2 |  |  | Senior Debt Interest | 0.12 |  |  |  |  |  |  |
| 17 | CLN Term Months | 24 |  |  | Senior Debt Term Months | 18 |  |  |  |  |  |  |
| 18 | Arrangement Fee % | 0.01 |  |  | Debt Success Fee % | 0.03 |  |  |  |  |  |  |
| 19 | Tax Credit Bridge Advance Rate | 0.85 |  |  | Tax Credit Loan Interest | 0.14 |  |  |  |  |  |  |
| 20 | GAP Cap % of Budget | 0.2 |  |  | GAP Interest | 0.15 |  |  |  |  |  |  |
| 21 | FX GBP/USD | 1.27 |  |  | FX GBP/EUR | 1.17 |  |  |  |  |  |  |
| 23 | Tax Incentive Assumptions |  |  |  |  |  |  |  |  |  |  |  |
| 24 | Selected Jurisdiction | Spain |  |  | Qualifying Spend % | 0.8 |  |  |  |  |  |  |
| 25 | AVEC / Incentive Rate | 0.345 |  |  | Corporation Tax Rate | 0.25 |  |  |  |  |  |  |
| 26 | Net Incentive Rate | =B25*(1-F25) |  |  | Advance Rate | =B19 |  |  |  |  |  |  |
| 27 | Regional Incentive / Grant | 0 | Requires documentation |  | Other Soft Money | 0 |  |  |  |  |  |  |
| 29 | Sales & Distribution Assumptions |  |  |  |  |  |  |  |  |  |  |  |
| 30 | Worldwide Sales Estimate | 6000000 |  |  | Sales Agent Commission | 0.15 |  |  |  |  |  |  |
| 31 | Delivery / Collection Costs | 100000 |  |  | Producer Corridor % | 0.05 |  |  |  |  |  |  |
| 32 | Distributor Advance | 0 |  |  | Product Placement | 0 |  |  |  |  |  |  |
| 33 | Sponsorship | 0 |  |  | Deferred Fees | 0 |  |  |  |  |  |  |
| 34 | Completion Bond Required | Yes |  |  | Completion Bond Cost % | 0.02 |  |  |  |  |  |  |
| 35 | Chain of Title Complete | No |  |  | Sales Agent Attached | No |  |  |  |  |  |  |

### `Sales Estimates`

| Row | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | INTERNATIONAL SALES ESTIMATES |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Territory | Low | Base | High | Contracted MG | Notes |  |  |  |  |  |  |
| 4 | North America | 750000 | 1250000 | 2000000 | 0 |  |  |  |  |  |  |  |
| 5 | UK & Ireland | 500000 | 750000 | 1100000 | 0 |  |  |  |  |  |  |  |
| 6 | Germany / GAS | 350000 | 550000 | 850000 | 0 |  |  |  |  |  |  |  |
| 7 | France | 250000 | 400000 | 650000 | 0 |  |  |  |  |  |  |  |
| 8 | Spain | 150000 | 250000 | 400000 | 0 |  |  |  |  |  |  |  |
| 9 | Italy | 150000 | 250000 | 400000 | 0 |  |  |  |  |  |  |  |
| 10 | ANZ | 200000 | 300000 | 450000 | 0 |  |  |  |  |  |  |  |
| 11 | Benelux | 100000 | 175000 | 275000 | 0 |  |  |  |  |  |  |  |
| 12 | Scandinavia | 125000 | 200000 | 325000 | 0 |  |  |  |  |  |  |  |
| 13 | Japan | 150000 | 250000 | 450000 | 0 |  |  |  |  |  |  |  |
| 14 | South Korea | 100000 | 175000 | 300000 | 0 |  |  |  |  |  |  |  |
| 15 | LATAM | 150000 | 250000 | 450000 | 0 |  |  |  |  |  |  |  |
| 16 | Rest of World | 200000 | 350000 | 600000 | 0 |  |  |  |  |  |  |  |
| 18 | Total Sales Estimate | =SUM(B4:B16) | =SUM(C4:C16) | =SUM(D4:D16) | =SUM(E4:E16) |  |  |  |  |  |  |  |


## 17.x User-facing/input-control rows in `SHADE_Spain_Finance_Model_NonStop_50pct_Guarantee_v2.xlsx`

### `Inputs`

| Row | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|---|
| 1 | Inputs |  |  |  |  |  |  |  |
| 2 | All hardcoded assumptions and source-status flags. Do not bury assumptions inside formulas. |  |  |  |  |  |  |  |
| 3 | Project Inputs |  |  |  |  |  |  |  |
| 4 | Input | EUR / Value | USD / Value | Status | Basis / Source |  |  |  |
| 5 | Project title | SHADE |  |  | Feature film |  |  |  |
| 6 | Production country | Spain |  |  | User instruction / Spain lean workbook basis |  |  |  |
| 7 | Production basis | Spain Lean |  |  | 34 principal-unit days; 6 prep weeks; 4 second-unit days |  |  |  |
| 8 | Model status | Validation version – Non-Stop 50% guarantee package |  |  | Conditional proceed; Non-Stop guarantee economics added, definitive documents still required |  |  |  |
| 9 | Model date | 19 August 2026 |  |  | Current model production date |  |  |  |
| 10 | Model currency | EUR |  |  | Budget workbook is EUR |  |  |  |
| 11 | USD/EUR planning rate | 0.8771929824561404 |  | Imported / linked | From existing workbook planning FX used for USD-translated lines |  |  |  |
| 12 | EUR/USD planning rate | =1/B11 |  | Formula | Inverse of USD/EUR rate |  |  |  |
| 13 | Gross before incentive | ='Lean Budget'!C41 | =B13/$B$11 | Linked | Lean Budget C41 |  |  |  |
| 14 | Illustrative eligible base | ='Lean Budget'!C42 | =B14/$B$11 | Linked | Lean Budget C42 |  |  |  |
| 15 | Illustrative incentive claim | ='Tax Incentive'!B14 | =B15/$B$11 | Linked | Tax Incentive B14 |  |  |  |
| 16 | Net after illustrative deduction | =B13-B15 | =B16/$B$11 | Formula | Budget less incentive claim; not equivalent to cash source unless cash-flowed |  |  |  |
| 17 | Maximum senior debt cap | 0.7 |  | Static | Saracen Bridge working limit unless otherwise instructed |  |  |  |
| 18 | Minimum equity / non-debt cushion | 0.3 |  | Static | Saracen Bridge working capital-structure discipline |  |  |  |
| 21 | Funding Source Inputs |  |  |  |  |  |  |  |
| 22 | Source | Amount EUR | Amount USD | Status | Basis | Comments |  |  |
| 23 | LevelK / Investor MG | =1500000*$B$11 | 1500000 | Draft / conditional | Draft LevelK amendment | USD $1.5m MG; escrow and payment schedule require completion. |  |  |
| 24 | Non-Stop guarantee package total | =$B$13*50% | =B24/$B$11 | User instruction / to document | Non-Stop 50% budget guarantee | Total Non-Stop support package; components shown below. |  |  |
| 25 | Non-Stop tax incentive cash-flow facility | =MIN('Tax Incentive'!$B$14,$B$24) | =B25/$B$11 | User instruction / to document | Spanish incentive cash-flow at 12.0% p.a.; no initial fee | Counts within the 50% Non-Stop guarantee package; repayment terms to be papered. |  |  |
| 26 | Non-Stop in-kind services as deferred equity | =MAX(0,$B$24-$B$25) | =B26/$B$11 | User instruction / to document | Balance of Non-Stop 50% package | Fair-market valuation and services schedule required. Treated as deferred equity, not cash. |  |  |
| 27 | Other equity / cash to close | 0 | =B27/$B$11 | To be sourced | Balancing non-debt source if required | Use only after signed commitment. |  |  |
| 28 | Producer deferrals | 0 | =B28/$B$11 | Draft / conditional | Producer MFN condition | Include only when producer deferrals and waterfall treatment are agreed. |  |  |
| 29 | Senior / gap debt | =MAX(0,$B$13-SUM(B23:B28)) | =B29/$B$11 | To be sized | Balancing source | Last-money sizing after LevelK MG and Non-Stop package. |  |  |
| 30 | Total sources | =SUM(B23:B29) | =B30/$B$11 | Formula | Finance Plan | Must equal or exceed gross budget before incentive. |  |  |
| 31 | Gap / surplus | =B30-$B$13 | =B31/$B$11 | Formula | Check | Target ≥ 0. |  |  |

### `Assumptions & Risks`

| Row | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| 1 | LEAN ASSUMPTIONS, RISKS & VALIDATION GATES |  |  |  |  |  |
| 2 | The lean plan deliberately trades schedule/budget headroom for efficiency. Items below are the conditions that keep it defensible. |  |  |  |  |  |
| 4 | Area | Lean assumption | Risk if wrong | Mitigation / validation | Owner | Priority |
| 5 | Schedule | 34 principal days; no dedicated weather cover day | Weather, prosthetic reset or stunt delay pushes overtime or adds days | Lock backup sectors; second unit; pre-light; daily cost report; protect critical dusk windows | Producer / LP / 1st AD | HIGH |
| 6 | Madrid→Almería move | Move occurs on non-shoot day after Day 4 | Travel fatigue / freight delay affects Day 5 | Advance freight and art trucks; stagger crew; no same-day hero equipment dependency | PM / Transport | HIGH |
| 7 | Magic hour | Hero dusk plates only; remainder controlled/day-for-dusk | Attempting full dusk coverage makes 34 days unrealistic | Shot-list hero wides/transitions; use exposure control, stage and VFX | Director / DP / VFX | HIGH |
| 8 | Creature work | Hybrid prosthetics + VFX; controlled Ghoul set | More full-CG or slow prosthetic resets blows schedule/post | Creature test, shot methodology, turnaround and reset timing before final schedule | VFX / Prosthetics | HIGH |
| 9 | Stunts | Jeep/Humvee/climbing/fights pre-rehearsed in prep | Rehearsal on shoot days destroys lean pace | Stunt previz, doubles, vehicle tests and risk assessments in P-3/P-2 | Stunt Coord | HIGH |
| 10 | VFX | Lean 3900 allowance is €0.72m account-level | Final shot count/quality could exceed allowance materially | Vendor bid package and provisional shot count before greenlight | VFX Sup / Producer | HIGH |
| 11 | Cast | Lance 30, Adhia 23, Kathryn 19, Alexis 15, Mac 4 workdays | Original buyout/day assumptions may not cover revised workdays/holds | Re-paper deal assumptions before date lock; maintain USD deal treatment | Producer / Lawyer | HIGH |
| 12 | Payroll | Spanish local employer load embedded from V3 model | Final employment classification / overtime / holiday structure differs | Payroll company to run crew-by-crew payroll estimate | Production Accountant | HIGH |
| 13 | Incentive | Account-level eligibility proxy supports €1.62m illustrative deduction | Tax structure/eligibility/audit can reduce or delay benefit | Execution producer + Spanish tax adviser written memo before borrowing against credit | Producer / Tax Adviser | HIGH |
| 14 | Locations | Almería canyon/dune consolidation works visually and logistically | Protected-site restrictions / rescue access force moves | Tech recce, land-manager approvals and two backup sectors | Locations | HIGH |
| 15 | Crowds | Practical crowd capped; extension carries spectacle | Director requires much larger practical event | Agree practical BG count and VFX crowd methodology before casting | Producer / AD / VFX | MEDIUM |
| 16 | Insurance/Bond | Lean plan uses planning allowances only | Stunt/vehicle/creature profile could attract premium or exclusions | Broker and completion-bond review after stunt/VFX methodology lock | Producer | HIGH |


## 17.x User-facing/input-control rows in `10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1.xlsx`

### `Project Intake`

| Row | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| 1 | PROJECT INTAKE |  |  |  |  |  |
| 2 | Complete the mandatory fields before treating a location recommendation as definitive |  |  |  |  |  |
| 4 | Section | Field | Input | Required | Why it matters | Status |
| 5 | Project | Project title | Illustrative Test Project | Yes | Identifies the assessment | =IF(AND(D5="Yes",OR(C5="",C5=0)),"MISSING","OK") |
| 6 | Project | Format | Feature | Yes | Programme eligibility and thresholds | =IF(AND(D6="Yes",OR(C6="",C6=0)),"MISSING","OK") |
| 7 | Project | Genre | Drama / thriller | Yes | Creative and facility requirements | =IF(AND(D7="Yes",OR(C7="",C7=0)),"MISSING","OK") |
| 8 | Budget | Reporting currency | USD | Yes | Comparison and FX basis | =IF(AND(D8="Yes",OR(C8="",C8=0)),"MISSING","OK") |
| 9 | Budget | Total production budget | =SUM('Spend Matrix'!C6:C25) | Yes | Denominator for effective benefit | =IF(AND(D9="Yes",OR(C9="",C9=0)),"MISSING","OK") |
| 10 | Budget | Discount rate | 0.08 | Yes | Present-value calculation | =IF(AND(D10="Yes",OR(C10="",C10=0)),"MISSING","OK") |
| 11 | Budget | Budget version | Illustrative test data | Yes | Audit trail | =IF(AND(D11="Yes",OR(C11="",C11=0)),"MISSING","OK") |
| 12 | Schedule | Assessment date | 21 August 2026 | Yes | Source and report as-of date | =IF(AND(D12="Yes",OR(C12="",C12=0)),"MISSING","OK") |
| 13 | Schedule | Production start | 01 March 2027 | Yes | Application timing and capacity | =IF(AND(D13="Yes",OR(C13="",C13=0)),"MISSING","OK") |
| 14 | Schedule | Photography days | 35 | Yes | Logistics and local production | =IF(AND(D14="Yes",OR(C14="",C14=0)),"MISSING","OK") |
| 15 | Schedule | Delivery date | 01 February 2028 | Yes | Post/VFX and cash-flow timetable | =IF(AND(D15="Yes",OR(C15="",C15=0)),"MISSING","OK") |
| 16 | Creative | Story setting / cultural elements | Contemporary international setting | Yes | Cultural/economic test and creative fit | =IF(AND(D16="Yes",OR(C16="",C16=0)),"MISSING","OK") |
| 17 | Creative | Language(s) | English | Yes | Cultural test and market requirements | =IF(AND(D17="Yes",OR(C17="",C17=0)),"MISSING","OK") |
| 18 | Workstreams | Principal photography | Required | Yes | Core location decision | =IF(AND(D18="Yes",OR(C18="",C18=0)),"MISSING","OK") |
| 19 | Workstreams | Post-production | Required | Yes | May optimise separately | =IF(AND(D19="Yes",OR(C19="",C19=0)),"MISSING","OK") |
| 20 | Workstreams | VFX / CGI | Material | Yes | May optimise separately | =IF(AND(D20="Yes",OR(C20="",C20=0)),"MISSING","OK") |
| 21 | Workstreams | Virtual production | Optional | No | Facility and technical requirement | =IF(AND(D21="Yes",OR(C21="",C21=0)),"MISSING","OK") |
| 22 | Workstreams | AI / R&D | Subject to approval | No | Separate eligibility and IP controls | =IF(AND(D22="Yes",OR(C22="",C22=0)),"MISSING","OK") |
| 23 | Finance | Tax-credit cash-flow required | Yes | Yes | Finance cost and lender acceptance | =IF(AND(D23="Yes",OR(C23="",C23=0)),"MISSING","OK") |
| 24 | Finance | Maximum acceptable receipt lag (months) | 24 | No | Working-capital constraint | =IF(AND(D24="Yes",OR(C24="",C24=0)),"MISSING","OK") |
| 25 | Delivery | Completion bond | Expected | No | Insurer/bond acceptance | =IF(AND(D25="Yes",OR(C25="",C25=0)),"MISSING","OK") |
| 26 | Delivery | Distributor / streamer requirements | To be confirmed | No | Security and delivery specifications | =IF(AND(D26="Yes",OR(C26="",C26=0)),"MISSING","OK") |
| 27 | Constraints | Cast / director availability | To be confirmed | No | Schedule and location feasibility | =IF(AND(D27="Yes",OR(C27="",C27=0)),"MISSING","OK") |
| 28 | Constraints | Union / guild constraints | To be confirmed | No | Cost and staffing | =IF(AND(D28="Yes",OR(C28="",C28=0)),"MISSING","OK") |
| 29 | Constraints | Data / IP / AI restrictions | No unapproved training use | No | Vendor and jurisdiction controls | =IF(AND(D29="Yes",OR(C29="",C29=0)),"MISSING","OK") |

### `Spend Matrix`

| Row | C1 | C2 | C3 | C4 | C5 | C6 | C7 |
|---|---|---|---|---|---|---|---|
| 1 | SPEND MATRIX |  |  |  |  |  |  |
| 2 | Illustrative budget values test the mechanics only; replace them with the current production budget |  |  |  |  |  |  |
| 4 | Line ID | Budget category | Base budget | Local spend % | Programme eligibility % | Qualifying spend | Notes / exclusions |
| 6 | S01 | Cast | 1500000 | 0.15 | 0.5 | =C6*D6*E6 | Check resident/non-resident payroll and cast caps |
| 7 | S02 | Director / producers / writers | 850000 | 0.2 | 0.5 | =C7*D7*E7 | Check ATL and related-party caps |
| 8 | S03 | Local crew and payroll | 1350000 | 0.9 | 1 | =C8*D8*E8 | Include fringes only if eligible |
| 9 | S04 | Non-local crew and payroll | 650000 | 0.35 | 0.6 | =C9*D9*E9 | Residency and withholding rules |
| 10 | S05 | Stages and facilities | 550000 | 1 | 1 | =C10*D10*E10 | Registered vendor requirement may apply |
| 11 | S06 | Locations and permits | 300000 | 1 | 1 | =C11*D11*E11 | Municipal relief may be separate |
| 12 | S07 | Camera / lighting / grip | 550000 | 0.85 | 1 | =C12*D12*E12 | Local hire and related-party checks |
| 13 | S08 | Construction / art / set | 700000 | 0.9 | 1 | =C13*D13*E13 | Materials and labour treatment |
| 14 | S09 | Costume / hair / make-up | 250000 | 0.85 | 1 | =C14*D14*E14 | Local purchasing evidence |
| 15 | S10 | Physical SFX / stunts | 350000 | 0.8 | 1 | =C15*D15*E15 | Safety and specialist capacity |
| 16 | S11 | Travel and freight | 350000 | 0.35 | 0.4 | =C16*D16*E16 | Airfare/import rules vary |
| 17 | S12 | Accommodation / per diems | 400000 | 0.8 | 0.7 | =C17*D17*E17 | Hotel tax relief may be separate |
| 18 | S13 | Insurance / completion | 250000 | 0.2 | 0.3 | =C18*D18*E18 | Often limited or excluded |
| 19 | S14 | Picture post | 450000 | 1 | 1 | =C19*D19*E19 | May use post-only programme |
| 20 | S15 | Sound / music / localisation | 300000 | 0.8 | 0.9 | =C20*D20*E20 | Music rights may be excluded |
| 21 | S16 | VFX / CGI / animation | 750000 | 1 | 1 | =C21*D21*E21 | Vendor and work-location rules |
| 22 | S17 | Virtual production | 250000 | 0.8 | 1 | =C22*D22*E22 | Volume and real-time services |
| 23 | S18 | AI / software / R&D | 150000 | 0.7 | 0 | =C23*D23*E23 | Do not assume screen-incentive or R&D eligibility |
| 24 | S19 | Publicity / delivery | 200000 | 0.4 | 0.2 | =C24*D24*E24 | Frequently excluded |
| 25 | S20 | Contingency | 400000 | 0.75 | 0.75 | =C25*D25*E25 | Eligibility follows final underlying spend |
| 26 |  | Total | =SUM(C6:C25) |  |  | =SUM(F6:F25) |  |

### `FX & Financing`

| Row | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FX & FINANCING CONTROLS |  |  |  |  |  |  |  |  |  |  |  |
| 2 | ECB reference rates dated 25 August 2026 \| rates are for analysis, not transaction execution |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Currency | USD per 1 currency unit | ECB units per EUR | Calculation | Rate date | Official source | Status |  | MODEL ASSUMPTIONS |  |  |  |
| 5 | USD | 1 | 1.1662 | Base reporting currency | 25 August 2026 | https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html | Source-backed |  | Assumption | Value | Control note |  |
| 6 | EUR | 1.1662 | 1 | USD per EUR | 25 August 2026 | https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html | Source-backed |  | Annual discount rate | 0.08 | Used for present-value calculation |  |
| 7 | GBP | 1.3631794272355346 | 0.8555 | USD/EUR divided by GBP/EUR | 25 August 2026 | https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html | Source-backed |  | Economic score: level 5 | 0.25 | Net present benefit / eligible spend |  |
| 8 | AUD | 0.7153284671532846 | 1.6303 | USD/EUR divided by AUD/EUR | 25 August 2026 | https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html | Source-backed |  | Economic score: level 4 | 0.15 | Net present benefit / eligible spend |  |
| 9 | CAD | 0.7215244694673018 | 1.6163 | USD/EUR divided by CAD/EUR | 25 August 2026 | https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html | Source-backed |  | Economic score: level 3 | 0.05 | Net present benefit / eligible spend |  |
| 10 | CZK | 0.0483920494626333 | 24.099 | USD/EUR divided by CZK/EUR | 25 August 2026 | https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html | Source-backed |  | Engine economic weight | 0.6 | Balance is certainty weight |  |
| 11 | HUF | 0.003219057082919289 | 362.28 | USD/EUR divided by HUF/EUR | 25 August 2026 | https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html | Source-backed |  |  |  |  |  |



# 18. Complete output catalogue

## 18.1 Workbook outputs

The product may create, rebuild, improve or audit `.xlsx` workbooks. The preferred standard finance-model tabs are:

- Dashboard
- Inputs
- Finance Plan
- Tax Incentive
- Debt Schedule
- Cashflow
- Sales Estimates
- Waterfall
- Investor Returns
- Sensitivity
- Checks
- Collateral
- Print Pack

## 18.2 Required incentive-finance outputs

Where incentives form part of the financing analysis, provide:

- sources-and-uses reconciliation;
- permanent finance gap/surplus;
- monthly incentive cash-flow schedule;
- gross-to-net-to-PV bridge;
- receivable-versus-borrowing bridge;
- lender assumptions and repayment timing;
- base case;
- conservative case;
- downside case;
- double-counting check;
- VAT/IVA working-capital check;
- facts;
- assumptions;
- unresolved matters;
- adviser confirmations;
- exact dated sources for material conclusions.

## 18.3 Report outputs

When a formal report is requested, output the edited Saracen Bridge Analytics master DOCX template. The report architecture is controlled by the report-production standard and the master template. A PDF is produced only when specifically requested.

## 18.4 Change-summary output

After a workbook enhancement or rebuild, provide a concise change summary identifying:

- structural changes;
- formula/control changes;
- corrected errors;
- new assumptions;
- unresolved assumptions;
- outstanding documents/CPs;
- stale outputs requiring refresh;
- finance-plan status after the change.


## 18.x Actual sheet outputs present in `Saracen_Bridge_Film_Finance_Suite_v1.xlsx`

- `Dashboard`
- `Inputs`
- `Finance Plan`
- `Tax Incentive`
- `Debt Schedule`
- `Cashflow`
- `Sales Estimates`
- `Waterfall`
- `Investor Returns`
- `Sensitivity`
- `Checks`
- `Collateral`
- `Print Pack`

## 18.x Actual sheet outputs present in `SHADE_Spain_Finance_Model_NonStop_50pct_Guarantee_v2.xlsx`

- `Dashboard`
- `Inputs`
- `Finance Plan`
- `Tax Incentive`
- `Debt Schedule`
- `Cashflow`
- `Waterfall`
- `Checks`
- `Collateral`
- `Print Pack`
- `Executive Summary`
- `Production Calendar`
- `Shooting Schedule`
- `Scene Breakdown`
- `Second Unit`
- `Cast DOOD`
- `Location Plan`
- `Detail Crew`
- `Detail Non-Labour`
- `Lean Budget`
- `Assumptions & Risks`
- `Sources`

## 18.x Actual sheet outputs present in `10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1.xlsx`

- `Cover`
- `Project Intake`
- `Spend Matrix`
- `Priority Jurisdictions`
- `Incentive Database`
- `Scenario Engine`
- `Scoring`
- `Output Summary`
- `Sources & Audit`
- `Test Cases`
- `Checks`
- `Lists & Config`
- `Changelog`
- `Coverage Gaps`
- `Programme Rules`
- `FX & Financing`
- `Audit Regression`

# 19. Calculation and decision logic

This section states the controlled calculation logic. The complete cell-by-cell Excel formula catalogue follows in Section 20.

## 19.1 Finance plan reconciliation

`Permanent Finance Gap / (Surplus) = Permanent Uses - Permanent Sources`

or, where the workbook uses a signed surplus convention:

`Gap / Surplus = Total Sources - Gross Budget`

A negative or positive sign must be labelled clearly so users know which direction represents a shortfall.

## 19.2 Debt/equity cap

Default policy check:

`Debt % = Total Debt / Total Capital`

`Equity or Non-Debt % = Total Equity and Other Non-Debt / Total Capital`

Flag a breach where debt exceeds 70% unless the user provides a different approved capital-structure policy.

## 19.3 Development finance cap

Default planning limit:

`Development Finance Cap = Total Budget × 3% to 5%`

Use the project-specific approved percentage when provided.

## 19.4 Basic qualifying spend

Where a line uses local-spend and eligibility percentages:

`Qualifying Spend = Base Budget × Local Spend % × Programme Eligibility %`

Do not use an invented eligibility percentage if programme rules require line-level legal analysis; mark Manual Review/Unknown instead.

## 19.5 Tiered incentive

For a two-tier programme:

`Tier 1 Benefit = MIN(Qualifying Base, Tier 1 Threshold) × Tier 1 Rate`

`Tier 2 Benefit = MAX(MIN(Qualifying Base, Applicable Base Cap) - Tier 1 Threshold, 0) × Tier 2 Rate`

`Gross Statutory Benefit = Tier 1 Benefit + Tier 2 Benefit`

Then apply benefit caps/intensity limits separately.

## 19.6 Benefit cap

`Capped Gross Benefit = MIN(Calculated Gross Benefit, Benefit Cap)`

Do not confuse a benefit cap with an eligible-expenditure-base cap, annual programme allocation or total production-cost threshold.

## 19.7 FX conversion

Preserve programme currency and use a dated FX source.

Where FX is quoted as reporting-currency units per one programme-currency unit:

`Reporting Currency Amount = Programme Currency Amount × FX Rate`

The audited incentive engine also computes cross-rates from its controlled FX table. Show source and rate date.

## 19.8 Tax/transfer leakage

Keep tax effects and transfer haircuts separate. A general structure is:

`After-Tax / After-Transfer Amount = Gross Benefit - Tax Effects - Assistance Effects - Transfer Haircut`

Where a transfer haircut is percentage-based:

`Transfer Haircut = Transferable Portion × Haircut %`

Unknown haircut is not zero.

## 19.9 Bankable / monetisable amount

A controlled structure is:

`Bankable Amount = Eligible Receivable × Lender Advance Rate`

subject to:

- programme availability;
- hard-gate pass;
- lender acceptance;
- tax capacity/assignability/transferability;
- documented advance rate.

Unknown advance rate remains unconfirmed.

## 19.10 Incentive finance cost

For simple time-based interest:

`Interest = Principal × Annual Interest Rate × Months Outstanding / 12`

Then:

`Total Financing Cost = Interest + Upfront Fee + Legal/Closing Costs + Other Facility Costs`

Do not assume fees are zero.

## 19.11 Incentive present value

For annual discount rate `r` and receipt lag `m` months:

`Present Value = Future Net Receipt / (1 + r)^(m/12)`

Use the controlled discount rate and receipt date/lag.

## 19.12 Net present realisable benefit

Controlled bridge:

`Net Present Realisable Benefit = Present-Value Benefit - Incremental Location Cost`

Expanded economic bridge:

`Net Present Realisable Benefit = Gross Statutory Benefit - Tax and Assistance Effects - Fees and Transfer Haircut - Finance Cost - Incremental Location Cost`

The model should show the intermediate amounts so both representations reconcile.

## 19.13 Incentive receivable versus borrowing

Do not add both as permanent finance.

Correct bridge:

`Receivable Face Value`
→ `Eligible / Bankable Receivable`
→ `Lender Advance`
→ `Interest and Fees`
→ `Cash Receipt / Certification`
→ `Loan Repayment`
→ `Residual Incentive Proceeds`

The lender advance is temporary funding against the receivable, not a second permanent source.

## 19.14 VAT/IVA

VAT/IVA recovery and other repayable tax facilities are working-capital items. They must not be used to eliminate the permanent-finance gap.

## 19.15 Non-Stop SHADE package

`Non-Stop Package Amount = Gross Budget × 50%`

`Incentive Facility Amount = MIN(Spanish Incentive Amount, Non-Stop Package Amount)`

`In-Kind Deferred Equity = MAX(0, Non-Stop Package Amount - Incentive Facility Amount)`

`Senior / Gap Debt = MAX(0, Gross Budget - Other Included Sources)`

`Total Sources = SUM(All Finance Sources)`

`Gap / Surplus = Total Sources - Gross Budget`

## 19.16 Net incentive rate in the generic Saracen finance suite

The supplied finance suite contains:

`Net Incentive Rate = Gross Incentive Rate × (1 - Corporation Tax Rate)`

This is a workbook-specific generic calculation and must not override programme-specific audited rules.

## 19.17 Sales scenarios

Where low/base/high sales estimates are used, each territory is modelled separately. Totals aggregate territory values. Deductions such as sales-agent commission and delivery/collection costs are then applied according to the model terms.

Do not present a low/base/high scenario unless the methodology is stated and evidence supports it.

## 19.18 Waterfall

Repayment is sequential according to documented priority. A generic waterfall step is:

`Cash Available for Tier N = MAX(0, Cash Available After Prior Tier)`

`Distribution to Tier N = MIN(Tier N Claim, Cash Available for Tier N)`

`Residual Cash = Cash Available for Tier N - Distribution to Tier N`

Do not create participation or recoupment rights that are not documented.

## 19.19 Investor returns

Where supported:

`MOIC = Total Investor Distributions / Investor Capital Invested`

IRR is calculated from dated or periodic investor cash flows using the workbook's chosen periodicity. Do not present IRR when timing is not sufficiently specified.

## 19.20 Hard-gate logic

A mandatory gate failure forces `FAIL` and zero controlled programme value where the programme is legally unavailable/ineligible.

Unresolved mandatory items force `PRELIMINARY`, not PASS/Green.

Examples of fail conditions in the audited engine include:

- programme closed/test-only/unavailable;
- explicit eligibility condition = No;
- mutually exclusive programme routes selected together;
- required parent enhancement programme missing;
- minimum spend not met;
- minimum production cost not met;
- maximum production cost exceeded;
- incompatible borrowing/transfer assumptions.

Examples of preliminary conditions include:

- Unknown/blank eligibility;
- missing commercial inputs;
- non-Active programme status;
- Low/Unverified evidence;
- manual award amount missing.

## 19.21 Scoring

The audited incentive engine separates economic score and certainty score. Scoring cannot override a failed/unresolved hard gate. A Green recommendation requires all hard gates to pass.

## 19.22 Coverage-gap logic

If no programme record exists for a scoped jurisdiction, classify as `Research gap`, not zero incentive.

If a record exists and an Active/Limited programme is present, classify as `Core programme verified`.

Otherwise classify as `Record present / unavailable`.

## 19.23 Change-control recalculation

Recalculate affected outputs whenever budget allocation, jurisdiction, schedule, entity route, programme rule, FX or lender terms change. Identify stale outputs explicitly rather than silently carrying forward old incentive values.

# 20. Complete workbook formula catalogue

The following catalogues reproduce every Excel formula currently present in the three uploaded `.xlsx` models, by workbook, sheet and cell. They document the actual implementation logic in addition to the conceptual rules above.

## `Saracen_Bridge_Film_Finance_Suite_v1.xlsx`

Total formulas: **410**

### Sheet: `Dashboard`
Formula count: **22**

| Cell | Formula |
|---|---|
| `B5` | `=Inputs!B4` |
| `G5` | `='Finance Plan'!E5` |
| `H5` | `='Finance Plan'!F5` |
| `B6` | `=Inputs!B5` |
| `G6` | `='Finance Plan'!E6` |
| `H6` | `='Finance Plan'!F6` |
| `B7` | `=Inputs!B6` |
| `G7` | `='Finance Plan'!E4` |
| `H7` | `='Finance Plan'!F4` |
| `B8` | `=Inputs!B7` |
| `G8` | `='Finance Plan'!E12` |
| `H8` | `='Finance Plan'!F12` |
| `B9` | `=Inputs!B9` |
| `G9` | `=Collateral!B10` |
| `B10` | `='Finance Plan'!E26` |
| `G10` | `='Finance Plan'!E30` |
| `B11` | `='Finance Plan'!E27` |
| `G11` | `='Finance Plan'!E31` |
| `B12` | `='Finance Plan'!E28` |
| `G12` | `='Finance Plan'!E32` |
| `B13` | `=Checks!B5` |
| `G13` | `='Debt Schedule'!E7` |

### Sheet: `Inputs`
Formula count: **2**

| Cell | Formula |
|---|---|
| `B26` | `=B25*(1-F25)` |
| `F26` | `=B19` |

### Sheet: `Finance Plan`
Formula count: **52**

| Cell | Formula |
|---|---|
| `E4` | `=Inputs!B9*Inputs!B15` |
| `F4` | `=E4/Inputs!B9` |
| `E5` | `=Inputs!B9*Inputs!F15` |
| `F5` | `=E5/Inputs!B9` |
| `D6` | `='Tax Incentive'!B12` |
| `E6` | `=D6` |
| `F6` | `=E6/Inputs!B9` |
| `D7` | `='Sales Estimates'!E18` |
| `E7` | `=MAX(C7,D7)` |
| `F7` | `=E7/Inputs!B9` |
| `E8` | `=MIN(C8,Inputs!B9*Inputs!F20)` |
| `F8` | `=E8/Inputs!B9` |
| `D9` | `=Inputs!B32` |
| `E9` | `=MAX(C9,D9)` |
| `F9` | `=E9/Inputs!B9` |
| `D10` | `=Inputs!F32` |
| `E10` | `=MAX(C10,D10)` |
| `F10` | `=E10/Inputs!B9` |
| `D11` | `=Inputs!B33` |
| `E11` | `=MAX(C11,D11)` |
| `F11` | `=E11/Inputs!B9` |
| `D12` | `=Inputs!B27+Inputs!F27` |
| `E12` | `=D12` |
| `F12` | `=E12/Inputs!B9` |
| `D13` | `=Inputs!F33` |
| `E13` | `=MAX(C13,D13)` |
| `F13` | `=E13/Inputs!B9` |
| `E14` | `=C14` |
| `F14` | `=E14/Inputs!B9` |
| `E15` | `=C15` |
| `F15` | `=E15/Inputs!B9` |
| `E19` | `=Inputs!B9` |
| `F19` | `=E19/Inputs!B9` |
| `E20` | `=SUM(E4:E15)` |
| `F20` | `=E20/Inputs!B9` |
| `E21` | `=E19-E20` |
| `F21` | `=E21/Inputs!B9` |
| `E22` | `=E20/E19` |
| `E23` | `=SUM(E5,E6,E8)` |
| `F23` | `=E23/Inputs!B9` |
| `E24` | `=E4` |
| `F24` | `=E24/Inputs!B9` |
| `E25` | `=SUM(E10:E12)` |
| `F25` | `=E25/Inputs!B9` |
| `E26` | `=E20` |
| `E27` | `=E21` |
| `E28` | `=E22` |
| `E30` | `=E23/Inputs!B9` |
| `E31` | `=E24/Inputs!B9` |
| `E32` | `=E6/Inputs!B9` |
| `E33` | `=IF(ABS(E21)<1,"Balanced","Review")` |
| `E34` | `=Checks!B5` |

### Sheet: `Tax Incentive`
Formula count: **12**

| Cell | Formula |
|---|---|
| `B4` | `=Inputs!B9` |
| `B5` | `=Inputs!F24` |
| `B6` | `=B4*B5` |
| `B7` | `=Inputs!B25` |
| `B8` | `=B6*B7` |
| `B9` | `=Inputs!F25` |
| `B10` | `=B8*(1-B9)` |
| `B11` | `=Inputs!F26` |
| `B12` | `=B10*B11` |
| `B13` | `=Inputs!F19` |
| `B14` | `=B12*B13*Inputs!F17/12` |
| `B15` | `=B12-B14` |

### Sheet: `Debt Schedule`
Formula count: **32**

| Cell | Formula |
|---|---|
| `B4` | `='Finance Plan'!E5` |
| `C4` | `=Inputs!F16` |
| `D4` | `=Inputs!F17` |
| `E4` | `=B4*C4*D4/12` |
| `F4` | `=B4*Inputs!B18` |
| `G4` | `=B4*Inputs!F18` |
| `H4` | `=SUM(E4:G4)` |
| `B5` | `='Finance Plan'!E6` |
| `C5` | `=Inputs!F19` |
| `D5` | `=Inputs!F17` |
| `E5` | `=B5*C5*D5/12` |
| `F5` | `=B5*Inputs!B18` |
| `G5` | `=B5*Inputs!F18` |
| `H5` | `=SUM(E5:G5)` |
| `B6` | `='Finance Plan'!E8` |
| `C6` | `=Inputs!F20` |
| `D6` | `=Inputs!F17` |
| `E6` | `=B6*C6*D6/12` |
| `F6` | `=B6*Inputs!B18` |
| `G6` | `=B6*Inputs!F18` |
| `H6` | `=SUM(E6:G6)` |
| `B7` | `=SUM(B4:B6)` |
| `E7` | `=SUM(E4:E6)` |
| `F7` | `=SUM(F4:F6)` |
| `G7` | `=SUM(G4:G6)` |
| `H7` | `=SUM(H4:H6)` |
| `B11` | `=B4/Inputs!B9` |
| `B12` | `=B5/Inputs!B9` |
| `B13` | `=B6/Inputs!B9` |
| `B14` | `=B7/Inputs!B9` |
| `B15` | `=H7/B7` |
| `B16` | `=E7` |

### Sheet: `Cashflow`
Formula count: **169**

| Cell | Formula |
|---|---|
| `B4` | `=Inputs!B9*Inputs!B12` |
| `C4` | `=B4*0.4` |
| `D4` | `=B4*0.3` |
| `E4` | `=B4*0.2` |
| `F4` | `=B4*0.1` |
| `G4` | `=B4*0` |
| `H4` | `=B4*0` |
| `I4` | `=B4*0` |
| `J4` | `=B4*0` |
| `K4` | `=B4*0` |
| `L4` | `=B4*0` |
| `M4` | `=B4*0` |
| `N4` | `=B4*0` |
| `B5` | `=Inputs!B9*0.15` |
| `C5` | `=B5*0` |
| `D5` | `=B5*0.1` |
| `E5` | `=B5*0.3` |
| `F5` | `=B5*0.4` |
| `G5` | `=B5*0.2` |
| `H5` | `=B5*0` |
| `I5` | `=B5*0` |
| `J5` | `=B5*0` |
| `K5` | `=B5*0` |
| `L5` | `=B5*0` |
| `M5` | `=B5*0` |
| `N5` | `=B5*0` |
| `B6` | `=Inputs!B9*0.5` |
| `C6` | `=B6*0` |
| `D6` | `=B6*0` |
| `E6` | `=B6*0` |
| `F6` | `=B6*0.15` |
| `G6` | `=B6*0.3` |
| `H6` | `=B6*0.3` |
| `I6` | `=B6*0.2` |
| `J6` | `=B6*0.05` |
| `K6` | `=B6*0` |
| `L6` | `=B6*0` |
| `M6` | `=B6*0` |
| `N6` | `=B6*0` |
| `B7` | `=Inputs!B9*0.25` |
| `C7` | `=B7*0` |
| `D7` | `=B7*0` |
| `E7` | `=B7*0` |
| `F7` | `=B7*0` |
| `G7` | `=B7*0` |
| `H7` | `=B7*0.05` |
| `I7` | `=B7*0.15` |
| `J7` | `=B7*0.2` |
| `K7` | `=B7*0.25` |
| `L7` | `=B7*0.2` |
| `M7` | `=B7*0.1` |
| `N7` | `=B7*0.05` |
| `B8` | `=Inputs!B9*Inputs!B10` |
| `C8` | `=B8*0` |
| `D8` | `=B8*0` |
| `E8` | `=B8*0` |
| `F8` | `=B8*0.1` |
| `G8` | `=B8*0.15` |
| `H8` | `=B8*0.2` |
| `I8` | `=B8*0.2` |
| `J8` | `=B8*0.15` |
| `K8` | `=B8*0.1` |
| `L8` | `=B8*0.05` |
| `M8` | `=B8*0.03` |
| `N8` | `=B8*0.02` |
| `B9` | `=SUM(B4:B8)` |
| `C9` | `=SUM(C4:C8)` |
| `D9` | `=SUM(D4:D8)` |
| `E9` | `=SUM(E4:E8)` |
| `F9` | `=SUM(F4:F8)` |
| `G9` | `=SUM(G4:G8)` |
| `H9` | `=SUM(H4:H8)` |
| `I9` | `=SUM(I4:I8)` |
| `J9` | `=SUM(J4:J8)` |
| `K9` | `=SUM(K4:K8)` |
| `L9` | `=SUM(L4:L8)` |
| `M9` | `=SUM(M4:M8)` |
| `N9` | `=SUM(N4:N8)` |
| `B14` | `='Finance Plan'!E4` |
| `C14` | `=B14*0.25` |
| `D14` | `=B14*0.25` |
| `E14` | `=B14*0.25` |
| `F14` | `=B14*0.25` |
| `G14` | `=B14*0` |
| `H14` | `=B14*0` |
| `I14` | `=B14*0` |
| `J14` | `=B14*0` |
| `K14` | `=B14*0` |
| `L14` | `=B14*0` |
| `M14` | `=B14*0` |
| `N14` | `=B14*0` |
| `B15` | `='Finance Plan'!E5` |
| `C15` | `=B15*0` |
| `D15` | `=B15*0` |
| `E15` | `=B15*0.2` |
| `F15` | `=B15*0.25` |
| `G15` | `=B15*0.25` |
| `H15` | `=B15*0.2` |
| `I15` | `=B15*0.1` |
| `J15` | `=B15*0` |
| `K15` | `=B15*0` |
| `L15` | `=B15*0` |
| `M15` | `=B15*0` |
| `N15` | `=B15*0` |
| `B16` | `='Finance Plan'!E6` |
| `C16` | `=B16*0` |
| `D16` | `=B16*0` |
| `E16` | `=B16*0` |
| `F16` | `=B16*0.2` |
| `G16` | `=B16*0.2` |
| `H16` | `=B16*0.2` |
| `I16` | `=B16*0.2` |
| `J16` | `=B16*0.2` |
| `K16` | `=B16*0` |
| `L16` | `=B16*0` |
| `M16` | `=B16*0` |
| `N16` | `=B16*0` |
| `B17` | `='Finance Plan'!E12` |
| `C17` | `=B17*0.25` |
| `D17` | `=B17*0.25` |
| `E17` | `=B17*0.25` |
| `F17` | `=B17*0.25` |
| `G17` | `=B17*0` |
| `H17` | `=B17*0` |
| `I17` | `=B17*0` |
| `J17` | `=B17*0` |
| `K17` | `=B17*0` |
| `L17` | `=B17*0` |
| `M17` | `=B17*0` |
| `N17` | `=B17*0` |
| `B18` | `=SUM(B14:B17)` |
| `C18` | `=SUM(C14:C17)` |
| `D18` | `=SUM(D14:D17)` |
| `E18` | `=SUM(E14:E17)` |
| `F18` | `=SUM(F14:F17)` |
| `G18` | `=SUM(G14:G17)` |
| `H18` | `=SUM(H14:H17)` |
| `I18` | `=SUM(I14:I17)` |
| `J18` | `=SUM(J14:J17)` |
| `K18` | `=SUM(K14:K17)` |
| `L18` | `=SUM(L14:L17)` |
| `M18` | `=SUM(M14:M17)` |
| `N18` | `=SUM(N14:N17)` |
| `B19` | `=B18-B9` |
| `C19` | `=C18-C9` |
| `D19` | `=D18-D9` |
| `E19` | `=E18-E9` |
| `F19` | `=F18-F9` |
| `G19` | `=G18-G9` |
| `H19` | `=H18-H9` |
| `I19` | `=I18-I9` |
| `J19` | `=J18-J9` |
| `K19` | `=K18-K9` |
| `L19` | `=L18-L9` |
| `M19` | `=M18-M9` |
| `N19` | `=N18-N9` |
| `B20` | `=B19` |
| `C20` | `=C19` |
| `D20` | `=C20+D19` |
| `E20` | `=D20+E19` |
| `F20` | `=E20+F19` |
| `G20` | `=F20+G19` |
| `H20` | `=G20+H19` |
| `I20` | `=H20+I19` |
| `J20` | `=I20+J19` |
| `K20` | `=J20+K19` |
| `L20` | `=K20+L19` |
| `M20` | `=L20+M19` |
| `N20` | `=M20+N19` |

### Sheet: `Sales Estimates`
Formula count: **4**

| Cell | Formula |
|---|---|
| `B18` | `=SUM(B4:B16)` |
| `C18` | `=SUM(C4:C16)` |
| `D18` | `=SUM(D4:D16)` |
| `E18` | `=SUM(E4:E16)` |

### Sheet: `Waterfall`
Formula count: **30**

| Cell | Formula |
|---|---|
| `B4` | `='Sales Estimates'!C18` |
| `D4` | `='Sales Estimates'!B18` |
| `E4` | `='Sales Estimates'!D18` |
| `B5` | `=B4*Inputs!F30` |
| `D5` | `=D4*Inputs!F30` |
| `E5` | `=E4*Inputs!F30` |
| `B6` | `=Inputs!B31` |
| `D6` | `=Inputs!B31` |
| `E6` | `=Inputs!B31` |
| `B7` | `=B4-B5-B6` |
| `D7` | `=D4-D5-D6` |
| `E7` | `=E4-E5-E6` |
| `B8` | `=MIN(B7,'Debt Schedule'!B4+'Debt Schedule'!H4)` |
| `D8` | `=MIN(D7,'Debt Schedule'!B4+'Debt Schedule'!H4)` |
| `E8` | `=MIN(E7,'Debt Schedule'!B4+'Debt Schedule'!H4)` |
| `B9` | `=MIN(B7-B8,'Debt Schedule'!B5+'Debt Schedule'!H5)` |
| `D9` | `=MIN(D7-D8,'Debt Schedule'!B5+'Debt Schedule'!H5)` |
| `E9` | `=MIN(E7-E8,'Debt Schedule'!B5+'Debt Schedule'!H5)` |
| `B10` | `='Finance Plan'!E4*Inputs!B16*Inputs!B17/12` |
| `D10` | `='Finance Plan'!E4*Inputs!B16*Inputs!B17/12` |
| `E10` | `='Finance Plan'!E4*Inputs!B16*Inputs!B17/12` |
| `B11` | `=MIN(B7-B8-B9-B10,'Finance Plan'!E4)` |
| `D11` | `=MIN(D7-D8-D9-D10,'Finance Plan'!E4)` |
| `E11` | `=MIN(E7-E8-E9-E10,'Finance Plan'!E4)` |
| `B12` | `=MAX(0,(B7-B8-B9-B10-B11)*Inputs!F31)` |
| `D12` | `=MAX(0,(D7-D8-D9-D10-D11)*Inputs!F31)` |
| `E12` | `=MAX(0,(E7-E8-E9-E10-E11)*Inputs!F31)` |
| `B13` | `=B7-B8-B9-B10-B11-B12` |
| `D13` | `=D7-D8-D9-D10-D11-D12` |
| `E13` | `=E7-E8-E9-E10-E11-E12` |

### Sheet: `Investor Returns`
Formula count: **21**

| Cell | Formula |
|---|---|
| `B4` | `='Finance Plan'!E4` |
| `C4` | `='Finance Plan'!E4` |
| `D4` | `='Finance Plan'!E4` |
| `B5` | `=B4*Inputs!B16*Inputs!B17/12` |
| `C5` | `=C4*Inputs!B16*Inputs!B17/12` |
| `D5` | `=D4*Inputs!B16*Inputs!B17/12` |
| `B6` | `=MIN(B4,Waterfall!D11)` |
| `C6` | `=MIN(C4,Waterfall!B11)` |
| `D6` | `=MIN(D4,Waterfall!E11)` |
| `B7` | `=B5+B6` |
| `C7` | `=C5+C6` |
| `D7` | `=D5+D6` |
| `B8` | `=B7/B4` |
| `C8` | `=C7/C4` |
| `D8` | `=D7/D4` |
| `B9` | `=(B7/B4-1)/(Inputs!B17/12)` |
| `C9` | `=(C7/C4-1)/(Inputs!B17/12)` |
| `D9` | `=(D7/D4-1)/(Inputs!B17/12)` |
| `B10` | `=Waterfall!D13` |
| `C10` | `=Waterfall!B13` |
| `D10` | `=Waterfall!E13` |

### Sheet: `Sensitivity`
Formula count: **28**

| Cell | Formula |
|---|---|
| `B4` | `='Sales Estimates'!B18*0.75` |
| `C4` | `='Sales Estimates'!C18*0.75` |
| `D4` | `='Sales Estimates'!D18*0.75` |
| `E4` | `=Inputs!B9` |
| `F4` | `='Finance Plan'!E27` |
| `G4` | `=C4-E4` |
| `H4` | `=IF(G4>0,"Surplus","Deficit")` |
| `B5` | `='Sales Estimates'!B18*1` |
| `C5` | `='Sales Estimates'!C18*1` |
| `D5` | `='Sales Estimates'!D18*1` |
| `E5` | `=Inputs!B9` |
| `F5` | `='Finance Plan'!E27` |
| `G5` | `=C5-E5` |
| `H5` | `=IF(G5>0,"Surplus","Deficit")` |
| `B6` | `='Sales Estimates'!B18*1.25` |
| `C6` | `='Sales Estimates'!C18*1.25` |
| `D6` | `='Sales Estimates'!D18*1.25` |
| `E6` | `=Inputs!B9` |
| `F6` | `='Finance Plan'!E27` |
| `G6` | `=C6-E6` |
| `H6` | `=IF(G6>0,"Surplus","Deficit")` |
| `B7` | `='Sales Estimates'!B18*1.5` |
| `C7` | `='Sales Estimates'!C18*1.5` |
| `D7` | `='Sales Estimates'!D18*1.5` |
| `E7` | `=Inputs!B9` |
| `F7` | `='Finance Plan'!E27` |
| `G7` | `=C7-E7` |
| `H7` | `=IF(G7>0,"Surplus","Deficit")` |

### Sheet: `Checks`
Formula count: **11**

| Cell | Formula |
|---|---|
| `B4` | `=IF(ABS('Finance Plan'!E27)<1,"Pass","Review")` |
| `B5` | `=IF(COUNTIF(B4:B14,"Review")=0,"Pass","Review")` |
| `B6` | `=IF(Inputs!B34="Yes","Pass","Review")` |
| `B7` | `=IF(Inputs!B24="United Kingdom","Review","N/A")` |
| `B8` | `=IF('Tax Incentive'!B12>0,"Review","N/A")` |
| `B9` | `=IF(Inputs!F35="Yes","Pass","Review")` |
| `B10` | `=IF(Inputs!B35="Yes","Pass","Review")` |
| `B11` | `=IF(Inputs!B9>0,"Review","Review")` |
| `B12` | `=IF(Collateral!B10>=1,"Pass","Review")` |
| `B13` | `=IF('Finance Plan'!E27<=0,"Pass","Review")` |
| `B14` | `="Manual scan required"` |

### Sheet: `Collateral`
Formula count: **17**

| Cell | Formula |
|---|---|
| `B4` | `='Tax Incentive'!B10` |
| `C4` | `=Inputs!F26` |
| `D4` | `=B4*C4` |
| `B5` | `='Sales Estimates'!E18` |
| `C5` | `=0.85` |
| `D5` | `=B5*C5` |
| `B6` | `='Finance Plan'!E12` |
| `C6` | `=0.8` |
| `D6` | `=B6*C6` |
| `B7` | `=0` |
| `C7` | `=0.75` |
| `D7` | `=B7*C7` |
| `B8` | `=SUM(B4:B7)` |
| `D8` | `=SUM(D4:D7)` |
| `B9` | `='Debt Schedule'!B7` |
| `B10` | `=D8/B9` |
| `E18` | `=B10` |

### Sheet: `Print Pack`
Formula count: **10**

| Cell | Formula |
|---|---|
| `B3` | `=Inputs!B4` |
| `B4` | `=Inputs!B9` |
| `B5` | `='Finance Plan'!E26` |
| `B6` | `='Finance Plan'!E27` |
| `B7` | `='Finance Plan'!E6` |
| `B8` | `='Finance Plan'!E5` |
| `B9` | `='Finance Plan'!E4` |
| `B10` | `='Finance Plan'!E12` |
| `B11` | `=Collateral!B10` |
| `B12` | `=Checks!B5` |


## `SHADE_Spain_Finance_Model_NonStop_50pct_Guarantee_v2.xlsx`

Total formulas: **776**

### Sheet: `Dashboard`
Formula count: **14**

| Cell | Formula |
|---|---|
| `B10` | `='Inputs'!B13` |
| `C10` | `='Inputs'!C13` |
| `B11` | `='Inputs'!B14` |
| `C11` | `='Inputs'!C14` |
| `B12` | `='Tax Incentive'!B14` |
| `C12` | `='Tax Incentive'!C14` |
| `B13` | `='Inputs'!B16` |
| `C13` | `='Inputs'!C16` |
| `B14` | `='Inputs'!B24` |
| `C14` | `='Inputs'!C24` |
| `B15` | `='Finance Plan'!B22` |
| `C15` | `='Finance Plan'!C22` |
| `B16` | `='Finance Plan'!B23` |
| `C16` | `='Finance Plan'!C23` |

### Sheet: `Inputs`
Formula count: **24**

| Cell | Formula |
|---|---|
| `B12` | `=1/B11` |
| `B13` | `='Lean Budget'!C41` |
| `C13` | `=B13/$B$11` |
| `B14` | `='Lean Budget'!C42` |
| `C14` | `=B14/$B$11` |
| `B15` | `='Tax Incentive'!B14` |
| `C15` | `=B15/$B$11` |
| `B16` | `=B13-B15` |
| `C16` | `=B16/$B$11` |
| `B23` | `=1500000*$B$11` |
| `B24` | `=$B$13*50%` |
| `C24` | `=B24/$B$11` |
| `B25` | `=MIN('Tax Incentive'!$B$14,$B$24)` |
| `C25` | `=B25/$B$11` |
| `B26` | `=MAX(0,$B$24-$B$25)` |
| `C26` | `=B26/$B$11` |
| `C27` | `=B27/$B$11` |
| `C28` | `=B28/$B$11` |
| `B29` | `=MAX(0,$B$13-SUM(B23:B28))` |
| `C29` | `=B29/$B$11` |
| `B30` | `=SUM(B23:B29)` |
| `C30` | `=B30/$B$11` |
| `B31` | `=B30-$B$13` |
| `C31` | `=B31/$B$11` |

### Sheet: `Finance Plan`
Formula count: **32**

| Cell | Formula |
|---|---|
| `B5` | `='Inputs'!B13` |
| `C5` | `='Inputs'!C13` |
| `B7` | `=SUM(B5:B6)` |
| `C7` | `=SUM(C5:C6)` |
| `B12` | `='Inputs'!B23` |
| `C12` | `='Inputs'!C23` |
| `D12` | `='Inputs'!D23` |
| `B13` | `='Inputs'!B25` |
| `C13` | `='Inputs'!C25` |
| `D13` | `='Inputs'!D25` |
| `B14` | `='Inputs'!B26` |
| `C14` | `='Inputs'!C26` |
| `D14` | `='Inputs'!D26` |
| `B15` | `='Inputs'!B27` |
| `C15` | `='Inputs'!C27` |
| `D15` | `='Inputs'!D27` |
| `B16` | `='Inputs'!B28` |
| `C16` | `='Inputs'!C28` |
| `D16` | `='Inputs'!D28` |
| `B18` | `='Inputs'!B29` |
| `C18` | `='Inputs'!C29` |
| `D18` | `='Inputs'!D29` |
| `B22` | `=SUM(B12:B18)` |
| `C22` | `=SUM(C12:C18)` |
| `B23` | `=B22-B7` |
| `C23` | `=C22-C7` |
| `D23` | `=IF(B23>=0,"Balanced / surplus","Shortfall")` |
| `B28` | `=B18/B7` |
| `D28` | `=IF(B28<=70%,"Within cap","Exceeds cap")` |
| `B29` | `=(B22-B18)/B7` |
| `D29` | `=IF(B29>=30%,"Within target","Below target")` |
| `B30` | `=SUMIF(D12:D18,"Confirmed",B12:B18)+SUMIF(D12:D18,"Signed conditional",B12:B18)+SUMIF(D12:D18,"User instruction / to document",B12:B18)` |

### Sheet: `Tax Incentive`
Formula count: **14**

| Cell | Formula |
|---|---|
| `B5` | `='Inputs'!B6` |
| `B7` | `='Lean Budget'!C42` |
| `C7` | `=B7/'Inputs'!B11` |
| `C8` | `=B8/'Inputs'!B11` |
| `B11` | `=IF(B7<B8,0,B9*MIN(B7,B8)+B10*MAX(0,B7-B8))` |
| `C11` | `=B11/'Inputs'!B11` |
| `C12` | `=B12/'Inputs'!B11` |
| `B14` | `=MIN(B11,B12)*B13` |
| `C14` | `=B14/'Inputs'!B11` |
| `B15` | `='Inputs'!B13-B14` |
| `C15` | `=B15/'Inputs'!B11` |
| `B25` | `=B14` |
| `B26` | `=B25*B23` |
| `B27` | `=B25+B26+B24` |

### Sheet: `Debt Schedule`
Formula count: **13**

| Cell | Formula |
|---|---|
| `B5` | `='Inputs'!B13` |
| `C5` | `='Inputs'!C13` |
| `B6` | `='Inputs'!B17` |
| `B7` | `=B5*B6` |
| `C7` | `=B7/'Inputs'!B11` |
| `B8` | `='Inputs'!B29` |
| `C8` | `='Inputs'!C29` |
| `B9` | `=B7-B8` |
| `C9` | `=B9/'Inputs'!B11` |
| `D9` | `=IF(B9>=0,"Within cap","Exceeds cap")` |
| `B17` | `=B8*B14*B15/12` |
| `B18` | `=B8*B16` |
| `B19` | `=B8+B17+B18` |

### Sheet: `Cashflow`
Formula count: **101**

| Cell | Formula |
|---|---|
| `K5` | `=SUM(B5:J5)` |
| `B6` | `='Inputs'!$B$13*B$5` |
| `C6` | `='Inputs'!$B$13*C$5` |
| `D6` | `='Inputs'!$B$13*D$5` |
| `E6` | `='Inputs'!$B$13*E$5` |
| `F6` | `='Inputs'!$B$13*F$5` |
| `G6` | `='Inputs'!$B$13*G$5` |
| `H6` | `='Inputs'!$B$13*H$5` |
| `I6` | `='Inputs'!$B$13*I$5` |
| `J6` | `='Inputs'!$B$13*J$5` |
| `K6` | `=SUM(B6:J6)` |
| `B9` | `='Inputs'!$B$23*0` |
| `C9` | `='Inputs'!$B$23*0.5` |
| `D9` | `='Inputs'!$B$23*0.5` |
| `E9` | `='Inputs'!$B$23*0` |
| `F9` | `='Inputs'!$B$23*0` |
| `G9` | `='Inputs'!$B$23*0` |
| `H9` | `='Inputs'!$B$23*0` |
| `I9` | `='Inputs'!$B$23*0` |
| `J9` | `='Inputs'!$B$23*0` |
| `K9` | `=SUM(B9:J9)` |
| `B10` | `='Inputs'!$B$25*0` |
| `C10` | `='Inputs'!$B$25*0` |
| `D10` | `='Inputs'!$B$25*0.25` |
| `E10` | `='Inputs'!$B$25*0.25` |
| `F10` | `='Inputs'!$B$25*0.25` |
| `G10` | `='Inputs'!$B$25*0.25` |
| `H10` | `='Inputs'!$B$25*0` |
| `I10` | `='Inputs'!$B$24*0` |
| `J10` | `='Inputs'!$B$24*0` |
| `K10` | `=SUM(B10:J10)` |
| `B11` | `='Inputs'!$B$26*0.2` |
| `C11` | `='Inputs'!$B$26*0.2` |
| `D11` | `='Inputs'!$B$26*0.2` |
| `E11` | `='Inputs'!$B$26*0.2` |
| `F11` | `='Inputs'!$B$26*0.2` |
| `G11` | `='Inputs'!$B$26*0` |
| `H11` | `='Inputs'!$B$26*0` |
| `I11` | `='Inputs'!$B$25*0` |
| `J11` | `='Inputs'!$B$25*0` |
| `K11` | `=SUM(B11:J11)` |
| `B12` | `='Inputs'!$B$23*0` |
| `C12` | `='Inputs'!$B$23*0.5` |
| `D12` | `='Inputs'!$B$23*0.5` |
| `E12` | `='Inputs'!$B$23*0` |
| `F12` | `='Inputs'!$B$23*0` |
| `G12` | `='Inputs'!$B$23*0` |
| `H12` | `='Inputs'!$B$23*0` |
| `I12` | `='Inputs'!$B$27*0` |
| `J12` | `='Inputs'!$B$27*0` |
| `K12` | `=SUM(B12:J12)` |
| `B13` | `=('Inputs'!$B$27+'Inputs'!$B$28)*0.2` |
| `C13` | `=('Inputs'!$B$27+'Inputs'!$B$28)*0.2` |
| `D13` | `=('Inputs'!$B$27+'Inputs'!$B$28)*0.2` |
| `E13` | `=('Inputs'!$B$27+'Inputs'!$B$28)*0.2` |
| `F13` | `=('Inputs'!$B$27+'Inputs'!$B$28)*0.2` |
| `G13` | `=('Inputs'!$B$27+'Inputs'!$B$28)*0` |
| `H13` | `=('Inputs'!$B$27+'Inputs'!$B$28)*0` |
| `I13` | `='Inputs'!$B$28*0` |
| `J13` | `='Inputs'!$B$28*0` |
| `K13` | `=SUM(B13:J13)` |
| `B14` | `=MAX(0,B6-SUM(B9:B13))` |
| `C14` | `=MAX(0,C6-SUM(C9:C13))` |
| `D14` | `=MAX(0,D6-SUM(D9:D13))` |
| `E14` | `=MAX(0,E6-SUM(E9:E13))` |
| `F14` | `=MAX(0,F6-SUM(F9:F13))` |
| `G14` | `=MAX(0,G6-SUM(G9:G13))` |
| `H14` | `=MAX(0,H6-SUM(H9:H13))` |
| `I14` | `=MAX(0,I6-SUM(I9:I13))` |
| `J14` | `=MAX(0,J6-SUM(J9:J13))` |
| `K14` | `=SUM(B14:J14)` |
| `B15` | `=SUM(B9:B14)` |
| `C15` | `=SUM(C9:C14)` |
| `D15` | `=SUM(D9:D14)` |
| `E15` | `=SUM(E9:E14)` |
| `F15` | `=SUM(F9:F14)` |
| `G15` | `=SUM(G9:G14)` |
| `H15` | `=SUM(H9:H14)` |
| `I15` | `=SUM(I9:I14)` |
| `J15` | `=SUM(J9:J14)` |
| `K15` | `=SUM(B15:J15)` |
| `B16` | `=B15-B6` |
| `C16` | `=C15-C6` |
| `D16` | `=D15-D6` |
| `E16` | `=E15-E6` |
| `F16` | `=F15-F6` |
| `G16` | `=G15-G6` |
| `H16` | `=H15-H6` |
| `I16` | `=I15-I6` |
| `J16` | `=J15-J6` |
| `K16` | `=SUM(B16:J16)` |
| `B17` | `=0+B16` |
| `C17` | `=B17+C16` |
| `D17` | `=C17+D16` |
| `E17` | `=D17+E16` |
| `F17` | `=E17+F16` |
| `G17` | `=F17+G16` |
| `H17` | `=G17+H16` |
| `I17` | `=H17+I16` |
| `J17` | `=I17+J16` |
| `K17` | `=J17` |

### Sheet: `Waterfall`
Formula count: **17**

| Cell | Formula |
|---|---|
| `C5` | `=B5/'Inputs'!B11` |
| `C12` | `=B5*$B$6` |
| `D12` | `=MIN(C12,$B$5)` |
| `C13` | `=B5*$B$7` |
| `D13` | `=MIN(C13,MAX(0,$B$5-SUM(D$12:D12)))` |
| `C14` | `='Debt Schedule'!B19` |
| `D14` | `=MIN(C14,MAX(0,$B$5-SUM(D$12:D13)))` |
| `C15` | `='Tax Incentive'!B27` |
| `D15` | `=MIN(C15,MAX(0,$B$5-SUM(D$12:D14)))` |
| `C16` | `='Inputs'!B23` |
| `D16` | `=MIN(C16,MAX(0,$B$5-SUM(D$12:D15)))` |
| `C17` | `='Inputs'!B26` |
| `D17` | `=MIN(C17,MAX(0,$B$5-SUM(D$12:D16)))` |
| `C18` | `='Inputs'!B28` |
| `D18` | `=MIN(C18,MAX(0,$B$5-SUM(D$12:D17)))` |
| `C19` | `=MAX(0,$B$5-SUM(D$12:D18))` |
| `D19` | `=C19` |

### Sheet: `Checks`
Formula count: **22**

| Cell | Formula |
|---|---|
| `C5` | `='Inputs'!B6` |
| `D5` | `=IF(C5="Spain","Green","Red")` |
| `C7` | `='Finance Plan'!B23` |
| `D7` | `=IF(C7>=0,"Green","Red")` |
| `C8` | `='Finance Plan'!B28` |
| `D8` | `=IF(C8<=70%,"Green","Red")` |
| `C9` | `='Tax Incentive'!B20` |
| `D9` | `=IF(C9="Received","Green","Red")` |
| `C10` | `='Tax Incentive'!B21` |
| `D10` | `=IF(C10="Received","Green","Amber")` |
| `C11` | `='Tax Incentive'!B22&" / "&TEXT('Tax Incentive'!B23,"0.0%")&" p.a. / fee "&TEXT('Tax Incentive'!B24,"€#,##0")` |
| `D11` | `=IF(AND('Tax Incentive'!B22="Yes – user instruction",'Tax Incentive'!B23=12%,'Tax Incentive'!B24=0),"Amber","Red")` |
| `C12` | `='Debt Schedule'!B24` |
| `D12` | `=IF(C12="Received","Green","Red")` |
| `C13` | `='Debt Schedule'!B25` |
| `D13` | `=IF(C13="Received","Green","Red")` |
| `C14` | `='Inputs'!D23` |
| `D14` | `=IF(OR(C14="Confirmed",C14="Signed conditional"),"Green","Amber")` |
| `C15` | `='Inputs'!D24&" / "&'Inputs'!D25&" / "&'Inputs'!D26` |
| `D15` | `=IF(AND('Inputs'!D24="Confirmed",'Inputs'!D25="Confirmed",'Inputs'!D26="Confirmed"),"Green","Amber")` |
| `C16` | `='Inputs'!B24/'Inputs'!B13` |
| `D16` | `=IF(ROUND(C16,4)=50%,"Amber","Red")` |

### Sheet: `Collateral`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Print Pack`
Formula count: **3**

| Cell | Formula |
|---|---|
| `B8` | `='Inputs'!B13` |
| `B9` | `='Inputs'!B24` |
| `B10` | `='Finance Plan'!D23` |

### Sheet: `Executive Summary`
Formula count: **4**

| Cell | Formula |
|---|---|
| `A18` | `='Lean Budget'!C41` |
| `B18` | `='Lean Budget'!C42` |
| `C18` | `='Lean Budget'!C43` |
| `D18` | `='Lean Budget'!C44` |

### Sheet: `Production Calendar`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Shooting Schedule`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Scene Breakdown`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Second Unit`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Cast DOOD`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Location Plan`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Detail Crew`
Formula count: **182**

| Cell | Formula |
|---|---|
| `L5` | `=D5*(E5+F5+G5)*H5*I5*(1+J5)*(1+K5)` |
| `N5` | `=L5*M5` |
| `L6` | `=D6*(E6+F6+G6)*H6*I6*(1+J6)*(1+K6)` |
| `N6` | `=L6*M6` |
| `L7` | `=D7*(E7+F7+G7)*H7*I7*(1+J7)*(1+K7)` |
| `N7` | `=L7*M7` |
| `L8` | `=D8*(E8+F8+G8)*H8*I8*(1+J8)*(1+K8)` |
| `N8` | `=L8*M8` |
| `L9` | `=D9*(E9+F9+G9)*H9*I9*(1+J9)*(1+K9)` |
| `N9` | `=L9*M9` |
| `L10` | `=D10*(E10+F10+G10)*H10*I10*(1+J10)*(1+K10)` |
| `N10` | `=L10*M10` |
| `L11` | `=D11*(E11+F11+G11)*H11*I11*(1+J11)*(1+K11)` |
| `N11` | `=L11*M11` |
| `L12` | `=D12*(E12+F12+G12)*H12*I12*(1+J12)*(1+K12)` |
| `N12` | `=L12*M12` |
| `L13` | `=D13*(E13+F13+G13)*H13*I13*(1+J13)*(1+K13)` |
| `N13` | `=L13*M13` |
| `L14` | `=D14*(E14+F14+G14)*H14*I14*(1+J14)*(1+K14)` |
| `N14` | `=L14*M14` |
| `L15` | `=D15*(E15+F15+G15)*H15*I15*(1+J15)*(1+K15)` |
| `N15` | `=L15*M15` |
| `L16` | `=D16*(E16+F16+G16)*H16*I16*(1+J16)*(1+K16)` |
| `N16` | `=L16*M16` |
| `L17` | `=D17*(E17+F17+G17)*H17*I17*(1+J17)*(1+K17)` |
| `N17` | `=L17*M17` |
| `L18` | `=D18*(E18+F18+G18)*H18*I18*(1+J18)*(1+K18)` |
| `N18` | `=L18*M18` |
| `L19` | `=D19*(E19+F19+G19)*H19*I19*(1+J19)*(1+K19)` |
| `N19` | `=L19*M19` |
| `L20` | `=D20*(E20+F20+G20)*H20*I20*(1+J20)*(1+K20)` |
| `N20` | `=L20*M20` |
| `L21` | `=D21*(E21+F21+G21)*H21*I21*(1+J21)*(1+K21)` |
| `N21` | `=L21*M21` |
| `L22` | `=D22*(E22+F22+G22)*H22*I22*(1+J22)*(1+K22)` |
| `N22` | `=L22*M22` |
| `L23` | `=D23*(E23+F23+G23)*H23*I23*(1+J23)*(1+K23)` |
| `N23` | `=L23*M23` |
| `L24` | `=D24*(E24+F24+G24)*H24*I24*(1+J24)*(1+K24)` |
| `N24` | `=L24*M24` |
| `L25` | `=D25*(E25+F25+G25)*H25*I25*(1+J25)*(1+K25)` |
| `N25` | `=L25*M25` |
| `L26` | `=D26*(E26+F26+G26)*H26*I26*(1+J26)*(1+K26)` |
| `N26` | `=L26*M26` |
| `L27` | `=D27*(E27+F27+G27)*H27*I27*(1+J27)*(1+K27)` |
| `N27` | `=L27*M27` |
| `L28` | `=D28*(E28+F28+G28)*H28*I28*(1+J28)*(1+K28)` |
| `N28` | `=L28*M28` |
| `L29` | `=D29*(E29+F29+G29)*H29*I29*(1+J29)*(1+K29)` |
| `N29` | `=L29*M29` |
| `L30` | `=D30*(E30+F30+G30)*H30*I30*(1+J30)*(1+K30)` |
| `N30` | `=L30*M30` |
| `L31` | `=D31*(E31+F31+G31)*H31*I31*(1+J31)*(1+K31)` |
| `N31` | `=L31*M31` |
| `L32` | `=D32*(E32+F32+G32)*H32*I32*(1+J32)*(1+K32)` |
| `N32` | `=L32*M32` |
| `L33` | `=D33*(E33+F33+G33)*H33*I33*(1+J33)*(1+K33)` |
| `N33` | `=L33*M33` |
| `L34` | `=D34*(E34+F34+G34)*H34*I34*(1+J34)*(1+K34)` |
| `N34` | `=L34*M34` |
| `L35` | `=D35*(E35+F35+G35)*H35*I35*(1+J35)*(1+K35)` |
| `N35` | `=L35*M35` |
| `L36` | `=D36*(E36+F36+G36)*H36*I36*(1+J36)*(1+K36)` |
| `N36` | `=L36*M36` |
| `L37` | `=D37*(E37+F37+G37)*H37*I37*(1+J37)*(1+K37)` |
| `N37` | `=L37*M37` |
| `L38` | `=D38*(E38+F38+G38)*H38*I38*(1+J38)*(1+K38)` |
| `N38` | `=L38*M38` |
| `L39` | `=D39*(E39+F39+G39)*H39*I39*(1+J39)*(1+K39)` |
| `N39` | `=L39*M39` |
| `L40` | `=D40*(E40+F40+G40)*H40*I40*(1+J40)*(1+K40)` |
| `N40` | `=L40*M40` |
| `L41` | `=D41*(E41+F41+G41)*H41*I41*(1+J41)*(1+K41)` |
| `N41` | `=L41*M41` |
| `L42` | `=D42*(E42+F42+G42)*H42*I42*(1+J42)*(1+K42)` |
| `N42` | `=L42*M42` |
| `L43` | `=D43*(E43+F43+G43)*H43*I43*(1+J43)*(1+K43)` |
| `N43` | `=L43*M43` |
| `L44` | `=D44*(E44+F44+G44)*H44*I44*(1+J44)*(1+K44)` |
| `N44` | `=L44*M44` |
| `L45` | `=D45*(E45+F45+G45)*H45*I45*(1+J45)*(1+K45)` |
| `N45` | `=L45*M45` |
| `L46` | `=D46*(E46+F46+G46)*H46*I46*(1+J46)*(1+K46)` |
| `N46` | `=L46*M46` |
| `L47` | `=D47*(E47+F47+G47)*H47*I47*(1+J47)*(1+K47)` |
| `N47` | `=L47*M47` |
| `L48` | `=D48*(E48+F48+G48)*H48*I48*(1+J48)*(1+K48)` |
| `N48` | `=L48*M48` |
| `L49` | `=D49*(E49+F49+G49)*H49*I49*(1+J49)*(1+K49)` |
| `N49` | `=L49*M49` |
| `L50` | `=D50*(E50+F50+G50)*H50*I50*(1+J50)*(1+K50)` |
| `N50` | `=L50*M50` |
| `L51` | `=D51*(E51+F51+G51)*H51*I51*(1+J51)*(1+K51)` |
| `N51` | `=L51*M51` |
| `L52` | `=D52*(E52+F52+G52)*H52*I52*(1+J52)*(1+K52)` |
| `N52` | `=L52*M52` |
| `L53` | `=D53*(E53+F53+G53)*H53*I53*(1+J53)*(1+K53)` |
| `N53` | `=L53*M53` |
| `L54` | `=D54*(E54+F54+G54)*H54*I54*(1+J54)*(1+K54)` |
| `N54` | `=L54*M54` |
| `L55` | `=D55*(E55+F55+G55)*H55*I55*(1+J55)*(1+K55)` |
| `N55` | `=L55*M55` |
| `L56` | `=D56*(E56+F56+G56)*H56*I56*(1+J56)*(1+K56)` |
| `N56` | `=L56*M56` |
| `L57` | `=D57*(E57+F57+G57)*H57*I57*(1+J57)*(1+K57)` |
| `N57` | `=L57*M57` |
| `L58` | `=D58*(E58+F58+G58)*H58*I58*(1+J58)*(1+K58)` |
| `N58` | `=L58*M58` |
| `L59` | `=D59*(E59+F59+G59)*H59*I59*(1+J59)*(1+K59)` |
| `N59` | `=L59*M59` |
| `L60` | `=D60*(E60+F60+G60)*H60*I60*(1+J60)*(1+K60)` |
| `N60` | `=L60*M60` |
| `L61` | `=D61*(E61+F61+G61)*H61*I61*(1+J61)*(1+K61)` |
| `N61` | `=L61*M61` |
| `L62` | `=D62*(E62+F62+G62)*H62*I62*(1+J62)*(1+K62)` |
| `N62` | `=L62*M62` |
| `L63` | `=D63*(E63+F63+G63)*H63*I63*(1+J63)*(1+K63)` |
| `N63` | `=L63*M63` |
| `L64` | `=D64*(E64+F64+G64)*H64*I64*(1+J64)*(1+K64)` |
| `N64` | `=L64*M64` |
| `L65` | `=D65*(E65+F65+G65)*H65*I65*(1+J65)*(1+K65)` |
| `N65` | `=L65*M65` |
| `L66` | `=D66*(E66+F66+G66)*H66*I66*(1+J66)*(1+K66)` |
| `N66` | `=L66*M66` |
| `L67` | `=D67*(E67+F67+G67)*H67*I67*(1+J67)*(1+K67)` |
| `N67` | `=L67*M67` |
| `L68` | `=D68*(E68+F68+G68)*H68*I68*(1+J68)*(1+K68)` |
| `N68` | `=L68*M68` |
| `L69` | `=D69*(E69+F69+G69)*H69*I69*(1+J69)*(1+K69)` |
| `N69` | `=L69*M69` |
| `L70` | `=D70*(E70+F70+G70)*H70*I70*(1+J70)*(1+K70)` |
| `N70` | `=L70*M70` |
| `L71` | `=D71*(E71+F71+G71)*H71*I71*(1+J71)*(1+K71)` |
| `N71` | `=L71*M71` |
| `L72` | `=D72*(E72+F72+G72)*H72*I72*(1+J72)*(1+K72)` |
| `N72` | `=L72*M72` |
| `L73` | `=D73*(E73+F73+G73)*H73*I73*(1+J73)*(1+K73)` |
| `N73` | `=L73*M73` |
| `L74` | `=D74*(E74+F74+G74)*H74*I74*(1+J74)*(1+K74)` |
| `N74` | `=L74*M74` |
| `L75` | `=D75*(E75+F75+G75)*H75*I75*(1+J75)*(1+K75)` |
| `N75` | `=L75*M75` |
| `L76` | `=D76*(E76+F76+G76)*H76*I76*(1+J76)*(1+K76)` |
| `N76` | `=L76*M76` |
| `L77` | `=D77*(E77+F77+G77)*H77*I77*(1+J77)*(1+K77)` |
| `N77` | `=L77*M77` |
| `L78` | `=D78*(E78+F78+G78)*H78*I78*(1+J78)*(1+K78)` |
| `N78` | `=L78*M78` |
| `L79` | `=D79*(E79+F79+G79)*H79*I79*(1+J79)*(1+K79)` |
| `N79` | `=L79*M79` |
| `L80` | `=D80*(E80+F80+G80)*H80*I80*(1+J80)*(1+K80)` |
| `N80` | `=L80*M80` |
| `L81` | `=D81*(E81+F81+G81)*H81*I81*(1+J81)*(1+K81)` |
| `N81` | `=L81*M81` |
| `L82` | `=D82*(E82+F82+G82)*H82*I82*(1+J82)*(1+K82)` |
| `N82` | `=L82*M82` |
| `L83` | `=D83*(E83+F83+G83)*H83*I83*(1+J83)*(1+K83)` |
| `N83` | `=L83*M83` |
| `L84` | `=D84*(E84+F84+G84)*H84*I84*(1+J84)*(1+K84)` |
| `N84` | `=L84*M84` |
| `L85` | `=D85*(E85+F85+G85)*H85*I85*(1+J85)*(1+K85)` |
| `N85` | `=L85*M85` |
| `L86` | `=D86*(E86+F86+G86)*H86*I86*(1+J86)*(1+K86)` |
| `N86` | `=L86*M86` |
| `L87` | `=D87*(E87+F87+G87)*H87*I87*(1+J87)*(1+K87)` |
| `N87` | `=L87*M87` |
| `L88` | `=D88*(E88+F88+G88)*H88*I88*(1+J88)*(1+K88)` |
| `N88` | `=L88*M88` |
| `L89` | `=D89*(E89+F89+G89)*H89*I89*(1+J89)*(1+K89)` |
| `N89` | `=L89*M89` |
| `L90` | `=D90*(E90+F90+G90)*H90*I90*(1+J90)*(1+K90)` |
| `N90` | `=L90*M90` |
| `L91` | `=D91*(E91+F91+G91)*H91*I91*(1+J91)*(1+K91)` |
| `N91` | `=L91*M91` |
| `L92` | `=D92*(E92+F92+G92)*H92*I92*(1+J92)*(1+K92)` |
| `N92` | `=L92*M92` |
| `L93` | `=D93*(E93+F93+G93)*H93*I93*(1+J93)*(1+K93)` |
| `N93` | `=L93*M93` |
| `L94` | `=D94*(E94+F94+G94)*H94*I94*(1+J94)*(1+K94)` |
| `N94` | `=L94*M94` |
| `L95` | `=D95*(E95+F95+G95)*H95*I95*(1+J95)*(1+K95)` |
| `N95` | `=L95*M95` |

### Sheet: `Detail Non-Labour`
Formula count: **278**

| Cell | Formula |
|---|---|
| `I5` | `=D5*F5*H5` |
| `K5` | `=I5*J5` |
| `I6` | `=D6*F6*H6` |
| `K6` | `=I6*J6` |
| `I7` | `=D7*F7*H7` |
| `K7` | `=I7*J7` |
| `I8` | `=D8*F8*H8` |
| `K8` | `=I8*J8` |
| `I9` | `=D9*F9*H9` |
| `K9` | `=I9*J9` |
| `I10` | `=D10*F10*H10` |
| `K10` | `=I10*J10` |
| `I11` | `=D11*F11*H11` |
| `K11` | `=I11*J11` |
| `I12` | `=D12*F12*H12` |
| `K12` | `=I12*J12` |
| `I13` | `=D13*F13*H13` |
| `K13` | `=I13*J13` |
| `I14` | `=D14*F14*H14` |
| `K14` | `=I14*J14` |
| `I15` | `=D15*F15*H15` |
| `K15` | `=I15*J15` |
| `I16` | `=D16*F16*H16` |
| `K16` | `=I16*J16` |
| `I17` | `=D17*F17*H17` |
| `K17` | `=I17*J17` |
| `I18` | `=D18*F18*H18` |
| `K18` | `=I18*J18` |
| `I19` | `=D19*F19*H19` |
| `K19` | `=I19*J19` |
| `I20` | `=D20*F20*H20` |
| `K20` | `=I20*J20` |
| `I21` | `=D21*F21*H21` |
| `K21` | `=I21*J21` |
| `I22` | `=D22*F22*H22` |
| `K22` | `=I22*J22` |
| `I23` | `=D23*F23*H23` |
| `K23` | `=I23*J23` |
| `I24` | `=D24*F24*H24` |
| `K24` | `=I24*J24` |
| `I25` | `=D25*F25*H25` |
| `K25` | `=I25*J25` |
| `I26` | `=D26*F26*H26` |
| `K26` | `=I26*J26` |
| `I27` | `=D27*F27*H27` |
| `K27` | `=I27*J27` |
| `I28` | `=D28*F28*H28` |
| `K28` | `=I28*J28` |
| `I29` | `=D29*F29*H29` |
| `K29` | `=I29*J29` |
| `I30` | `=D30*F30*H30` |
| `K30` | `=I30*J30` |
| `I31` | `=D31*F31*H31` |
| `K31` | `=I31*J31` |
| `I32` | `=D32*F32*H32` |
| `K32` | `=I32*J32` |
| `I33` | `=D33*F33*H33` |
| `K33` | `=I33*J33` |
| `I34` | `=D34*F34*H34` |
| `K34` | `=I34*J34` |
| `I35` | `=D35*F35*H35` |
| `K35` | `=I35*J35` |
| `I36` | `=D36*F36*H36` |
| `K36` | `=I36*J36` |
| `I37` | `=D37*F37*H37` |
| `K37` | `=I37*J37` |
| `I38` | `=D38*F38*H38` |
| `K38` | `=I38*J38` |
| `I39` | `=D39*F39*H39` |
| `K39` | `=I39*J39` |
| `I40` | `=D40*F40*H40` |
| `K40` | `=I40*J40` |
| `I41` | `=D41*F41*H41` |
| `K41` | `=I41*J41` |
| `I42` | `=D42*F42*H42` |
| `K42` | `=I42*J42` |
| `I43` | `=D43*F43*H43` |
| `K43` | `=I43*J43` |
| `I44` | `=D44*F44*H44` |
| `K44` | `=I44*J44` |
| `I45` | `=D45*F45*H45` |
| `K45` | `=I45*J45` |
| `I46` | `=D46*F46*H46` |
| `K46` | `=I46*J46` |
| `I47` | `=D47*F47*H47` |
| `K47` | `=I47*J47` |
| `I48` | `=D48*F48*H48` |
| `K48` | `=I48*J48` |
| `I49` | `=D49*F49*H49` |
| `K49` | `=I49*J49` |
| `I50` | `=D50*F50*H50` |
| `K50` | `=I50*J50` |
| `I51` | `=D51*F51*H51` |
| `K51` | `=I51*J51` |
| `I52` | `=D52*F52*H52` |
| `K52` | `=I52*J52` |
| `I53` | `=D53*F53*H53` |
| `K53` | `=I53*J53` |
| `I54` | `=D54*F54*H54` |
| `K54` | `=I54*J54` |
| `I55` | `=D55*F55*H55` |
| `K55` | `=I55*J55` |
| `I56` | `=D56*F56*H56` |
| `K56` | `=I56*J56` |
| `I57` | `=D57*F57*H57` |
| `K57` | `=I57*J57` |
| `I58` | `=D58*F58*H58` |
| `K58` | `=I58*J58` |
| `I59` | `=D59*F59*H59` |
| `K59` | `=I59*J59` |
| `I60` | `=D60*F60*H60` |
| `K60` | `=I60*J60` |
| `I61` | `=D61*F61*H61` |
| `K61` | `=I61*J61` |
| `I62` | `=D62*F62*H62` |
| `K62` | `=I62*J62` |
| `I63` | `=D63*F63*H63` |
| `K63` | `=I63*J63` |
| `I64` | `=D64*F64*H64` |
| `K64` | `=I64*J64` |
| `I65` | `=D65*F65*H65` |
| `K65` | `=I65*J65` |
| `I66` | `=D66*F66*H66` |
| `K66` | `=I66*J66` |
| `I67` | `=D67*F67*H67` |
| `K67` | `=I67*J67` |
| `I68` | `=D68*F68*H68` |
| `K68` | `=I68*J68` |
| `I69` | `=D69*F69*H69` |
| `K69` | `=I69*J69` |
| `I70` | `=D70*F70*H70` |
| `K70` | `=I70*J70` |
| `I71` | `=D71*F71*H71` |
| `K71` | `=I71*J71` |
| `I72` | `=D72*F72*H72` |
| `K72` | `=I72*J72` |
| `I73` | `=D73*F73*H73` |
| `K73` | `=I73*J73` |
| `I74` | `=D74*F74*H74` |
| `K74` | `=I74*J74` |
| `I75` | `=D75*F75*H75` |
| `K75` | `=I75*J75` |
| `I76` | `=D76*F76*H76` |
| `K76` | `=I76*J76` |
| `I77` | `=D77*F77*H77` |
| `K77` | `=I77*J77` |
| `I78` | `=D78*F78*H78` |
| `K78` | `=I78*J78` |
| `I79` | `=D79*F79*H79` |
| `K79` | `=I79*J79` |
| `I80` | `=D80*F80*H80` |
| `K80` | `=I80*J80` |
| `I81` | `=D81*F81*H81` |
| `K81` | `=I81*J81` |
| `I82` | `=D82*F82*H82` |
| `K82` | `=I82*J82` |
| `I83` | `=D83*F83*H83` |
| `K83` | `=I83*J83` |
| `I84` | `=D84*F84*H84` |
| `K84` | `=I84*J84` |
| `I85` | `=D85*F85*H85` |
| `K85` | `=I85*J85` |
| `I86` | `=D86*F86*H86` |
| `K86` | `=I86*J86` |
| `I87` | `=D87*F87*H87` |
| `K87` | `=I87*J87` |
| `I88` | `=D88*F88*H88` |
| `K88` | `=I88*J88` |
| `I89` | `=D89*F89*H89` |
| `K89` | `=I89*J89` |
| `I90` | `=D90*F90*H90` |
| `K90` | `=I90*J90` |
| `I91` | `=D91*F91*H91` |
| `K91` | `=I91*J91` |
| `I92` | `=D92*F92*H92` |
| `K92` | `=I92*J92` |
| `I93` | `=D93*F93*H93` |
| `K93` | `=I93*J93` |
| `I94` | `=D94*F94*H94` |
| `K94` | `=I94*J94` |
| `I95` | `=D95*F95*H95` |
| `K95` | `=I95*J95` |
| `I96` | `=D96*F96*H96` |
| `K96` | `=I96*J96` |
| `I97` | `=D97*F97*H97` |
| `K97` | `=I97*J97` |
| `I98` | `=D98*F98*H98` |
| `K98` | `=I98*J98` |
| `I99` | `=D99*F99*H99` |
| `K99` | `=I99*J99` |
| `I100` | `=D100*F100*H100` |
| `K100` | `=I100*J100` |
| `I101` | `=D101*F101*H101` |
| `K101` | `=I101*J101` |
| `I102` | `=D102*F102*H102` |
| `K102` | `=I102*J102` |
| `I103` | `=D103*F103*H103` |
| `K103` | `=I103*J103` |
| `I104` | `=D104*F104*H104` |
| `K104` | `=I104*J104` |
| `I105` | `=D105*F105*H105` |
| `K105` | `=I105*J105` |
| `I106` | `=D106*F106*H106` |
| `K106` | `=I106*J106` |
| `I107` | `=D107*F107*H107` |
| `K107` | `=I107*J107` |
| `I108` | `=D108*F108*H108` |
| `K108` | `=I108*J108` |
| `I109` | `=D109*F109*H109` |
| `K109` | `=I109*J109` |
| `I110` | `=D110*F110*H110` |
| `K110` | `=I110*J110` |
| `I111` | `=D111*F111*H111` |
| `K111` | `=I111*J111` |
| `I112` | `=D112*F112*H112` |
| `K112` | `=I112*J112` |
| `I113` | `=D113*F113*H113` |
| `K113` | `=I113*J113` |
| `I114` | `=D114*F114*H114` |
| `K114` | `=I114*J114` |
| `I115` | `=D115*F115*H115` |
| `K115` | `=I115*J115` |
| `I116` | `=D116*F116*H116` |
| `K116` | `=I116*J116` |
| `I117` | `=D117*F117*H117` |
| `K117` | `=I117*J117` |
| `I118` | `=D118*F118*H118` |
| `K118` | `=I118*J118` |
| `I119` | `=D119*F119*H119` |
| `K119` | `=I119*J119` |
| `I120` | `=D120*F120*H120` |
| `K120` | `=I120*J120` |
| `I121` | `=D121*F121*H121` |
| `K121` | `=I121*J121` |
| `I122` | `=D122*F122*H122` |
| `K122` | `=I122*J122` |
| `I123` | `=D123*F123*H123` |
| `K123` | `=I123*J123` |
| `I124` | `=D124*F124*H124` |
| `K124` | `=I124*J124` |
| `I125` | `=D125*F125*H125` |
| `K125` | `=I125*J125` |
| `I126` | `=D126*F126*H126` |
| `K126` | `=I126*J126` |
| `I127` | `=D127*F127*H127` |
| `K127` | `=I127*J127` |
| `I128` | `=D128*F128*H128` |
| `K128` | `=I128*J128` |
| `I129` | `=D129*F129*H129` |
| `K129` | `=I129*J129` |
| `I130` | `=D130*F130*H130` |
| `K130` | `=I130*J130` |
| `I131` | `=D131*F131*H131` |
| `K131` | `=I131*J131` |
| `I132` | `=D132*F132*H132` |
| `K132` | `=I132*J132` |
| `I133` | `=D133*F133*H133` |
| `K133` | `=I133*J133` |
| `I134` | `=D134*F134*H134` |
| `K134` | `=I134*J134` |
| `I135` | `=D135*F135*H135` |
| `K135` | `=I135*J135` |
| `I136` | `=D136*F136*H136` |
| `K136` | `=I136*J136` |
| `I137` | `=D137*F137*H137` |
| `K137` | `=I137*J137` |
| `I138` | `=D138*F138*H138` |
| `K138` | `=I138*J138` |
| `I139` | `=D139*F139*H139` |
| `K139` | `=I139*J139` |
| `I140` | `=D140*F140*H140` |
| `K140` | `=I140*J140` |
| `I141` | `=D141*F141*H141` |
| `K141` | `=I141*J141` |
| `I142` | `=D142*F142*H142` |
| `K142` | `=I142*J142` |
| `I143` | `=D143*F143*H143` |
| `K143` | `=I143*J143` |

### Sheet: `Lean Budget`
Formula count: **72**

| Cell | Formula |
|---|---|
| `C5` | `=SUMIF('Detail Crew'!$A:$A,A5,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A5,'Detail Non-Labour'!$K:$K)` |
| `F5` | `=C5*E5` |
| `C6` | `=SUMIF('Detail Crew'!$A:$A,A6,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A6,'Detail Non-Labour'!$K:$K)` |
| `F6` | `=C6*E6` |
| `C7` | `=SUMIF('Detail Crew'!$A:$A,A7,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A7,'Detail Non-Labour'!$K:$K)` |
| `F7` | `=C7*E7` |
| `C8` | `=SUMIF('Detail Crew'!$A:$A,A8,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A8,'Detail Non-Labour'!$K:$K)` |
| `F8` | `=C8*E8` |
| `C9` | `=SUMIF('Detail Crew'!$A:$A,A9,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A9,'Detail Non-Labour'!$K:$K)` |
| `F9` | `=C9*E9` |
| `C10` | `=SUMIF('Detail Crew'!$A:$A,A10,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A10,'Detail Non-Labour'!$K:$K)` |
| `F10` | `=C10*E10` |
| `C11` | `=SUMIF('Detail Crew'!$A:$A,A11,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A11,'Detail Non-Labour'!$K:$K)` |
| `F11` | `=C11*E11` |
| `C12` | `=SUMIF('Detail Crew'!$A:$A,A12,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A12,'Detail Non-Labour'!$K:$K)` |
| `F12` | `=C12*E12` |
| `C13` | `=SUMIF('Detail Crew'!$A:$A,A13,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A13,'Detail Non-Labour'!$K:$K)` |
| `F13` | `=C13*E13` |
| `C14` | `=SUMIF('Detail Crew'!$A:$A,A14,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A14,'Detail Non-Labour'!$K:$K)` |
| `F14` | `=C14*E14` |
| `C15` | `=SUMIF('Detail Crew'!$A:$A,A15,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A15,'Detail Non-Labour'!$K:$K)` |
| `F15` | `=C15*E15` |
| `C16` | `=SUMIF('Detail Crew'!$A:$A,A16,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A16,'Detail Non-Labour'!$K:$K)` |
| `F16` | `=C16*E16` |
| `C17` | `=SUMIF('Detail Crew'!$A:$A,A17,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A17,'Detail Non-Labour'!$K:$K)` |
| `F17` | `=C17*E17` |
| `C18` | `=SUMIF('Detail Crew'!$A:$A,A18,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A18,'Detail Non-Labour'!$K:$K)` |
| `F18` | `=C18*E18` |
| `C19` | `=SUMIF('Detail Crew'!$A:$A,A19,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A19,'Detail Non-Labour'!$K:$K)` |
| `F19` | `=C19*E19` |
| `C20` | `=SUMIF('Detail Crew'!$A:$A,A20,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A20,'Detail Non-Labour'!$K:$K)` |
| `F20` | `=C20*E20` |
| `C21` | `=SUMIF('Detail Crew'!$A:$A,A21,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A21,'Detail Non-Labour'!$K:$K)` |
| `F21` | `=C21*E21` |
| `C22` | `=SUMIF('Detail Crew'!$A:$A,A22,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A22,'Detail Non-Labour'!$K:$K)` |
| `F22` | `=C22*E22` |
| `C23` | `=SUMIF('Detail Crew'!$A:$A,A23,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A23,'Detail Non-Labour'!$K:$K)` |
| `F23` | `=C23*E23` |
| `C24` | `=SUMIF('Detail Crew'!$A:$A,A24,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A24,'Detail Non-Labour'!$K:$K)` |
| `F24` | `=C24*E24` |
| `C25` | `=SUMIF('Detail Crew'!$A:$A,A25,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A25,'Detail Non-Labour'!$K:$K)` |
| `F25` | `=C25*E25` |
| `C26` | `=SUMIF('Detail Crew'!$A:$A,A26,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A26,'Detail Non-Labour'!$K:$K)` |
| `F26` | `=C26*E26` |
| `C27` | `=SUMIF('Detail Crew'!$A:$A,A27,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A27,'Detail Non-Labour'!$K:$K)` |
| `F27` | `=C27*E27` |
| `C28` | `=SUMIF('Detail Crew'!$A:$A,A28,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A28,'Detail Non-Labour'!$K:$K)` |
| `F28` | `=C28*E28` |
| `C29` | `=SUMIF('Detail Crew'!$A:$A,A29,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A29,'Detail Non-Labour'!$K:$K)` |
| `F29` | `=C29*E29` |
| `C30` | `=SUMIF('Detail Crew'!$A:$A,A30,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A30,'Detail Non-Labour'!$K:$K)` |
| `F30` | `=C30*E30` |
| `C31` | `=SUMIF('Detail Crew'!$A:$A,A31,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A31,'Detail Non-Labour'!$K:$K)` |
| `F31` | `=C31*E31` |
| `C32` | `=SUMIF('Detail Crew'!$A:$A,A32,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A32,'Detail Non-Labour'!$K:$K)` |
| `F32` | `=C32*E32` |
| `C33` | `=SUMIF('Detail Crew'!$A:$A,A33,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A33,'Detail Non-Labour'!$K:$K)` |
| `F33` | `=C33*E33` |
| `C34` | `=SUMIF('Detail Crew'!$A:$A,A34,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A34,'Detail Non-Labour'!$K:$K)` |
| `F34` | `=C34*E34` |
| `C35` | `=SUMIF('Detail Crew'!$A:$A,A35,'Detail Crew'!$N:$N)+SUMIF('Detail Non-Labour'!$A:$A,A35,'Detail Non-Labour'!$K:$K)` |
| `F35` | `=C35*E35` |
| `C36` | `=MAX(10000,SUM(C5:C28)*0.01)` |
| `F36` | `=C36*E36` |
| `C38` | `=SUM(C8:C28)*0.05` |
| `F38` | `=C38*E38` |
| `C39` | `=(SUM(C8:C28)+SUM(C29:C33))*0.075` |
| `C41` | `=SUM(C5:C39)` |
| `C42` | `=SUM(F5:F38)` |
| `C43` | `=IF(C42<1000000,0,MIN(20000000,0.30*1000000+0.25*MAX(0,C42-1000000)))` |
| `C44` | `=C41-C43` |
| `C45` | `=C44*1.14` |

### Sheet: `Assumptions & Risks`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Sources`
Formula count: **0**

_No formulas in this sheet._


## `10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1.xlsx`

Total formulas: **1979**

### Sheet: `Cover`
Formula count: **2**

| Cell | Formula |
|---|---|
| `B19` | `='Checks'!F23` |
| `H30` | `=COUNTIF('Audit Regression'!G6:G17,"FAIL")` |

### Sheet: `Project Intake`
Formula count: **26**

| Cell | Formula |
|---|---|
| `F5` | `=IF(AND(D5="Yes",OR(C5="",C5=0)),"MISSING","OK")` |
| `F6` | `=IF(AND(D6="Yes",OR(C6="",C6=0)),"MISSING","OK")` |
| `F7` | `=IF(AND(D7="Yes",OR(C7="",C7=0)),"MISSING","OK")` |
| `F8` | `=IF(AND(D8="Yes",OR(C8="",C8=0)),"MISSING","OK")` |
| `C9` | `=SUM('Spend Matrix'!C6:C25)` |
| `F9` | `=IF(AND(D9="Yes",OR(C9="",C9=0)),"MISSING","OK")` |
| `F10` | `=IF(AND(D10="Yes",OR(C10="",C10=0)),"MISSING","OK")` |
| `F11` | `=IF(AND(D11="Yes",OR(C11="",C11=0)),"MISSING","OK")` |
| `F12` | `=IF(AND(D12="Yes",OR(C12="",C12=0)),"MISSING","OK")` |
| `F13` | `=IF(AND(D13="Yes",OR(C13="",C13=0)),"MISSING","OK")` |
| `F14` | `=IF(AND(D14="Yes",OR(C14="",C14=0)),"MISSING","OK")` |
| `F15` | `=IF(AND(D15="Yes",OR(C15="",C15=0)),"MISSING","OK")` |
| `F16` | `=IF(AND(D16="Yes",OR(C16="",C16=0)),"MISSING","OK")` |
| `F17` | `=IF(AND(D17="Yes",OR(C17="",C17=0)),"MISSING","OK")` |
| `F18` | `=IF(AND(D18="Yes",OR(C18="",C18=0)),"MISSING","OK")` |
| `F19` | `=IF(AND(D19="Yes",OR(C19="",C19=0)),"MISSING","OK")` |
| `F20` | `=IF(AND(D20="Yes",OR(C20="",C20=0)),"MISSING","OK")` |
| `F21` | `=IF(AND(D21="Yes",OR(C21="",C21=0)),"MISSING","OK")` |
| `F22` | `=IF(AND(D22="Yes",OR(C22="",C22=0)),"MISSING","OK")` |
| `F23` | `=IF(AND(D23="Yes",OR(C23="",C23=0)),"MISSING","OK")` |
| `F24` | `=IF(AND(D24="Yes",OR(C24="",C24=0)),"MISSING","OK")` |
| `F25` | `=IF(AND(D25="Yes",OR(C25="",C25=0)),"MISSING","OK")` |
| `F26` | `=IF(AND(D26="Yes",OR(C26="",C26=0)),"MISSING","OK")` |
| `F27` | `=IF(AND(D27="Yes",OR(C27="",C27=0)),"MISSING","OK")` |
| `F28` | `=IF(AND(D28="Yes",OR(C28="",C28=0)),"MISSING","OK")` |
| `F29` | `=IF(AND(D29="Yes",OR(C29="",C29=0)),"MISSING","OK")` |

### Sheet: `Spend Matrix`
Formula count: **22**

| Cell | Formula |
|---|---|
| `F6` | `=C6*D6*E6` |
| `F7` | `=C7*D7*E7` |
| `F8` | `=C8*D8*E8` |
| `F9` | `=C9*D9*E9` |
| `F10` | `=C10*D10*E10` |
| `F11` | `=C11*D11*E11` |
| `F12` | `=C12*D12*E12` |
| `F13` | `=C13*D13*E13` |
| `F14` | `=C14*D14*E14` |
| `F15` | `=C15*D15*E15` |
| `F16` | `=C16*D16*E16` |
| `F17` | `=C17*D17*E17` |
| `F18` | `=C18*D18*E18` |
| `F19` | `=C19*D19*E19` |
| `F20` | `=C20*D20*E20` |
| `F21` | `=C21*D21*E21` |
| `F22` | `=C22*D22*E22` |
| `F23` | `=C23*D23*E23` |
| `F24` | `=C24*D24*E24` |
| `F25` | `=C25*D25*E25` |
| `C26` | `=SUM(C6:C25)` |
| `F26` | `=SUM(F6:F25)` |

### Sheet: `Priority Jurisdictions`
Formula count: **82**

| Cell | Formula |
|---|---|
| `D4` | `=COUNTA(A7:A120)` |
| `H7` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A7,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H8` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A8,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H9` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A9,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H10` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A10,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H11` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A11,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H12` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A12,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H13` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A13,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H14` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A14,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H15` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A15,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H16` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A16,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H17` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A17,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H18` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A18,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H19` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A19,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H20` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A20,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H21` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A21,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H22` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A22,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H23` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A23,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H24` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A24,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H25` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A25,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H26` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A26,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H27` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A27,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H28` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A28,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H29` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A29,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H30` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A30,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H31` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A31,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H32` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A32,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H33` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A33,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H34` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A34,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H35` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A35,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H36` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A36,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H37` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A37,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H38` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A38,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H39` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A39,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H40` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A40,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H41` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A41,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H42` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A42,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H43` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A43,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H44` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A44,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H45` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A45,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H46` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A46,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H47` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A47,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H48` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A48,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H49` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A49,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H50` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A50,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H51` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A51,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H52` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A52,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H53` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A53,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H54` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A54,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H55` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A55,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H56` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A56,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H57` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A57,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H58` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A58,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H59` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A59,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H60` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A60,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H61` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A61,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H62` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A62,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H63` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A63,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H64` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A64,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H65` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A65,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H66` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A66,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H67` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A67,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H68` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A68,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H69` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A69,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H70` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A70,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H71` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A71,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H72` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A72,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H73` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A73,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H74` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A74,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H75` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A75,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H76` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A76,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H77` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A77,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H78` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A78,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H79` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A79,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H80` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A80,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H81` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A81,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H82` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A82,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H83` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A83,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H84` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A84,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H85` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A85,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H86` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A86,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |
| `H87` | `=IFERROR(INDEX('Coverage Gaps'!$F$6:$F$86,MATCH(A87,'Coverage Gaps'!$A$6:$A$86,0)),"Research gap")` |

### Sheet: `Incentive Database`
Formula count: **174**

| Cell | Formula |
|---|---|
| `J6` | `=IF(A6="","",MIN(H6+I6,1))` |
| `J7` | `=IF(A7="","",MIN(H7+I7,1))` |
| `J8` | `=IF(A8="","",MIN(H8+I8,1))` |
| `J9` | `=IF(A9="","",MIN(H9+I9,1))` |
| `J10` | `=IF(A10="","",MIN(H10+I10,1))` |
| `J11` | `=IF(A11="","",MIN(H11+I11,1))` |
| `J12` | `=IF(A12="","",MIN(H12+I12,1))` |
| `J13` | `=IF(A13="","",MIN(H13+I13,1))` |
| `J14` | `=IF(A14="","",MIN(H14+I14,1))` |
| `J15` | `=IF(A15="","",MIN(H15+I15,1))` |
| `J16` | `=IF(A16="","",MIN(H16+I16,1))` |
| `J17` | `=IF(A17="","",MIN(H17+I17,1))` |
| `J18` | `=IF(A18="","",MIN(H18+I18,1))` |
| `J19` | `=IF(A19="","",MIN(H19+I19,1))` |
| `J20` | `=IF(A20="","",MIN(H20+I20,1))` |
| `J21` | `=IF(A21="","",MIN(H21+I21,1))` |
| `J22` | `=IF(A22="","",MIN(H22+I22,1))` |
| `J23` | `=IF(A23="","",MIN(H23+I23,1))` |
| `J24` | `=IF(A24="","",MIN(H24+I24,1))` |
| `J25` | `=IF(A25="","",MIN(H25+I25,1))` |
| `J26` | `=IF(A26="","",MIN(H26+I26,1))` |
| `J27` | `=IF(A27="","",MIN(H27+I27,1))` |
| `J28` | `=IF(A28="","",MIN(H28+I28,1))` |
| `J29` | `=IF(A29="","",MIN(H29+I29,1))` |
| `J30` | `=IF(A30="","",MIN(H30+I30,1))` |
| `J31` | `=IF(A31="","",MIN(H31+I31,1))` |
| `J32` | `=IF(A32="","",MIN(H32+I32,1))` |
| `J33` | `=IF(A33="","",MIN(H33+I33,1))` |
| `J34` | `=IF(A34="","",MIN(H34+I34,1))` |
| `J35` | `=IF(A35="","",MIN(H35+I35,1))` |
| `J36` | `=IF(A36="","",MIN(H36+I36,1))` |
| `J37` | `=IF(A37="","",MIN(H37+I37,1))` |
| `J38` | `=IF(A38="","",MIN(H38+I38,1))` |
| `J39` | `=IF(A39="","",MIN(H39+I39,1))` |
| `J40` | `=IF(A40="","",MIN(H40+I40,1))` |
| `J41` | `=IF(A41="","",MIN(H41+I41,1))` |
| `J42` | `=IF(A42="","",MIN(H42+I42,1))` |
| `J43` | `=IF(A43="","",MIN(H43+I43,1))` |
| `J45` | `=IF(A45="","",MIN(H45+I45,1))` |
| `J46` | `=IF(A46="","",MIN(H46+I46,1))` |
| `J47` | `=IF(A47="","",MIN(H47+I47,1))` |
| `J48` | `=IF(A48="","",MIN(H48+I48,1))` |
| `J49` | `=IF(A49="","",MIN(H49+I49,1))` |
| `J50` | `=IF(A50="","",MIN(H50+I50,1))` |
| `J51` | `=IF(A51="","",MIN(H51+I51,1))` |
| `J52` | `=IF(A52="","",MIN(H52+I52,1))` |
| `J53` | `=IF(A53="","",MIN(H53+I53,1))` |
| `J54` | `=IF(A54="","",MIN(H54+I54,1))` |
| `J55` | `=IF(A55="","",MIN(H55+I55,1))` |
| `J56` | `=IF(A56="","",MIN(H56+I56,1))` |
| `J57` | `=IF(A57="","",MIN(H57+I57,1))` |
| `J58` | `=IF(A58="","",MIN(H58+I58,1))` |
| `J59` | `=IF(A59="","",MIN(H59+I59,1))` |
| `J60` | `=IF(A60="","",MIN(H60+I60,1))` |
| `J61` | `=IF(A61="","",MIN(H61+I61,1))` |
| `J62` | `=IF(A62="","",MIN(H62+I62,1))` |
| `J63` | `=IF(A63="","",MIN(H63+I63,1))` |
| `J64` | `=IF(A64="","",MIN(H64+I64,1))` |
| `J65` | `=IF(A65="","",MIN(H65+I65,1))` |
| `J66` | `=IF(A66="","",MIN(H66+I66,1))` |
| `J67` | `=IF(A67="","",MIN(H67+I67,1))` |
| `J68` | `=IF(A68="","",MIN(H68+I68,1))` |
| `J69` | `=IF(A69="","",MIN(H69+I69,1))` |
| `J70` | `=IF(A70="","",MIN(H70+I70,1))` |
| `J71` | `=IF(A71="","",MIN(H71+I71,1))` |
| `J72` | `=IF(A72="","",MIN(H72+I72,1))` |
| `J73` | `=IF(A73="","",MIN(H73+I73,1))` |
| `J74` | `=IF(A74="","",MIN(H74+I74,1))` |
| `J75` | `=IF(A75="","",MIN(H75+I75,1))` |
| `J76` | `=IF(A76="","",MIN(H76+I76,1))` |
| `J77` | `=IF(A77="","",MIN(H77+I77,1))` |
| `J78` | `=IF(A78="","",MIN(H78+I78,1))` |
| `J79` | `=IF(A79="","",MIN(H79+I79,1))` |
| `J80` | `=IF(A80="","",MIN(H80+I80,1))` |
| `J81` | `=IF(A81="","",MIN(H81+I81,1))` |
| `J82` | `=IF(A82="","",MIN(H82+I82,1))` |
| `J83` | `=IF(A83="","",MIN(H83+I83,1))` |
| `J84` | `=IF(A84="","",MIN(H84+I84,1))` |
| `J85` | `=IF(A85="","",MIN(H85+I85,1))` |
| `J86` | `=IF(A86="","",MIN(H86+I86,1))` |
| `J87` | `=IF(A87="","",MIN(H87+I87,1))` |
| `J88` | `=IF(A88="","",MIN(H88+I88,1))` |
| `J89` | `=IF(A89="","",MIN(H89+I89,1))` |
| `J90` | `=IF(A90="","",MIN(H90+I90,1))` |
| `J91` | `=IF(A91="","",MIN(H91+I91,1))` |
| `J92` | `=IF(A92="","",MIN(H92+I92,1))` |
| `J93` | `=IF(A93="","",MIN(H93+I93,1))` |
| `J94` | `=IF(A94="","",MIN(H94+I94,1))` |
| `J95` | `=IF(A95="","",MIN(H95+I95,1))` |
| `J96` | `=IF(A96="","",MIN(H96+I96,1))` |
| `J97` | `=IF(A97="","",MIN(H97+I97,1))` |
| `J98` | `=IF(A98="","",MIN(H98+I98,1))` |
| `J99` | `=IF(A99="","",MIN(H99+I99,1))` |
| `J100` | `=IF(A100="","",MIN(H100+I100,1))` |
| `J101` | `=IF(A101="","",MIN(H101+I101,1))` |
| `J102` | `=IF(A102="","",MIN(H102+I102,1))` |
| `J103` | `=IF(A103="","",MIN(H103+I103,1))` |
| `J104` | `=IF(A104="","",MIN(H104+I104,1))` |
| `J105` | `=IF(A105="","",MIN(H105+I105,1))` |
| `J106` | `=IF(A106="","",MIN(H106+I106,1))` |
| `J107` | `=IF(A107="","",MIN(H107+I107,1))` |
| `J108` | `=IF(A108="","",MIN(H108+I108,1))` |
| `J109` | `=IF(A109="","",MIN(H109+I109,1))` |
| `J110` | `=IF(A110="","",MIN(H110+I110,1))` |
| `J111` | `=IF(A111="","",MIN(H111+I111,1))` |
| `J112` | `=IF(A112="","",MIN(H112+I112,1))` |
| `J113` | `=IF(A113="","",MIN(H113+I113,1))` |
| `J114` | `=IF(A114="","",MIN(H114+I114,1))` |
| `J115` | `=IF(A115="","",MIN(H115+I115,1))` |
| `J116` | `=IF(A116="","",MIN(H116+I116,1))` |
| `J117` | `=IF(A117="","",MIN(H117+I117,1))` |
| `J118` | `=IF(A118="","",MIN(H118+I118,1))` |
| `J119` | `=IF(A119="","",MIN(H119+I119,1))` |
| `J120` | `=IF(A120="","",MIN(H120+I120,1))` |
| `J121` | `=IF(A121="","",MIN(H121+I121,1))` |
| `J122` | `=IF(A122="","",MIN(H122+I122,1))` |
| `J123` | `=IF(A123="","",MIN(H123+I123,1))` |
| `J124` | `=IF(A124="","",MIN(H124+I124,1))` |
| `J125` | `=IF(A125="","",MIN(H125+I125,1))` |
| `J126` | `=IF(A126="","",MIN(H126+I126,1))` |
| `J127` | `=IF(A127="","",MIN(H127+I127,1))` |
| `J128` | `=IF(A128="","",MIN(H128+I128,1))` |
| `J129` | `=IF(A129="","",MIN(H129+I129,1))` |
| `J130` | `=IF(A130="","",MIN(H130+I130,1))` |
| `J131` | `=IF(A131="","",MIN(H131+I131,1))` |
| `J132` | `=IF(A132="","",MIN(H132+I132,1))` |
| `J133` | `=IF(A133="","",MIN(H133+I133,1))` |
| `J134` | `=IF(A134="","",MIN(H134+I134,1))` |
| `J135` | `=IF(A135="","",MIN(H135+I135,1))` |
| `J136` | `=IF(A136="","",MIN(H136+I136,1))` |
| `J137` | `=IF(A137="","",MIN(H137+I137,1))` |
| `J138` | `=IF(A138="","",MIN(H138+I138,1))` |
| `J139` | `=IF(A139="","",MIN(H139+I139,1))` |
| `J140` | `=IF(A140="","",MIN(H140+I140,1))` |
| `J141` | `=IF(A141="","",MIN(H141+I141,1))` |
| `J142` | `=IF(A142="","",MIN(H142+I142,1))` |
| `J143` | `=IF(A143="","",MIN(H143+I143,1))` |
| `J144` | `=IF(A144="","",MIN(H144+I144,1))` |
| `J145` | `=IF(A145="","",MIN(H145+I145,1))` |
| `J146` | `=IF(A146="","",MIN(H146+I146,1))` |
| `J147` | `=IF(A147="","",MIN(H147+I147,1))` |
| `J148` | `=IF(A148="","",MIN(H148+I148,1))` |
| `J149` | `=IF(A149="","",MIN(H149+I149,1))` |
| `J150` | `=IF(A150="","",MIN(H150+I150,1))` |
| `J151` | `=IF(A151="","",MIN(H151+I151,1))` |
| `J152` | `=IF(A152="","",MIN(H152+I152,1))` |
| `J153` | `=IF(A153="","",MIN(H153+I153,1))` |
| `J154` | `=IF(A154="","",MIN(H154+I154,1))` |
| `J155` | `=IF(A155="","",MIN(H155+I155,1))` |
| `J156` | `=IF(A156="","",MIN(H156+I156,1))` |
| `J157` | `=IF(A157="","",MIN(H157+I157,1))` |
| `J158` | `=IF(A158="","",MIN(H158+I158,1))` |
| `J159` | `=IF(A159="","",MIN(H159+I159,1))` |
| `J160` | `=IF(A160="","",MIN(H160+I160,1))` |
| `J161` | `=IF(A161="","",MIN(H161+I161,1))` |
| `J162` | `=IF(A162="","",MIN(H162+I162,1))` |
| `J163` | `=IF(A163="","",MIN(H163+I163,1))` |
| `J164` | `=IF(A164="","",MIN(H164+I164,1))` |
| `J165` | `=IF(A165="","",MIN(H165+I165,1))` |
| `J166` | `=IF(A166="","",MIN(H166+I166,1))` |
| `J167` | `=IF(A167="","",MIN(H167+I167,1))` |
| `J168` | `=IF(A168="","",MIN(H168+I168,1))` |
| `J169` | `=IF(A169="","",MIN(H169+I169,1))` |
| `J170` | `=IF(A170="","",MIN(H170+I170,1))` |
| `J171` | `=IF(A171="","",MIN(H171+I171,1))` |
| `J172` | `=IF(A172="","",MIN(H172+I172,1))` |
| `J173` | `=IF(A173="","",MIN(H173+I173,1))` |
| `J174` | `=IF(A174="","",MIN(H174+I174,1))` |
| `J175` | `=IF(A175="","",MIN(H175+I175,1))` |
| `J176` | `=IF(A176="","",MIN(H176+I176,1))` |
| `J177` | `=IF(A177="","",MIN(H177+I177,1))` |
| `J178` | `=IF(A178="","",MIN(H178+I178,1))` |
| `J179` | `=IF(A179="","",MIN(H179+I179,1))` |
| `J180` | `=IF(A180="","",MIN(H180+I180,1))` |

### Sheet: `Scenario Engine`
Formula count: **680**

| Cell | Formula |
|---|---|
| `V6` | `=IF($C6="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W6` | `=IF(OR($C6="",$E6="",$V6=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V6,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E6,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X6` | `=IF(OR($F6="",$W6=0),0,$F6/$W6)` |
| `Y6` | `=IF($C6="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI6` | `=IF($C6="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ6` | `=IF($C6="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK6` | `=IF($C6="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL6` | `=IF($C6="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM6` | `=IF($C6="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN6` | `=IF($C6="","",IF(OR($AL6="Closed",$AL6="Test only",COUNTIF($H6:$N6,"No")>0,AND($AK6<>"",IF($AK6="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK6="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK6="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ6<>"",COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,$AJ6)=0),AND($AF6>0,$X6<$AF6),AND($AG6>0,$G6/$W6<$AG6),AND($AH6>0,$G6/$W6>$AH6),AND($T6>0,$R6>0)),"FAIL",IF(OR(COUNTIF($H6:$N6,"Unknown")>0,COUNTBLANK($H6:$N6)>0,COUNTBLANK($Q6:$U6)>0,$AL6<>"Active",OR($AM6="Low",$AM6="Unverified"),AND($Y6="Manual award",$O6="")),"PRELIMINARY","PASS")))` |
| `AO6` | `=IF($C6="","",IF($AL6="Closed","Programme unavailable",IF(COUNTIF($H6:$N6,"No")>0,"Eligibility requirement not met",IF(AND($AK6<>"",IF($AK6="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK6="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK6="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ6<>"",COUNTIFS($A$6:$A$25,$A6,$C$6:$C$25,$AJ6)=0),"Required parent programme missing",IF(AND($AF6>0,$X6<$AF6),"Minimum programme spend not met",IF(AND($AG6>0,$G6/$W6<$AG6),"Minimum project cost not met",IF(AND($AH6>0,$G6/$W6>$AH6),"Maximum project cost exceeded",IF(AND($T6>0,$R6>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H6:$N6,"Unknown")>0,COUNTBLANK($H6:$N6)>0,COUNTBLANK($Q6:$U6)>0,$AL6<>"Active",OR($AM6="Low",$AM6="Unverified"),AND($Y6="Manual award",$O6="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP6` | `=IF(OR($C6="",$AN6="FAIL"),0,IF($AE6>0,MIN(IF($Y6="Manual award",IF($O6="",0,$O6),IF($Y6="Tiered",MIN(MIN($X6,IF($AC6>0,$AC6,$X6),IF($AD6>0,($G6/$W6)*$AD6,$X6)),$AA6)*$Z6+MAX(MIN($X6,IF($AC6>0,$AC6,$X6),IF($AD6>0,($G6/$W6)*$AD6,$X6))-$AA6,0)*$AB6,MIN($X6,IF($AC6>0,$AC6,$X6),IF($AD6>0,($G6/$W6)*$AD6,$X6))*$Z6)),$AE6),IF($Y6="Manual award",IF($O6="",0,$O6),IF($Y6="Tiered",MIN(MIN($X6,IF($AC6>0,$AC6,$X6),IF($AD6>0,($G6/$W6)*$AD6,$X6)),$AA6)*$Z6+MAX(MIN($X6,IF($AC6>0,$AC6,$X6),IF($AD6>0,($G6/$W6)*$AD6,$X6))-$AA6,0)*$AB6,MIN($X6,IF($AC6>0,$AC6,$X6),IF($AD6>0,($G6/$W6)*$AD6,$X6))*$Z6))))` |
| `AQ6` | `=$AP6*$W6` |
| `AR6` | `=IF($C6="",0,$AP6*$AI6+($AP6*(1-$AI6))*$T6)` |
| `AS6` | `=IF($C6="",0,($AP6*(1-$AI6)*(1-$T6)*$R6*$S6*$Q6/12)+$U6+($AP6*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT6` | `=IF(OR($C6="",COUNTBLANK($Q6:$U6)>0),"",$AP6-$AR6-$AS6)` |
| `AU6` | `=IF(OR($C6="",COUNTBLANK($Q6:$U6)>0),"",((($AP6*(1-$AI6)*(1-$T6)*$R6)-(($AP6*(1-$AI6)*(1-$T6)*$R6*$S6*$Q6/12)+$U6+($AP6*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),0))))*$W6)+(($AP6*(1-$AI6)*(1-$T6)*(1-$R6)*$W6)/((1+'FX & Financing'!$J$6)^($Q6/12))))` |
| `AV6` | `=IF($C6="",0,$P6)` |
| `AW6` | `=IF($AU6="","",$AU6-$AV6)` |
| `AX6` | `=IFERROR($AW6/$F6,0)` |
| `AY6` | `=IF($C6="",0,IF($AX6>='FX & Financing'!$J$7,5,IF($AX6>='FX & Financing'!$J$8,4,IF($AX6>='FX & Financing'!$J$9,3,IF($AX6>0,2,1)))))` |
| `AZ6` | `=IF($C6="",0,MAX(1,IF($AM6="High",5,IF($AM6="Medium",3,IF($AM6="Low",2,1)))-IF($AN6="PRELIMINARY",1,IF($AN6="FAIL",4,0))))` |
| `BA6` | `=IF($C6="",0,$AY6*'FX & Financing'!$J$10+$AZ6*(1-'FX & Financing'!$J$10))` |
| `BB6` | `=IF($C6="","",IF($AN6="FAIL","Red",IF($AN6="PRELIMINARY","Amber",IF($BA6>=4,"Green",IF($BA6>=3.25,"Amber","Red")))))` |
| `BC6` | `=IF($C6="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C6,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V7` | `=IF($C7="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W7` | `=IF(OR($C7="",$E7="",$V7=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V7,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E7,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X7` | `=IF(OR($F7="",$W7=0),0,$F7/$W7)` |
| `Y7` | `=IF($C7="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI7` | `=IF($C7="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ7` | `=IF($C7="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK7` | `=IF($C7="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL7` | `=IF($C7="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM7` | `=IF($C7="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN7` | `=IF($C7="","",IF(OR($AL7="Closed",$AL7="Test only",COUNTIF($H7:$N7,"No")>0,AND($AK7<>"",IF($AK7="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK7="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK7="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ7<>"",COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,$AJ7)=0),AND($AF7>0,$X7<$AF7),AND($AG7>0,$G7/$W7<$AG7),AND($AH7>0,$G7/$W7>$AH7),AND($T7>0,$R7>0)),"FAIL",IF(OR(COUNTIF($H7:$N7,"Unknown")>0,COUNTBLANK($H7:$N7)>0,COUNTBLANK($Q7:$U7)>0,$AL7<>"Active",OR($AM7="Low",$AM7="Unverified"),AND($Y7="Manual award",$O7="")),"PRELIMINARY","PASS")))` |
| `AO7` | `=IF($C7="","",IF($AL7="Closed","Programme unavailable",IF(COUNTIF($H7:$N7,"No")>0,"Eligibility requirement not met",IF(AND($AK7<>"",IF($AK7="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK7="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK7="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ7<>"",COUNTIFS($A$6:$A$25,$A7,$C$6:$C$25,$AJ7)=0),"Required parent programme missing",IF(AND($AF7>0,$X7<$AF7),"Minimum programme spend not met",IF(AND($AG7>0,$G7/$W7<$AG7),"Minimum project cost not met",IF(AND($AH7>0,$G7/$W7>$AH7),"Maximum project cost exceeded",IF(AND($T7>0,$R7>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H7:$N7,"Unknown")>0,COUNTBLANK($H7:$N7)>0,COUNTBLANK($Q7:$U7)>0,$AL7<>"Active",OR($AM7="Low",$AM7="Unverified"),AND($Y7="Manual award",$O7="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP7` | `=IF(OR($C7="",$AN7="FAIL"),0,IF($AE7>0,MIN(IF($Y7="Manual award",IF($O7="",0,$O7),IF($Y7="Tiered",MIN(MIN($X7,IF($AC7>0,$AC7,$X7),IF($AD7>0,($G7/$W7)*$AD7,$X7)),$AA7)*$Z7+MAX(MIN($X7,IF($AC7>0,$AC7,$X7),IF($AD7>0,($G7/$W7)*$AD7,$X7))-$AA7,0)*$AB7,MIN($X7,IF($AC7>0,$AC7,$X7),IF($AD7>0,($G7/$W7)*$AD7,$X7))*$Z7)),$AE7),IF($Y7="Manual award",IF($O7="",0,$O7),IF($Y7="Tiered",MIN(MIN($X7,IF($AC7>0,$AC7,$X7),IF($AD7>0,($G7/$W7)*$AD7,$X7)),$AA7)*$Z7+MAX(MIN($X7,IF($AC7>0,$AC7,$X7),IF($AD7>0,($G7/$W7)*$AD7,$X7))-$AA7,0)*$AB7,MIN($X7,IF($AC7>0,$AC7,$X7),IF($AD7>0,($G7/$W7)*$AD7,$X7))*$Z7))))` |
| `AQ7` | `=$AP7*$W7` |
| `AR7` | `=IF($C7="",0,$AP7*$AI7+($AP7*(1-$AI7))*$T7)` |
| `AS7` | `=IF($C7="",0,($AP7*(1-$AI7)*(1-$T7)*$R7*$S7*$Q7/12)+$U7+($AP7*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT7` | `=IF(OR($C7="",COUNTBLANK($Q7:$U7)>0),"",$AP7-$AR7-$AS7)` |
| `AU7` | `=IF(OR($C7="",COUNTBLANK($Q7:$U7)>0),"",((($AP7*(1-$AI7)*(1-$T7)*$R7)-(($AP7*(1-$AI7)*(1-$T7)*$R7*$S7*$Q7/12)+$U7+($AP7*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),0))))*$W7)+(($AP7*(1-$AI7)*(1-$T7)*(1-$R7)*$W7)/((1+'FX & Financing'!$J$6)^($Q7/12))))` |
| `AV7` | `=IF($C7="",0,$P7)` |
| `AW7` | `=IF($AU7="","",$AU7-$AV7)` |
| `AX7` | `=IFERROR($AW7/$F7,0)` |
| `AY7` | `=IF($C7="",0,IF($AX7>='FX & Financing'!$J$7,5,IF($AX7>='FX & Financing'!$J$8,4,IF($AX7>='FX & Financing'!$J$9,3,IF($AX7>0,2,1)))))` |
| `AZ7` | `=IF($C7="",0,MAX(1,IF($AM7="High",5,IF($AM7="Medium",3,IF($AM7="Low",2,1)))-IF($AN7="PRELIMINARY",1,IF($AN7="FAIL",4,0))))` |
| `BA7` | `=IF($C7="",0,$AY7*'FX & Financing'!$J$10+$AZ7*(1-'FX & Financing'!$J$10))` |
| `BB7` | `=IF($C7="","",IF($AN7="FAIL","Red",IF($AN7="PRELIMINARY","Amber",IF($BA7>=4,"Green",IF($BA7>=3.25,"Amber","Red")))))` |
| `BC7` | `=IF($C7="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C7,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V8` | `=IF($C8="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W8` | `=IF(OR($C8="",$E8="",$V8=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V8,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E8,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X8` | `=IF(OR($F8="",$W8=0),0,$F8/$W8)` |
| `Y8` | `=IF($C8="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI8` | `=IF($C8="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ8` | `=IF($C8="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK8` | `=IF($C8="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL8` | `=IF($C8="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM8` | `=IF($C8="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN8` | `=IF($C8="","",IF(OR($AL8="Closed",$AL8="Test only",COUNTIF($H8:$N8,"No")>0,AND($AK8<>"",IF($AK8="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK8="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK8="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ8<>"",COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,$AJ8)=0),AND($AF8>0,$X8<$AF8),AND($AG8>0,$G8/$W8<$AG8),AND($AH8>0,$G8/$W8>$AH8),AND($T8>0,$R8>0)),"FAIL",IF(OR(COUNTIF($H8:$N8,"Unknown")>0,COUNTBLANK($H8:$N8)>0,COUNTBLANK($Q8:$U8)>0,$AL8<>"Active",OR($AM8="Low",$AM8="Unverified"),AND($Y8="Manual award",$O8="")),"PRELIMINARY","PASS")))` |
| `AO8` | `=IF($C8="","",IF($AL8="Closed","Programme unavailable",IF(COUNTIF($H8:$N8,"No")>0,"Eligibility requirement not met",IF(AND($AK8<>"",IF($AK8="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK8="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK8="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ8<>"",COUNTIFS($A$6:$A$25,$A8,$C$6:$C$25,$AJ8)=0),"Required parent programme missing",IF(AND($AF8>0,$X8<$AF8),"Minimum programme spend not met",IF(AND($AG8>0,$G8/$W8<$AG8),"Minimum project cost not met",IF(AND($AH8>0,$G8/$W8>$AH8),"Maximum project cost exceeded",IF(AND($T8>0,$R8>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H8:$N8,"Unknown")>0,COUNTBLANK($H8:$N8)>0,COUNTBLANK($Q8:$U8)>0,$AL8<>"Active",OR($AM8="Low",$AM8="Unverified"),AND($Y8="Manual award",$O8="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP8` | `=IF(OR($C8="",$AN8="FAIL"),0,IF($AE8>0,MIN(IF($Y8="Manual award",IF($O8="",0,$O8),IF($Y8="Tiered",MIN(MIN($X8,IF($AC8>0,$AC8,$X8),IF($AD8>0,($G8/$W8)*$AD8,$X8)),$AA8)*$Z8+MAX(MIN($X8,IF($AC8>0,$AC8,$X8),IF($AD8>0,($G8/$W8)*$AD8,$X8))-$AA8,0)*$AB8,MIN($X8,IF($AC8>0,$AC8,$X8),IF($AD8>0,($G8/$W8)*$AD8,$X8))*$Z8)),$AE8),IF($Y8="Manual award",IF($O8="",0,$O8),IF($Y8="Tiered",MIN(MIN($X8,IF($AC8>0,$AC8,$X8),IF($AD8>0,($G8/$W8)*$AD8,$X8)),$AA8)*$Z8+MAX(MIN($X8,IF($AC8>0,$AC8,$X8),IF($AD8>0,($G8/$W8)*$AD8,$X8))-$AA8,0)*$AB8,MIN($X8,IF($AC8>0,$AC8,$X8),IF($AD8>0,($G8/$W8)*$AD8,$X8))*$Z8))))` |
| `AQ8` | `=$AP8*$W8` |
| `AR8` | `=IF($C8="",0,$AP8*$AI8+($AP8*(1-$AI8))*$T8)` |
| `AS8` | `=IF($C8="",0,($AP8*(1-$AI8)*(1-$T8)*$R8*$S8*$Q8/12)+$U8+($AP8*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT8` | `=IF(OR($C8="",COUNTBLANK($Q8:$U8)>0),"",$AP8-$AR8-$AS8)` |
| `AU8` | `=IF(OR($C8="",COUNTBLANK($Q8:$U8)>0),"",((($AP8*(1-$AI8)*(1-$T8)*$R8)-(($AP8*(1-$AI8)*(1-$T8)*$R8*$S8*$Q8/12)+$U8+($AP8*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),0))))*$W8)+(($AP8*(1-$AI8)*(1-$T8)*(1-$R8)*$W8)/((1+'FX & Financing'!$J$6)^($Q8/12))))` |
| `AV8` | `=IF($C8="",0,$P8)` |
| `AW8` | `=IF($AU8="","",$AU8-$AV8)` |
| `AX8` | `=IFERROR($AW8/$F8,0)` |
| `AY8` | `=IF($C8="",0,IF($AX8>='FX & Financing'!$J$7,5,IF($AX8>='FX & Financing'!$J$8,4,IF($AX8>='FX & Financing'!$J$9,3,IF($AX8>0,2,1)))))` |
| `AZ8` | `=IF($C8="",0,MAX(1,IF($AM8="High",5,IF($AM8="Medium",3,IF($AM8="Low",2,1)))-IF($AN8="PRELIMINARY",1,IF($AN8="FAIL",4,0))))` |
| `BA8` | `=IF($C8="",0,$AY8*'FX & Financing'!$J$10+$AZ8*(1-'FX & Financing'!$J$10))` |
| `BB8` | `=IF($C8="","",IF($AN8="FAIL","Red",IF($AN8="PRELIMINARY","Amber",IF($BA8>=4,"Green",IF($BA8>=3.25,"Amber","Red")))))` |
| `BC8` | `=IF($C8="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C8,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V9` | `=IF($C9="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W9` | `=IF(OR($C9="",$E9="",$V9=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V9,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E9,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X9` | `=IF(OR($F9="",$W9=0),0,$F9/$W9)` |
| `Y9` | `=IF($C9="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI9` | `=IF($C9="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ9` | `=IF($C9="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK9` | `=IF($C9="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL9` | `=IF($C9="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM9` | `=IF($C9="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN9` | `=IF($C9="","",IF(OR($AL9="Closed",$AL9="Test only",COUNTIF($H9:$N9,"No")>0,AND($AK9<>"",IF($AK9="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK9="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK9="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ9<>"",COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,$AJ9)=0),AND($AF9>0,$X9<$AF9),AND($AG9>0,$G9/$W9<$AG9),AND($AH9>0,$G9/$W9>$AH9),AND($T9>0,$R9>0)),"FAIL",IF(OR(COUNTIF($H9:$N9,"Unknown")>0,COUNTBLANK($H9:$N9)>0,COUNTBLANK($Q9:$U9)>0,$AL9<>"Active",OR($AM9="Low",$AM9="Unverified"),AND($Y9="Manual award",$O9="")),"PRELIMINARY","PASS")))` |
| `AO9` | `=IF($C9="","",IF($AL9="Closed","Programme unavailable",IF(COUNTIF($H9:$N9,"No")>0,"Eligibility requirement not met",IF(AND($AK9<>"",IF($AK9="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK9="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK9="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ9<>"",COUNTIFS($A$6:$A$25,$A9,$C$6:$C$25,$AJ9)=0),"Required parent programme missing",IF(AND($AF9>0,$X9<$AF9),"Minimum programme spend not met",IF(AND($AG9>0,$G9/$W9<$AG9),"Minimum project cost not met",IF(AND($AH9>0,$G9/$W9>$AH9),"Maximum project cost exceeded",IF(AND($T9>0,$R9>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H9:$N9,"Unknown")>0,COUNTBLANK($H9:$N9)>0,COUNTBLANK($Q9:$U9)>0,$AL9<>"Active",OR($AM9="Low",$AM9="Unverified"),AND($Y9="Manual award",$O9="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP9` | `=IF(OR($C9="",$AN9="FAIL"),0,IF($AE9>0,MIN(IF($Y9="Manual award",IF($O9="",0,$O9),IF($Y9="Tiered",MIN(MIN($X9,IF($AC9>0,$AC9,$X9),IF($AD9>0,($G9/$W9)*$AD9,$X9)),$AA9)*$Z9+MAX(MIN($X9,IF($AC9>0,$AC9,$X9),IF($AD9>0,($G9/$W9)*$AD9,$X9))-$AA9,0)*$AB9,MIN($X9,IF($AC9>0,$AC9,$X9),IF($AD9>0,($G9/$W9)*$AD9,$X9))*$Z9)),$AE9),IF($Y9="Manual award",IF($O9="",0,$O9),IF($Y9="Tiered",MIN(MIN($X9,IF($AC9>0,$AC9,$X9),IF($AD9>0,($G9/$W9)*$AD9,$X9)),$AA9)*$Z9+MAX(MIN($X9,IF($AC9>0,$AC9,$X9),IF($AD9>0,($G9/$W9)*$AD9,$X9))-$AA9,0)*$AB9,MIN($X9,IF($AC9>0,$AC9,$X9),IF($AD9>0,($G9/$W9)*$AD9,$X9))*$Z9))))` |
| `AQ9` | `=$AP9*$W9` |
| `AR9` | `=IF($C9="",0,$AP9*$AI9+($AP9*(1-$AI9))*$T9)` |
| `AS9` | `=IF($C9="",0,($AP9*(1-$AI9)*(1-$T9)*$R9*$S9*$Q9/12)+$U9+($AP9*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT9` | `=IF(OR($C9="",COUNTBLANK($Q9:$U9)>0),"",$AP9-$AR9-$AS9)` |
| `AU9` | `=IF(OR($C9="",COUNTBLANK($Q9:$U9)>0),"",((($AP9*(1-$AI9)*(1-$T9)*$R9)-(($AP9*(1-$AI9)*(1-$T9)*$R9*$S9*$Q9/12)+$U9+($AP9*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),0))))*$W9)+(($AP9*(1-$AI9)*(1-$T9)*(1-$R9)*$W9)/((1+'FX & Financing'!$J$6)^($Q9/12))))` |
| `AV9` | `=IF($C9="",0,$P9)` |
| `AW9` | `=IF($AU9="","",$AU9-$AV9)` |
| `AX9` | `=IFERROR($AW9/$F9,0)` |
| `AY9` | `=IF($C9="",0,IF($AX9>='FX & Financing'!$J$7,5,IF($AX9>='FX & Financing'!$J$8,4,IF($AX9>='FX & Financing'!$J$9,3,IF($AX9>0,2,1)))))` |
| `AZ9` | `=IF($C9="",0,MAX(1,IF($AM9="High",5,IF($AM9="Medium",3,IF($AM9="Low",2,1)))-IF($AN9="PRELIMINARY",1,IF($AN9="FAIL",4,0))))` |
| `BA9` | `=IF($C9="",0,$AY9*'FX & Financing'!$J$10+$AZ9*(1-'FX & Financing'!$J$10))` |
| `BB9` | `=IF($C9="","",IF($AN9="FAIL","Red",IF($AN9="PRELIMINARY","Amber",IF($BA9>=4,"Green",IF($BA9>=3.25,"Amber","Red")))))` |
| `BC9` | `=IF($C9="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C9,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V10` | `=IF($C10="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W10` | `=IF(OR($C10="",$E10="",$V10=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V10,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E10,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X10` | `=IF(OR($F10="",$W10=0),0,$F10/$W10)` |
| `Y10` | `=IF($C10="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI10` | `=IF($C10="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ10` | `=IF($C10="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK10` | `=IF($C10="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL10` | `=IF($C10="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM10` | `=IF($C10="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN10` | `=IF($C10="","",IF(OR($AL10="Closed",$AL10="Test only",COUNTIF($H10:$N10,"No")>0,AND($AK10<>"",IF($AK10="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK10="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK10="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ10<>"",COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,$AJ10)=0),AND($AF10>0,$X10<$AF10),AND($AG10>0,$G10/$W10<$AG10),AND($AH10>0,$G10/$W10>$AH10),AND($T10>0,$R10>0)),"FAIL",IF(OR(COUNTIF($H10:$N10,"Unknown")>0,COUNTBLANK($H10:$N10)>0,COUNTBLANK($Q10:$U10)>0,$AL10<>"Active",OR($AM10="Low",$AM10="Unverified"),AND($Y10="Manual award",$O10="")),"PRELIMINARY","PASS")))` |
| `AO10` | `=IF($C10="","",IF($AL10="Closed","Programme unavailable",IF(COUNTIF($H10:$N10,"No")>0,"Eligibility requirement not met",IF(AND($AK10<>"",IF($AK10="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK10="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK10="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ10<>"",COUNTIFS($A$6:$A$25,$A10,$C$6:$C$25,$AJ10)=0),"Required parent programme missing",IF(AND($AF10>0,$X10<$AF10),"Minimum programme spend not met",IF(AND($AG10>0,$G10/$W10<$AG10),"Minimum project cost not met",IF(AND($AH10>0,$G10/$W10>$AH10),"Maximum project cost exceeded",IF(AND($T10>0,$R10>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H10:$N10,"Unknown")>0,COUNTBLANK($H10:$N10)>0,COUNTBLANK($Q10:$U10)>0,$AL10<>"Active",OR($AM10="Low",$AM10="Unverified"),AND($Y10="Manual award",$O10="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP10` | `=IF(OR($C10="",$AN10="FAIL"),0,IF($AE10>0,MIN(IF($Y10="Manual award",IF($O10="",0,$O10),IF($Y10="Tiered",MIN(MIN($X10,IF($AC10>0,$AC10,$X10),IF($AD10>0,($G10/$W10)*$AD10,$X10)),$AA10)*$Z10+MAX(MIN($X10,IF($AC10>0,$AC10,$X10),IF($AD10>0,($G10/$W10)*$AD10,$X10))-$AA10,0)*$AB10,MIN($X10,IF($AC10>0,$AC10,$X10),IF($AD10>0,($G10/$W10)*$AD10,$X10))*$Z10)),$AE10),IF($Y10="Manual award",IF($O10="",0,$O10),IF($Y10="Tiered",MIN(MIN($X10,IF($AC10>0,$AC10,$X10),IF($AD10>0,($G10/$W10)*$AD10,$X10)),$AA10)*$Z10+MAX(MIN($X10,IF($AC10>0,$AC10,$X10),IF($AD10>0,($G10/$W10)*$AD10,$X10))-$AA10,0)*$AB10,MIN($X10,IF($AC10>0,$AC10,$X10),IF($AD10>0,($G10/$W10)*$AD10,$X10))*$Z10))))` |
| `AQ10` | `=$AP10*$W10` |
| `AR10` | `=IF($C10="",0,$AP10*$AI10+($AP10*(1-$AI10))*$T10)` |
| `AS10` | `=IF($C10="",0,($AP10*(1-$AI10)*(1-$T10)*$R10*$S10*$Q10/12)+$U10+($AP10*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT10` | `=IF(OR($C10="",COUNTBLANK($Q10:$U10)>0),"",$AP10-$AR10-$AS10)` |
| `AU10` | `=IF(OR($C10="",COUNTBLANK($Q10:$U10)>0),"",((($AP10*(1-$AI10)*(1-$T10)*$R10)-(($AP10*(1-$AI10)*(1-$T10)*$R10*$S10*$Q10/12)+$U10+($AP10*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),0))))*$W10)+(($AP10*(1-$AI10)*(1-$T10)*(1-$R10)*$W10)/((1+'FX & Financing'!$J$6)^($Q10/12))))` |
| `AV10` | `=IF($C10="",0,$P10)` |
| `AW10` | `=IF($AU10="","",$AU10-$AV10)` |
| `AX10` | `=IFERROR($AW10/$F10,0)` |
| `AY10` | `=IF($C10="",0,IF($AX10>='FX & Financing'!$J$7,5,IF($AX10>='FX & Financing'!$J$8,4,IF($AX10>='FX & Financing'!$J$9,3,IF($AX10>0,2,1)))))` |
| `AZ10` | `=IF($C10="",0,MAX(1,IF($AM10="High",5,IF($AM10="Medium",3,IF($AM10="Low",2,1)))-IF($AN10="PRELIMINARY",1,IF($AN10="FAIL",4,0))))` |
| `BA10` | `=IF($C10="",0,$AY10*'FX & Financing'!$J$10+$AZ10*(1-'FX & Financing'!$J$10))` |
| `BB10` | `=IF($C10="","",IF($AN10="FAIL","Red",IF($AN10="PRELIMINARY","Amber",IF($BA10>=4,"Green",IF($BA10>=3.25,"Amber","Red")))))` |
| `BC10` | `=IF($C10="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C10,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V11` | `=IF($C11="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W11` | `=IF(OR($C11="",$E11="",$V11=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V11,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E11,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X11` | `=IF(OR($F11="",$W11=0),0,$F11/$W11)` |
| `Y11` | `=IF($C11="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI11` | `=IF($C11="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ11` | `=IF($C11="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK11` | `=IF($C11="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL11` | `=IF($C11="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM11` | `=IF($C11="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN11` | `=IF($C11="","",IF(OR($AL11="Closed",$AL11="Test only",COUNTIF($H11:$N11,"No")>0,AND($AK11<>"",IF($AK11="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK11="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK11="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ11<>"",COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,$AJ11)=0),AND($AF11>0,$X11<$AF11),AND($AG11>0,$G11/$W11<$AG11),AND($AH11>0,$G11/$W11>$AH11),AND($T11>0,$R11>0)),"FAIL",IF(OR(COUNTIF($H11:$N11,"Unknown")>0,COUNTBLANK($H11:$N11)>0,COUNTBLANK($Q11:$U11)>0,$AL11<>"Active",OR($AM11="Low",$AM11="Unverified"),AND($Y11="Manual award",$O11="")),"PRELIMINARY","PASS")))` |
| `AO11` | `=IF($C11="","",IF($AL11="Closed","Programme unavailable",IF(COUNTIF($H11:$N11,"No")>0,"Eligibility requirement not met",IF(AND($AK11<>"",IF($AK11="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK11="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK11="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ11<>"",COUNTIFS($A$6:$A$25,$A11,$C$6:$C$25,$AJ11)=0),"Required parent programme missing",IF(AND($AF11>0,$X11<$AF11),"Minimum programme spend not met",IF(AND($AG11>0,$G11/$W11<$AG11),"Minimum project cost not met",IF(AND($AH11>0,$G11/$W11>$AH11),"Maximum project cost exceeded",IF(AND($T11>0,$R11>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H11:$N11,"Unknown")>0,COUNTBLANK($H11:$N11)>0,COUNTBLANK($Q11:$U11)>0,$AL11<>"Active",OR($AM11="Low",$AM11="Unverified"),AND($Y11="Manual award",$O11="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP11` | `=IF(OR($C11="",$AN11="FAIL"),0,IF($AE11>0,MIN(IF($Y11="Manual award",IF($O11="",0,$O11),IF($Y11="Tiered",MIN(MIN($X11,IF($AC11>0,$AC11,$X11),IF($AD11>0,($G11/$W11)*$AD11,$X11)),$AA11)*$Z11+MAX(MIN($X11,IF($AC11>0,$AC11,$X11),IF($AD11>0,($G11/$W11)*$AD11,$X11))-$AA11,0)*$AB11,MIN($X11,IF($AC11>0,$AC11,$X11),IF($AD11>0,($G11/$W11)*$AD11,$X11))*$Z11)),$AE11),IF($Y11="Manual award",IF($O11="",0,$O11),IF($Y11="Tiered",MIN(MIN($X11,IF($AC11>0,$AC11,$X11),IF($AD11>0,($G11/$W11)*$AD11,$X11)),$AA11)*$Z11+MAX(MIN($X11,IF($AC11>0,$AC11,$X11),IF($AD11>0,($G11/$W11)*$AD11,$X11))-$AA11,0)*$AB11,MIN($X11,IF($AC11>0,$AC11,$X11),IF($AD11>0,($G11/$W11)*$AD11,$X11))*$Z11))))` |
| `AQ11` | `=$AP11*$W11` |
| `AR11` | `=IF($C11="",0,$AP11*$AI11+($AP11*(1-$AI11))*$T11)` |
| `AS11` | `=IF($C11="",0,($AP11*(1-$AI11)*(1-$T11)*$R11*$S11*$Q11/12)+$U11+($AP11*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT11` | `=IF(OR($C11="",COUNTBLANK($Q11:$U11)>0),"",$AP11-$AR11-$AS11)` |
| `AU11` | `=IF(OR($C11="",COUNTBLANK($Q11:$U11)>0),"",((($AP11*(1-$AI11)*(1-$T11)*$R11)-(($AP11*(1-$AI11)*(1-$T11)*$R11*$S11*$Q11/12)+$U11+($AP11*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),0))))*$W11)+(($AP11*(1-$AI11)*(1-$T11)*(1-$R11)*$W11)/((1+'FX & Financing'!$J$6)^($Q11/12))))` |
| `AV11` | `=IF($C11="",0,$P11)` |
| `AW11` | `=IF($AU11="","",$AU11-$AV11)` |
| `AX11` | `=IFERROR($AW11/$F11,0)` |
| `AY11` | `=IF($C11="",0,IF($AX11>='FX & Financing'!$J$7,5,IF($AX11>='FX & Financing'!$J$8,4,IF($AX11>='FX & Financing'!$J$9,3,IF($AX11>0,2,1)))))` |
| `AZ11` | `=IF($C11="",0,MAX(1,IF($AM11="High",5,IF($AM11="Medium",3,IF($AM11="Low",2,1)))-IF($AN11="PRELIMINARY",1,IF($AN11="FAIL",4,0))))` |
| `BA11` | `=IF($C11="",0,$AY11*'FX & Financing'!$J$10+$AZ11*(1-'FX & Financing'!$J$10))` |
| `BB11` | `=IF($C11="","",IF($AN11="FAIL","Red",IF($AN11="PRELIMINARY","Amber",IF($BA11>=4,"Green",IF($BA11>=3.25,"Amber","Red")))))` |
| `BC11` | `=IF($C11="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C11,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V12` | `=IF($C12="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W12` | `=IF(OR($C12="",$E12="",$V12=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V12,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E12,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X12` | `=IF(OR($F12="",$W12=0),0,$F12/$W12)` |
| `Y12` | `=IF($C12="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI12` | `=IF($C12="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ12` | `=IF($C12="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK12` | `=IF($C12="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL12` | `=IF($C12="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM12` | `=IF($C12="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN12` | `=IF($C12="","",IF(OR($AL12="Closed",$AL12="Test only",COUNTIF($H12:$N12,"No")>0,AND($AK12<>"",IF($AK12="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK12="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK12="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ12<>"",COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,$AJ12)=0),AND($AF12>0,$X12<$AF12),AND($AG12>0,$G12/$W12<$AG12),AND($AH12>0,$G12/$W12>$AH12),AND($T12>0,$R12>0)),"FAIL",IF(OR(COUNTIF($H12:$N12,"Unknown")>0,COUNTBLANK($H12:$N12)>0,COUNTBLANK($Q12:$U12)>0,$AL12<>"Active",OR($AM12="Low",$AM12="Unverified"),AND($Y12="Manual award",$O12="")),"PRELIMINARY","PASS")))` |
| `AO12` | `=IF($C12="","",IF($AL12="Closed","Programme unavailable",IF(COUNTIF($H12:$N12,"No")>0,"Eligibility requirement not met",IF(AND($AK12<>"",IF($AK12="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK12="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK12="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ12<>"",COUNTIFS($A$6:$A$25,$A12,$C$6:$C$25,$AJ12)=0),"Required parent programme missing",IF(AND($AF12>0,$X12<$AF12),"Minimum programme spend not met",IF(AND($AG12>0,$G12/$W12<$AG12),"Minimum project cost not met",IF(AND($AH12>0,$G12/$W12>$AH12),"Maximum project cost exceeded",IF(AND($T12>0,$R12>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H12:$N12,"Unknown")>0,COUNTBLANK($H12:$N12)>0,COUNTBLANK($Q12:$U12)>0,$AL12<>"Active",OR($AM12="Low",$AM12="Unverified"),AND($Y12="Manual award",$O12="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP12` | `=IF(OR($C12="",$AN12="FAIL"),0,IF($AE12>0,MIN(IF($Y12="Manual award",IF($O12="",0,$O12),IF($Y12="Tiered",MIN(MIN($X12,IF($AC12>0,$AC12,$X12),IF($AD12>0,($G12/$W12)*$AD12,$X12)),$AA12)*$Z12+MAX(MIN($X12,IF($AC12>0,$AC12,$X12),IF($AD12>0,($G12/$W12)*$AD12,$X12))-$AA12,0)*$AB12,MIN($X12,IF($AC12>0,$AC12,$X12),IF($AD12>0,($G12/$W12)*$AD12,$X12))*$Z12)),$AE12),IF($Y12="Manual award",IF($O12="",0,$O12),IF($Y12="Tiered",MIN(MIN($X12,IF($AC12>0,$AC12,$X12),IF($AD12>0,($G12/$W12)*$AD12,$X12)),$AA12)*$Z12+MAX(MIN($X12,IF($AC12>0,$AC12,$X12),IF($AD12>0,($G12/$W12)*$AD12,$X12))-$AA12,0)*$AB12,MIN($X12,IF($AC12>0,$AC12,$X12),IF($AD12>0,($G12/$W12)*$AD12,$X12))*$Z12))))` |
| `AQ12` | `=$AP12*$W12` |
| `AR12` | `=IF($C12="",0,$AP12*$AI12+($AP12*(1-$AI12))*$T12)` |
| `AS12` | `=IF($C12="",0,($AP12*(1-$AI12)*(1-$T12)*$R12*$S12*$Q12/12)+$U12+($AP12*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT12` | `=IF(OR($C12="",COUNTBLANK($Q12:$U12)>0),"",$AP12-$AR12-$AS12)` |
| `AU12` | `=IF(OR($C12="",COUNTBLANK($Q12:$U12)>0),"",((($AP12*(1-$AI12)*(1-$T12)*$R12)-(($AP12*(1-$AI12)*(1-$T12)*$R12*$S12*$Q12/12)+$U12+($AP12*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),0))))*$W12)+(($AP12*(1-$AI12)*(1-$T12)*(1-$R12)*$W12)/((1+'FX & Financing'!$J$6)^($Q12/12))))` |
| `AV12` | `=IF($C12="",0,$P12)` |
| `AW12` | `=IF($AU12="","",$AU12-$AV12)` |
| `AX12` | `=IFERROR($AW12/$F12,0)` |
| `AY12` | `=IF($C12="",0,IF($AX12>='FX & Financing'!$J$7,5,IF($AX12>='FX & Financing'!$J$8,4,IF($AX12>='FX & Financing'!$J$9,3,IF($AX12>0,2,1)))))` |
| `AZ12` | `=IF($C12="",0,MAX(1,IF($AM12="High",5,IF($AM12="Medium",3,IF($AM12="Low",2,1)))-IF($AN12="PRELIMINARY",1,IF($AN12="FAIL",4,0))))` |
| `BA12` | `=IF($C12="",0,$AY12*'FX & Financing'!$J$10+$AZ12*(1-'FX & Financing'!$J$10))` |
| `BB12` | `=IF($C12="","",IF($AN12="FAIL","Red",IF($AN12="PRELIMINARY","Amber",IF($BA12>=4,"Green",IF($BA12>=3.25,"Amber","Red")))))` |
| `BC12` | `=IF($C12="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C12,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V13` | `=IF($C13="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W13` | `=IF(OR($C13="",$E13="",$V13=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V13,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E13,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X13` | `=IF(OR($F13="",$W13=0),0,$F13/$W13)` |
| `Y13` | `=IF($C13="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI13` | `=IF($C13="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ13` | `=IF($C13="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK13` | `=IF($C13="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL13` | `=IF($C13="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM13` | `=IF($C13="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN13` | `=IF($C13="","",IF(OR($AL13="Closed",$AL13="Test only",COUNTIF($H13:$N13,"No")>0,AND($AK13<>"",IF($AK13="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK13="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK13="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ13<>"",COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,$AJ13)=0),AND($AF13>0,$X13<$AF13),AND($AG13>0,$G13/$W13<$AG13),AND($AH13>0,$G13/$W13>$AH13),AND($T13>0,$R13>0)),"FAIL",IF(OR(COUNTIF($H13:$N13,"Unknown")>0,COUNTBLANK($H13:$N13)>0,COUNTBLANK($Q13:$U13)>0,$AL13<>"Active",OR($AM13="Low",$AM13="Unverified"),AND($Y13="Manual award",$O13="")),"PRELIMINARY","PASS")))` |
| `AO13` | `=IF($C13="","",IF($AL13="Closed","Programme unavailable",IF(COUNTIF($H13:$N13,"No")>0,"Eligibility requirement not met",IF(AND($AK13<>"",IF($AK13="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK13="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK13="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ13<>"",COUNTIFS($A$6:$A$25,$A13,$C$6:$C$25,$AJ13)=0),"Required parent programme missing",IF(AND($AF13>0,$X13<$AF13),"Minimum programme spend not met",IF(AND($AG13>0,$G13/$W13<$AG13),"Minimum project cost not met",IF(AND($AH13>0,$G13/$W13>$AH13),"Maximum project cost exceeded",IF(AND($T13>0,$R13>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H13:$N13,"Unknown")>0,COUNTBLANK($H13:$N13)>0,COUNTBLANK($Q13:$U13)>0,$AL13<>"Active",OR($AM13="Low",$AM13="Unverified"),AND($Y13="Manual award",$O13="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP13` | `=IF(OR($C13="",$AN13="FAIL"),0,IF($AE13>0,MIN(IF($Y13="Manual award",IF($O13="",0,$O13),IF($Y13="Tiered",MIN(MIN($X13,IF($AC13>0,$AC13,$X13),IF($AD13>0,($G13/$W13)*$AD13,$X13)),$AA13)*$Z13+MAX(MIN($X13,IF($AC13>0,$AC13,$X13),IF($AD13>0,($G13/$W13)*$AD13,$X13))-$AA13,0)*$AB13,MIN($X13,IF($AC13>0,$AC13,$X13),IF($AD13>0,($G13/$W13)*$AD13,$X13))*$Z13)),$AE13),IF($Y13="Manual award",IF($O13="",0,$O13),IF($Y13="Tiered",MIN(MIN($X13,IF($AC13>0,$AC13,$X13),IF($AD13>0,($G13/$W13)*$AD13,$X13)),$AA13)*$Z13+MAX(MIN($X13,IF($AC13>0,$AC13,$X13),IF($AD13>0,($G13/$W13)*$AD13,$X13))-$AA13,0)*$AB13,MIN($X13,IF($AC13>0,$AC13,$X13),IF($AD13>0,($G13/$W13)*$AD13,$X13))*$Z13))))` |
| `AQ13` | `=$AP13*$W13` |
| `AR13` | `=IF($C13="",0,$AP13*$AI13+($AP13*(1-$AI13))*$T13)` |
| `AS13` | `=IF($C13="",0,($AP13*(1-$AI13)*(1-$T13)*$R13*$S13*$Q13/12)+$U13+($AP13*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT13` | `=IF(OR($C13="",COUNTBLANK($Q13:$U13)>0),"",$AP13-$AR13-$AS13)` |
| `AU13` | `=IF(OR($C13="",COUNTBLANK($Q13:$U13)>0),"",((($AP13*(1-$AI13)*(1-$T13)*$R13)-(($AP13*(1-$AI13)*(1-$T13)*$R13*$S13*$Q13/12)+$U13+($AP13*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),0))))*$W13)+(($AP13*(1-$AI13)*(1-$T13)*(1-$R13)*$W13)/((1+'FX & Financing'!$J$6)^($Q13/12))))` |
| `AV13` | `=IF($C13="",0,$P13)` |
| `AW13` | `=IF($AU13="","",$AU13-$AV13)` |
| `AX13` | `=IFERROR($AW13/$F13,0)` |
| `AY13` | `=IF($C13="",0,IF($AX13>='FX & Financing'!$J$7,5,IF($AX13>='FX & Financing'!$J$8,4,IF($AX13>='FX & Financing'!$J$9,3,IF($AX13>0,2,1)))))` |
| `AZ13` | `=IF($C13="",0,MAX(1,IF($AM13="High",5,IF($AM13="Medium",3,IF($AM13="Low",2,1)))-IF($AN13="PRELIMINARY",1,IF($AN13="FAIL",4,0))))` |
| `BA13` | `=IF($C13="",0,$AY13*'FX & Financing'!$J$10+$AZ13*(1-'FX & Financing'!$J$10))` |
| `BB13` | `=IF($C13="","",IF($AN13="FAIL","Red",IF($AN13="PRELIMINARY","Amber",IF($BA13>=4,"Green",IF($BA13>=3.25,"Amber","Red")))))` |
| `BC13` | `=IF($C13="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C13,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V14` | `=IF($C14="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W14` | `=IF(OR($C14="",$E14="",$V14=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V14,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E14,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X14` | `=IF(OR($F14="",$W14=0),0,$F14/$W14)` |
| `Y14` | `=IF($C14="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI14` | `=IF($C14="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ14` | `=IF($C14="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK14` | `=IF($C14="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL14` | `=IF($C14="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM14` | `=IF($C14="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN14` | `=IF($C14="","",IF(OR($AL14="Closed",$AL14="Test only",COUNTIF($H14:$N14,"No")>0,AND($AK14<>"",IF($AK14="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK14="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK14="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ14<>"",COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,$AJ14)=0),AND($AF14>0,$X14<$AF14),AND($AG14>0,$G14/$W14<$AG14),AND($AH14>0,$G14/$W14>$AH14),AND($T14>0,$R14>0)),"FAIL",IF(OR(COUNTIF($H14:$N14,"Unknown")>0,COUNTBLANK($H14:$N14)>0,COUNTBLANK($Q14:$U14)>0,$AL14<>"Active",OR($AM14="Low",$AM14="Unverified"),AND($Y14="Manual award",$O14="")),"PRELIMINARY","PASS")))` |
| `AO14` | `=IF($C14="","",IF($AL14="Closed","Programme unavailable",IF(COUNTIF($H14:$N14,"No")>0,"Eligibility requirement not met",IF(AND($AK14<>"",IF($AK14="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK14="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK14="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ14<>"",COUNTIFS($A$6:$A$25,$A14,$C$6:$C$25,$AJ14)=0),"Required parent programme missing",IF(AND($AF14>0,$X14<$AF14),"Minimum programme spend not met",IF(AND($AG14>0,$G14/$W14<$AG14),"Minimum project cost not met",IF(AND($AH14>0,$G14/$W14>$AH14),"Maximum project cost exceeded",IF(AND($T14>0,$R14>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H14:$N14,"Unknown")>0,COUNTBLANK($H14:$N14)>0,COUNTBLANK($Q14:$U14)>0,$AL14<>"Active",OR($AM14="Low",$AM14="Unverified"),AND($Y14="Manual award",$O14="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP14` | `=IF(OR($C14="",$AN14="FAIL"),0,IF($AE14>0,MIN(IF($Y14="Manual award",IF($O14="",0,$O14),IF($Y14="Tiered",MIN(MIN($X14,IF($AC14>0,$AC14,$X14),IF($AD14>0,($G14/$W14)*$AD14,$X14)),$AA14)*$Z14+MAX(MIN($X14,IF($AC14>0,$AC14,$X14),IF($AD14>0,($G14/$W14)*$AD14,$X14))-$AA14,0)*$AB14,MIN($X14,IF($AC14>0,$AC14,$X14),IF($AD14>0,($G14/$W14)*$AD14,$X14))*$Z14)),$AE14),IF($Y14="Manual award",IF($O14="",0,$O14),IF($Y14="Tiered",MIN(MIN($X14,IF($AC14>0,$AC14,$X14),IF($AD14>0,($G14/$W14)*$AD14,$X14)),$AA14)*$Z14+MAX(MIN($X14,IF($AC14>0,$AC14,$X14),IF($AD14>0,($G14/$W14)*$AD14,$X14))-$AA14,0)*$AB14,MIN($X14,IF($AC14>0,$AC14,$X14),IF($AD14>0,($G14/$W14)*$AD14,$X14))*$Z14))))` |
| `AQ14` | `=$AP14*$W14` |
| `AR14` | `=IF($C14="",0,$AP14*$AI14+($AP14*(1-$AI14))*$T14)` |
| `AS14` | `=IF($C14="",0,($AP14*(1-$AI14)*(1-$T14)*$R14*$S14*$Q14/12)+$U14+($AP14*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT14` | `=IF(OR($C14="",COUNTBLANK($Q14:$U14)>0),"",$AP14-$AR14-$AS14)` |
| `AU14` | `=IF(OR($C14="",COUNTBLANK($Q14:$U14)>0),"",((($AP14*(1-$AI14)*(1-$T14)*$R14)-(($AP14*(1-$AI14)*(1-$T14)*$R14*$S14*$Q14/12)+$U14+($AP14*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),0))))*$W14)+(($AP14*(1-$AI14)*(1-$T14)*(1-$R14)*$W14)/((1+'FX & Financing'!$J$6)^($Q14/12))))` |
| `AV14` | `=IF($C14="",0,$P14)` |
| `AW14` | `=IF($AU14="","",$AU14-$AV14)` |
| `AX14` | `=IFERROR($AW14/$F14,0)` |
| `AY14` | `=IF($C14="",0,IF($AX14>='FX & Financing'!$J$7,5,IF($AX14>='FX & Financing'!$J$8,4,IF($AX14>='FX & Financing'!$J$9,3,IF($AX14>0,2,1)))))` |
| `AZ14` | `=IF($C14="",0,MAX(1,IF($AM14="High",5,IF($AM14="Medium",3,IF($AM14="Low",2,1)))-IF($AN14="PRELIMINARY",1,IF($AN14="FAIL",4,0))))` |
| `BA14` | `=IF($C14="",0,$AY14*'FX & Financing'!$J$10+$AZ14*(1-'FX & Financing'!$J$10))` |
| `BB14` | `=IF($C14="","",IF($AN14="FAIL","Red",IF($AN14="PRELIMINARY","Amber",IF($BA14>=4,"Green",IF($BA14>=3.25,"Amber","Red")))))` |
| `BC14` | `=IF($C14="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C14,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V15` | `=IF($C15="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W15` | `=IF(OR($C15="",$E15="",$V15=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V15,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E15,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X15` | `=IF(OR($F15="",$W15=0),0,$F15/$W15)` |
| `Y15` | `=IF($C15="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI15` | `=IF($C15="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ15` | `=IF($C15="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK15` | `=IF($C15="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL15` | `=IF($C15="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM15` | `=IF($C15="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN15` | `=IF($C15="","",IF(OR($AL15="Closed",$AL15="Test only",COUNTIF($H15:$N15,"No")>0,AND($AK15<>"",IF($AK15="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK15="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK15="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ15<>"",COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,$AJ15)=0),AND($AF15>0,$X15<$AF15),AND($AG15>0,$G15/$W15<$AG15),AND($AH15>0,$G15/$W15>$AH15),AND($T15>0,$R15>0)),"FAIL",IF(OR(COUNTIF($H15:$N15,"Unknown")>0,COUNTBLANK($H15:$N15)>0,COUNTBLANK($Q15:$U15)>0,$AL15<>"Active",OR($AM15="Low",$AM15="Unverified"),AND($Y15="Manual award",$O15="")),"PRELIMINARY","PASS")))` |
| `AO15` | `=IF($C15="","",IF($AL15="Closed","Programme unavailable",IF(COUNTIF($H15:$N15,"No")>0,"Eligibility requirement not met",IF(AND($AK15<>"",IF($AK15="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK15="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK15="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ15<>"",COUNTIFS($A$6:$A$25,$A15,$C$6:$C$25,$AJ15)=0),"Required parent programme missing",IF(AND($AF15>0,$X15<$AF15),"Minimum programme spend not met",IF(AND($AG15>0,$G15/$W15<$AG15),"Minimum project cost not met",IF(AND($AH15>0,$G15/$W15>$AH15),"Maximum project cost exceeded",IF(AND($T15>0,$R15>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H15:$N15,"Unknown")>0,COUNTBLANK($H15:$N15)>0,COUNTBLANK($Q15:$U15)>0,$AL15<>"Active",OR($AM15="Low",$AM15="Unverified"),AND($Y15="Manual award",$O15="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP15` | `=IF(OR($C15="",$AN15="FAIL"),0,IF($AE15>0,MIN(IF($Y15="Manual award",IF($O15="",0,$O15),IF($Y15="Tiered",MIN(MIN($X15,IF($AC15>0,$AC15,$X15),IF($AD15>0,($G15/$W15)*$AD15,$X15)),$AA15)*$Z15+MAX(MIN($X15,IF($AC15>0,$AC15,$X15),IF($AD15>0,($G15/$W15)*$AD15,$X15))-$AA15,0)*$AB15,MIN($X15,IF($AC15>0,$AC15,$X15),IF($AD15>0,($G15/$W15)*$AD15,$X15))*$Z15)),$AE15),IF($Y15="Manual award",IF($O15="",0,$O15),IF($Y15="Tiered",MIN(MIN($X15,IF($AC15>0,$AC15,$X15),IF($AD15>0,($G15/$W15)*$AD15,$X15)),$AA15)*$Z15+MAX(MIN($X15,IF($AC15>0,$AC15,$X15),IF($AD15>0,($G15/$W15)*$AD15,$X15))-$AA15,0)*$AB15,MIN($X15,IF($AC15>0,$AC15,$X15),IF($AD15>0,($G15/$W15)*$AD15,$X15))*$Z15))))` |
| `AQ15` | `=$AP15*$W15` |
| `AR15` | `=IF($C15="",0,$AP15*$AI15+($AP15*(1-$AI15))*$T15)` |
| `AS15` | `=IF($C15="",0,($AP15*(1-$AI15)*(1-$T15)*$R15*$S15*$Q15/12)+$U15+($AP15*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT15` | `=IF(OR($C15="",COUNTBLANK($Q15:$U15)>0),"",$AP15-$AR15-$AS15)` |
| `AU15` | `=IF(OR($C15="",COUNTBLANK($Q15:$U15)>0),"",((($AP15*(1-$AI15)*(1-$T15)*$R15)-(($AP15*(1-$AI15)*(1-$T15)*$R15*$S15*$Q15/12)+$U15+($AP15*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),0))))*$W15)+(($AP15*(1-$AI15)*(1-$T15)*(1-$R15)*$W15)/((1+'FX & Financing'!$J$6)^($Q15/12))))` |
| `AV15` | `=IF($C15="",0,$P15)` |
| `AW15` | `=IF($AU15="","",$AU15-$AV15)` |
| `AX15` | `=IFERROR($AW15/$F15,0)` |
| `AY15` | `=IF($C15="",0,IF($AX15>='FX & Financing'!$J$7,5,IF($AX15>='FX & Financing'!$J$8,4,IF($AX15>='FX & Financing'!$J$9,3,IF($AX15>0,2,1)))))` |
| `AZ15` | `=IF($C15="",0,MAX(1,IF($AM15="High",5,IF($AM15="Medium",3,IF($AM15="Low",2,1)))-IF($AN15="PRELIMINARY",1,IF($AN15="FAIL",4,0))))` |
| `BA15` | `=IF($C15="",0,$AY15*'FX & Financing'!$J$10+$AZ15*(1-'FX & Financing'!$J$10))` |
| `BB15` | `=IF($C15="","",IF($AN15="FAIL","Red",IF($AN15="PRELIMINARY","Amber",IF($BA15>=4,"Green",IF($BA15>=3.25,"Amber","Red")))))` |
| `BC15` | `=IF($C15="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C15,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V16` | `=IF($C16="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W16` | `=IF(OR($C16="",$E16="",$V16=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V16,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E16,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X16` | `=IF(OR($F16="",$W16=0),0,$F16/$W16)` |
| `Y16` | `=IF($C16="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI16` | `=IF($C16="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ16` | `=IF($C16="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK16` | `=IF($C16="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL16` | `=IF($C16="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM16` | `=IF($C16="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN16` | `=IF($C16="","",IF(OR($AL16="Closed",$AL16="Test only",COUNTIF($H16:$N16,"No")>0,AND($AK16<>"",IF($AK16="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK16="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK16="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ16<>"",COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,$AJ16)=0),AND($AF16>0,$X16<$AF16),AND($AG16>0,$G16/$W16<$AG16),AND($AH16>0,$G16/$W16>$AH16),AND($T16>0,$R16>0)),"FAIL",IF(OR(COUNTIF($H16:$N16,"Unknown")>0,COUNTBLANK($H16:$N16)>0,COUNTBLANK($Q16:$U16)>0,$AL16<>"Active",OR($AM16="Low",$AM16="Unverified"),AND($Y16="Manual award",$O16="")),"PRELIMINARY","PASS")))` |
| `AO16` | `=IF($C16="","",IF($AL16="Closed","Programme unavailable",IF(COUNTIF($H16:$N16,"No")>0,"Eligibility requirement not met",IF(AND($AK16<>"",IF($AK16="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK16="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK16="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ16<>"",COUNTIFS($A$6:$A$25,$A16,$C$6:$C$25,$AJ16)=0),"Required parent programme missing",IF(AND($AF16>0,$X16<$AF16),"Minimum programme spend not met",IF(AND($AG16>0,$G16/$W16<$AG16),"Minimum project cost not met",IF(AND($AH16>0,$G16/$W16>$AH16),"Maximum project cost exceeded",IF(AND($T16>0,$R16>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H16:$N16,"Unknown")>0,COUNTBLANK($H16:$N16)>0,COUNTBLANK($Q16:$U16)>0,$AL16<>"Active",OR($AM16="Low",$AM16="Unverified"),AND($Y16="Manual award",$O16="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP16` | `=IF(OR($C16="",$AN16="FAIL"),0,IF($AE16>0,MIN(IF($Y16="Manual award",IF($O16="",0,$O16),IF($Y16="Tiered",MIN(MIN($X16,IF($AC16>0,$AC16,$X16),IF($AD16>0,($G16/$W16)*$AD16,$X16)),$AA16)*$Z16+MAX(MIN($X16,IF($AC16>0,$AC16,$X16),IF($AD16>0,($G16/$W16)*$AD16,$X16))-$AA16,0)*$AB16,MIN($X16,IF($AC16>0,$AC16,$X16),IF($AD16>0,($G16/$W16)*$AD16,$X16))*$Z16)),$AE16),IF($Y16="Manual award",IF($O16="",0,$O16),IF($Y16="Tiered",MIN(MIN($X16,IF($AC16>0,$AC16,$X16),IF($AD16>0,($G16/$W16)*$AD16,$X16)),$AA16)*$Z16+MAX(MIN($X16,IF($AC16>0,$AC16,$X16),IF($AD16>0,($G16/$W16)*$AD16,$X16))-$AA16,0)*$AB16,MIN($X16,IF($AC16>0,$AC16,$X16),IF($AD16>0,($G16/$W16)*$AD16,$X16))*$Z16))))` |
| `AQ16` | `=$AP16*$W16` |
| `AR16` | `=IF($C16="",0,$AP16*$AI16+($AP16*(1-$AI16))*$T16)` |
| `AS16` | `=IF($C16="",0,($AP16*(1-$AI16)*(1-$T16)*$R16*$S16*$Q16/12)+$U16+($AP16*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT16` | `=IF(OR($C16="",COUNTBLANK($Q16:$U16)>0),"",$AP16-$AR16-$AS16)` |
| `AU16` | `=IF(OR($C16="",COUNTBLANK($Q16:$U16)>0),"",((($AP16*(1-$AI16)*(1-$T16)*$R16)-(($AP16*(1-$AI16)*(1-$T16)*$R16*$S16*$Q16/12)+$U16+($AP16*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),0))))*$W16)+(($AP16*(1-$AI16)*(1-$T16)*(1-$R16)*$W16)/((1+'FX & Financing'!$J$6)^($Q16/12))))` |
| `AV16` | `=IF($C16="",0,$P16)` |
| `AW16` | `=IF($AU16="","",$AU16-$AV16)` |
| `AX16` | `=IFERROR($AW16/$F16,0)` |
| `AY16` | `=IF($C16="",0,IF($AX16>='FX & Financing'!$J$7,5,IF($AX16>='FX & Financing'!$J$8,4,IF($AX16>='FX & Financing'!$J$9,3,IF($AX16>0,2,1)))))` |
| `AZ16` | `=IF($C16="",0,MAX(1,IF($AM16="High",5,IF($AM16="Medium",3,IF($AM16="Low",2,1)))-IF($AN16="PRELIMINARY",1,IF($AN16="FAIL",4,0))))` |
| `BA16` | `=IF($C16="",0,$AY16*'FX & Financing'!$J$10+$AZ16*(1-'FX & Financing'!$J$10))` |
| `BB16` | `=IF($C16="","",IF($AN16="FAIL","Red",IF($AN16="PRELIMINARY","Amber",IF($BA16>=4,"Green",IF($BA16>=3.25,"Amber","Red")))))` |
| `BC16` | `=IF($C16="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C16,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V17` | `=IF($C17="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W17` | `=IF(OR($C17="",$E17="",$V17=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V17,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E17,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X17` | `=IF(OR($F17="",$W17=0),0,$F17/$W17)` |
| `Y17` | `=IF($C17="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI17` | `=IF($C17="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ17` | `=IF($C17="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK17` | `=IF($C17="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL17` | `=IF($C17="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM17` | `=IF($C17="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN17` | `=IF($C17="","",IF(OR($AL17="Closed",$AL17="Test only",COUNTIF($H17:$N17,"No")>0,AND($AK17<>"",IF($AK17="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK17="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK17="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ17<>"",COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,$AJ17)=0),AND($AF17>0,$X17<$AF17),AND($AG17>0,$G17/$W17<$AG17),AND($AH17>0,$G17/$W17>$AH17),AND($T17>0,$R17>0)),"FAIL",IF(OR(COUNTIF($H17:$N17,"Unknown")>0,COUNTBLANK($H17:$N17)>0,COUNTBLANK($Q17:$U17)>0,$AL17<>"Active",OR($AM17="Low",$AM17="Unverified"),AND($Y17="Manual award",$O17="")),"PRELIMINARY","PASS")))` |
| `AO17` | `=IF($C17="","",IF($AL17="Closed","Programme unavailable",IF(COUNTIF($H17:$N17,"No")>0,"Eligibility requirement not met",IF(AND($AK17<>"",IF($AK17="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK17="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK17="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ17<>"",COUNTIFS($A$6:$A$25,$A17,$C$6:$C$25,$AJ17)=0),"Required parent programme missing",IF(AND($AF17>0,$X17<$AF17),"Minimum programme spend not met",IF(AND($AG17>0,$G17/$W17<$AG17),"Minimum project cost not met",IF(AND($AH17>0,$G17/$W17>$AH17),"Maximum project cost exceeded",IF(AND($T17>0,$R17>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H17:$N17,"Unknown")>0,COUNTBLANK($H17:$N17)>0,COUNTBLANK($Q17:$U17)>0,$AL17<>"Active",OR($AM17="Low",$AM17="Unverified"),AND($Y17="Manual award",$O17="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP17` | `=IF(OR($C17="",$AN17="FAIL"),0,IF($AE17>0,MIN(IF($Y17="Manual award",IF($O17="",0,$O17),IF($Y17="Tiered",MIN(MIN($X17,IF($AC17>0,$AC17,$X17),IF($AD17>0,($G17/$W17)*$AD17,$X17)),$AA17)*$Z17+MAX(MIN($X17,IF($AC17>0,$AC17,$X17),IF($AD17>0,($G17/$W17)*$AD17,$X17))-$AA17,0)*$AB17,MIN($X17,IF($AC17>0,$AC17,$X17),IF($AD17>0,($G17/$W17)*$AD17,$X17))*$Z17)),$AE17),IF($Y17="Manual award",IF($O17="",0,$O17),IF($Y17="Tiered",MIN(MIN($X17,IF($AC17>0,$AC17,$X17),IF($AD17>0,($G17/$W17)*$AD17,$X17)),$AA17)*$Z17+MAX(MIN($X17,IF($AC17>0,$AC17,$X17),IF($AD17>0,($G17/$W17)*$AD17,$X17))-$AA17,0)*$AB17,MIN($X17,IF($AC17>0,$AC17,$X17),IF($AD17>0,($G17/$W17)*$AD17,$X17))*$Z17))))` |
| `AQ17` | `=$AP17*$W17` |
| `AR17` | `=IF($C17="",0,$AP17*$AI17+($AP17*(1-$AI17))*$T17)` |
| `AS17` | `=IF($C17="",0,($AP17*(1-$AI17)*(1-$T17)*$R17*$S17*$Q17/12)+$U17+($AP17*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT17` | `=IF(OR($C17="",COUNTBLANK($Q17:$U17)>0),"",$AP17-$AR17-$AS17)` |
| `AU17` | `=IF(OR($C17="",COUNTBLANK($Q17:$U17)>0),"",((($AP17*(1-$AI17)*(1-$T17)*$R17)-(($AP17*(1-$AI17)*(1-$T17)*$R17*$S17*$Q17/12)+$U17+($AP17*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),0))))*$W17)+(($AP17*(1-$AI17)*(1-$T17)*(1-$R17)*$W17)/((1+'FX & Financing'!$J$6)^($Q17/12))))` |
| `AV17` | `=IF($C17="",0,$P17)` |
| `AW17` | `=IF($AU17="","",$AU17-$AV17)` |
| `AX17` | `=IFERROR($AW17/$F17,0)` |
| `AY17` | `=IF($C17="",0,IF($AX17>='FX & Financing'!$J$7,5,IF($AX17>='FX & Financing'!$J$8,4,IF($AX17>='FX & Financing'!$J$9,3,IF($AX17>0,2,1)))))` |
| `AZ17` | `=IF($C17="",0,MAX(1,IF($AM17="High",5,IF($AM17="Medium",3,IF($AM17="Low",2,1)))-IF($AN17="PRELIMINARY",1,IF($AN17="FAIL",4,0))))` |
| `BA17` | `=IF($C17="",0,$AY17*'FX & Financing'!$J$10+$AZ17*(1-'FX & Financing'!$J$10))` |
| `BB17` | `=IF($C17="","",IF($AN17="FAIL","Red",IF($AN17="PRELIMINARY","Amber",IF($BA17>=4,"Green",IF($BA17>=3.25,"Amber","Red")))))` |
| `BC17` | `=IF($C17="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C17,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V18` | `=IF($C18="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W18` | `=IF(OR($C18="",$E18="",$V18=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V18,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E18,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X18` | `=IF(OR($F18="",$W18=0),0,$F18/$W18)` |
| `Y18` | `=IF($C18="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI18` | `=IF($C18="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ18` | `=IF($C18="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK18` | `=IF($C18="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL18` | `=IF($C18="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM18` | `=IF($C18="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN18` | `=IF($C18="","",IF(OR($AL18="Closed",$AL18="Test only",COUNTIF($H18:$N18,"No")>0,AND($AK18<>"",IF($AK18="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK18="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK18="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ18<>"",COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,$AJ18)=0),AND($AF18>0,$X18<$AF18),AND($AG18>0,$G18/$W18<$AG18),AND($AH18>0,$G18/$W18>$AH18),AND($T18>0,$R18>0)),"FAIL",IF(OR(COUNTIF($H18:$N18,"Unknown")>0,COUNTBLANK($H18:$N18)>0,COUNTBLANK($Q18:$U18)>0,$AL18<>"Active",OR($AM18="Low",$AM18="Unverified"),AND($Y18="Manual award",$O18="")),"PRELIMINARY","PASS")))` |
| `AO18` | `=IF($C18="","",IF($AL18="Closed","Programme unavailable",IF(COUNTIF($H18:$N18,"No")>0,"Eligibility requirement not met",IF(AND($AK18<>"",IF($AK18="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK18="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK18="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ18<>"",COUNTIFS($A$6:$A$25,$A18,$C$6:$C$25,$AJ18)=0),"Required parent programme missing",IF(AND($AF18>0,$X18<$AF18),"Minimum programme spend not met",IF(AND($AG18>0,$G18/$W18<$AG18),"Minimum project cost not met",IF(AND($AH18>0,$G18/$W18>$AH18),"Maximum project cost exceeded",IF(AND($T18>0,$R18>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H18:$N18,"Unknown")>0,COUNTBLANK($H18:$N18)>0,COUNTBLANK($Q18:$U18)>0,$AL18<>"Active",OR($AM18="Low",$AM18="Unverified"),AND($Y18="Manual award",$O18="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP18` | `=IF(OR($C18="",$AN18="FAIL"),0,IF($AE18>0,MIN(IF($Y18="Manual award",IF($O18="",0,$O18),IF($Y18="Tiered",MIN(MIN($X18,IF($AC18>0,$AC18,$X18),IF($AD18>0,($G18/$W18)*$AD18,$X18)),$AA18)*$Z18+MAX(MIN($X18,IF($AC18>0,$AC18,$X18),IF($AD18>0,($G18/$W18)*$AD18,$X18))-$AA18,0)*$AB18,MIN($X18,IF($AC18>0,$AC18,$X18),IF($AD18>0,($G18/$W18)*$AD18,$X18))*$Z18)),$AE18),IF($Y18="Manual award",IF($O18="",0,$O18),IF($Y18="Tiered",MIN(MIN($X18,IF($AC18>0,$AC18,$X18),IF($AD18>0,($G18/$W18)*$AD18,$X18)),$AA18)*$Z18+MAX(MIN($X18,IF($AC18>0,$AC18,$X18),IF($AD18>0,($G18/$W18)*$AD18,$X18))-$AA18,0)*$AB18,MIN($X18,IF($AC18>0,$AC18,$X18),IF($AD18>0,($G18/$W18)*$AD18,$X18))*$Z18))))` |
| `AQ18` | `=$AP18*$W18` |
| `AR18` | `=IF($C18="",0,$AP18*$AI18+($AP18*(1-$AI18))*$T18)` |
| `AS18` | `=IF($C18="",0,($AP18*(1-$AI18)*(1-$T18)*$R18*$S18*$Q18/12)+$U18+($AP18*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT18` | `=IF(OR($C18="",COUNTBLANK($Q18:$U18)>0),"",$AP18-$AR18-$AS18)` |
| `AU18` | `=IF(OR($C18="",COUNTBLANK($Q18:$U18)>0),"",((($AP18*(1-$AI18)*(1-$T18)*$R18)-(($AP18*(1-$AI18)*(1-$T18)*$R18*$S18*$Q18/12)+$U18+($AP18*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),0))))*$W18)+(($AP18*(1-$AI18)*(1-$T18)*(1-$R18)*$W18)/((1+'FX & Financing'!$J$6)^($Q18/12))))` |
| `AV18` | `=IF($C18="",0,$P18)` |
| `AW18` | `=IF($AU18="","",$AU18-$AV18)` |
| `AX18` | `=IFERROR($AW18/$F18,0)` |
| `AY18` | `=IF($C18="",0,IF($AX18>='FX & Financing'!$J$7,5,IF($AX18>='FX & Financing'!$J$8,4,IF($AX18>='FX & Financing'!$J$9,3,IF($AX18>0,2,1)))))` |
| `AZ18` | `=IF($C18="",0,MAX(1,IF($AM18="High",5,IF($AM18="Medium",3,IF($AM18="Low",2,1)))-IF($AN18="PRELIMINARY",1,IF($AN18="FAIL",4,0))))` |
| `BA18` | `=IF($C18="",0,$AY18*'FX & Financing'!$J$10+$AZ18*(1-'FX & Financing'!$J$10))` |
| `BB18` | `=IF($C18="","",IF($AN18="FAIL","Red",IF($AN18="PRELIMINARY","Amber",IF($BA18>=4,"Green",IF($BA18>=3.25,"Amber","Red")))))` |
| `BC18` | `=IF($C18="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C18,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V19` | `=IF($C19="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W19` | `=IF(OR($C19="",$E19="",$V19=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V19,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E19,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X19` | `=IF(OR($F19="",$W19=0),0,$F19/$W19)` |
| `Y19` | `=IF($C19="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI19` | `=IF($C19="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ19` | `=IF($C19="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK19` | `=IF($C19="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL19` | `=IF($C19="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM19` | `=IF($C19="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN19` | `=IF($C19="","",IF(OR($AL19="Closed",$AL19="Test only",COUNTIF($H19:$N19,"No")>0,AND($AK19<>"",IF($AK19="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK19="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK19="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ19<>"",COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,$AJ19)=0),AND($AF19>0,$X19<$AF19),AND($AG19>0,$G19/$W19<$AG19),AND($AH19>0,$G19/$W19>$AH19),AND($T19>0,$R19>0)),"FAIL",IF(OR(COUNTIF($H19:$N19,"Unknown")>0,COUNTBLANK($H19:$N19)>0,COUNTBLANK($Q19:$U19)>0,$AL19<>"Active",OR($AM19="Low",$AM19="Unverified"),AND($Y19="Manual award",$O19="")),"PRELIMINARY","PASS")))` |
| `AO19` | `=IF($C19="","",IF($AL19="Closed","Programme unavailable",IF(COUNTIF($H19:$N19,"No")>0,"Eligibility requirement not met",IF(AND($AK19<>"",IF($AK19="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK19="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK19="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ19<>"",COUNTIFS($A$6:$A$25,$A19,$C$6:$C$25,$AJ19)=0),"Required parent programme missing",IF(AND($AF19>0,$X19<$AF19),"Minimum programme spend not met",IF(AND($AG19>0,$G19/$W19<$AG19),"Minimum project cost not met",IF(AND($AH19>0,$G19/$W19>$AH19),"Maximum project cost exceeded",IF(AND($T19>0,$R19>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H19:$N19,"Unknown")>0,COUNTBLANK($H19:$N19)>0,COUNTBLANK($Q19:$U19)>0,$AL19<>"Active",OR($AM19="Low",$AM19="Unverified"),AND($Y19="Manual award",$O19="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP19` | `=IF(OR($C19="",$AN19="FAIL"),0,IF($AE19>0,MIN(IF($Y19="Manual award",IF($O19="",0,$O19),IF($Y19="Tiered",MIN(MIN($X19,IF($AC19>0,$AC19,$X19),IF($AD19>0,($G19/$W19)*$AD19,$X19)),$AA19)*$Z19+MAX(MIN($X19,IF($AC19>0,$AC19,$X19),IF($AD19>0,($G19/$W19)*$AD19,$X19))-$AA19,0)*$AB19,MIN($X19,IF($AC19>0,$AC19,$X19),IF($AD19>0,($G19/$W19)*$AD19,$X19))*$Z19)),$AE19),IF($Y19="Manual award",IF($O19="",0,$O19),IF($Y19="Tiered",MIN(MIN($X19,IF($AC19>0,$AC19,$X19),IF($AD19>0,($G19/$W19)*$AD19,$X19)),$AA19)*$Z19+MAX(MIN($X19,IF($AC19>0,$AC19,$X19),IF($AD19>0,($G19/$W19)*$AD19,$X19))-$AA19,0)*$AB19,MIN($X19,IF($AC19>0,$AC19,$X19),IF($AD19>0,($G19/$W19)*$AD19,$X19))*$Z19))))` |
| `AQ19` | `=$AP19*$W19` |
| `AR19` | `=IF($C19="",0,$AP19*$AI19+($AP19*(1-$AI19))*$T19)` |
| `AS19` | `=IF($C19="",0,($AP19*(1-$AI19)*(1-$T19)*$R19*$S19*$Q19/12)+$U19+($AP19*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT19` | `=IF(OR($C19="",COUNTBLANK($Q19:$U19)>0),"",$AP19-$AR19-$AS19)` |
| `AU19` | `=IF(OR($C19="",COUNTBLANK($Q19:$U19)>0),"",((($AP19*(1-$AI19)*(1-$T19)*$R19)-(($AP19*(1-$AI19)*(1-$T19)*$R19*$S19*$Q19/12)+$U19+($AP19*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),0))))*$W19)+(($AP19*(1-$AI19)*(1-$T19)*(1-$R19)*$W19)/((1+'FX & Financing'!$J$6)^($Q19/12))))` |
| `AV19` | `=IF($C19="",0,$P19)` |
| `AW19` | `=IF($AU19="","",$AU19-$AV19)` |
| `AX19` | `=IFERROR($AW19/$F19,0)` |
| `AY19` | `=IF($C19="",0,IF($AX19>='FX & Financing'!$J$7,5,IF($AX19>='FX & Financing'!$J$8,4,IF($AX19>='FX & Financing'!$J$9,3,IF($AX19>0,2,1)))))` |
| `AZ19` | `=IF($C19="",0,MAX(1,IF($AM19="High",5,IF($AM19="Medium",3,IF($AM19="Low",2,1)))-IF($AN19="PRELIMINARY",1,IF($AN19="FAIL",4,0))))` |
| `BA19` | `=IF($C19="",0,$AY19*'FX & Financing'!$J$10+$AZ19*(1-'FX & Financing'!$J$10))` |
| `BB19` | `=IF($C19="","",IF($AN19="FAIL","Red",IF($AN19="PRELIMINARY","Amber",IF($BA19>=4,"Green",IF($BA19>=3.25,"Amber","Red")))))` |
| `BC19` | `=IF($C19="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C19,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V20` | `=IF($C20="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W20` | `=IF(OR($C20="",$E20="",$V20=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V20,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E20,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X20` | `=IF(OR($F20="",$W20=0),0,$F20/$W20)` |
| `Y20` | `=IF($C20="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI20` | `=IF($C20="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ20` | `=IF($C20="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK20` | `=IF($C20="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL20` | `=IF($C20="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM20` | `=IF($C20="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN20` | `=IF($C20="","",IF(OR($AL20="Closed",$AL20="Test only",COUNTIF($H20:$N20,"No")>0,AND($AK20<>"",IF($AK20="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK20="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK20="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ20<>"",COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,$AJ20)=0),AND($AF20>0,$X20<$AF20),AND($AG20>0,$G20/$W20<$AG20),AND($AH20>0,$G20/$W20>$AH20),AND($T20>0,$R20>0)),"FAIL",IF(OR(COUNTIF($H20:$N20,"Unknown")>0,COUNTBLANK($H20:$N20)>0,COUNTBLANK($Q20:$U20)>0,$AL20<>"Active",OR($AM20="Low",$AM20="Unverified"),AND($Y20="Manual award",$O20="")),"PRELIMINARY","PASS")))` |
| `AO20` | `=IF($C20="","",IF($AL20="Closed","Programme unavailable",IF(COUNTIF($H20:$N20,"No")>0,"Eligibility requirement not met",IF(AND($AK20<>"",IF($AK20="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK20="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK20="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ20<>"",COUNTIFS($A$6:$A$25,$A20,$C$6:$C$25,$AJ20)=0),"Required parent programme missing",IF(AND($AF20>0,$X20<$AF20),"Minimum programme spend not met",IF(AND($AG20>0,$G20/$W20<$AG20),"Minimum project cost not met",IF(AND($AH20>0,$G20/$W20>$AH20),"Maximum project cost exceeded",IF(AND($T20>0,$R20>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H20:$N20,"Unknown")>0,COUNTBLANK($H20:$N20)>0,COUNTBLANK($Q20:$U20)>0,$AL20<>"Active",OR($AM20="Low",$AM20="Unverified"),AND($Y20="Manual award",$O20="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP20` | `=IF(OR($C20="",$AN20="FAIL"),0,IF($AE20>0,MIN(IF($Y20="Manual award",IF($O20="",0,$O20),IF($Y20="Tiered",MIN(MIN($X20,IF($AC20>0,$AC20,$X20),IF($AD20>0,($G20/$W20)*$AD20,$X20)),$AA20)*$Z20+MAX(MIN($X20,IF($AC20>0,$AC20,$X20),IF($AD20>0,($G20/$W20)*$AD20,$X20))-$AA20,0)*$AB20,MIN($X20,IF($AC20>0,$AC20,$X20),IF($AD20>0,($G20/$W20)*$AD20,$X20))*$Z20)),$AE20),IF($Y20="Manual award",IF($O20="",0,$O20),IF($Y20="Tiered",MIN(MIN($X20,IF($AC20>0,$AC20,$X20),IF($AD20>0,($G20/$W20)*$AD20,$X20)),$AA20)*$Z20+MAX(MIN($X20,IF($AC20>0,$AC20,$X20),IF($AD20>0,($G20/$W20)*$AD20,$X20))-$AA20,0)*$AB20,MIN($X20,IF($AC20>0,$AC20,$X20),IF($AD20>0,($G20/$W20)*$AD20,$X20))*$Z20))))` |
| `AQ20` | `=$AP20*$W20` |
| `AR20` | `=IF($C20="",0,$AP20*$AI20+($AP20*(1-$AI20))*$T20)` |
| `AS20` | `=IF($C20="",0,($AP20*(1-$AI20)*(1-$T20)*$R20*$S20*$Q20/12)+$U20+($AP20*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT20` | `=IF(OR($C20="",COUNTBLANK($Q20:$U20)>0),"",$AP20-$AR20-$AS20)` |
| `AU20` | `=IF(OR($C20="",COUNTBLANK($Q20:$U20)>0),"",((($AP20*(1-$AI20)*(1-$T20)*$R20)-(($AP20*(1-$AI20)*(1-$T20)*$R20*$S20*$Q20/12)+$U20+($AP20*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),0))))*$W20)+(($AP20*(1-$AI20)*(1-$T20)*(1-$R20)*$W20)/((1+'FX & Financing'!$J$6)^($Q20/12))))` |
| `AV20` | `=IF($C20="",0,$P20)` |
| `AW20` | `=IF($AU20="","",$AU20-$AV20)` |
| `AX20` | `=IFERROR($AW20/$F20,0)` |
| `AY20` | `=IF($C20="",0,IF($AX20>='FX & Financing'!$J$7,5,IF($AX20>='FX & Financing'!$J$8,4,IF($AX20>='FX & Financing'!$J$9,3,IF($AX20>0,2,1)))))` |
| `AZ20` | `=IF($C20="",0,MAX(1,IF($AM20="High",5,IF($AM20="Medium",3,IF($AM20="Low",2,1)))-IF($AN20="PRELIMINARY",1,IF($AN20="FAIL",4,0))))` |
| `BA20` | `=IF($C20="",0,$AY20*'FX & Financing'!$J$10+$AZ20*(1-'FX & Financing'!$J$10))` |
| `BB20` | `=IF($C20="","",IF($AN20="FAIL","Red",IF($AN20="PRELIMINARY","Amber",IF($BA20>=4,"Green",IF($BA20>=3.25,"Amber","Red")))))` |
| `BC20` | `=IF($C20="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C20,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V21` | `=IF($C21="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W21` | `=IF(OR($C21="",$E21="",$V21=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V21,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E21,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X21` | `=IF(OR($F21="",$W21=0),0,$F21/$W21)` |
| `Y21` | `=IF($C21="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI21` | `=IF($C21="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ21` | `=IF($C21="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK21` | `=IF($C21="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL21` | `=IF($C21="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM21` | `=IF($C21="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN21` | `=IF($C21="","",IF(OR($AL21="Closed",$AL21="Test only",COUNTIF($H21:$N21,"No")>0,AND($AK21<>"",IF($AK21="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK21="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK21="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ21<>"",COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,$AJ21)=0),AND($AF21>0,$X21<$AF21),AND($AG21>0,$G21/$W21<$AG21),AND($AH21>0,$G21/$W21>$AH21),AND($T21>0,$R21>0)),"FAIL",IF(OR(COUNTIF($H21:$N21,"Unknown")>0,COUNTBLANK($H21:$N21)>0,COUNTBLANK($Q21:$U21)>0,$AL21<>"Active",OR($AM21="Low",$AM21="Unverified"),AND($Y21="Manual award",$O21="")),"PRELIMINARY","PASS")))` |
| `AO21` | `=IF($C21="","",IF($AL21="Closed","Programme unavailable",IF(COUNTIF($H21:$N21,"No")>0,"Eligibility requirement not met",IF(AND($AK21<>"",IF($AK21="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK21="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK21="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ21<>"",COUNTIFS($A$6:$A$25,$A21,$C$6:$C$25,$AJ21)=0),"Required parent programme missing",IF(AND($AF21>0,$X21<$AF21),"Minimum programme spend not met",IF(AND($AG21>0,$G21/$W21<$AG21),"Minimum project cost not met",IF(AND($AH21>0,$G21/$W21>$AH21),"Maximum project cost exceeded",IF(AND($T21>0,$R21>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H21:$N21,"Unknown")>0,COUNTBLANK($H21:$N21)>0,COUNTBLANK($Q21:$U21)>0,$AL21<>"Active",OR($AM21="Low",$AM21="Unverified"),AND($Y21="Manual award",$O21="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP21` | `=IF(OR($C21="",$AN21="FAIL"),0,IF($AE21>0,MIN(IF($Y21="Manual award",IF($O21="",0,$O21),IF($Y21="Tiered",MIN(MIN($X21,IF($AC21>0,$AC21,$X21),IF($AD21>0,($G21/$W21)*$AD21,$X21)),$AA21)*$Z21+MAX(MIN($X21,IF($AC21>0,$AC21,$X21),IF($AD21>0,($G21/$W21)*$AD21,$X21))-$AA21,0)*$AB21,MIN($X21,IF($AC21>0,$AC21,$X21),IF($AD21>0,($G21/$W21)*$AD21,$X21))*$Z21)),$AE21),IF($Y21="Manual award",IF($O21="",0,$O21),IF($Y21="Tiered",MIN(MIN($X21,IF($AC21>0,$AC21,$X21),IF($AD21>0,($G21/$W21)*$AD21,$X21)),$AA21)*$Z21+MAX(MIN($X21,IF($AC21>0,$AC21,$X21),IF($AD21>0,($G21/$W21)*$AD21,$X21))-$AA21,0)*$AB21,MIN($X21,IF($AC21>0,$AC21,$X21),IF($AD21>0,($G21/$W21)*$AD21,$X21))*$Z21))))` |
| `AQ21` | `=$AP21*$W21` |
| `AR21` | `=IF($C21="",0,$AP21*$AI21+($AP21*(1-$AI21))*$T21)` |
| `AS21` | `=IF($C21="",0,($AP21*(1-$AI21)*(1-$T21)*$R21*$S21*$Q21/12)+$U21+($AP21*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT21` | `=IF(OR($C21="",COUNTBLANK($Q21:$U21)>0),"",$AP21-$AR21-$AS21)` |
| `AU21` | `=IF(OR($C21="",COUNTBLANK($Q21:$U21)>0),"",((($AP21*(1-$AI21)*(1-$T21)*$R21)-(($AP21*(1-$AI21)*(1-$T21)*$R21*$S21*$Q21/12)+$U21+($AP21*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),0))))*$W21)+(($AP21*(1-$AI21)*(1-$T21)*(1-$R21)*$W21)/((1+'FX & Financing'!$J$6)^($Q21/12))))` |
| `AV21` | `=IF($C21="",0,$P21)` |
| `AW21` | `=IF($AU21="","",$AU21-$AV21)` |
| `AX21` | `=IFERROR($AW21/$F21,0)` |
| `AY21` | `=IF($C21="",0,IF($AX21>='FX & Financing'!$J$7,5,IF($AX21>='FX & Financing'!$J$8,4,IF($AX21>='FX & Financing'!$J$9,3,IF($AX21>0,2,1)))))` |
| `AZ21` | `=IF($C21="",0,MAX(1,IF($AM21="High",5,IF($AM21="Medium",3,IF($AM21="Low",2,1)))-IF($AN21="PRELIMINARY",1,IF($AN21="FAIL",4,0))))` |
| `BA21` | `=IF($C21="",0,$AY21*'FX & Financing'!$J$10+$AZ21*(1-'FX & Financing'!$J$10))` |
| `BB21` | `=IF($C21="","",IF($AN21="FAIL","Red",IF($AN21="PRELIMINARY","Amber",IF($BA21>=4,"Green",IF($BA21>=3.25,"Amber","Red")))))` |
| `BC21` | `=IF($C21="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C21,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V22` | `=IF($C22="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W22` | `=IF(OR($C22="",$E22="",$V22=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V22,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E22,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X22` | `=IF(OR($F22="",$W22=0),0,$F22/$W22)` |
| `Y22` | `=IF($C22="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI22` | `=IF($C22="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ22` | `=IF($C22="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK22` | `=IF($C22="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL22` | `=IF($C22="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM22` | `=IF($C22="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN22` | `=IF($C22="","",IF(OR($AL22="Closed",$AL22="Test only",COUNTIF($H22:$N22,"No")>0,AND($AK22<>"",IF($AK22="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK22="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK22="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ22<>"",COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,$AJ22)=0),AND($AF22>0,$X22<$AF22),AND($AG22>0,$G22/$W22<$AG22),AND($AH22>0,$G22/$W22>$AH22),AND($T22>0,$R22>0)),"FAIL",IF(OR(COUNTIF($H22:$N22,"Unknown")>0,COUNTBLANK($H22:$N22)>0,COUNTBLANK($Q22:$U22)>0,$AL22<>"Active",OR($AM22="Low",$AM22="Unverified"),AND($Y22="Manual award",$O22="")),"PRELIMINARY","PASS")))` |
| `AO22` | `=IF($C22="","",IF($AL22="Closed","Programme unavailable",IF(COUNTIF($H22:$N22,"No")>0,"Eligibility requirement not met",IF(AND($AK22<>"",IF($AK22="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK22="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK22="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ22<>"",COUNTIFS($A$6:$A$25,$A22,$C$6:$C$25,$AJ22)=0),"Required parent programme missing",IF(AND($AF22>0,$X22<$AF22),"Minimum programme spend not met",IF(AND($AG22>0,$G22/$W22<$AG22),"Minimum project cost not met",IF(AND($AH22>0,$G22/$W22>$AH22),"Maximum project cost exceeded",IF(AND($T22>0,$R22>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H22:$N22,"Unknown")>0,COUNTBLANK($H22:$N22)>0,COUNTBLANK($Q22:$U22)>0,$AL22<>"Active",OR($AM22="Low",$AM22="Unverified"),AND($Y22="Manual award",$O22="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP22` | `=IF(OR($C22="",$AN22="FAIL"),0,IF($AE22>0,MIN(IF($Y22="Manual award",IF($O22="",0,$O22),IF($Y22="Tiered",MIN(MIN($X22,IF($AC22>0,$AC22,$X22),IF($AD22>0,($G22/$W22)*$AD22,$X22)),$AA22)*$Z22+MAX(MIN($X22,IF($AC22>0,$AC22,$X22),IF($AD22>0,($G22/$W22)*$AD22,$X22))-$AA22,0)*$AB22,MIN($X22,IF($AC22>0,$AC22,$X22),IF($AD22>0,($G22/$W22)*$AD22,$X22))*$Z22)),$AE22),IF($Y22="Manual award",IF($O22="",0,$O22),IF($Y22="Tiered",MIN(MIN($X22,IF($AC22>0,$AC22,$X22),IF($AD22>0,($G22/$W22)*$AD22,$X22)),$AA22)*$Z22+MAX(MIN($X22,IF($AC22>0,$AC22,$X22),IF($AD22>0,($G22/$W22)*$AD22,$X22))-$AA22,0)*$AB22,MIN($X22,IF($AC22>0,$AC22,$X22),IF($AD22>0,($G22/$W22)*$AD22,$X22))*$Z22))))` |
| `AQ22` | `=$AP22*$W22` |
| `AR22` | `=IF($C22="",0,$AP22*$AI22+($AP22*(1-$AI22))*$T22)` |
| `AS22` | `=IF($C22="",0,($AP22*(1-$AI22)*(1-$T22)*$R22*$S22*$Q22/12)+$U22+($AP22*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT22` | `=IF(OR($C22="",COUNTBLANK($Q22:$U22)>0),"",$AP22-$AR22-$AS22)` |
| `AU22` | `=IF(OR($C22="",COUNTBLANK($Q22:$U22)>0),"",((($AP22*(1-$AI22)*(1-$T22)*$R22)-(($AP22*(1-$AI22)*(1-$T22)*$R22*$S22*$Q22/12)+$U22+($AP22*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),0))))*$W22)+(($AP22*(1-$AI22)*(1-$T22)*(1-$R22)*$W22)/((1+'FX & Financing'!$J$6)^($Q22/12))))` |
| `AV22` | `=IF($C22="",0,$P22)` |
| `AW22` | `=IF($AU22="","",$AU22-$AV22)` |
| `AX22` | `=IFERROR($AW22/$F22,0)` |
| `AY22` | `=IF($C22="",0,IF($AX22>='FX & Financing'!$J$7,5,IF($AX22>='FX & Financing'!$J$8,4,IF($AX22>='FX & Financing'!$J$9,3,IF($AX22>0,2,1)))))` |
| `AZ22` | `=IF($C22="",0,MAX(1,IF($AM22="High",5,IF($AM22="Medium",3,IF($AM22="Low",2,1)))-IF($AN22="PRELIMINARY",1,IF($AN22="FAIL",4,0))))` |
| `BA22` | `=IF($C22="",0,$AY22*'FX & Financing'!$J$10+$AZ22*(1-'FX & Financing'!$J$10))` |
| `BB22` | `=IF($C22="","",IF($AN22="FAIL","Red",IF($AN22="PRELIMINARY","Amber",IF($BA22>=4,"Green",IF($BA22>=3.25,"Amber","Red")))))` |
| `BC22` | `=IF($C22="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C22,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V23` | `=IF($C23="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W23` | `=IF(OR($C23="",$E23="",$V23=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V23,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E23,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X23` | `=IF(OR($F23="",$W23=0),0,$F23/$W23)` |
| `Y23` | `=IF($C23="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI23` | `=IF($C23="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ23` | `=IF($C23="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK23` | `=IF($C23="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL23` | `=IF($C23="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM23` | `=IF($C23="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN23` | `=IF($C23="","",IF(OR($AL23="Closed",$AL23="Test only",COUNTIF($H23:$N23,"No")>0,AND($AK23<>"",IF($AK23="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK23="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK23="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ23<>"",COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,$AJ23)=0),AND($AF23>0,$X23<$AF23),AND($AG23>0,$G23/$W23<$AG23),AND($AH23>0,$G23/$W23>$AH23),AND($T23>0,$R23>0)),"FAIL",IF(OR(COUNTIF($H23:$N23,"Unknown")>0,COUNTBLANK($H23:$N23)>0,COUNTBLANK($Q23:$U23)>0,$AL23<>"Active",OR($AM23="Low",$AM23="Unverified"),AND($Y23="Manual award",$O23="")),"PRELIMINARY","PASS")))` |
| `AO23` | `=IF($C23="","",IF($AL23="Closed","Programme unavailable",IF(COUNTIF($H23:$N23,"No")>0,"Eligibility requirement not met",IF(AND($AK23<>"",IF($AK23="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK23="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK23="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ23<>"",COUNTIFS($A$6:$A$25,$A23,$C$6:$C$25,$AJ23)=0),"Required parent programme missing",IF(AND($AF23>0,$X23<$AF23),"Minimum programme spend not met",IF(AND($AG23>0,$G23/$W23<$AG23),"Minimum project cost not met",IF(AND($AH23>0,$G23/$W23>$AH23),"Maximum project cost exceeded",IF(AND($T23>0,$R23>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H23:$N23,"Unknown")>0,COUNTBLANK($H23:$N23)>0,COUNTBLANK($Q23:$U23)>0,$AL23<>"Active",OR($AM23="Low",$AM23="Unverified"),AND($Y23="Manual award",$O23="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP23` | `=IF(OR($C23="",$AN23="FAIL"),0,IF($AE23>0,MIN(IF($Y23="Manual award",IF($O23="",0,$O23),IF($Y23="Tiered",MIN(MIN($X23,IF($AC23>0,$AC23,$X23),IF($AD23>0,($G23/$W23)*$AD23,$X23)),$AA23)*$Z23+MAX(MIN($X23,IF($AC23>0,$AC23,$X23),IF($AD23>0,($G23/$W23)*$AD23,$X23))-$AA23,0)*$AB23,MIN($X23,IF($AC23>0,$AC23,$X23),IF($AD23>0,($G23/$W23)*$AD23,$X23))*$Z23)),$AE23),IF($Y23="Manual award",IF($O23="",0,$O23),IF($Y23="Tiered",MIN(MIN($X23,IF($AC23>0,$AC23,$X23),IF($AD23>0,($G23/$W23)*$AD23,$X23)),$AA23)*$Z23+MAX(MIN($X23,IF($AC23>0,$AC23,$X23),IF($AD23>0,($G23/$W23)*$AD23,$X23))-$AA23,0)*$AB23,MIN($X23,IF($AC23>0,$AC23,$X23),IF($AD23>0,($G23/$W23)*$AD23,$X23))*$Z23))))` |
| `AQ23` | `=$AP23*$W23` |
| `AR23` | `=IF($C23="",0,$AP23*$AI23+($AP23*(1-$AI23))*$T23)` |
| `AS23` | `=IF($C23="",0,($AP23*(1-$AI23)*(1-$T23)*$R23*$S23*$Q23/12)+$U23+($AP23*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT23` | `=IF(OR($C23="",COUNTBLANK($Q23:$U23)>0),"",$AP23-$AR23-$AS23)` |
| `AU23` | `=IF(OR($C23="",COUNTBLANK($Q23:$U23)>0),"",((($AP23*(1-$AI23)*(1-$T23)*$R23)-(($AP23*(1-$AI23)*(1-$T23)*$R23*$S23*$Q23/12)+$U23+($AP23*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),0))))*$W23)+(($AP23*(1-$AI23)*(1-$T23)*(1-$R23)*$W23)/((1+'FX & Financing'!$J$6)^($Q23/12))))` |
| `AV23` | `=IF($C23="",0,$P23)` |
| `AW23` | `=IF($AU23="","",$AU23-$AV23)` |
| `AX23` | `=IFERROR($AW23/$F23,0)` |
| `AY23` | `=IF($C23="",0,IF($AX23>='FX & Financing'!$J$7,5,IF($AX23>='FX & Financing'!$J$8,4,IF($AX23>='FX & Financing'!$J$9,3,IF($AX23>0,2,1)))))` |
| `AZ23` | `=IF($C23="",0,MAX(1,IF($AM23="High",5,IF($AM23="Medium",3,IF($AM23="Low",2,1)))-IF($AN23="PRELIMINARY",1,IF($AN23="FAIL",4,0))))` |
| `BA23` | `=IF($C23="",0,$AY23*'FX & Financing'!$J$10+$AZ23*(1-'FX & Financing'!$J$10))` |
| `BB23` | `=IF($C23="","",IF($AN23="FAIL","Red",IF($AN23="PRELIMINARY","Amber",IF($BA23>=4,"Green",IF($BA23>=3.25,"Amber","Red")))))` |
| `BC23` | `=IF($C23="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C23,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V24` | `=IF($C24="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W24` | `=IF(OR($C24="",$E24="",$V24=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V24,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E24,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X24` | `=IF(OR($F24="",$W24=0),0,$F24/$W24)` |
| `Y24` | `=IF($C24="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI24` | `=IF($C24="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ24` | `=IF($C24="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK24` | `=IF($C24="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL24` | `=IF($C24="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM24` | `=IF($C24="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN24` | `=IF($C24="","",IF(OR($AL24="Closed",$AL24="Test only",COUNTIF($H24:$N24,"No")>0,AND($AK24<>"",IF($AK24="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK24="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK24="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ24<>"",COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,$AJ24)=0),AND($AF24>0,$X24<$AF24),AND($AG24>0,$G24/$W24<$AG24),AND($AH24>0,$G24/$W24>$AH24),AND($T24>0,$R24>0)),"FAIL",IF(OR(COUNTIF($H24:$N24,"Unknown")>0,COUNTBLANK($H24:$N24)>0,COUNTBLANK($Q24:$U24)>0,$AL24<>"Active",OR($AM24="Low",$AM24="Unverified"),AND($Y24="Manual award",$O24="")),"PRELIMINARY","PASS")))` |
| `AO24` | `=IF($C24="","",IF($AL24="Closed","Programme unavailable",IF(COUNTIF($H24:$N24,"No")>0,"Eligibility requirement not met",IF(AND($AK24<>"",IF($AK24="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK24="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK24="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ24<>"",COUNTIFS($A$6:$A$25,$A24,$C$6:$C$25,$AJ24)=0),"Required parent programme missing",IF(AND($AF24>0,$X24<$AF24),"Minimum programme spend not met",IF(AND($AG24>0,$G24/$W24<$AG24),"Minimum project cost not met",IF(AND($AH24>0,$G24/$W24>$AH24),"Maximum project cost exceeded",IF(AND($T24>0,$R24>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H24:$N24,"Unknown")>0,COUNTBLANK($H24:$N24)>0,COUNTBLANK($Q24:$U24)>0,$AL24<>"Active",OR($AM24="Low",$AM24="Unverified"),AND($Y24="Manual award",$O24="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP24` | `=IF(OR($C24="",$AN24="FAIL"),0,IF($AE24>0,MIN(IF($Y24="Manual award",IF($O24="",0,$O24),IF($Y24="Tiered",MIN(MIN($X24,IF($AC24>0,$AC24,$X24),IF($AD24>0,($G24/$W24)*$AD24,$X24)),$AA24)*$Z24+MAX(MIN($X24,IF($AC24>0,$AC24,$X24),IF($AD24>0,($G24/$W24)*$AD24,$X24))-$AA24,0)*$AB24,MIN($X24,IF($AC24>0,$AC24,$X24),IF($AD24>0,($G24/$W24)*$AD24,$X24))*$Z24)),$AE24),IF($Y24="Manual award",IF($O24="",0,$O24),IF($Y24="Tiered",MIN(MIN($X24,IF($AC24>0,$AC24,$X24),IF($AD24>0,($G24/$W24)*$AD24,$X24)),$AA24)*$Z24+MAX(MIN($X24,IF($AC24>0,$AC24,$X24),IF($AD24>0,($G24/$W24)*$AD24,$X24))-$AA24,0)*$AB24,MIN($X24,IF($AC24>0,$AC24,$X24),IF($AD24>0,($G24/$W24)*$AD24,$X24))*$Z24))))` |
| `AQ24` | `=$AP24*$W24` |
| `AR24` | `=IF($C24="",0,$AP24*$AI24+($AP24*(1-$AI24))*$T24)` |
| `AS24` | `=IF($C24="",0,($AP24*(1-$AI24)*(1-$T24)*$R24*$S24*$Q24/12)+$U24+($AP24*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT24` | `=IF(OR($C24="",COUNTBLANK($Q24:$U24)>0),"",$AP24-$AR24-$AS24)` |
| `AU24` | `=IF(OR($C24="",COUNTBLANK($Q24:$U24)>0),"",((($AP24*(1-$AI24)*(1-$T24)*$R24)-(($AP24*(1-$AI24)*(1-$T24)*$R24*$S24*$Q24/12)+$U24+($AP24*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),0))))*$W24)+(($AP24*(1-$AI24)*(1-$T24)*(1-$R24)*$W24)/((1+'FX & Financing'!$J$6)^($Q24/12))))` |
| `AV24` | `=IF($C24="",0,$P24)` |
| `AW24` | `=IF($AU24="","",$AU24-$AV24)` |
| `AX24` | `=IFERROR($AW24/$F24,0)` |
| `AY24` | `=IF($C24="",0,IF($AX24>='FX & Financing'!$J$7,5,IF($AX24>='FX & Financing'!$J$8,4,IF($AX24>='FX & Financing'!$J$9,3,IF($AX24>0,2,1)))))` |
| `AZ24` | `=IF($C24="",0,MAX(1,IF($AM24="High",5,IF($AM24="Medium",3,IF($AM24="Low",2,1)))-IF($AN24="PRELIMINARY",1,IF($AN24="FAIL",4,0))))` |
| `BA24` | `=IF($C24="",0,$AY24*'FX & Financing'!$J$10+$AZ24*(1-'FX & Financing'!$J$10))` |
| `BB24` | `=IF($C24="","",IF($AN24="FAIL","Red",IF($AN24="PRELIMINARY","Amber",IF($BA24>=4,"Green",IF($BA24>=3.25,"Amber","Red")))))` |
| `BC24` | `=IF($C24="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C24,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `V25` | `=IF($C25="","",IFERROR(INDEX('Programme Rules'!$E$5:$E$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `W25` | `=IF(OR($C25="",$E25="",$V25=""),0,IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($V25,'FX & Financing'!$A$5:$A$20,0)),0)/IFERROR(INDEX('FX & Financing'!$B$5:$B$20,MATCH($E25,'FX & Financing'!$A$5:$A$20,0)),0))` |
| `X25` | `=IF(OR($F25="",$W25=0),0,$F25/$W25)` |
| `Y25` | `=IF($C25="","",IFERROR(INDEX('Programme Rules'!$I$5:$I$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `Z25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$K$5:$K$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AA25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$L$5:$L$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AB25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$M$5:$M$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AC25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$N$5:$N$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AD25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$O$5:$O$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AE25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$P$5:$P$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AF25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$Q$5:$Q$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AG25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$R$5:$R$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AH25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$S$5:$S$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AI25` | `=IF($C25="",0,IFERROR(INDEX('Programme Rules'!$U$5:$U$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))` |
| `AJ25` | `=IF($C25="","",IFERROR(INDEX('Programme Rules'!$V$5:$V$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AK25` | `=IF($C25="","",IFERROR(INDEX('Programme Rules'!$X$5:$X$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AL25` | `=IF($C25="","",IFERROR(INDEX('Programme Rules'!$H$5:$H$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AM25` | `=IF($C25="","",IFERROR(INDEX('Programme Rules'!$AE$5:$AE$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),""))` |
| `AN25` | `=IF($C25="","",IF(OR($AL25="Closed",$AL25="Test only",COUNTIF($H25:$N25,"No")>0,AND($AK25<>"",IF($AK25="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK25="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK25="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),AND($AJ25<>"",COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,$AJ25)=0),AND($AF25>0,$X25<$AF25),AND($AG25>0,$G25/$W25<$AG25),AND($AH25>0,$G25/$W25>$AH25),AND($T25>0,$R25>0)),"FAIL",IF(OR(COUNTIF($H25:$N25,"Unknown")>0,COUNTBLANK($H25:$N25)>0,COUNTBLANK($Q25:$U25)>0,$AL25<>"Active",OR($AM25="Low",$AM25="Unverified"),AND($Y25="Manual award",$O25="")),"PRELIMINARY","PASS")))` |
| `AO25` | `=IF($C25="","",IF($AL25="Closed","Programme unavailable",IF(COUNTIF($H25:$N25,"No")>0,"Eligibility requirement not met",IF(AND($AK25<>"",IF($AK25="AUS-FED-OFFSET",COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"AUS-LOC")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"AUS-PDV")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"AUS-PROD-FEAT")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"AUS-PROD-OTHER"),IF($AK25="CAN-FED-ROUTE",COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"CAN-FED-CPTC")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"CAN-FED-PSTC"),IF($AK25="CAN-MB-ELECTION",COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"CAN-MB-ALL")+COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,"CAN-MB-LAB"),0)))>1),"Mutually exclusive programme election",IF(AND($AJ25<>"",COUNTIFS($A$6:$A$25,$A25,$C$6:$C$25,$AJ25)=0),"Required parent programme missing",IF(AND($AF25>0,$X25<$AF25),"Minimum programme spend not met",IF(AND($AG25>0,$G25/$W25<$AG25),"Minimum project cost not met",IF(AND($AH25>0,$G25/$W25>$AH25),"Maximum project cost exceeded",IF(AND($T25>0,$R25>0),"Borrowing and transfer inputs conflict",IF(OR(COUNTIF($H25:$N25,"Unknown")>0,COUNTBLANK($H25:$N25)>0,COUNTBLANK($Q25:$U25)>0,$AL25<>"Active",OR($AM25="Low",$AM25="Unverified"),AND($Y25="Manual award",$O25="")),"Eligibility, availability or commercial inputs unconfirmed","Eligible subject to evidence"))))))))))` |
| `AP25` | `=IF(OR($C25="",$AN25="FAIL"),0,IF($AE25>0,MIN(IF($Y25="Manual award",IF($O25="",0,$O25),IF($Y25="Tiered",MIN(MIN($X25,IF($AC25>0,$AC25,$X25),IF($AD25>0,($G25/$W25)*$AD25,$X25)),$AA25)*$Z25+MAX(MIN($X25,IF($AC25>0,$AC25,$X25),IF($AD25>0,($G25/$W25)*$AD25,$X25))-$AA25,0)*$AB25,MIN($X25,IF($AC25>0,$AC25,$X25),IF($AD25>0,($G25/$W25)*$AD25,$X25))*$Z25)),$AE25),IF($Y25="Manual award",IF($O25="",0,$O25),IF($Y25="Tiered",MIN(MIN($X25,IF($AC25>0,$AC25,$X25),IF($AD25>0,($G25/$W25)*$AD25,$X25)),$AA25)*$Z25+MAX(MIN($X25,IF($AC25>0,$AC25,$X25),IF($AD25>0,($G25/$W25)*$AD25,$X25))-$AA25,0)*$AB25,MIN($X25,IF($AC25>0,$AC25,$X25),IF($AD25>0,($G25/$W25)*$AD25,$X25))*$Z25))))` |
| `AQ25` | `=$AP25*$W25` |
| `AR25` | `=IF($C25="",0,$AP25*$AI25+($AP25*(1-$AI25))*$T25)` |
| `AS25` | `=IF($C25="",0,($AP25*(1-$AI25)*(1-$T25)*$R25*$S25*$Q25/12)+$U25+($AP25*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0)))` |
| `AT25` | `=IF(OR($C25="",COUNTBLANK($Q25:$U25)>0),"",$AP25-$AR25-$AS25)` |
| `AU25` | `=IF(OR($C25="",COUNTBLANK($Q25:$U25)>0),"",((($AP25*(1-$AI25)*(1-$T25)*$R25)-(($AP25*(1-$AI25)*(1-$T25)*$R25*$S25*$Q25/12)+$U25+($AP25*IFERROR(INDEX('Programme Rules'!$AB$5:$AB$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),0))))*$W25)+(($AP25*(1-$AI25)*(1-$T25)*(1-$R25)*$W25)/((1+'FX & Financing'!$J$6)^($Q25/12))))` |
| `AV25` | `=IF($C25="",0,$P25)` |
| `AW25` | `=IF($AU25="","",$AU25-$AV25)` |
| `AX25` | `=IFERROR($AW25/$F25,0)` |
| `AY25` | `=IF($C25="",0,IF($AX25>='FX & Financing'!$J$7,5,IF($AX25>='FX & Financing'!$J$8,4,IF($AX25>='FX & Financing'!$J$9,3,IF($AX25>0,2,1)))))` |
| `AZ25` | `=IF($C25="",0,MAX(1,IF($AM25="High",5,IF($AM25="Medium",3,IF($AM25="Low",2,1)))-IF($AN25="PRELIMINARY",1,IF($AN25="FAIL",4,0))))` |
| `BA25` | `=IF($C25="",0,$AY25*'FX & Financing'!$J$10+$AZ25*(1-'FX & Financing'!$J$10))` |
| `BB25` | `=IF($C25="","",IF($AN25="FAIL","Red",IF($AN25="PRELIMINARY","Amber",IF($BA25>=4,"Green",IF($BA25>=3.25,"Amber","Red")))))` |
| `BC25` | `=IF($C25="","",IFERROR(INDEX('Programme Rules'!$AF$5:$AF$90,MATCH($C25,'Programme Rules'!$A$5:$A$90,0)),""))` |

### Sheet: `Scoring`
Formula count: **28**

| Cell | Formula |
|---|---|
| `D6` | `='Output Summary'!J6` |
| `E6` | `='Output Summary'!J7` |
| `F6` | `='Output Summary'!J8` |
| `G6` | `='Output Summary'!J9` |
| `H6` | `='Output Summary'!J10` |
| `I6` | `='Output Summary'!J11` |
| `J6` | `='Output Summary'!J12` |
| `D7` | `='Output Summary'!K6` |
| `E7` | `='Output Summary'!K7` |
| `F7` | `='Output Summary'!K8` |
| `G7` | `='Output Summary'!K9` |
| `H7` | `='Output Summary'!K10` |
| `I7` | `='Output Summary'!K11` |
| `J7` | `='Output Summary'!K12` |
| `D18` | `=SUMPRODUCT($B$6:$B$17,D$6:D$17)` |
| `E18` | `=SUMPRODUCT($B$6:$B$17,E$6:E$17)` |
| `F18` | `=SUMPRODUCT($B$6:$B$17,F$6:F$17)` |
| `G18` | `=SUMPRODUCT($B$6:$B$17,G$6:G$17)` |
| `H18` | `=SUMPRODUCT($B$6:$B$17,H$6:H$17)` |
| `I18` | `=SUMPRODUCT($B$6:$B$17,I$6:I$17)` |
| `J18` | `=SUMPRODUCT($B$6:$B$17,J$6:J$17)` |
| `D19` | `=IF('Output Summary'!D6="FAIL","Red",IF('Output Summary'!D6="PRELIMINARY","Amber",IF(D18>=4,"Green",IF(D18>=3.25,"Amber","Red"))))` |
| `E19` | `=IF('Output Summary'!D7="FAIL","Red",IF('Output Summary'!D7="PRELIMINARY","Amber",IF(E18>=4,"Green",IF(E18>=3.25,"Amber","Red"))))` |
| `F19` | `=IF('Output Summary'!D8="FAIL","Red",IF('Output Summary'!D8="PRELIMINARY","Amber",IF(F18>=4,"Green",IF(F18>=3.25,"Amber","Red"))))` |
| `G19` | `=IF('Output Summary'!D9="FAIL","Red",IF('Output Summary'!D9="PRELIMINARY","Amber",IF(G18>=4,"Green",IF(G18>=3.25,"Amber","Red"))))` |
| `H19` | `=IF('Output Summary'!D10="FAIL","Red",IF('Output Summary'!D10="PRELIMINARY","Amber",IF(H18>=4,"Green",IF(H18>=3.25,"Amber","Red"))))` |
| `I19` | `=IF('Output Summary'!D11="FAIL","Red",IF('Output Summary'!D11="PRELIMINARY","Amber",IF(I18>=4,"Green",IF(I18>=3.25,"Amber","Red"))))` |
| `J19` | `=IF('Output Summary'!D12="FAIL","Red",IF('Output Summary'!D12="PRELIMINARY","Amber",IF(J18>=4,"Green",IF(J18>=3.25,"Amber","Red"))))` |

### Sheet: `Output Summary`
Formula count: **91**

| Cell | Formula |
|---|---|
| `A6` | `=IF($B6="","",RANK($H6,$H$6:$H$12,0))` |
| `C6` | `=COUNTIF('Scenario Engine'!$A$6:$A$25,$B6)` |
| `D6` | `=IF($B6="","",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B6,'Scenario Engine'!$AN$6:$AN$25,"FAIL")>0,"FAIL",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B6,'Scenario Engine'!$AN$6:$AN$25,"PRELIMINARY")>0,"PRELIMINARY","PASS")))` |
| `E6` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B6,'Scenario Engine'!$AQ$6:$AQ$25)` |
| `F6` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B6,'Scenario Engine'!$AU$6:$AU$25)` |
| `G6` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B6,'Scenario Engine'!$AV$6:$AV$25)` |
| `H6` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B6,'Scenario Engine'!$AW$6:$AW$25)` |
| `I6` | `=IFERROR($H6/SUMIF('Scenario Engine'!$A$6:$A$25,$B6,'Scenario Engine'!$F$6:$F$25),0)` |
| `J6` | `=IF($I6>='FX & Financing'!$J$7,5,IF($I6>='FX & Financing'!$J$8,4,IF($I6>='FX & Financing'!$J$9,3,IF($I6>0,2,1))))` |
| `K6` | `=IF($D6="FAIL",1,IF($D6="PRELIMINARY",3,5))` |
| `L6` | `=INDEX(Scoring!$D$18:$J$18,1,ROW()-5)` |
| `M6` | `=INDEX(Scoring!$D$19:$J$19,1,ROW()-5)` |
| `N6` | `=IF($D6="FAIL","Do not rely: a hard gate failed",IF($D6="PRELIMINARY","Conditional only: resolve open gates and commercial assumptions","Eligible subject to final evidence and source re-verification"))` |
| `A7` | `=IF($B7="","",RANK($H7,$H$6:$H$12,0))` |
| `C7` | `=COUNTIF('Scenario Engine'!$A$6:$A$25,$B7)` |
| `D7` | `=IF($B7="","",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B7,'Scenario Engine'!$AN$6:$AN$25,"FAIL")>0,"FAIL",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B7,'Scenario Engine'!$AN$6:$AN$25,"PRELIMINARY")>0,"PRELIMINARY","PASS")))` |
| `E7` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B7,'Scenario Engine'!$AQ$6:$AQ$25)` |
| `F7` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B7,'Scenario Engine'!$AU$6:$AU$25)` |
| `G7` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B7,'Scenario Engine'!$AV$6:$AV$25)` |
| `H7` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B7,'Scenario Engine'!$AW$6:$AW$25)` |
| `I7` | `=IFERROR($H7/SUMIF('Scenario Engine'!$A$6:$A$25,$B7,'Scenario Engine'!$F$6:$F$25),0)` |
| `J7` | `=IF($I7>='FX & Financing'!$J$7,5,IF($I7>='FX & Financing'!$J$8,4,IF($I7>='FX & Financing'!$J$9,3,IF($I7>0,2,1))))` |
| `K7` | `=IF($D7="FAIL",1,IF($D7="PRELIMINARY",3,5))` |
| `L7` | `=INDEX(Scoring!$D$18:$J$18,1,ROW()-5)` |
| `M7` | `=INDEX(Scoring!$D$19:$J$19,1,ROW()-5)` |
| `N7` | `=IF($D7="FAIL","Do not rely: a hard gate failed",IF($D7="PRELIMINARY","Conditional only: resolve open gates and commercial assumptions","Eligible subject to final evidence and source re-verification"))` |
| `A8` | `=IF($B8="","",RANK($H8,$H$6:$H$12,0))` |
| `C8` | `=COUNTIF('Scenario Engine'!$A$6:$A$25,$B8)` |
| `D8` | `=IF($B8="","",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B8,'Scenario Engine'!$AN$6:$AN$25,"FAIL")>0,"FAIL",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B8,'Scenario Engine'!$AN$6:$AN$25,"PRELIMINARY")>0,"PRELIMINARY","PASS")))` |
| `E8` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B8,'Scenario Engine'!$AQ$6:$AQ$25)` |
| `F8` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B8,'Scenario Engine'!$AU$6:$AU$25)` |
| `G8` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B8,'Scenario Engine'!$AV$6:$AV$25)` |
| `H8` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B8,'Scenario Engine'!$AW$6:$AW$25)` |
| `I8` | `=IFERROR($H8/SUMIF('Scenario Engine'!$A$6:$A$25,$B8,'Scenario Engine'!$F$6:$F$25),0)` |
| `J8` | `=IF($I8>='FX & Financing'!$J$7,5,IF($I8>='FX & Financing'!$J$8,4,IF($I8>='FX & Financing'!$J$9,3,IF($I8>0,2,1))))` |
| `K8` | `=IF($D8="FAIL",1,IF($D8="PRELIMINARY",3,5))` |
| `L8` | `=INDEX(Scoring!$D$18:$J$18,1,ROW()-5)` |
| `M8` | `=INDEX(Scoring!$D$19:$J$19,1,ROW()-5)` |
| `N8` | `=IF($D8="FAIL","Do not rely: a hard gate failed",IF($D8="PRELIMINARY","Conditional only: resolve open gates and commercial assumptions","Eligible subject to final evidence and source re-verification"))` |
| `A9` | `=IF($B9="","",RANK($H9,$H$6:$H$12,0))` |
| `C9` | `=COUNTIF('Scenario Engine'!$A$6:$A$25,$B9)` |
| `D9` | `=IF($B9="","",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B9,'Scenario Engine'!$AN$6:$AN$25,"FAIL")>0,"FAIL",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B9,'Scenario Engine'!$AN$6:$AN$25,"PRELIMINARY")>0,"PRELIMINARY","PASS")))` |
| `E9` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B9,'Scenario Engine'!$AQ$6:$AQ$25)` |
| `F9` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B9,'Scenario Engine'!$AU$6:$AU$25)` |
| `G9` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B9,'Scenario Engine'!$AV$6:$AV$25)` |
| `H9` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B9,'Scenario Engine'!$AW$6:$AW$25)` |
| `I9` | `=IFERROR($H9/SUMIF('Scenario Engine'!$A$6:$A$25,$B9,'Scenario Engine'!$F$6:$F$25),0)` |
| `J9` | `=IF($I9>='FX & Financing'!$J$7,5,IF($I9>='FX & Financing'!$J$8,4,IF($I9>='FX & Financing'!$J$9,3,IF($I9>0,2,1))))` |
| `K9` | `=IF($D9="FAIL",1,IF($D9="PRELIMINARY",3,5))` |
| `L9` | `=INDEX(Scoring!$D$18:$J$18,1,ROW()-5)` |
| `M9` | `=INDEX(Scoring!$D$19:$J$19,1,ROW()-5)` |
| `N9` | `=IF($D9="FAIL","Do not rely: a hard gate failed",IF($D9="PRELIMINARY","Conditional only: resolve open gates and commercial assumptions","Eligible subject to final evidence and source re-verification"))` |
| `A10` | `=IF($B10="","",RANK($H10,$H$6:$H$12,0))` |
| `C10` | `=COUNTIF('Scenario Engine'!$A$6:$A$25,$B10)` |
| `D10` | `=IF($B10="","",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B10,'Scenario Engine'!$AN$6:$AN$25,"FAIL")>0,"FAIL",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B10,'Scenario Engine'!$AN$6:$AN$25,"PRELIMINARY")>0,"PRELIMINARY","PASS")))` |
| `E10` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B10,'Scenario Engine'!$AQ$6:$AQ$25)` |
| `F10` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B10,'Scenario Engine'!$AU$6:$AU$25)` |
| `G10` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B10,'Scenario Engine'!$AV$6:$AV$25)` |
| `H10` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B10,'Scenario Engine'!$AW$6:$AW$25)` |
| `I10` | `=IFERROR($H10/SUMIF('Scenario Engine'!$A$6:$A$25,$B10,'Scenario Engine'!$F$6:$F$25),0)` |
| `J10` | `=IF($I10>='FX & Financing'!$J$7,5,IF($I10>='FX & Financing'!$J$8,4,IF($I10>='FX & Financing'!$J$9,3,IF($I10>0,2,1))))` |
| `K10` | `=IF($D10="FAIL",1,IF($D10="PRELIMINARY",3,5))` |
| `L10` | `=INDEX(Scoring!$D$18:$J$18,1,ROW()-5)` |
| `M10` | `=INDEX(Scoring!$D$19:$J$19,1,ROW()-5)` |
| `N10` | `=IF($D10="FAIL","Do not rely: a hard gate failed",IF($D10="PRELIMINARY","Conditional only: resolve open gates and commercial assumptions","Eligible subject to final evidence and source re-verification"))` |
| `A11` | `=IF($B11="","",RANK($H11,$H$6:$H$12,0))` |
| `C11` | `=COUNTIF('Scenario Engine'!$A$6:$A$25,$B11)` |
| `D11` | `=IF($B11="","",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B11,'Scenario Engine'!$AN$6:$AN$25,"FAIL")>0,"FAIL",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B11,'Scenario Engine'!$AN$6:$AN$25,"PRELIMINARY")>0,"PRELIMINARY","PASS")))` |
| `E11` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B11,'Scenario Engine'!$AQ$6:$AQ$25)` |
| `F11` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B11,'Scenario Engine'!$AU$6:$AU$25)` |
| `G11` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B11,'Scenario Engine'!$AV$6:$AV$25)` |
| `H11` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B11,'Scenario Engine'!$AW$6:$AW$25)` |
| `I11` | `=IFERROR($H11/SUMIF('Scenario Engine'!$A$6:$A$25,$B11,'Scenario Engine'!$F$6:$F$25),0)` |
| `J11` | `=IF($I11>='FX & Financing'!$J$7,5,IF($I11>='FX & Financing'!$J$8,4,IF($I11>='FX & Financing'!$J$9,3,IF($I11>0,2,1))))` |
| `K11` | `=IF($D11="FAIL",1,IF($D11="PRELIMINARY",3,5))` |
| `L11` | `=INDEX(Scoring!$D$18:$J$18,1,ROW()-5)` |
| `M11` | `=INDEX(Scoring!$D$19:$J$19,1,ROW()-5)` |
| `N11` | `=IF($D11="FAIL","Do not rely: a hard gate failed",IF($D11="PRELIMINARY","Conditional only: resolve open gates and commercial assumptions","Eligible subject to final evidence and source re-verification"))` |
| `A12` | `=IF($B12="","",RANK($H12,$H$6:$H$12,0))` |
| `C12` | `=COUNTIF('Scenario Engine'!$A$6:$A$25,$B12)` |
| `D12` | `=IF($B12="","",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B12,'Scenario Engine'!$AN$6:$AN$25,"FAIL")>0,"FAIL",IF(COUNTIFS('Scenario Engine'!$A$6:$A$25,$B12,'Scenario Engine'!$AN$6:$AN$25,"PRELIMINARY")>0,"PRELIMINARY","PASS")))` |
| `E12` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B12,'Scenario Engine'!$AQ$6:$AQ$25)` |
| `F12` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B12,'Scenario Engine'!$AU$6:$AU$25)` |
| `G12` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B12,'Scenario Engine'!$AV$6:$AV$25)` |
| `H12` | `=SUMIF('Scenario Engine'!$A$6:$A$25,$B12,'Scenario Engine'!$AW$6:$AW$25)` |
| `I12` | `=IFERROR($H12/SUMIF('Scenario Engine'!$A$6:$A$25,$B12,'Scenario Engine'!$F$6:$F$25),0)` |
| `J12` | `=IF($I12>='FX & Financing'!$J$7,5,IF($I12>='FX & Financing'!$J$8,4,IF($I12>='FX & Financing'!$J$9,3,IF($I12>0,2,1))))` |
| `K12` | `=IF($D12="FAIL",1,IF($D12="PRELIMINARY",3,5))` |
| `L12` | `=INDEX(Scoring!$D$18:$J$18,1,ROW()-5)` |
| `M12` | `=INDEX(Scoring!$D$19:$J$19,1,ROW()-5)` |
| `N12` | `=IF($D12="FAIL","Do not rely: a hard gate failed",IF($D12="PRELIMINARY","Conditional only: resolve open gates and commercial assumptions","Eligible subject to final evidence and source re-verification"))` |

### Sheet: `Sources & Audit`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Test Cases`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Checks`
Formula count: **49**

| Cell | Formula |
|---|---|
| `B6` | `=COUNTIFS('Incentive Database'!A6:A180,"<>",'Incentive Database'!AI6:AI180,"<>Test only")` |
| `D6` | `=IF(AND(ISNUMBER(B6),ISNUMBER(C6)),B6-C6,"")` |
| `F6` | `=IF(AND(ISNUMBER(B6),ISNUMBER(C6)),IF(ABS(D6)<=E6,"OK","FAIL"),IF(B6=C6,"OK","FAIL"))` |
| `B7` | `=COUNTIFS('Programme Rules'!A5:A90,"<>",'Programme Rules'!H5:H90,"<>Test only")` |
| `D7` | `=IF(AND(ISNUMBER(B7),ISNUMBER(C7)),B7-C7,"")` |
| `F7` | `=IF(AND(ISNUMBER(B7),ISNUMBER(C7)),IF(ABS(D7)<=E7,"OK","FAIL"),IF(B7=C7,"OK","FAIL"))` |
| `B8` | `=COUNTIF('Lists & Config'!J6:J100,"USA-NY-IND")` |
| `D8` | `=IF(AND(ISNUMBER(B8),ISNUMBER(C8)),B8-C8,"")` |
| `F8` | `=IF(AND(ISNUMBER(B8),ISNUMBER(C8)),IF(ABS(D8)<=E8,"OK","FAIL"),IF(B8=C8,"OK","FAIL"))` |
| `B9` | `='Audit Regression'!D14` |
| `D9` | `=IF(AND(ISNUMBER(B9),ISNUMBER(C9)),B9-C9,"")` |
| `F9` | `=IF(AND(ISNUMBER(B9),ISNUMBER(C9)),IF(ABS(D9)<=E9,"OK","FAIL"),IF(B9=C9,"OK","FAIL"))` |
| `B10` | `='Audit Regression'!D15` |
| `D10` | `=IF(AND(ISNUMBER(B10),ISNUMBER(C10)),B10-C10,"")` |
| `F10` | `=IF(AND(ISNUMBER(B10),ISNUMBER(C10)),IF(ABS(D10)<=E10,"OK","FAIL"),IF(B10=C10,"OK","FAIL"))` |
| `B11` | `=COUNTIF('FX & Financing'!A5:A11,"<>")` |
| `D11` | `=IF(AND(ISNUMBER(B11),ISNUMBER(C11)),B11-C11,"")` |
| `F11` | `=IF(AND(ISNUMBER(B11),ISNUMBER(C11)),IF(ABS(D11)<=E11,"OK","FAIL"),IF(B11=C11,"OK","FAIL"))` |
| `B12` | `=COUNTBLANK('FX & Financing'!B5:B11)` |
| `D12` | `=IF(AND(ISNUMBER(B12),ISNUMBER(C12)),B12-C12,"")` |
| `F12` | `=IF(AND(ISNUMBER(B12),ISNUMBER(C12)),IF(ABS(D12)<=E12,"OK","FAIL"),IF(B12=C12,"OK","FAIL"))` |
| `B13` | `=COUNT('Incentive Database'!AA6:AF81)` |
| `D13` | `=IF(AND(ISNUMBER(B13),ISNUMBER(C13)),B13-C13,"")` |
| `F13` | `=IF(AND(ISNUMBER(B13),ISNUMBER(C13)),IF(ABS(D13)<=E13,"OK","FAIL"),IF(B13=C13,"OK","FAIL"))` |
| `B14` | `='Audit Regression'!D6` |
| `D14` | `=IF(AND(ISNUMBER(B14),ISNUMBER(C14)),B14-C14,"")` |
| `F14` | `=IF(AND(ISNUMBER(B14),ISNUMBER(C14)),IF(ABS(D14)<=E14,"OK","FAIL"),IF(B14=C14,"OK","FAIL"))` |
| `B15` | `='Audit Regression'!D8` |
| `D15` | `=IF(AND(ISNUMBER(B15),ISNUMBER(C15)),B15-C15,"")` |
| `F15` | `=IF(AND(ISNUMBER(B15),ISNUMBER(C15)),IF(ABS(D15)<=E15,"OK","FAIL"),IF(B15=C15,"OK","FAIL"))` |
| `B16` | `='Audit Regression'!D9` |
| `D16` | `=IF(AND(ISNUMBER(B16),ISNUMBER(C16)),B16-C16,"")` |
| `F16` | `=IF(AND(ISNUMBER(B16),ISNUMBER(C16)),IF(ABS(D16)<=E16,"OK","FAIL"),IF(B16=C16,"OK","FAIL"))` |
| `B17` | `='Audit Regression'!D10` |
| `D17` | `=IF(AND(ISNUMBER(B17),ISNUMBER(C17)),B17-C17,"")` |
| `F17` | `=IF(AND(ISNUMBER(B17),ISNUMBER(C17)),IF(ABS(D17)<=E17,"OK","FAIL"),IF(B17=C17,"OK","FAIL"))` |
| `B18` | `='Audit Regression'!D11` |
| `D18` | `=IF(AND(ISNUMBER(B18),ISNUMBER(C18)),B18-C18,"")` |
| `F18` | `=IF(AND(ISNUMBER(B18),ISNUMBER(C18)),IF(ABS(D18)<=E18,"OK","FAIL"),IF(B18=C18,"OK","FAIL"))` |
| `B19` | `='Audit Regression'!D12` |
| `D19` | `=IF(AND(ISNUMBER(B19),ISNUMBER(C19)),B19-C19,"")` |
| `F19` | `=IF(AND(ISNUMBER(B19),ISNUMBER(C19)),IF(ABS(D19)<=E19,"OK","FAIL"),IF(B19=C19,"OK","FAIL"))` |
| `B20` | `=SUM('Lists & Config'!G6:G17)` |
| `D20` | `=IF(AND(ISNUMBER(B20),ISNUMBER(C20)),B20-C20,"")` |
| `F20` | `=IF(AND(ISNUMBER(B20),ISNUMBER(C20)),IF(ABS(D20)<=E20,"OK","FAIL"),IF(B20=C20,"OK","FAIL"))` |
| `B21` | `=COUNTIF('Audit Regression'!G6:G17,"FAIL")` |
| `D21` | `=IF(AND(ISNUMBER(B21),ISNUMBER(C21)),B21-C21,"")` |
| `F21` | `=IF(AND(ISNUMBER(B21),ISNUMBER(C21)),IF(ABS(D21)<=E21,"OK","FAIL"),IF(B21=C21,"OK","FAIL"))` |
| `F23` | `=IF(COUNTIF(F6:F21,"FAIL")=0,"OK — AUDITED ENGINE","REVIEW")` |

### Sheet: `Lists & Config`
Formula count: **139**

| Cell | Formula |
|---|---|
| `K6` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J6,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L6` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J6,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K7` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J7,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L7` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J7,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K8` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J8,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L8` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J8,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K9` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J9,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L9` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J9,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K10` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J10,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L10` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J10,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K11` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J11,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L11` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J11,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K12` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J12,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L12` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J12,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K13` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J13,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L13` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J13,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K14` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J14,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L14` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J14,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K15` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J15,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L15` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J15,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K16` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J16,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L16` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J16,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K17` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J17,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L17` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J17,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `G18` | `=SUM(G6:G17)` |
| `K18` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J18,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L18` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J18,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K19` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J19,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L19` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J19,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K20` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J20,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L20` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J20,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K21` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J21,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L21` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J21,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K22` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J22,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L22` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J22,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K23` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J23,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L23` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J23,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K24` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J24,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L24` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J24,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K25` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J25,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L25` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J25,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K26` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J26,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L26` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J26,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K27` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J27,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L27` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J27,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K28` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J28,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L28` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J28,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K29` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J29,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L29` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J29,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K30` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J30,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L30` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J30,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K31` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J31,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L31` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J31,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K32` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J32,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L32` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J32,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K33` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J33,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L33` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J33,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K34` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J34,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L34` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J34,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K35` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J35,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L35` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J35,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K36` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J36,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L36` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J36,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K37` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J37,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L37` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J37,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K38` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J38,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L38` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J38,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K39` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J39,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L39` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J39,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K40` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J40,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L40` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J40,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K41` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J41,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L41` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J41,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K42` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J42,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L42` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J42,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K43` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J43,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L43` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J43,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K44` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J44,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L44` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J44,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K45` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J45,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L45` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J45,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K46` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J46,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L46` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J46,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K47` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J47,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L47` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J47,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K48` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J48,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L48` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J48,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K49` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J49,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L49` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J49,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K50` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J50,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L50` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J50,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K51` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J51,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L51` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J51,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K52` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J52,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L52` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J52,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K53` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J53,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L53` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J53,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K54` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J54,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L54` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J54,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K55` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J55,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L55` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J55,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K56` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J56,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L56` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J56,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K57` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J57,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L57` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J57,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K58` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J58,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L58` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J58,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K59` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J59,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L59` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J59,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K60` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J60,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L60` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J60,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K61` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J61,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L61` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J61,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K62` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J62,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L62` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J62,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K63` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J63,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L63` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J63,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K64` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J64,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L64` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J64,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K65` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J65,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L65` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J65,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K66` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J66,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L66` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J66,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K67` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J67,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L67` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J67,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K68` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J68,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L68` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J68,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K69` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J69,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L69` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J69,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K70` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J70,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L70` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J70,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K71` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J71,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L71` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J71,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K72` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J72,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L72` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J72,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K73` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J73,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L73` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J73,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `K74` | `=IFERROR(INDEX('Programme Rules'!$B$5:$B$90,MATCH(J74,'Programme Rules'!$A$5:$A$90,0)),"")` |
| `L74` | `=IFERROR(INDEX('Programme Rules'!$C$5:$C$90,MATCH(J74,'Programme Rules'!$A$5:$A$90,0)),"")` |

### Sheet: `Changelog`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Coverage Gaps`
Formula count: **650**

| Cell | Formula |
|---|---|
| `D4` | `=COUNTIFS('Incentive Database'!A6:A180,"<>",'Incentive Database'!AI6:AI180,"<>Test only")` |
| `F4` | `=COUNTIF(F6:F86,"Research gap")` |
| `A6` | `='Priority Jurisdictions'!A7` |
| `B6` | `='Priority Jurisdictions'!B7` |
| `C6` | `='Priority Jurisdictions'!C7` |
| `D6` | `='Priority Jurisdictions'!D7` |
| `E6` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D6)` |
| `F6` | `=IF(E6=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D6,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D6,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G6` | `=IF(E6=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D6,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D6,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H6` | `=IF(E6=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A7` | `='Priority Jurisdictions'!A8` |
| `B7` | `='Priority Jurisdictions'!B8` |
| `C7` | `='Priority Jurisdictions'!C8` |
| `D7` | `='Priority Jurisdictions'!D8` |
| `E7` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D7)` |
| `F7` | `=IF(E7=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D7,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D7,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G7` | `=IF(E7=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D7,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D7,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H7` | `=IF(E7=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A8` | `='Priority Jurisdictions'!A9` |
| `B8` | `='Priority Jurisdictions'!B9` |
| `C8` | `='Priority Jurisdictions'!C9` |
| `D8` | `='Priority Jurisdictions'!D9` |
| `E8` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D8)` |
| `F8` | `=IF(E8=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D8,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D8,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G8` | `=IF(E8=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D8,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D8,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H8` | `=IF(E8=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A9` | `='Priority Jurisdictions'!A10` |
| `B9` | `='Priority Jurisdictions'!B10` |
| `C9` | `='Priority Jurisdictions'!C10` |
| `D9` | `='Priority Jurisdictions'!D10` |
| `E9` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D9)` |
| `F9` | `=IF(E9=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D9,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D9,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G9` | `=IF(E9=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D9,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D9,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H9` | `=IF(E9=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A10` | `='Priority Jurisdictions'!A11` |
| `B10` | `='Priority Jurisdictions'!B11` |
| `C10` | `='Priority Jurisdictions'!C11` |
| `D10` | `='Priority Jurisdictions'!D11` |
| `E10` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D10)` |
| `F10` | `=IF(E10=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D10,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D10,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G10` | `=IF(E10=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D10,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D10,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H10` | `=IF(E10=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A11` | `='Priority Jurisdictions'!A12` |
| `B11` | `='Priority Jurisdictions'!B12` |
| `C11` | `='Priority Jurisdictions'!C12` |
| `D11` | `='Priority Jurisdictions'!D12` |
| `E11` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D11)` |
| `F11` | `=IF(E11=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D11,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D11,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G11` | `=IF(E11=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D11,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D11,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H11` | `=IF(E11=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A12` | `='Priority Jurisdictions'!A13` |
| `B12` | `='Priority Jurisdictions'!B13` |
| `C12` | `='Priority Jurisdictions'!C13` |
| `D12` | `='Priority Jurisdictions'!D13` |
| `E12` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D12)` |
| `F12` | `=IF(E12=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D12,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D12,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G12` | `=IF(E12=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D12,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D12,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H12` | `=IF(E12=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A13` | `='Priority Jurisdictions'!A14` |
| `B13` | `='Priority Jurisdictions'!B14` |
| `C13` | `='Priority Jurisdictions'!C14` |
| `D13` | `='Priority Jurisdictions'!D14` |
| `E13` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D13)` |
| `F13` | `=IF(E13=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D13,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D13,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G13` | `=IF(E13=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D13,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D13,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H13` | `=IF(E13=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A14` | `='Priority Jurisdictions'!A15` |
| `B14` | `='Priority Jurisdictions'!B15` |
| `C14` | `='Priority Jurisdictions'!C15` |
| `D14` | `='Priority Jurisdictions'!D15` |
| `E14` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D14)` |
| `F14` | `=IF(E14=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D14,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D14,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G14` | `=IF(E14=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D14,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D14,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H14` | `=IF(E14=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A15` | `='Priority Jurisdictions'!A16` |
| `B15` | `='Priority Jurisdictions'!B16` |
| `C15` | `='Priority Jurisdictions'!C16` |
| `D15` | `='Priority Jurisdictions'!D16` |
| `E15` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D15)` |
| `F15` | `=IF(E15=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D15,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D15,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G15` | `=IF(E15=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D15,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D15,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H15` | `=IF(E15=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A16` | `='Priority Jurisdictions'!A17` |
| `B16` | `='Priority Jurisdictions'!B17` |
| `C16` | `='Priority Jurisdictions'!C17` |
| `D16` | `='Priority Jurisdictions'!D17` |
| `E16` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D16)` |
| `F16` | `=IF(E16=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D16,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D16,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G16` | `=IF(E16=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D16,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D16,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H16` | `=IF(E16=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A17` | `='Priority Jurisdictions'!A18` |
| `B17` | `='Priority Jurisdictions'!B18` |
| `C17` | `='Priority Jurisdictions'!C18` |
| `D17` | `='Priority Jurisdictions'!D18` |
| `E17` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D17)` |
| `F17` | `=IF(E17=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D17,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D17,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G17` | `=IF(E17=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D17,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D17,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H17` | `=IF(E17=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A18` | `='Priority Jurisdictions'!A19` |
| `B18` | `='Priority Jurisdictions'!B19` |
| `C18` | `='Priority Jurisdictions'!C19` |
| `D18` | `='Priority Jurisdictions'!D19` |
| `E18` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D18)` |
| `F18` | `=IF(E18=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D18,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D18,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G18` | `=IF(E18=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D18,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D18,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H18` | `=IF(E18=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A19` | `='Priority Jurisdictions'!A20` |
| `B19` | `='Priority Jurisdictions'!B20` |
| `C19` | `='Priority Jurisdictions'!C20` |
| `D19` | `='Priority Jurisdictions'!D20` |
| `E19` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D19)` |
| `F19` | `=IF(E19=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D19,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D19,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G19` | `=IF(E19=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D19,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D19,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H19` | `=IF(E19=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A20` | `='Priority Jurisdictions'!A21` |
| `B20` | `='Priority Jurisdictions'!B21` |
| `C20` | `='Priority Jurisdictions'!C21` |
| `D20` | `='Priority Jurisdictions'!D21` |
| `E20` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D20)` |
| `F20` | `=IF(E20=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D20,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D20,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G20` | `=IF(E20=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D20,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D20,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H20` | `=IF(E20=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A21` | `='Priority Jurisdictions'!A22` |
| `B21` | `='Priority Jurisdictions'!B22` |
| `C21` | `='Priority Jurisdictions'!C22` |
| `D21` | `='Priority Jurisdictions'!D22` |
| `E21` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D21)` |
| `F21` | `=IF(E21=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D21,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D21,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G21` | `=IF(E21=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D21,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D21,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H21` | `=IF(E21=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A22` | `='Priority Jurisdictions'!A23` |
| `B22` | `='Priority Jurisdictions'!B23` |
| `C22` | `='Priority Jurisdictions'!C23` |
| `D22` | `='Priority Jurisdictions'!D23` |
| `E22` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D22)` |
| `F22` | `=IF(E22=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D22,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D22,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G22` | `=IF(E22=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D22,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D22,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H22` | `=IF(E22=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A23` | `='Priority Jurisdictions'!A24` |
| `B23` | `='Priority Jurisdictions'!B24` |
| `C23` | `='Priority Jurisdictions'!C24` |
| `D23` | `='Priority Jurisdictions'!D24` |
| `E23` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D23)` |
| `F23` | `=IF(E23=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D23,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D23,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G23` | `=IF(E23=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D23,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D23,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H23` | `=IF(E23=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A24` | `='Priority Jurisdictions'!A25` |
| `B24` | `='Priority Jurisdictions'!B25` |
| `C24` | `='Priority Jurisdictions'!C25` |
| `D24` | `='Priority Jurisdictions'!D25` |
| `E24` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D24)` |
| `F24` | `=IF(E24=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D24,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D24,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G24` | `=IF(E24=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D24,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D24,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H24` | `=IF(E24=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A25` | `='Priority Jurisdictions'!A26` |
| `B25` | `='Priority Jurisdictions'!B26` |
| `C25` | `='Priority Jurisdictions'!C26` |
| `D25` | `='Priority Jurisdictions'!D26` |
| `E25` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D25)` |
| `F25` | `=IF(E25=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D25,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D25,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G25` | `=IF(E25=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D25,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D25,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H25` | `=IF(E25=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A26` | `='Priority Jurisdictions'!A27` |
| `B26` | `='Priority Jurisdictions'!B27` |
| `C26` | `='Priority Jurisdictions'!C27` |
| `D26` | `='Priority Jurisdictions'!D27` |
| `E26` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D26)` |
| `F26` | `=IF(E26=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D26,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D26,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G26` | `=IF(E26=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D26,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D26,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H26` | `=IF(E26=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A27` | `='Priority Jurisdictions'!A28` |
| `B27` | `='Priority Jurisdictions'!B28` |
| `C27` | `='Priority Jurisdictions'!C28` |
| `D27` | `='Priority Jurisdictions'!D28` |
| `E27` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D27)` |
| `F27` | `=IF(E27=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D27,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D27,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G27` | `=IF(E27=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D27,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D27,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H27` | `=IF(E27=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A28` | `='Priority Jurisdictions'!A29` |
| `B28` | `='Priority Jurisdictions'!B29` |
| `C28` | `='Priority Jurisdictions'!C29` |
| `D28` | `='Priority Jurisdictions'!D29` |
| `E28` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D28)` |
| `F28` | `=IF(E28=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D28,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D28,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G28` | `=IF(E28=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D28,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D28,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H28` | `=IF(E28=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A29` | `='Priority Jurisdictions'!A30` |
| `B29` | `='Priority Jurisdictions'!B30` |
| `C29` | `='Priority Jurisdictions'!C30` |
| `D29` | `='Priority Jurisdictions'!D30` |
| `E29` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D29)` |
| `F29` | `=IF(E29=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D29,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D29,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G29` | `=IF(E29=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D29,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D29,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H29` | `=IF(E29=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A30` | `='Priority Jurisdictions'!A31` |
| `B30` | `='Priority Jurisdictions'!B31` |
| `C30` | `='Priority Jurisdictions'!C31` |
| `D30` | `='Priority Jurisdictions'!D31` |
| `E30` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D30)` |
| `F30` | `=IF(E30=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D30,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D30,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G30` | `=IF(E30=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D30,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D30,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H30` | `=IF(E30=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A31` | `='Priority Jurisdictions'!A32` |
| `B31` | `='Priority Jurisdictions'!B32` |
| `C31` | `='Priority Jurisdictions'!C32` |
| `D31` | `='Priority Jurisdictions'!D32` |
| `E31` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D31)` |
| `F31` | `=IF(E31=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D31,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D31,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G31` | `=IF(E31=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D31,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D31,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H31` | `=IF(E31=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A32` | `='Priority Jurisdictions'!A33` |
| `B32` | `='Priority Jurisdictions'!B33` |
| `C32` | `='Priority Jurisdictions'!C33` |
| `D32` | `='Priority Jurisdictions'!D33` |
| `E32` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D32)` |
| `F32` | `=IF(E32=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D32,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D32,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G32` | `=IF(E32=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D32,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D32,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H32` | `=IF(E32=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A33` | `='Priority Jurisdictions'!A34` |
| `B33` | `='Priority Jurisdictions'!B34` |
| `C33` | `='Priority Jurisdictions'!C34` |
| `D33` | `='Priority Jurisdictions'!D34` |
| `E33` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D33)` |
| `F33` | `=IF(E33=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D33,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D33,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G33` | `=IF(E33=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D33,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D33,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H33` | `=IF(E33=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A34` | `='Priority Jurisdictions'!A35` |
| `B34` | `='Priority Jurisdictions'!B35` |
| `C34` | `='Priority Jurisdictions'!C35` |
| `D34` | `='Priority Jurisdictions'!D35` |
| `E34` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D34)` |
| `F34` | `=IF(E34=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D34,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D34,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G34` | `=IF(E34=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D34,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D34,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H34` | `=IF(E34=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A35` | `='Priority Jurisdictions'!A36` |
| `B35` | `='Priority Jurisdictions'!B36` |
| `C35` | `='Priority Jurisdictions'!C36` |
| `D35` | `='Priority Jurisdictions'!D36` |
| `E35` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D35)` |
| `F35` | `=IF(E35=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D35,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D35,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G35` | `=IF(E35=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D35,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D35,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H35` | `=IF(E35=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A36` | `='Priority Jurisdictions'!A37` |
| `B36` | `='Priority Jurisdictions'!B37` |
| `C36` | `='Priority Jurisdictions'!C37` |
| `D36` | `='Priority Jurisdictions'!D37` |
| `E36` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D36)` |
| `F36` | `=IF(E36=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D36,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D36,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G36` | `=IF(E36=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D36,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D36,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H36` | `=IF(E36=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A37` | `='Priority Jurisdictions'!A38` |
| `B37` | `='Priority Jurisdictions'!B38` |
| `C37` | `='Priority Jurisdictions'!C38` |
| `D37` | `='Priority Jurisdictions'!D38` |
| `E37` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D37)` |
| `F37` | `=IF(E37=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D37,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D37,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G37` | `=IF(E37=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D37,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D37,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H37` | `=IF(E37=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A38` | `='Priority Jurisdictions'!A39` |
| `B38` | `='Priority Jurisdictions'!B39` |
| `C38` | `='Priority Jurisdictions'!C39` |
| `D38` | `='Priority Jurisdictions'!D39` |
| `E38` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D38)` |
| `F38` | `=IF(E38=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D38,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D38,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G38` | `=IF(E38=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D38,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D38,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H38` | `=IF(E38=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A39` | `='Priority Jurisdictions'!A40` |
| `B39` | `='Priority Jurisdictions'!B40` |
| `C39` | `='Priority Jurisdictions'!C40` |
| `D39` | `='Priority Jurisdictions'!D40` |
| `E39` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D39)` |
| `F39` | `=IF(E39=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D39,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D39,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G39` | `=IF(E39=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D39,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D39,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H39` | `=IF(E39=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A40` | `='Priority Jurisdictions'!A41` |
| `B40` | `='Priority Jurisdictions'!B41` |
| `C40` | `='Priority Jurisdictions'!C41` |
| `D40` | `='Priority Jurisdictions'!D41` |
| `E40` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D40)` |
| `F40` | `=IF(E40=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D40,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D40,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G40` | `=IF(E40=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D40,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D40,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H40` | `=IF(E40=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A41` | `='Priority Jurisdictions'!A42` |
| `B41` | `='Priority Jurisdictions'!B42` |
| `C41` | `='Priority Jurisdictions'!C42` |
| `D41` | `='Priority Jurisdictions'!D42` |
| `E41` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D41)` |
| `F41` | `=IF(E41=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D41,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D41,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G41` | `=IF(E41=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D41,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D41,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H41` | `=IF(E41=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A42` | `='Priority Jurisdictions'!A43` |
| `B42` | `='Priority Jurisdictions'!B43` |
| `C42` | `='Priority Jurisdictions'!C43` |
| `D42` | `='Priority Jurisdictions'!D43` |
| `E42` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D42)` |
| `F42` | `=IF(E42=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D42,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D42,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G42` | `=IF(E42=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D42,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D42,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H42` | `=IF(E42=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A43` | `='Priority Jurisdictions'!A44` |
| `B43` | `='Priority Jurisdictions'!B44` |
| `C43` | `='Priority Jurisdictions'!C44` |
| `D43` | `='Priority Jurisdictions'!D44` |
| `E43` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D43)` |
| `F43` | `=IF(E43=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D43,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D43,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G43` | `=IF(E43=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D43,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D43,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H43` | `=IF(E43=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A44` | `='Priority Jurisdictions'!A45` |
| `B44` | `='Priority Jurisdictions'!B45` |
| `C44` | `='Priority Jurisdictions'!C45` |
| `D44` | `='Priority Jurisdictions'!D45` |
| `E44` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D44)` |
| `F44` | `=IF(E44=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D44,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D44,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G44` | `=IF(E44=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D44,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D44,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H44` | `=IF(E44=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A45` | `='Priority Jurisdictions'!A46` |
| `B45` | `='Priority Jurisdictions'!B46` |
| `C45` | `='Priority Jurisdictions'!C46` |
| `D45` | `='Priority Jurisdictions'!D46` |
| `E45` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D45)` |
| `F45` | `=IF(E45=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D45,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D45,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G45` | `=IF(E45=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D45,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D45,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H45` | `=IF(E45=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A46` | `='Priority Jurisdictions'!A47` |
| `B46` | `='Priority Jurisdictions'!B47` |
| `C46` | `='Priority Jurisdictions'!C47` |
| `D46` | `='Priority Jurisdictions'!D47` |
| `E46` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D46)` |
| `F46` | `=IF(E46=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D46,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D46,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G46` | `=IF(E46=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D46,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D46,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H46` | `=IF(E46=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A47` | `='Priority Jurisdictions'!A48` |
| `B47` | `='Priority Jurisdictions'!B48` |
| `C47` | `='Priority Jurisdictions'!C48` |
| `D47` | `='Priority Jurisdictions'!D48` |
| `E47` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D47)` |
| `F47` | `=IF(E47=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D47,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D47,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G47` | `=IF(E47=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D47,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D47,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H47` | `=IF(E47=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A48` | `='Priority Jurisdictions'!A49` |
| `B48` | `='Priority Jurisdictions'!B49` |
| `C48` | `='Priority Jurisdictions'!C49` |
| `D48` | `='Priority Jurisdictions'!D49` |
| `E48` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D48)` |
| `F48` | `=IF(E48=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D48,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D48,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G48` | `=IF(E48=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D48,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D48,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H48` | `=IF(E48=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A49` | `='Priority Jurisdictions'!A50` |
| `B49` | `='Priority Jurisdictions'!B50` |
| `C49` | `='Priority Jurisdictions'!C50` |
| `D49` | `='Priority Jurisdictions'!D50` |
| `E49` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D49)` |
| `F49` | `=IF(E49=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D49,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D49,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G49` | `=IF(E49=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D49,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D49,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H49` | `=IF(E49=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A50` | `='Priority Jurisdictions'!A51` |
| `B50` | `='Priority Jurisdictions'!B51` |
| `C50` | `='Priority Jurisdictions'!C51` |
| `D50` | `='Priority Jurisdictions'!D51` |
| `E50` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D50)` |
| `F50` | `=IF(E50=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D50,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D50,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G50` | `=IF(E50=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D50,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D50,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H50` | `=IF(E50=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A51` | `='Priority Jurisdictions'!A52` |
| `B51` | `='Priority Jurisdictions'!B52` |
| `C51` | `='Priority Jurisdictions'!C52` |
| `D51` | `='Priority Jurisdictions'!D52` |
| `E51` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D51)` |
| `F51` | `=IF(E51=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D51,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D51,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G51` | `=IF(E51=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D51,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D51,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H51` | `=IF(E51=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A52` | `='Priority Jurisdictions'!A53` |
| `B52` | `='Priority Jurisdictions'!B53` |
| `C52` | `='Priority Jurisdictions'!C53` |
| `D52` | `='Priority Jurisdictions'!D53` |
| `E52` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D52)` |
| `F52` | `=IF(E52=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D52,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D52,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G52` | `=IF(E52=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D52,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D52,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H52` | `=IF(E52=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A53` | `='Priority Jurisdictions'!A54` |
| `B53` | `='Priority Jurisdictions'!B54` |
| `C53` | `='Priority Jurisdictions'!C54` |
| `D53` | `='Priority Jurisdictions'!D54` |
| `E53` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D53)` |
| `F53` | `=IF(E53=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D53,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D53,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G53` | `=IF(E53=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D53,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D53,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H53` | `=IF(E53=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A54` | `='Priority Jurisdictions'!A55` |
| `B54` | `='Priority Jurisdictions'!B55` |
| `C54` | `='Priority Jurisdictions'!C55` |
| `D54` | `='Priority Jurisdictions'!D55` |
| `E54` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D54)` |
| `F54` | `=IF(E54=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D54,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D54,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G54` | `=IF(E54=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D54,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D54,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H54` | `=IF(E54=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A55` | `='Priority Jurisdictions'!A56` |
| `B55` | `='Priority Jurisdictions'!B56` |
| `C55` | `='Priority Jurisdictions'!C56` |
| `D55` | `='Priority Jurisdictions'!D56` |
| `E55` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D55)` |
| `F55` | `=IF(E55=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D55,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D55,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G55` | `=IF(E55=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D55,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D55,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H55` | `=IF(E55=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A56` | `='Priority Jurisdictions'!A57` |
| `B56` | `='Priority Jurisdictions'!B57` |
| `C56` | `='Priority Jurisdictions'!C57` |
| `D56` | `='Priority Jurisdictions'!D57` |
| `E56` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D56)` |
| `F56` | `=IF(E56=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D56,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D56,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G56` | `=IF(E56=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D56,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D56,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H56` | `=IF(E56=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A57` | `='Priority Jurisdictions'!A58` |
| `B57` | `='Priority Jurisdictions'!B58` |
| `C57` | `='Priority Jurisdictions'!C58` |
| `D57` | `='Priority Jurisdictions'!D58` |
| `E57` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D57)` |
| `F57` | `=IF(E57=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D57,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D57,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G57` | `=IF(E57=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D57,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D57,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H57` | `=IF(E57=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A58` | `='Priority Jurisdictions'!A59` |
| `B58` | `='Priority Jurisdictions'!B59` |
| `C58` | `='Priority Jurisdictions'!C59` |
| `D58` | `='Priority Jurisdictions'!D59` |
| `E58` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D58)` |
| `F58` | `=IF(E58=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D58,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D58,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G58` | `=IF(E58=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D58,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D58,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H58` | `=IF(E58=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A59` | `='Priority Jurisdictions'!A60` |
| `B59` | `='Priority Jurisdictions'!B60` |
| `C59` | `='Priority Jurisdictions'!C60` |
| `D59` | `='Priority Jurisdictions'!D60` |
| `E59` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D59)` |
| `F59` | `=IF(E59=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D59,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D59,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G59` | `=IF(E59=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D59,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D59,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H59` | `=IF(E59=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A60` | `='Priority Jurisdictions'!A61` |
| `B60` | `='Priority Jurisdictions'!B61` |
| `C60` | `='Priority Jurisdictions'!C61` |
| `D60` | `='Priority Jurisdictions'!D61` |
| `E60` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D60)` |
| `F60` | `=IF(E60=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D60,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D60,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G60` | `=IF(E60=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D60,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D60,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H60` | `=IF(E60=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A61` | `='Priority Jurisdictions'!A62` |
| `B61` | `='Priority Jurisdictions'!B62` |
| `C61` | `='Priority Jurisdictions'!C62` |
| `D61` | `='Priority Jurisdictions'!D62` |
| `E61` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D61)` |
| `F61` | `=IF(E61=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D61,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D61,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G61` | `=IF(E61=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D61,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D61,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H61` | `=IF(E61=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A62` | `='Priority Jurisdictions'!A63` |
| `B62` | `='Priority Jurisdictions'!B63` |
| `C62` | `='Priority Jurisdictions'!C63` |
| `D62` | `='Priority Jurisdictions'!D63` |
| `E62` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D62)` |
| `F62` | `=IF(E62=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D62,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D62,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G62` | `=IF(E62=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D62,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D62,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H62` | `=IF(E62=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A63` | `='Priority Jurisdictions'!A64` |
| `B63` | `='Priority Jurisdictions'!B64` |
| `C63` | `='Priority Jurisdictions'!C64` |
| `D63` | `='Priority Jurisdictions'!D64` |
| `E63` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D63)` |
| `F63` | `=IF(E63=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D63,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D63,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G63` | `=IF(E63=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D63,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D63,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H63` | `=IF(E63=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A64` | `='Priority Jurisdictions'!A65` |
| `B64` | `='Priority Jurisdictions'!B65` |
| `C64` | `='Priority Jurisdictions'!C65` |
| `D64` | `='Priority Jurisdictions'!D65` |
| `E64` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D64)` |
| `F64` | `=IF(E64=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D64,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D64,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G64` | `=IF(E64=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D64,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D64,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H64` | `=IF(E64=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A65` | `='Priority Jurisdictions'!A66` |
| `B65` | `='Priority Jurisdictions'!B66` |
| `C65` | `='Priority Jurisdictions'!C66` |
| `D65` | `='Priority Jurisdictions'!D66` |
| `E65` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D65)` |
| `F65` | `=IF(E65=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D65,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D65,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G65` | `=IF(E65=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D65,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D65,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H65` | `=IF(E65=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A66` | `='Priority Jurisdictions'!A67` |
| `B66` | `='Priority Jurisdictions'!B67` |
| `C66` | `='Priority Jurisdictions'!C67` |
| `D66` | `='Priority Jurisdictions'!D67` |
| `E66` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D66)` |
| `F66` | `=IF(E66=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D66,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D66,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G66` | `=IF(E66=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D66,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D66,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H66` | `=IF(E66=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A67` | `='Priority Jurisdictions'!A68` |
| `B67` | `='Priority Jurisdictions'!B68` |
| `C67` | `='Priority Jurisdictions'!C68` |
| `D67` | `='Priority Jurisdictions'!D68` |
| `E67` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D67)` |
| `F67` | `=IF(E67=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D67,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D67,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G67` | `=IF(E67=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D67,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D67,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H67` | `=IF(E67=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A68` | `='Priority Jurisdictions'!A69` |
| `B68` | `='Priority Jurisdictions'!B69` |
| `C68` | `='Priority Jurisdictions'!C69` |
| `D68` | `='Priority Jurisdictions'!D69` |
| `E68` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D68)` |
| `F68` | `=IF(E68=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D68,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D68,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G68` | `=IF(E68=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D68,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D68,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H68` | `=IF(E68=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A69` | `='Priority Jurisdictions'!A70` |
| `B69` | `='Priority Jurisdictions'!B70` |
| `C69` | `='Priority Jurisdictions'!C70` |
| `D69` | `='Priority Jurisdictions'!D70` |
| `E69` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D69)` |
| `F69` | `=IF(E69=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D69,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D69,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G69` | `=IF(E69=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D69,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D69,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H69` | `=IF(E69=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A70` | `='Priority Jurisdictions'!A71` |
| `B70` | `='Priority Jurisdictions'!B71` |
| `C70` | `='Priority Jurisdictions'!C71` |
| `D70` | `='Priority Jurisdictions'!D71` |
| `E70` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D70)` |
| `F70` | `=IF(E70=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D70,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D70,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G70` | `=IF(E70=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D70,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D70,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H70` | `=IF(E70=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A71` | `='Priority Jurisdictions'!A72` |
| `B71` | `='Priority Jurisdictions'!B72` |
| `C71` | `='Priority Jurisdictions'!C72` |
| `D71` | `='Priority Jurisdictions'!D72` |
| `E71` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D71)` |
| `F71` | `=IF(E71=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D71,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D71,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G71` | `=IF(E71=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D71,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D71,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H71` | `=IF(E71=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A72` | `='Priority Jurisdictions'!A73` |
| `B72` | `='Priority Jurisdictions'!B73` |
| `C72` | `='Priority Jurisdictions'!C73` |
| `D72` | `='Priority Jurisdictions'!D73` |
| `E72` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D72)` |
| `F72` | `=IF(E72=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D72,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D72,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G72` | `=IF(E72=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D72,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D72,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H72` | `=IF(E72=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A73` | `='Priority Jurisdictions'!A74` |
| `B73` | `='Priority Jurisdictions'!B74` |
| `C73` | `='Priority Jurisdictions'!C74` |
| `D73` | `='Priority Jurisdictions'!D74` |
| `E73` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D73)` |
| `F73` | `=IF(E73=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D73,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D73,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G73` | `=IF(E73=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D73,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D73,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H73` | `=IF(E73=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A74` | `='Priority Jurisdictions'!A75` |
| `B74` | `='Priority Jurisdictions'!B75` |
| `C74` | `='Priority Jurisdictions'!C75` |
| `D74` | `='Priority Jurisdictions'!D75` |
| `E74` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D74)` |
| `F74` | `=IF(E74=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D74,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D74,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G74` | `=IF(E74=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D74,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D74,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H74` | `=IF(E74=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A75` | `='Priority Jurisdictions'!A76` |
| `B75` | `='Priority Jurisdictions'!B76` |
| `C75` | `='Priority Jurisdictions'!C76` |
| `D75` | `='Priority Jurisdictions'!D76` |
| `E75` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D75)` |
| `F75` | `=IF(E75=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D75,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D75,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G75` | `=IF(E75=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D75,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D75,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H75` | `=IF(E75=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A76` | `='Priority Jurisdictions'!A77` |
| `B76` | `='Priority Jurisdictions'!B77` |
| `C76` | `='Priority Jurisdictions'!C77` |
| `D76` | `='Priority Jurisdictions'!D77` |
| `E76` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D76)` |
| `F76` | `=IF(E76=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D76,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D76,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G76` | `=IF(E76=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D76,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D76,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H76` | `=IF(E76=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A77` | `='Priority Jurisdictions'!A78` |
| `B77` | `='Priority Jurisdictions'!B78` |
| `C77` | `='Priority Jurisdictions'!C78` |
| `D77` | `='Priority Jurisdictions'!D78` |
| `E77` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D77)` |
| `F77` | `=IF(E77=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D77,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D77,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G77` | `=IF(E77=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D77,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D77,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H77` | `=IF(E77=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A78` | `='Priority Jurisdictions'!A79` |
| `B78` | `='Priority Jurisdictions'!B79` |
| `C78` | `='Priority Jurisdictions'!C79` |
| `D78` | `='Priority Jurisdictions'!D79` |
| `E78` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D78)` |
| `F78` | `=IF(E78=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D78,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D78,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G78` | `=IF(E78=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D78,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D78,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H78` | `=IF(E78=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A79` | `='Priority Jurisdictions'!A80` |
| `B79` | `='Priority Jurisdictions'!B80` |
| `C79` | `='Priority Jurisdictions'!C80` |
| `D79` | `='Priority Jurisdictions'!D80` |
| `E79` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D79)` |
| `F79` | `=IF(E79=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D79,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D79,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G79` | `=IF(E79=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D79,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D79,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H79` | `=IF(E79=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A80` | `='Priority Jurisdictions'!A81` |
| `B80` | `='Priority Jurisdictions'!B81` |
| `C80` | `='Priority Jurisdictions'!C81` |
| `D80` | `='Priority Jurisdictions'!D81` |
| `E80` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D80)` |
| `F80` | `=IF(E80=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D80,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D80,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G80` | `=IF(E80=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D80,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D80,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H80` | `=IF(E80=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A81` | `='Priority Jurisdictions'!A82` |
| `B81` | `='Priority Jurisdictions'!B82` |
| `C81` | `='Priority Jurisdictions'!C82` |
| `D81` | `='Priority Jurisdictions'!D82` |
| `E81` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D81)` |
| `F81` | `=IF(E81=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D81,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D81,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G81` | `=IF(E81=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D81,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D81,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H81` | `=IF(E81=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A82` | `='Priority Jurisdictions'!A83` |
| `B82` | `='Priority Jurisdictions'!B83` |
| `C82` | `='Priority Jurisdictions'!C83` |
| `D82` | `='Priority Jurisdictions'!D83` |
| `E82` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D82)` |
| `F82` | `=IF(E82=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D82,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D82,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G82` | `=IF(E82=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D82,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D82,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H82` | `=IF(E82=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A83` | `='Priority Jurisdictions'!A84` |
| `B83` | `='Priority Jurisdictions'!B84` |
| `C83` | `='Priority Jurisdictions'!C84` |
| `D83` | `='Priority Jurisdictions'!D84` |
| `E83` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D83)` |
| `F83` | `=IF(E83=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D83,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D83,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G83` | `=IF(E83=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D83,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D83,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H83` | `=IF(E83=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A84` | `='Priority Jurisdictions'!A85` |
| `B84` | `='Priority Jurisdictions'!B85` |
| `C84` | `='Priority Jurisdictions'!C85` |
| `D84` | `='Priority Jurisdictions'!D85` |
| `E84` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D84)` |
| `F84` | `=IF(E84=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D84,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D84,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G84` | `=IF(E84=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D84,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D84,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H84` | `=IF(E84=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A85` | `='Priority Jurisdictions'!A86` |
| `B85` | `='Priority Jurisdictions'!B86` |
| `C85` | `='Priority Jurisdictions'!C86` |
| `D85` | `='Priority Jurisdictions'!D86` |
| `E85` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D85)` |
| `F85` | `=IF(E85=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D85,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D85,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G85` | `=IF(E85=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D85,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D85,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H85` | `=IF(E85=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |
| `A86` | `='Priority Jurisdictions'!A87` |
| `B86` | `='Priority Jurisdictions'!B87` |
| `C86` | `='Priority Jurisdictions'!C87` |
| `D86` | `='Priority Jurisdictions'!D87` |
| `E86` | `=COUNTIF('Incentive Database'!$D$6:$D$180,D86)` |
| `F86` | `=IF(E86=0,"Research gap",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D86,'Incentive Database'!$AI$6:$AI$180,"Active")+COUNTIFS('Incentive Database'!$D$6:$D$180,D86,'Incentive Database'!$AI$6:$AI$180,"Limited")>0,"Core programme verified","Record present / unavailable"))` |
| `G86` | `=IF(E86=0,"-",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D86,'Incentive Database'!$AN$6:$AN$180,"High")>0,"High",IF(COUNTIFS('Incentive Database'!$D$6:$D$180,D86,'Incentive Database'!$AN$6:$AN$180,"Medium")>0,"Medium","Low")))` |
| `H86` | `=IF(E86=0,"Research current official regional/local programmes and availability","Review programme notes, eligible-cost bases, stacking, capacity and adviser confirmation")` |

### Sheet: `Programme Rules`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `FX & Financing`
Formula count: **0**

_No formulas in this sheet._

### Sheet: `Audit Regression`
Formula count: **36**

| Cell | Formula |
|---|---|
| `D6` | `='Scenario Engine'!AP6` |
| `E6` | `=IF(AND(ISNUMBER(C6),ISNUMBER(D6)),D6-C6,"")` |
| `G6` | `=IF(AND(ISNUMBER(C6),ISNUMBER(D6)),IF(ABS(E6)<=F6,"OK","FAIL"),IF(C6=D6,"OK","FAIL"))` |
| `D7` | `='Scenario Engine'!AP7` |
| `E7` | `=IF(AND(ISNUMBER(C7),ISNUMBER(D7)),D7-C7,"")` |
| `G7` | `=IF(AND(ISNUMBER(C7),ISNUMBER(D7)),IF(ABS(E7)<=F7,"OK","FAIL"),IF(C7=D7,"OK","FAIL"))` |
| `D8` | `='Scenario Engine'!AP7*(1-'Scenario Engine'!AI7)` |
| `E8` | `=IF(AND(ISNUMBER(C8),ISNUMBER(D8)),D8-C8,"")` |
| `G8` | `=IF(AND(ISNUMBER(C8),ISNUMBER(D8)),IF(ABS(E8)<=F8,"OK","FAIL"),IF(C8=D8,"OK","FAIL"))` |
| `D9` | `='Scenario Engine'!AP15` |
| `E9` | `=IF(AND(ISNUMBER(C9),ISNUMBER(D9)),D9-C9,"")` |
| `G9` | `=IF(AND(ISNUMBER(C9),ISNUMBER(D9)),IF(ABS(E9)<=F9,"OK","FAIL"),IF(C9=D9,"OK","FAIL"))` |
| `D10` | `='Scenario Engine'!AN11` |
| `E10` | `=IF(AND(ISNUMBER(C10),ISNUMBER(D10)),D10-C10,"")` |
| `G10` | `=IF(AND(ISNUMBER(C10),ISNUMBER(D10)),IF(ABS(E10)<=F10,"OK","FAIL"),IF(C10=D10,"OK","FAIL"))` |
| `D11` | `='Scenario Engine'!AN12` |
| `E11` | `=IF(AND(ISNUMBER(C11),ISNUMBER(D11)),D11-C11,"")` |
| `G11` | `=IF(AND(ISNUMBER(C11),ISNUMBER(D11)),IF(ABS(E11)<=F11,"OK","FAIL"),IF(C11=D11,"OK","FAIL"))` |
| `D12` | `='Scenario Engine'!AN14` |
| `E12` | `=IF(AND(ISNUMBER(C12),ISNUMBER(D12)),D12-C12,"")` |
| `G12` | `=IF(AND(ISNUMBER(C12),ISNUMBER(D12)),IF(ABS(E12)<=F12,"OK","FAIL"),IF(C12=D12,"OK","FAIL"))` |
| `D13` | `=COUNTIF('Lists & Config'!J6:J100,"USA-NY-IND")` |
| `E13` | `=IF(AND(ISNUMBER(C13),ISNUMBER(D13)),D13-C13,"")` |
| `G13` | `=IF(AND(ISNUMBER(C13),ISNUMBER(D13)),IF(ABS(E13)<=F13,"OK","FAIL"),IF(C13=D13,"OK","FAIL"))` |
| `D14` | `=COUNTIF('Lists & Config'!J6:J100,"DEU-GMPF")+COUNTIF('Lists & Config'!J6:J100,"ITA-INTL")+COUNTIF('Lists & Config'!J6:J100,"USA-NJ-DIGITAL")+COUNTIF('Lists & Config'!J6:J100,"CAN-NB-LIFT-MAJOR")+COUNTIF('Lists & Config'!J6:J100,"CAN-NB-LIFT-MICRO")` |
| `E14` | `=IF(AND(ISNUMBER(C14),ISNUMBER(D14)),D14-C14,"")` |
| `G14` | `=IF(AND(ISNUMBER(C14),ISNUMBER(D14)),IF(ABS(E14)<=F14,"OK","FAIL"),IF(C14=D14,"OK","FAIL"))` |
| `D15` | `=COUNTIF('Lists & Config'!J6:J100,"TEST-*")` |
| `E15` | `=IF(AND(ISNUMBER(C15),ISNUMBER(D15)),D15-C15,"")` |
| `G15` | `=IF(AND(ISNUMBER(C15),ISNUMBER(D15)),IF(ABS(E15)<=F15,"OK","FAIL"),IF(C15=D15,"OK","FAIL"))` |
| `D16` | `='FX & Financing'!B7` |
| `E16` | `=IF(AND(ISNUMBER(C16),ISNUMBER(D16)),D16-C16,"")` |
| `G16` | `=IF(AND(ISNUMBER(C16),ISNUMBER(D16)),IF(ABS(E16)<=F16,"OK","FAIL"),IF(C16=D16,"OK","FAIL"))` |
| `D17` | `=COUNTIFS('Programme Rules'!A5:A90,"<>",'Programme Rules'!H5:H90,"<>Test only")` |
| `E17` | `=IF(AND(ISNUMBER(C17),ISNUMBER(D17)),D17-C17,"")` |
| `G17` | `=IF(AND(ISNUMBER(C17),ISNUMBER(D17)),IF(ABS(E17)<=F17,"OK","FAIL"),IF(C17=D17,"OK","FAIL"))` |


# 21. Incorporated Saracen Bridge knowledge documents — full text


## Source: `Saracen_Bridge_Analytics_Bespoke_GPT_Instructions.md`

# SARACEN BRIDGE ANALYTICS — REPORT PRODUCTION STANDARD

## Purpose
Use the uploaded `Saracen_Bridge_Analytics_Master_Report_Template.docx` as the mandatory base file for every Saracen Bridge Analytics report. Do not recreate the document from a blank file. The objective is consistent branding, page architecture, typography, table treatment, confidentiality wording and decision-led analysis across all report types.

## Mandatory production workflow
1. Complete the relevant intake and analysis before producing the report.
2. Open or copy the master DOCX template as the working document.
3. Replace every square-bracket placeholder, including placeholders in the cover, header, footer, tables and signature block.
4. Delete all instructional placeholder text that is not part of the final report.
5. Retain the cover, high-resolution logo, header, footer, page numbering, margins, confidentiality notice, typography, colours and table styles.
6. Use the named Word styles already present in the document. Do not apply ad-hoc fonts, colours or spacing.
7. Update the table of contents and all Word fields before delivery.
8. Deliver the completed report as a `.docx`. Produce a PDF only when the user asks for one.
9. Review every page before delivery. Correct clipping, awkward page breaks, split headings, crowded tables and excessive blank space.

## Brand and layout rules
- Page size: A4.
- Primary font: Calibri.
- Main section headings: 14 pt, bold, charcoal.
- Subsection headings: 11 pt, bold, gold.
- Body text: 11 pt, charcoal, approximately 1.15 line spacing.
- Palette: charcoal/black, metallic gold and restrained neutral greys. Do not introduce unrelated colours.
- Use the gold bridge logo only from the uploaded master assets. Do not redraw, recolour, distort or substitute the logo.
- Keep the cover premium and restrained. Do not add decorative graphics that compete with the logo.
- Tables must use the charcoal header row, gold lower rule, white body cells, deliberate column widths and sufficient padding.
- Do not use zebra striping, emojis, clip art, bright colours or generic stock imagery.
- Avoid long walls of text. Use headings, concise paragraphs, callouts and tables only where they improve comprehension.
- Keep headings with the paragraph or table that follows. Do not leave headings stranded at the bottom of a page.

## Language, figures and evidence
- Use UK English spelling and grammar.
- Use a commercially honest, analytical, investor-ready and tactfully direct tone.
- Distinguish confirmed facts, user-supplied information, assumptions, estimates and professional judgement.
- Never invent facts, sources, values, attachments, approvals or market evidence.
- Preserve the currency supplied by the user. Do not convert currencies unless expressly instructed.
- State all talent compensation, quote and value figures in USD.
- Use dates in the format `26 July 2026`.
- Use en dashes for ranges and minus signs only for negative numbers.
- Cite substantive external evidence. For film and television market assessments, include Deadline Hollywood and The Hollywood Reporter among the standard industry sources where relevant, together with appropriate primary or specialist sources.

## Mandatory confidentiality wording
Use this wording on the cover and in the limitations section:

> This report contains confidential analytical material prepared by Saracen Bridge Analytics. It is intended solely for authorised recipients and must not be distributed without permission.

## Core report architecture
Every report must contain:
1. Cover and document-control information.
2. Executive Summary with a decisive conclusion.
3. Project / Transaction Overview.
4. Analysis and Findings.
5. Commercial and Financial Assessment, where relevant.
6. Risk and Opportunity Assessment.
7. Recommendations and Next Steps.
8. Methodology, Sources and Limitations.

Delete sections that are genuinely irrelevant, but do not change the visual system or numbering logic.

## Report-type section maps

### International Sales Estimates
Executive Summary; Project Overview and Budget Band; Market Positioning; Cast and Director Value; Comparable Film Analysis; Territory-by-Territory MG / Pre-Sales; Streaming Value; Global Revenue Summary; Risks; Opportunities; Producer Action Checklist; Final Commercial Recommendation; Commercial Readiness Score; one-page Schedule C.

### Script Coverage
Executive Summary; Revised Logline and Five-Sentence Pitch; Synopsis; Creative Analysis; Market Positioning; Risks; Opportunities; Development Notes; Strengths and Weaknesses; Budget Band Guidance; Weighted Scoring Matrix; Producer Action Checklist; Final Recommendation.

### Finance / Viability / Investment
Executive Summary; Transaction Overview; Sources and Uses; Capital Stack; Revenue and Repayment Analysis; Scenario and Sensitivity Analysis; Security and Conditions Precedent; Principal Risks; Mitigants; Decisions Required; Immediate Actions.

### Casting / Bankability
Executive Summary; Role Requirements; Candidate Analysis; Audience Recognition; Territory and Platform Value; Comparable Performance; Availability / Quote Assumptions; Risks; Recommended Priority List; Approach Strategy.

### Due Diligence / Project Review
Executive Summary; Scope; Materials Reviewed; Findings by Workstream; Missing or Inconsistent Information; Risk Rating; Conditions to Proceed; Action Tracker; Final Recommendation.

### Meeting Brief / Action Tracker
Purpose; Current Position; Completed, Outstanding and Blocked Items; Owners; Evidence; Decisions Required; Exact Questions to Raise; Immediate Next Steps.

## Executive-summary standard
The Executive Summary must answer, without requiring the reader to search the report:
- What is the overall view?
- What is driving that view?
- What is the principal risk or dependency?
- What decision is required?
- What should happen next?

## Tables and financial presentation
- Use purposeful columns; do not make every column the same width.
- Right-align monetary amounts and percentages where practical.
- Show low, base and high scenarios only when supported by a stated methodology.
- State whether values are gross, net, producer receipts, distributor receipts, MG, pre-sale, valuation or enterprise value.
- State the date, currency and basis of every material valuation or forecast.
- Do not present unsupported precision. Use ranges where evidence supports ranges rather than a single point estimate.

## Final quality control
Before delivery, confirm that:
- all placeholders and drafting notes have been removed;
- the title, project, client, date, version and classification are correct;
- the header and footer match the report;
- the contents and page numbers are updated;
- figures reconcile across narrative and tables;
- sources are named and current;
- the conclusion, recommendation and action plan are internally consistent;
- the report contains no unsupported claims;
- the finished DOCX visually matches the master template.


## Source: `Saracen_Bridge_Finance_Model_Formatting_Knowledge_v1.md`

# Saracen Bridge Finance Model Formatting & Spain Production Finance Knowledge  
**Version:** V1.0  
**Date:** 19 August 2026  
**Prepared for:** Saracen Bridge Finance Plan Modeller bespoke GPT  
**Classification:** Internal / confidential working knowledge  

## 1. Purpose

This knowledge document records the preferred formatting, workbook architecture and modelling treatment established in the updated **SHADE Spain Finance Model – Non-Stop 50% Guarantee** workbook. It should be used by the bespoke GPT as a reference standard when building, improving or auditing Saracen Bridge Film & TV finance models.

The document is intended to improve consistency of:
- workbook structure;
- lender / investor presentation;
- conditional finance-source treatment;
- Spain production incentive modelling;
- Non-Stop / Screen Capital participation modelling;
- validation flags, checks and print-pack logic.

This document is not a legal, tax or accounting opinion. It should not override project-specific documents, signed agreements, professional tax advice or lender requirements.

## 2. Scope of Use

Use this standard when the user asks for:
- a film or television finance model;
- a lender-ready or investor-ready workbook;
- a finance-plan validation model;
- a Spain production model;
- a model involving tax-incentive cash-flowing;
- a model involving in-kind services, deferred equity, producer deferrals or conditional guarantees;
- an audit or improvement of an existing Saracen Bridge workbook.

Do **not** assume that the SHADE / Non-Stop terms apply to every project. Treat them as project-specific unless the user expressly instructs otherwise.

## 3. Core Modelling Principles

All Saracen Bridge finance models should observe the following principles:

1. Separate **Inputs**, **Calculations** and **Outputs**.
2. Do not bury assumptions inside formulas.
3. Use auditable formulas with clearly labelled source cells.
4. Keep all finance-source statuses visible.
5. Distinguish confirmed cash, signed conditional finance, draft finance, LOI-only finance, user assumptions and missing sources.
6. Show lender / investor implications clearly on the Dashboard and Print Pack.
7. Preserve Saracen Bridge branding: restrained charcoal / gold palette, clean tables, professional formatting and concise commentary.
8. Include checks for finance-plan imbalance, debt-cap breach, missing documentation, tax-incentive validation and source double counting.
9. Use UK English.
10. Treat all figures as user-supplied or model-derived unless independently verified.

## 4. Standard Workbook Architecture

For Film & TV finance models, use the following preferred tab structure:

1. **Dashboard**  
   Executive view of the model, overall status, capital stack summary, finance-plan balance, key alerts and recommendation.

2. **Inputs**  
   All core assumptions, including project details, currency, FX, budget, incentive assumptions, facility rates, finance-source assumptions and status flags.

3. **Finance Plan**  
   Sources and uses, conditional-source classification, finance-plan balance, source status, debt / equity split and funding shortfall.

4. **Tax Incentive**  
   Jurisdiction, eligible spend, deduction / credit percentage, cap, timing, cash-flow treatment, facility cost and validation status.

5. **Debt Schedule**  
   Senior / gap / incentive loan sizing, interest, fees, repayment priority and debt-cap checks.

6. **Cashflow**  
   Timing of spend, receipts, incentive drawdown, facility interest accrual, producer deferrals and cash shortfall / surplus.

7. **Sales Estimates**  
   Territory sales, MGs, pre-sales, estimates, timing, signed / draft status and reliance notes.

8. **Waterfall**  
   Repayment order, lender priority, incentive facility repayment, MG recoupment, deferred equity, producer deferrals and equity returns.

9. **Investor Returns**  
   Equity investment, recoupment, preferred return, profit participation, IRR / MOIC where supported.

10. **Sensitivity**  
   Low / base / high cases for budget, eligible spend, incentive timing, sales, interest rates and gap requirement.

11. **Checks**  
   Formula checks, balance checks, status checks, circularity checks, debt-cap checks, documentation checks and tax validation checks.

12. **Collateral**  
   Required documents, conditions precedent, owner, status and completion evidence.

13. **Print Pack**  
   Lender / investor one-page summary, sources and uses, conditional-source schedule, risk summary, CP checklist and decision recommendation.

Where a workbook already has project-specific operational tabs, such as schedule, budget detail, cast DOOD or location plan, retain them and add the Saracen Bridge finance tabs around them.

## 5. Formatting Standard

Use the SHADE v2 workbook presentation style as the preferred model format:

- dark charcoal section headers;
- restrained metallic gold highlights;
- white body cells;
- clear row and column spacing;
- consistent table headings;
- concise explanatory notes above key tables;
- traffic-light status logic;
- no bright colours, emojis, clip art or unnecessary decoration;
- professional lender-ready language;
- all monetary amounts clearly identified by currency;
- percentages formatted consistently;
- formulas used for derived values rather than hardcoded outputs.

Dashboard and Print Pack should be readable without the user needing to inspect detailed working sheets.

## 6. Finance-Source Status Logic

Use a clear source-status classification in the Finance Plan, Dashboard and Checks tabs.

Recommended categories:

| Status | Meaning | Model treatment |
|---|---|---|
| Confirmed cash | Fully documented, available and unconditional | Can be included as bankable finance |
| Signed but conditional | Executed but subject to CPs | Include with amber status and CP notes |
| Draft / conditional | Draft agreement or term sheet only | Include as conditional; do not treat as bankable |
| LOI / non-binding | Non-binding expression of intent | Include only with clear caveat |
| User instruction / to document | User has instructed modelling assumption but no supporting documents supplied | Include as scenario assumption only |
| Assumption only | Internal working assumption | Show as red / high risk |
| Missing | Required source or evidence absent | Exclude from bankable total unless user asks for pro forma view |

The model should separately show:
- total financing sources;
- bankable / confirmed sources;
- conditional sources;
- finance gap;
- sources requiring documentation.

## 7. Spain Production Modelling Standard

When a production is to be produced in Spain, include a dedicated Spain production basis in Inputs and Dashboard.

Key assumptions to capture:

- production country / territory;
- physical production hub;
- qualifying spend basis;
- eligible spend percentage;
- tax incentive / deduction percentage;
- cap and limitation assumptions;
- whether incentive is treated as a receivable, deduction, subsidy, tax credit or cash-flowed facility;
- who administers the incentive;
- who cash-flows the incentive;
- facility interest rate;
- upfront fee, if any;
- timing of drawdown and repayment;
- tax-counsel / accountant validation status;
- documentation required before lender reliance.

Unless Spanish tax advice has been supplied, mark the incentive as **illustrative / subject to validation**.

## 8. Non-Stop 50% Guarantee Package — Project-Specific Treatment

For SHADE, the user has instructed the following treatment:

> Non-Stop will guarantee 50% of the budget, including the Spanish tax incentive. Non-Stop will cash-flow the Spanish tax incentive at 12% per annum with no initial fee. The remainder of the 50% will be made up with in-kind services treated as equity deferred.

Model this as a single Non-Stop package to avoid double counting.

### 8.1 Calculation Logic

Let:

- **Gross Budget** = total gross production budget before incentive deduction.
- **Non-Stop Package %** = 50%.
- **Non-Stop Package Amount** = Gross Budget × 50%.
- **Spanish Incentive Amount** = modelled incentive / deduction / receivable.
- **Incentive Facility Amount** = Spanish Incentive Amount cash-flowed by Non-Stop.
- **Facility Interest Rate** = 12% per annum.
- **Initial Facility Fee** = 0%.
- **In-Kind Deferred Equity Amount** = Non-Stop Package Amount – Incentive Facility Amount.

The incentive facility and in-kind deferred equity must sit inside the 50% Non-Stop package, not on top of it.

### 8.2 Presentation

In the Finance Plan, show the Non-Stop package as:

| Component | Treatment |
|---|---|
| Non-Stop total guarantee package | 50% of gross budget |
| Spanish tax incentive cash-flow facility | Included within the 50% package |
| Facility interest | 12% p.a. |
| Initial fee | 0% |
| Remainder of 50% package | In-kind services treated as deferred equity |
| Status | User instruction / to document unless binding agreement supplied |

### 8.3 Required Checks

Add checks to confirm:

1. Non-Stop package equals 50% of gross budget.
2. Incentive facility is not double-counted as separate finance outside the 50% package.
3. In-kind deferred equity amount is not negative.
4. Facility interest rate is 12% p.a.
5. Initial fee is 0%.
6. Spanish incentive remains subject to validation unless supporting tax memo is supplied.
7. Binding guarantee / facility / services documents are listed as CPs.

## 9. Treatment of In-Kind Services as Deferred Equity

When services are contributed in kind and treated as deferred equity:

- identify the service provider;
- list service categories;
- require fair-market valuation support;
- distinguish cash spend avoided from recoupable / deferred equity value;
- check whether the services are eligible or non-eligible for incentive purposes;
- avoid counting the same value as both production cost reduction and equity contribution;
- include recoupment position in the Waterfall only after terms are documented;
- flag legal / tax / accounting validation as required.

The model should not present in-kind services as unconditional cash unless actual cash is being contributed.

## 10. Tax-Incentive Cash-Flowing

When a tax incentive is cash-flowed:

- show the underlying incentive amount separately from the financing facility;
- identify the lender / cash-flow provider;
- show interest rate, upfront fee, legal fees, closing costs and repayment date;
- calculate interest as a time-based cost;
- place repayment in the Waterfall before equity recoupment unless instructed otherwise;
- flag timing risk, audit risk, eligibility risk and certification risk;
- require a tax memo, production accountant review and incentive-administration plan.

For SHADE / Non-Stop, use:
- 12% p.a. interest;
- no initial fee;
- Spanish incentive cash-flowed by Non-Stop;
- included within the 50% Non-Stop package.

## 11. Debt and Capital Stack Standards

Default Saracen Bridge assumption unless instructed otherwise:

- maximum 70% debt / 30% equity capital structure;
- development finance generally limited to 3%–5% of budget;
- all debt must be supported by identifiable collateral or repayment source;
- gap / senior debt should be sized last, after signed MGs, equity, incentive and in-kind treatment are established.

Add debt-cap checks and finance-plan balance checks in the Checks tab.

## 12. Collateral and Conditions Precedent

The Collateral tab should include at least:

- final approved budget;
- signed finance plan;
- Spanish tax incentive memo;
- eligible spend mapping;
- Non-Stop 50% guarantee agreement;
- incentive cash-flow facility agreement;
- in-kind services / deferred-equity schedule;
- completion bond quote and approval;
- chain of title;
- sales estimates;
- pre-sale / MG agreements;
- CAMA / collection account;
- interparty agreement;
- production services agreement;
- insurance;
- payroll / employment structure review;
- tax-counsel sign-off.

Each item should include:
- workstream;
- status;
- required evidence;
- owner;
- completion test.

## 13. Print Pack Standard

The Print Pack should provide a one-page lender / investor summary with:

- project name;
- production basis;
- model conclusion;
- gross budget;
- net budget where relevant;
- Non-Stop package amount where applicable;
- incentive facility treatment;
- finance-plan status;
- principal risks;
- immediate decision required;
- CPs before investment close.

The summary must be concise, commercial and direct. It should be suitable for a lender, investor, producer, sales agent or completion guarantor.

## 14. Report Relationship

If a formal report is requested, continue to use the Saracen Bridge Analytics Master Report Template as the base document. Do not generate a report from a blank document.

This knowledge document is for model logic and formatting. It does not replace the report template or the report production standard.

## 15. Recommended Knowledge-File Use

Recommended bespoke GPT knowledge setup:

1. **Keep** the Saracen Bridge Analytics Master Report Template.  
   It remains the mandatory base file for formal reports.

2. **Keep** the Saracen Bridge Analytics Bespoke GPT Instructions / Report Production Standard.  
   It governs report workflow, branding, confidentiality language and source standards.

3. **Add** this document as a new knowledge file.  
   It gives the bespoke GPT a reusable standard for finance-model formatting, Spain production treatment and Non-Stop 50% package logic.

4. **Do not replace** existing core report knowledge with this document.  
   It has a different purpose.

5. **Consider replacing or archiving** any older, generic finance-model guidance only if it conflicts with this document or causes the GPT to produce a less polished workbook format.

## 16. Model Response Guidance for the GPT

When responding to finance-model tasks, the GPT should:

- be commercially realistic and concise;
- state whether the model is bankable, conditional or illustrative;
- avoid presenting unsigned or user-instructed assumptions as confirmed finance;
- flag missing documents;
- recommend next steps;
- preserve Saracen Bridge formatting;
- create actual workbooks where requested, rather than merely describing changes;
- provide a concise change summary after each workbook update.

## 17. Non-Negotiable Cautions

The GPT must not:

- treat a tax incentive as guaranteed cash without validation;
- double count an incentive as both a deduction and a finance source;
- double count in-kind services as both cost reduction and equity unless explicitly structured and documented;
- present non-binding LOIs as signed funding;
- bury assumptions inside formulas;
- remove audit checks to make a model appear cleaner;
- ignore mismatch between production country, country of origin, incentive jurisdiction and contractual documentation;
- create a formal report from a blank document when the master report template is available.


## Source: `02_Shared_Incentive_Model_Integration_Protocol.md`

# Saracen Bridge Shared Incentive Model Integration Protocol

Document ID: SB-XGPT-PROTOCOL-1.0  
Applies to: Finance Plan Modeller, Production Budgeting GPT and Production Scheduling GPT  
Effective: 26 August 2026

## Objective

Use one controlled incentive truth across budget, schedule and finance analysis without turning headline incentives into assumed cash. Maintain traceability from each budget line and schedule condition through the incentive component to permanent-finance treatment.

## Knowledge precedence

1. Reverify every material rule against a current official primary source before a definitive recommendation.
2. In the audited workbook, Programme Rules overrides headline or summary fields in Incentive Database.
3. Audit Exceptions, Sources and Audit, eligibility gates and availability status override scenario or scoring outputs.
4. Current operative official authority material overrides the dated workbook when more recent.
5. A blank, Not established, Subject to rules, zero placeholder or unresolved flag is unknown, not confirmed zero or affirmative eligibility.
6. Never use Closed, Limited, exhausted, oversubscribed, expired, time-limited or TEST programmes as committed value without current written confirmation of availability and project access.

## Shared identifiers

Every inter-GPT record must carry:

- Project ID — stable for the production.
- Scenario ID — stable for each location/finance structure.
- Programme ID — exactly as used in the approved incentive model.
- Component ID — stable for each programme and workstream combination.
- Budget Line ID — unique within the project.
- Milestone ID — unique within the project.
- Evidence Ref — a compact reference that maps to an official source, document, budget version or adviser confirmation.
- Version date — the date of the source project data.

Do not match records by title or description when an ID exists.

## Controlled workstream codes

Use: Development; Prep; Principal Photography; Second Unit; Stage; Virtual Production; SFX; Post; VFX; CGI; Animation; Sound; Music; Dubbing/Localisation; AI/Software/R&D; Training; Travel/Accommodation; Other.

Where one budget line spans workstreams, split the line or mark it Manual Review. Do not allocate by an invented percentage.

## Controlled status language

Eligibility Status: Eligible; Excluded; Manual Review; Unknown.  
Evidence Status: Confirmed; Assumption; Unresolved; Superseded.  
Gate Status: PASS; PRELIMINARY; FAIL.  
RAG: Green; Amber; Red.  
Recommendation Status: INDICATIVE; PRELIMINARY; CONDITIONALLY PREFERRED; VALIDATED.

Green requires all hard gates to pass. A high score cannot override a failed or unresolved eligibility, timing, availability, legal-route, tax-capacity, evidence or financing gate.

## Mandatory calculation bridge

Keep these values separate by component:

1. Qualifying-expenditure base.
2. Gross statutory benefit.
3. Tax, assistance or transfer leakage.
4. Application, audit, legal, entity and compliance costs.
5. Bankable or monetisable amount.
6. Incentive-loan advance and fees.
7. Expected certificate and cash-receipt dates.
8. Present-value benefit.
9. Incremental location cost.
10. Net present realisable benefit.

Net present realisable benefit equals present-value benefit less incremental location cost. Do not call gross statutory benefit cash received.

Unknown timing, fees, lender rate, advance rate, transfer haircut, tax effect or entity cost must remain unconfirmed and keep the result PRELIMINARY. Do not silently replace unknowns with zero.

## Budget handoff rules

The Budgeting GPT must supply line-level gross cost, currency, dated FX, reporting-currency cost, workstream, jurisdiction, payer or supplier/worker locality, residency where relevant, eligibility status and evidence.

It must distinguish local, non-local, eligible, excluded, Manual Review and Unknown spend. It must flag cast, ATL, related-party, payroll and workstream limitations. It must reconcile total mapped lines to the controlled project budget.

## Schedule handoff rules

The Scheduling GPT must supply application, pre-approval, cultural/economic certification, registration, start-of-qualifying-work, local-day, audit, completion, final-certificate and payment milestones.

It must show hard deadlines, dependencies, responsible owner and evidence. Expenditure before a required approval is a warning or failure under the programme rule. A missed mandatory deadline is Red.

## Finance handoff rules

The Finance Plan Modeller must import gross benefit, net/PV benefit, receipt date, bankable advance, repayment and costs as distinct fields.

An incentive receivable and a loan secured against that receivable are not two permanent finance sources. VAT or IVA recovery is working capital and must not close the permanent-finance gap.

## Cross-GPT change loop

A material change in any of the following returns the project through budget, schedule, incentive and finance checks:

- total budget or qualifying line allocation;
- jurisdiction, workstream or supplier/worker locality;
- prep, shoot, post, completion or application date;
- entity, payer, ownership or co-production route;
- programme status, rate, tier, cap, test or stacking rule;
- reporting currency, FX rate/date, lender term or payment timing.

The receiving GPT must state which prior outputs may now be stale.

## Source and confidentiality controls

Cite the exact official source for each material rate, cap, deadline, eligibility rule and status. Record source date and verification date. Secondary sources may discover a programme but cannot establish a material conclusion.

Keep projects separate. Never reuse a confidential budget, schedule, cast detail, finance term or commercial assumption in another project unless the user explicitly supplies it for that project.

## Required disclaimer

Every client-facing output must state:

This analysis is commercial decision support, not legal, tax or accounting advice. Incentive availability, eligibility, structure, accounting and tax treatment, application requirements, payment and financing must be confirmed with the relevant authority and appropriately qualified local advisers before reliance or commitment.


## Source: `09_Saracen_Bridge_Production_Incentives_GPT_Knowledge_v1_0.md`

# Saracen Bridge Production Incentives — Audited GPT Knowledge

**Document ID:** SB-PI-KB-1.0  
**Version:** 1.0 — final Stage 2 audit conversion  
**Snapshot date:** 26 August 2026  
**Source baseline:** Saracen_Bridge_Production_Incentive_Model_Stage_2.xlsx  
**Coverage:** 76 non-test programme records, 13 priority markets, 81 scoped jurisdictions, 40 declared research gaps  
**Intended use:** Knowledge file for a private production-location and incentive GPT  
**Authority:** Controlled research and screening aid; not tax, legal, accounting or investment advice

## Precedence and mandatory operating rules

This section overrides every programme record below.

1. **Treat this document as a dated candidate register, not live legal authority.** Reverify every rate, threshold, eligibility rule, application window, capacity, cap, stacking rule and source against a current official primary source before making a material recommendation.
2. **Never interpret “Not established,” “Subject to rules,” blank or a Stage 2 zero as zero cost, zero delay or affirmative eligibility.** It means unresolved.
3. **Do not calculate from headline rate alone.** Establish the legal route, qualifying applicant, eligible format, workstream, spend base, territoriality, resident/non-resident payroll, ATL/cast treatment, cultural/economic test, minimum spend, budget/episode thresholds, pre-approval date, caps, intensity limits and availability first.
4. **Use hard gates.** If a mandatory eligibility, timing, funding-capacity or evidence condition is failed, value the programme at zero. If it is unresolved, label the result PRELIMINARY and Amber or Red; never Green.
5. **Distinguish five amounts:** headline rate; qualifying-expenditure base; gross statutory benefit; bankable/monetisable proceeds; net present realisable benefit. Never call gross benefit “cash received.”
6. **Use programme-specific currency.** Convert project spend and benefits using a stated FX rate, source and date; show at least a sensitivity where currency exposure is material.
7. **Do not stack by default.** Establish whether programmes are compatible, mutually exclusive, alternative elections, parent/enhancement pairs, or subject to assistance/state-aid reductions.
8. **Do not use dependent enhancements independently.** In particular, British Columbia DAVE and Quebec VFX/animation enhancements require eligible parent claims and defined labour bases.
9. **Selective funds are probabilities, not receivables.** Present them separately from automatic credits/rebates and do not assume an award or full maximum.
10. **Closed, exhausted or oversubscribed programmes have zero available value** unless a current official window/allocation is confirmed.
11. **Cite the exact source supporting each material conclusion** and state the source date. If official sources conflict, use the operative legislation/current administrator guidance and escalate the conflict.
12. **Protect confidentiality.** Do not expose uploaded project budgets, financing plans, cast data or commercial terms outside the current authorised analysis.

## Required project intake before a definitive answer

Ask only for missing high-impact inputs, but obtain: format and episode/runtime; total budget and currency; detailed workstream spend; production/post/VFX schedule; shooting days; local and non-local payroll; applicant/production-company structure; ownership/co-production status; cultural-test facts; intended jurisdictions; finance plan; incentive borrowing assumptions; delivery route; and material creative/logistical constraints.

If the user provides insufficient data, give a preliminary shortlist and a targeted diligence list, not a definitive ranking.

## Approved calculation sequence

For each programme and workstream:

1. Determine project-specific qualifying spend from budget lines.
2. Apply statutory tiers and enhancements to the correct bases.
3. Apply eligible-base caps, credit caps, budget/episode caps, annual caps and state-aid/intensity limits according to their distinct meanings.
4. Apply taxability and interactions with grants or other assistance.
5. Convert to the project reporting currency using a stated dated FX rate.
6. Deduct application, audit, legal, local-company, transfer and monetisation costs.
7. Calculate bankable proceeds using lender advance rate and disallow unavailable amounts.
8. Calculate finance cost from amount, timing, rate and fees.
9. Discount the remaining receipt to present value using expected receipt date.
10. Deduct incremental location, travel, accommodation, payroll, infrastructure and compliance costs.

Report the following calculation explicitly:

`net present realisable benefit = gross statutory benefit - tax and assistance effects - fees and transfer haircut - finance cost - incremental location cost`

Never substitute a single flat-rate formula where a tier, enhancement, tax effect or base limitation applies.

## Required output controls

Every recommendation must state:

- Project facts, assumptions and unresolved items separately.
- Programme status and date verified.
- Exact legal route and eligible workstream.
- Headline, qualifying base, gross, bankable amount, expected cash receipt, timing, present value and true net saving.
- FX basis and sensitivity.
- Stacking/election treatment.
- RAG status with hard-gate reasons.
- Official sources and matters requiring local adviser/administrator confirmation.

## Known limitations inherited from Stage 2

- The original scenario engine is not approved for definitive calculations.
- Most programme cost, financing, transfer and payment-lag fields were unknown but stored as zero.
- Programme summaries do not establish project eligibility.
- Regional/local coverage is incomplete, as recorded in the research-gap register.
- A current official source may have changed after the snapshot date.

## Programme register

The records below preserve the Stage 2 research content but add an audit classification and a mandatory programme-specific control. The original confidence label reflects source discovery, not full project-level confidence.

## Spain

### ESP-NAT-DOM — Spanish domestic / co-production tax credit

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Do not apply the 30% total-rate field as a flat rate. Calculate 30% on the first EUR 1 million of qualifying expenditure and 25% on the remainder, then apply the relevant per-production/per-episode limits and cultural/territorial conditions.
- **Jurisdiction:** Spain; country Spain; region/state Spain.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 30%; basis: 30% on first EUR 1m; 25% thereafter. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field EUR 20,000,000; annual field Not established; minimum local spend 50%. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Per-production cap EUR 20m; EUR 10m per episode. Cultural certificate and territoriality rules apply.
- **Evidence:** [official source](https://spainfilmcommission.com/en/shooting-in-spain/tax-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### ESP-NAT-FOR — Spanish foreign production tax credit

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Do not apply 30% to the whole base. Calculate 30% on the first EUR 1 million and 25% thereafter. Confirm minimum Spanish spend, minimum production cost, the 80% qualifying-base limit, the Spanish service-company route and the applicable cap before use.
- **Jurisdiction:** Spain; country Spain; region/state Spain.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 30%; basis: 30% on first EUR 1m; 25% thereafter. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend EUR 1,000,000; project field EUR 20,000,000; annual field Not established; minimum local spend 50%. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Minimum Spanish spend EUR 1m (EUR 200k animation); minimum production cost EUR 2m; qualifying base capped at 80% of total cost.
- **Evidence:** [official source](https://spainfilmcommission.com/en/shooting-in-spain/tax-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### ESP-CAN-FOR — Canary Islands foreign production incentive

- **Audit classification:** HIGH; **permitted use:** Headline screening only.
- **Mandatory audit control:** Treat the displayed 54% as an upper-tier headline, not a flat rate. Confirm the current first-tier rate, remainder rate, cap, qualifying entity and island expenditure under current Canary rules before calculating.
- **Jurisdiction:** Canary Islands; country Spain; region/state Canary Islands.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 54%; basis: Up to 54%/50% first tier and 45% remainder; exact tier depends on current rules. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Special Canary fiscal regime. Confirm the exact first-tier percentage, cap, island spend and qualifying entity before modelling.
- **Evidence:** [official source](https://spainfilmcommission.com/en/shooting-in-spain/tax-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.

### ESP-CAN-GRANT — Canary Islands 2026 audiovisual grants

- **Audit classification:** HIGH; **permitted use:** Selective and time-limited.
- **Mandatory audit control:** This is a selective 2026 call, not an automatic incentive. The recorded window runs through 11 September 2026; recheck live status before presenting value and treat it as expired after that date unless a later call is confirmed.
- **Jurisdiction:** Canary Islands; country Spain; region/state Canary Islands.
- **Workstream / instrument:** Development / Grant.
- **Headline only:** Not percentage-modelled; basis: Selective grant; not percentage-modelled. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field EUR 30,000; annual field EUR 520,000; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; 2026 call open 23 July-11 September 2026; subject to selective assessment and available budget.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Development maximum EUR 30k; short production maximum EUR 20k. Use only for eligible calls and project types.
- **Evidence:** [official source](https://sede.gobiernodecanarias.org/sede/tramites/11006); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### ESP-NAV-DOM — Navarre domestic audiovisual deduction

- **Audit classification:** HIGH; **permitted use:** Headline screening only.
- **Mandatory audit control:** Use the current Navarre foral legislation and administrator confirmation for the exact tier, cap, intensity limit, certificate and territorial-spend requirements.
- **Jurisdiction:** Navarre; country Spain; region/state Navarre.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 50%; basis: Up to 50% on first EUR 5m; current foral conditions apply. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm current Navarre certification, territorial spend, intensity limits and company structure.
- **Evidence:** [official source](https://spainfilmcommission.com/en/shooting-in-spain/tax-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.

### ESP-NAV-FOR — Navarre international production deduction

- **Audit classification:** HIGH; **permitted use:** Headline screening only.
- **Mandatory audit control:** Use the current Navarre foral legislation and administrator confirmation for exact eligible expenditure, cap, intensity limit and service-company requirements.
- **Jurisdiction:** Navarre; country Spain; region/state Navarre.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 35%; basis: Up to 35% qualifying Navarre expenditure. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Use the current foral order and administrator confirmation for exact eligibility and cap.
- **Evidence:** [official source](https://spainfilmcommission.com/en/shooting-in-spain/tax-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.

### ESP-BAS-ARA — Araba audiovisual tax incentive

- **Audit classification:** HIGH; **permitted use:** Headline screening only.
- **Mandatory audit control:** The national Spain summary is insufficient calculation authority for Araba. Obtain the current territory-specific foral rule, effective provision, qualifying base, cap, intensity limit and monetisation route.
- **Jurisdiction:** Araba; country Spain; region/state Basque Country.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 60%; basis: Up to 60%; exact foral rate and base are territory-specific. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Separate foral authority. Confirm exact percentage, cap, cultural/territorial conditions and effective legislation.
- **Evidence:** [official source](https://spainfilmcommission.com/en/shooting-in-spain/tax-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.

### ESP-BAS-BIZ — Bizkaia audiovisual tax incentive

- **Audit classification:** HIGH; **permitted use:** Headline screening only.
- **Mandatory audit control:** The national Spain summary is insufficient calculation authority for Bizkaia. Obtain the current territory-specific foral rule, effective provision, qualifying base, cap, intensity limit and monetisation route.
- **Jurisdiction:** Bizkaia; country Spain; region/state Basque Country.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 60%; basis: Up to 60%; exact foral rate and base are territory-specific. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Separate foral authority. Confirm exact percentage, cap, cultural/territorial conditions and effective legislation.
- **Evidence:** [official source](https://spainfilmcommission.com/en/shooting-in-spain/tax-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.

### ESP-BAS-GIP — Gipuzkoa audiovisual tax incentive

- **Audit classification:** HIGH; **permitted use:** Headline screening only.
- **Mandatory audit control:** The national Spain summary is insufficient calculation authority for Gipuzkoa. Obtain the current territory-specific foral rule, effective provision, qualifying base, cap, intensity limit and monetisation route.
- **Jurisdiction:** Gipuzkoa; country Spain; region/state Basque Country.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 60%; basis: Up to 60%; exact foral rate and base are territory-specific. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Separate foral authority. Confirm exact percentage, cap, cultural/territorial conditions and effective legislation.
- **Evidence:** [official source](https://spainfilmcommission.com/en/shooting-in-spain/tax-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.


## United Kingdom

### GBR-AVEC — Audiovisual Expenditure Credit - standard film / HETV

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** The 34% AVEC rate is a taxable gross expenditure credit. Model the corporation-tax effect and the 80% qualifying-expenditure cap; at a 25% corporation-tax rate, 34% gross is 25.5% net before other leakage.
- **Jurisdiction:** United Kingdom; country United Kingdom; region/state United Kingdom.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 34%; basis: 34% taxable expenditure credit; model corporation-tax effect separately. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Certification required; test BFI cultural test / co-production route; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Qualifying UK expenditure and 80% cap rules apply. Do not treat 34% as net cash benefit without tax modelling.
- **Evidence:** [official source](https://www.gov.uk/hmrc-internal-manuals/creative-industries-expenditure-credit-manual/crec021110); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### GBR-AVEC-ANI — Audiovisual Expenditure Credit - animation / children's TV

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** The 39% rate is a taxable gross expenditure credit. Model the corporation-tax effect and the applicable 80% qualifying-expenditure cap; at 25% corporation tax, 39% gross is 29.25% net before other leakage.
- **Jurisdiction:** United Kingdom; country United Kingdom; region/state United Kingdom.
- **Workstream / instrument:** Animation / Refundable tax credit.
- **Headline only:** 39%; basis: 39% taxable expenditure credit; model corporation-tax effect separately. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Certification required; test BFI cultural test / co-production route; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm format qualification and qualifying UK expenditure.
- **Evidence:** [official source](https://www.gov.uk/hmrc-internal-manuals/creative-industries-expenditure-credit-manual/crec021110); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### GBR-IFTC — Independent Film Tax Credit

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** The 53% IFTC rate is taxable, not a net cash percentage. Confirm low-budget certification, creative connection, the GBP 23.5 million total-core-cost ceiling, the GBP 15 million relevant-expenditure cap and timing. At 25% corporation tax, 53% gross is 39.75% net before other leakage.
- **Jurisdiction:** United Kingdom; country United Kingdom; region/state United Kingdom.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 53%; basis: 53% taxable credit on qualifying expenditure; GBP 15m relevant global expenditure cap. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field GBP 7,950,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Certification required; test Independent film and BFI certification conditions; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Core expenditure must not exceed GBP 23.5m. Claims available from 1 April 2025. Net benefit requires corporation-tax adjustment.
- **Evidence:** [official source](https://www.gov.uk/hmrc-internal-manuals/creative-industries-expenditure-credit-manual/crec021110); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### GBR-VFX — Additional VFX expenditure credit

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** The 39% enhanced AVEC rate is taxable. The 80% cap is removed only for qualifying UK VFX costs. The enhanced claim requires a final certificate and is available in completion or later periods; interim claims remain at the standard rate.
- **Jurisdiction:** United Kingdom; country United Kingdom; region/state United Kingdom.
- **Workstream / instrument:** VFX/CGI / Refundable tax credit.
- **Headline only:** 39%; basis: 39% taxable credit on relevant UK VFX expenditure. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Certification required; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Relevant VFX expenditure is exempt from the usual 80% cap; claims from 1 April 2025.
- **Evidence:** [official source](https://www.gov.uk/government/publications/corporation-tax-additional-tax-credit-for-visual-effects-vfx-expenditure/additional-tax-relief-for-visual-effects-vfx); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.


## Ireland

### IRL-481 — Section 481 Film Tax Credit

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Apply 32% to the lowest statutory base, not automatically to all local spend. Confirm the 80% total-qualifying-cost limitation, EUR 125 million eligible-expenditure ceiling, EUR 40 million maximum credit, pre-commencement certification and payment timing.
- **Jurisdiction:** Republic of Ireland; country Ireland; region/state Republic of Ireland.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 32%; basis: 32% of the lowest of eligible spend, 80% total qualifying cost or EUR 125m. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field EUR 40,000,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Certification required; test Cultural test and producer-company conditions; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Up to 90% may be claimed against budgeted eligible expenditure, with balance on completion; project cap shown is 32% of EUR 125m.
- **Evidence:** [official source](https://www.revenue.ie/en/companies-and-charities/reliefs-and-exemptions/film-relief/index.aspx); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### IRL-UNSCRIPTED — Unscripted Production Corporation Tax Credit

- **Audit classification:** HIGH; **permitted use:** Conditional and time-limited.
- **Mandatory audit control:** Use 20% only after confirming the minimum EUR 250,000 total production cost, EUR 125,000 eligible spend, EUR 15 million eligible-spend ceiling, EUR 3 million maximum credit, interim certification and the 31 December 2028 end date.
- **Jurisdiction:** Republic of Ireland; country Ireland; region/state Republic of Ireland.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 20%; basis: 20% qualifying expenditure subject to current regulations. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Certification required; test Eligible unscripted production and certification; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm commencement, eligible formats, cap, certification and interaction with other support.
- **Evidence:** [official source](https://www.screenireland.ie/news/fis-eireann-screen-ireland-welcomes-the-newly-published-regulations-for-20-unscripted-production-corporation-tax-credit); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.

### IRL-SCREEN-FUND — Screen Ireland production funding

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not calculate this as an automatic percentage or assume an award. Confirm the relevant call, applicant route, budget availability, assessment result, drawdown and recoupment terms.
- **Jurisdiction:** Republic of Ireland; country Ireland; region/state Republic of Ireland.
- **Workstream / instrument:** Principal photography / Screen fund.
- **Headline only:** Not percentage-modelled; basis: Selective funding; not percentage-modelled. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Development, production and distribution support varies by call and project; treat as discretionary until an award is secured.
- **Evidence:** [official source](https://www.screenireland.ie/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence Medium.


## Australia

### AUS-LOC — Federal Location Offset

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** The Location, PDV and Producer Offsets are mutually exclusive federal routes. Confirm QAPE of at least AUD 20 million and, for series, AUD 1.5 million per hour; include the 1% training-expenditure requirement for applicable productions and the Australian post-production-provider condition.
- **Jurisdiction:** Australia; country Australia; region/state Australia.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 30%; basis: 30% qualifying Australian production expenditure. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend AUD 20,000,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Australian applicant / service structure required; pre-approval Yes; test QAPE and training/infrastructure obligations; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Series minimum AUD 1.5m per hour. Mutually exclusive with Producer and PDV offsets for the same production.
- **Evidence:** [official source](https://www.arts.gov.au/sites/default/files/documents/location-offset-guidelines-july-2026.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### AUS-PDV — Federal PDV Offset

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** The Location, PDV and Producer Offsets are mutually exclusive. Apply the PDV rules only to qualifying Australian PDV expenditure and confirm the Australian provider, certificate, timing and any training obligation.
- **Jurisdiction:** Australia; country Australia; region/state Australia.
- **Workstream / instrument:** VFX/CGI / Refundable tax credit.
- **Headline only:** 30%; basis: 30% qualifying Australian PDV expenditure. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend AUD 500,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Australian PDV provider required; pre-approval Yes; test QAPE test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Available regardless of where principal photography occurs; cannot be combined with Location or Producer Offset for the same production.
- **Evidence:** [official source](https://www.arts.gov.au/sites/default/files/documents/location-offset-guidelines-july-2026.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### AUS-PROD-FEAT — Federal Producer Offset - feature film

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Do not stack this federal Producer Offset with the federal Location or PDV Offset. Confirm significant Australian content, eligible format, QAPE base and certification before modelling 40%.
- **Jurisdiction:** Australia; country Australia; region/state Australia.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 40%; basis: 40% QAPE for qualifying feature films. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Australian producer required; pre-approval Yes; test Significant Australian content / official co-production; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Producer Offset route is mutually exclusive with Location and PDV offsets.
- **Evidence:** [official source](https://www.arts.gov.au/sites/default/files/documents/location-offset-guidelines-july-2026.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### AUS-PROD-OTHER — Federal Producer Offset - eligible non-feature formats

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Do not stack this federal Producer Offset with the federal Location or PDV Offset. Confirm format, significant Australian content, QAPE base and certification before modelling 30%.
- **Jurisdiction:** Australia; country Australia; region/state Australia.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 30%; basis: 30% QAPE for qualifying non-feature formats. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Australian producer required; pre-approval Yes; test Significant Australian content / official co-production; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm format and expenditure thresholds. Mutually exclusive with Location and PDV offsets.
- **Evidence:** [official source](https://www.arts.gov.au/sites/default/files/documents/location-offset-guidelines-july-2026.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### AUS-NSW-FIN — Screen NSW Production Finance

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** New South Wales; country Australia; region/state New South Wales.
- **Workstream / instrument:** Principal photography / Screen fund.
- **Headline only:** Not percentage-modelled; basis: Selective finance; not percentage-modelled. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Use current 2026 guidelines, intake status and project-specific offer; award is not automatic.
- **Evidence:** [official source](https://content.screen.nsw.gov.au/assets/Program-Documents/Production-Finance-Guidelines_20260618.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence Medium.

### AUS-QLD-INC — Screen Queensland production incentives

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Queensland; country Australia; region/state Queensland.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** Not percentage-modelled; basis: Discretionary incentive; project-specific offer. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm current programme, eligible Queensland spend, cap, application window and funding availability.
- **Evidence:** [official source](https://screenqueensland.com.au/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence Medium.

### AUS-VIC-INC — Victorian Screen Incentive

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Victoria; country Australia; region/state Victoria.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** Not percentage-modelled; basis: Discretionary 2026-27 incentive; project-specific offer. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Do not model a percentage until VicScreen issues or confirms a project-specific offer.
- **Evidence:** [official source](https://vicscreen.vic.gov.au/images/uploads/Funding_Programs/Guidelines/Victorian_Screen_Incentive_Guidelines_2026-27.docx); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence Medium.

### AUS-SA-PROD — South Australian Production Incentive

- **Audit classification:** MEDIUM; **permitted use:** Screening record; reverify before use.
- **Mandatory audit control:** The source and headline were identified in Stage 2, but project eligibility, exact qualifying base, fees, timing, stacking, capacity and monetisation were not fully established.
- **Jurisdiction:** South Australia; country Australia; region/state South Australia.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 10%; basis: 10% qualifying South Australian production spend. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm eligible spend, application timing and state funding availability.
- **Evidence:** [official source](https://www.safilm.com.au/incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### AUS-SA-PDV — South Australian PDV Rebate

- **Audit classification:** MEDIUM; **permitted use:** Screening record; reverify before use.
- **Mandatory audit control:** The source and headline were identified in Stage 2, but project eligibility, exact qualifying base, fees, timing, stacking, capacity and monetisation were not fully established.
- **Jurisdiction:** South Australia; country Australia; region/state South Australia.
- **Workstream / instrument:** VFX/CGI / Cash rebate.
- **Headline only:** 10%; basis: 10% qualifying South Australian PDV spend. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** May stack with the 30% federal PDV Offset subject to both programmes. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Potential combined headline support of 40% uses separate federal and state records; prevent double counting of ineligible bases.
- **Evidence:** [official source](https://www.safilm.com.au/incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### AUS-SA-PAY — South Australian payroll tax exemption

- **Audit classification:** MEDIUM; **permitted use:** Screening record; reverify before use.
- **Mandatory audit control:** The source and headline were identified in Stage 2, but project eligibility, exact qualifying base, fees, timing, stacking, capacity and monetisation were not fully established.
- **Jurisdiction:** South Australia; country Australia; region/state South Australia.
- **Workstream / instrument:** Principal photography / Payroll credit.
- **Headline only:** 5%; basis: Up to 4.95% payroll-tax saving on eligible feature-film payroll. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Apply only to payroll otherwise subject to South Australian payroll tax; not an all-spend rebate.
- **Evidence:** [official source](https://www.safilm.com.au/incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence Medium.

### AUS-WA-WAPAI — WA Production Attraction Incentive

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Western Australia; country Australia; region/state Western Australia.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 10%; basis: Discretionary base support of 10% qualifying WA expenditure. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend AUD 3,500,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Prior approval required; grant paid after completion and audit; assessment commonly 4-6 weeks.
- **Evidence:** [official source](https://www.screenwest.com.au/wp-content/uploads/2025/10/WA-Production-Attraction-Incentive-WAPAI-Guidelines.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### AUS-TAS-PROD — Screen Tasmania Production Support

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Tasmania; country Australia; region/state Tasmania.
- **Workstream / instrument:** Principal photography / Screen fund.
- **Headline only:** Not percentage-modelled; basis: Selective support; up to AUD 50k non-recoupable, larger support may be equity. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend AUD 30,000; project field AUD 50,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Expected spend ratio is typically 4:1 live action and 3:1 factual/animation; most finance must be in place.
- **Evidence:** [official source](https://www.screen.tas.gov.au/funding/production_support); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence Medium.

### AUS-NT-FUND — Screen Territory production support

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Northern Territory; country Australia; region/state Northern Territory.
- **Workstream / instrument:** Principal photography / Screen fund.
- **Headline only:** Not percentage-modelled; basis: Selective 2026-27 funding; not percentage-modelled. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm current stream, cap, local-spend ratio and intake before including value.
- **Evidence:** [official source](https://screenterritory.nt.gov.au/_resources/documents/screen-territory-guidelines-2026-2027.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence Medium.


## France

### FRA-TRIP — Tax Rebate for International Productions (TRIP)

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Confirm at least EUR 250,000 of French eligible spend or 50% of worldwide budget, the live-action shooting-day rule, cultural test, application-receipt timing and EUR 30 million cap. Use 40% only where qualifying French VFX expenditure exceeds EUR 2 million.
- **Jurisdiction:** France; country France; region/state France.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 40%; basis: 30% eligible French spend; 40% if qualifying French VFX spend exceeds EUR 2m. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend EUR 250,000; project field EUR 30,000,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Cultural / production criteria; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Minimum is EUR 250k or 50% of world budget; live action generally requires at least five French shoot days.
- **Evidence:** [official source](https://www.cnc.fr/web/en/tax-rebate/the-tax-rebate-for-international-productions-trip_190742?utm=); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.


## Germany

### DEU-DFFF-I — German Federal Film Fund I

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Germany; country Germany; region/state Germany.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 30%; basis: Up to 30% eligible German production costs. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend EUR 1,000,000; project field EUR 5,000,000; annual field Not established; minimum local spend 25%. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Eligible German cost base generally capped at 80% total; lower minimums apply to documentaries; animation/virtual minimum EUR 2m.
- **Evidence:** [official source](https://www.ffa.de/files/dfff/richtlinie/260101_DFFF_Guidelines_EN.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### DEU-DFFF-II — German Federal Film Fund II

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Germany; country Germany; region/state Germany.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 30%; basis: Up to 30% eligible German production-service costs. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend EUR 8,000,000; project field EUR 25,000,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Theatrical service production and German-cost thresholds; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Total production generally at least EUR 20m; German service costs at least EUR 8m, or EUR 2m for animation/virtual production.
- **Evidence:** [official source](https://www.ffa.de/files/dfff/richtlinie/260101_DFFF_Guidelines_EN.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### DEU-GMPF — German Motion Picture Fund

- **Audit classification:** HIGH; **permitted use:** Limited availability.
- **Mandatory audit control:** Keep excluded from definitive available value until the current application window and budget capacity are confirmed.
- **Jurisdiction:** Germany; country Germany; region/state Germany.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 30%; basis: Up to 30% eligible German costs. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test High-budget series / non-theatrical film rules; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Limited; 2026 applications constrained; 2027 applications paused pending further notice.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Non-repayable support. At least 45% financing is generally required at submission; check programme capacity before reliance.
- **Evidence:** [official source](https://www.ffa.de/german-motion-picture-fund-gmpf.html); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.


## Belgium

### BEL-TAX-SHELTER — Belgian audiovisual Tax Shelter

- **Audit classification:** CRITICAL; **permitted use:** Manual structure only.
- **Mandatory audit control:** This is an investor tax-shelter financing structure, not a simple production-spend percentage. Model the qualifying investor contribution, certificate, spend ratios, pricing, fees, state-aid limits and recoupment manually.
- **Jurisdiction:** Belgium; country Belgium; region/state Belgium.
- **Workstream / instrument:** Principal photography / Other.
- **Headline only:** Not percentage-modelled; basis: Investor tax-shelter financing; manual deal calculation required. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** The 310% investor exemption is not a production rebate rate. Model actual financing proceeds, qualifying Belgian spend, intermediary cost and recoupment terms separately.
- **Evidence:** [official source](https://finances.belgium.be/fr/entreprises/impot_des_societes/avantages_fiscaux/tax-shelter-production-audiovisuelle); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### BEL-FLA-SCREEN — Screen Flanders

- **Audit classification:** HIGH; **permitted use:** Selective and time-limited.
- **Mandatory audit control:** Treat as a selective fund. Recheck the current call date, annual budget and available capacity; do not assume the EUR 400,000 maximum will be awarded.
- **Jurisdiction:** Flanders; country Belgium; region/state Flemish Region and Flemish Community.
- **Workstream / instrument:** Principal photography / Screen fund.
- **Headline only:** Not percentage-modelled; basis: Selective refundable advance; not percentage-modelled. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field EUR 400,000; annual field EUR 3,500,000; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** 2026 budget EUR 3.5m across two calls; foreign projects apply through a Belgian co-producer.
- **Evidence:** [official source](https://www.screenflanders.be/en/financing/screen-flanders); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### BEL-WAL-WALLIMAGE — Wallimage production support

- **Audit classification:** HIGH; **permitted use:** Selective and time-limited.
- **Mandatory audit control:** Treat as selective support subject to the current 2026 sessions, eligibility, sustainability rules, assessment, disbursement and recoupment terms.
- **Jurisdiction:** Wallonia; country Belgium; region/state Walloon Region and French Community.
- **Workstream / instrument:** Principal photography / Screen fund.
- **Headline only:** Not percentage-modelled; basis: Selective regional investment; not percentage-modelled. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Four 2026 calls; local-spend, vendor and sustainability rules apply. Use project-specific award terms.
- **Evidence:** [official source](https://www.wallimage.be/news/reglement-2026-une-reforme-concertee-pour-lavenir-de-laudiovisuel-wallon/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.

### BEL-BRU-SCREEN — screen.brussels fund

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Confirm the live call, regional expenditure, assessment criteria, available budget, contract and recoupment terms; do not model an automatic rate.
- **Jurisdiction:** Brussels; country Belgium; region/state Brussels-Capital Region.
- **Workstream / instrument:** Principal photography / Screen fund.
- **Headline only:** Not percentage-modelled; basis: Selective regional funding; not percentage-modelled. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm the current call, eligible Brussels spend, project cap and availability before assigning value.
- **Evidence:** [official source](https://screen.brussels/en); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence Medium.


## Italy

### ITA-INTL — Italian tax credit for foreign productions

- **Audit classification:** CRITICAL; **permitted use:** Conditional and capacity-limited.
- **Mandatory audit control:** Replace the Stage 2 2024 source with the 2026 application decree. Availability is window- and budget-limited; confirm Italian executive-production/post-production eligibility, preventive approval, available resources and the current 70%/final-balance disbursement process.
- **Jurisdiction:** Italy; country Italy; region/state Italy.
- **Workstream / instrument:** Principal photography / Transferable tax credit.
- **Headline only:** 40%; basis: 40% eligible Italian production cost; 30% for specified non-European ATL costs. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend EUR 250,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Annual company/group cap EUR 20m; post-only work can qualify. AI costs are generally ineligible except specified AI special-effects costs with disclosure requirements.
- **Evidence:** [official source](https://cinema.cultura.gov.it/wp-content/uploads/2026/05/20260518_D1.D-apertura-sessione-Tax-credit-internazionale_signed_signed.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.


## Hungary

### HUN-FILM — Hungarian Film Incentive

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Distinguish the 30% statutory rate from the up-to-37.5% relationship to Hungarian spend created by capped non-Hungarian costs. Include the administration fee of up to 2.5%, financing/collection-account leakage and current capacity before presenting a net value.
- **Jurisdiction:** Hungary; country Hungary; region/state Hungary.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 37.5%; basis: 30% eligible Hungarian spend; effective support may reach 37.5% of Hungarian spend through capped non-Hungarian eligible costs. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field HUF 70,000,000,000; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Non-Hungarian eligible spend is capped at 25% of Hungarian eligible spend. Post-financing; registration and local production structure required.
- **Evidence:** [official source](https://nfi.hu/en/filming-in-hungary/hungarian-film-incentive); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.


## Czech Republic

### CZE-PROD — Czech audiovisual incentive - conventional production

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** The CZK 450 million figure is a maximum eligible-expenditure base, not a credit-value cap. Apply format-specific minimum spend, the 80% budget-base ceiling, 50% state-aid intensity limit, registration fee and application timing.
- **Jurisdiction:** Czech Republic; country Czech Republic; region/state Czech Republic.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 25%; basis: 25% eligible Czech spend. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CZK 18,000,000; project field CZK 450,000,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Minimum shown is feature-film threshold; format-specific thresholds apply. International costs may receive support based on withholding tax paid.
- **Evidence:** [official source](https://www.filmcommission.cz/en/production-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CZE-DIGITAL — Czech audiovisual incentive - animation / digital production

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** The CZK 450 million figure is a maximum eligible-expenditure base, not a credit-value cap. Apply the 35% digital/animation route only to its defined eligible base, with format thresholds, state-aid limits, registration fee and timing.
- **Jurisdiction:** Czech Republic; country Czech Republic; region/state Czech Republic.
- **Workstream / instrument:** Animation / Cash rebate.
- **Headline only:** 35%; basis: 35% eligible Czech animation / digital-production spend. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CZK 5,000,000; project field CZK 450,000,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm classification, Czech service-company requirement, cultural test and current allocation.
- **Evidence:** [official source](https://www.filmcommission.cz/en/production-incentives/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.


## Dominican Republic

### DOM-TTC — Dominican Republic Transferable Tax Credit

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Include the mandatory audit and transfer economics. The credit cannot be transferred below 60% of face value, so a material transfer haircut is possible; zero haircut in Stage 2 is an unknown, not a safe assumption.
- **Jurisdiction:** Dominican Republic; country Dominican Republic; region/state Dominican Republic.
- **Workstream / instrument:** Principal photography / Transferable tax credit.
- **Headline only:** 25%; basis: 25% qualifying Dominican production expenditure. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend USD 500,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** No stated project cap. Transfer price cannot be below 60% of face value; registration, audit and screen-credit requirements apply.
- **Evidence:** [official source](https://dgcine.gob.do/en/film-incentives/dr-film-incentives-overview/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### DOM-VAT — Dominican Republic VAT exemption

- **Audit classification:** CRITICAL; **permitted use:** Manual tax analysis only.
- **Mandatory audit control:** Do not calculate 18% of total local spend. Apply the exemption only to expressly eligible goods and services under the approved project route, after considering invoicing, import and recoverability rules.
- **Jurisdiction:** Dominican Republic; country Dominican Republic; region/state Dominican Republic.
- **Workstream / instrument:** Principal photography / VAT/sales tax relief.
- **Headline only:** 18%; basis: 18% VAT exemption only on directly related qualifying goods/services. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend USD 500,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** May complement the transferable credit; avoid applying 18% to non-taxable or ineligible spend. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Requires qualifying production and local legal presence. Model only the VAT actually avoided.
- **Evidence:** [official source](https://dgcine.gob.do/en/film-incentives/legal-framework/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence Medium.


## United States

### USA-GA-FILM — Georgia Entertainment Industry Investment Act credit

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Include mandatory audit and monetisation costs. Confirm the 20% base, conditional 10% uplift, USD 500,000 threshold, eligible company/spend, transfer or withholding route and current certification timing.
- **Jurisdiction:** Georgia; country United States; region/state Georgia.
- **Workstream / instrument:** Principal photography / Transferable tax credit.
- **Headline only:** 30%; basis: 20% base plus 10% Georgia promotion uplift. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend USD 500,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Credit may offset Georgia tax/withholding or be sold. Mandatory audit applies to productions certified from 2023.
- **Evidence:** [official source](https://dor.georgia.gov/film-tax-credit-information); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### USA-NY-IND — New York Independent Film Production Tax Credit

- **Audit classification:** CRITICAL; **permitted use:** Exclude while closed.
- **Mandatory audit control:** The 2026 allocation is exhausted and the programme is not accepting applications for that allocation. Do not include any benefit unless a current application window and allocation are confirmed.
- **Jurisdiction:** New York; country United States; region/state New York.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 40%; basis: 30% base with conditional 5-10% additions; programme-specific caps apply. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Closed; 2026 allocation fully committed; 2027 application windows published.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** USD 100m annual allocation. Separate pools apply by budget; non-labour qualified-cost cap USD 60m. Do not assume availability for 2026.
- **Evidence:** [official source](https://esd.ny.gov/new-york-state-independent-film-production-tax-credit-program); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### USA-NY-POST — New York Post-Production Tax Credit

- **Audit classification:** MEDIUM; **permitted use:** Screening record; reverify before use.
- **Mandatory audit control:** The source and headline were identified in Stage 2, but project eligibility, exact qualifying base, fees, timing, stacking, capacity and monetisation were not fully established.
- **Jurisdiction:** New York; country United States; region/state New York.
- **Workstream / instrument:** Picture post / Refundable tax credit.
- **Headline only:** 40%; basis: 30% qualifying post costs; conditional 5% upstate and 10% specified-county labour additions. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field USD 45,000,000; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Use workstream-specific eligible cost bases; annual allocation and application timing apply.
- **Evidence:** [official source](https://www.esd.ny.gov/new-york-state-film-tax-credit-program-post-production); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### USA-NJ-FILM — New Jersey Film and Digital Media Tax Credit - film

- **Audit classification:** CRITICAL; **permitted use:** Conditional and fee-loaded.
- **Mandatory audit control:** Apply the location-based rate and expenditure/threshold tests. Include application, approval, issuance, transfer, audit and third-party budget-review costs; Stage 2 zero-cost fields materially overstate net value.
- **Jurisdiction:** New Jersey; country United States; region/state New Jersey.
- **Workstream / instrument:** Principal photography / Transferable tax credit.
- **Headline only:** 35%; basis: 30% within 30-mile NYC radius; up to 35% elsewhere. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend USD 1,000,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Alternative 60% qualified-cost threshold may apply. Principal photography generally must begin within 180 days; end-credit requirements apply.
- **Evidence:** [official source](https://www.njeda.gov/film/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### USA-NJ-DIGITAL — New Jersey digital media content credit

- **Audit classification:** CRITICAL; **permitted use:** Limited/deferred capacity.
- **Mandatory audit control:** The digital-media allocation is oversubscribed. Treat as limited/deferred, not fully Active. Confirm the relevant fiscal-year queue, expenditure or payroll route and all programme fees before including value.
- **Jurisdiction:** New Jersey; country United States; region/state New Jersey.
- **Workstream / instrument:** VFX/CGI / Transferable tax credit.
- **Headline only:** 35%; basis: 30% qualifying digital media costs; 35% in specified southern counties. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Applications remain open for future allocations; current allocation is oversubscribed.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Confirm qualifying digital-media activity, labour, allocation year and location uplift.
- **Evidence:** [official source](https://www.njeda.gov/film/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### USA-NJ-POST — New Jersey independent post-production company credit

- **Audit classification:** CRITICAL; **permitted use:** Conditional and fee-loaded.
- **Mandatory audit control:** Apply the post-company eligibility and minimum qualifying-spend rules and include all application, review, issuance, audit and transfer costs. Do not use the headline rate as net value.
- **Jurisdiction:** New Jersey; country United States; region/state New Jersey.
- **Workstream / instrument:** Picture post / Transferable tax credit.
- **Headline only:** 40%; basis: 35% qualifying post spend; 40% at qualifying film-lease facility or studio partner. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend USD 500,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yes; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Project need not shoot in New Jersey. Confirm applicant and facility qualification.
- **Evidence:** [official source](https://www.njeda.gov/film/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.


## Canada

### CAN-FED-CPTC — Canadian Film or Video Production Tax Credit

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Apply the Canadian-content ownership/control and qualified-labour rules, assistance interactions, certification timing and CAVCO fee. Do not treat the rate as an all-spend credit.
- **Jurisdiction:** Canada; country Canada; region/state Canada.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 25%; basis: 25% qualified Canadian labour; labour base generally capped at 60% production cost. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Canadian-controlled taxable corporation; pre-approval CAVCO certification required; test Canadian content and ownership/control; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Mutually exclusive with federal PSTC for the same production. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Maximum effective benefit is generally 15% of production cost before provincial incentives; 180-day service standard.
- **Evidence:** [official source](https://www.canada.ca/en/canadian-heritage/services/funding/cavco-tax-credits/canadian-film-video-production.html); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-FED-PSTC — Film or Video Production Services Tax Credit

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** This is 16% of qualified Canadian labour, not all Canadian expenditure. Include CAVCO application fees and a realistic receipt timetable; the published service standard is 180 days.
- **Jurisdiction:** Canada; country Canada; region/state Canada.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 16%; basis: 16% qualified Canadian labour expenditure. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Canadian taxable production corporation; pre-approval CAVCO accreditation required; test Production services and minimum-cost tests; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Mutually exclusive with federal CPTC for the same production. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Foreign-owned productions may qualify through a Canadian corporation; 180-day service standard.
- **Evidence:** [official source](https://www.canada.ca/en/canadian-heritage/services/funding/cavco-tax-credits/film-video-production-services.html); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-BC-PSTC — British Columbia Production Services Tax Credit - basic

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Use the current 36% qualified-BC-labour basic rate and current procedure. Include the CAD 19,000 accreditation fee and confirm claim timing. Do not apply DAVE as a separate standalone incentive.
- **Jurisdiction:** British Columbia; country Canada; region/state British Columbia.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 36%; basis: 36% accredited BC labour for productions starting after 31 Dec 2024. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible BC production corporation; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Regional, distant, DAVE and major-production bonuses have separate qualifying bases and conditions; do not add them uniformly.
- **Evidence:** [official source](https://creativebc.com/motion-picture-tax-credits/production-services-tax-credit/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-BC-PSTC-DAVE — British Columbia PSTC DAVE bonus

- **Audit classification:** CRITICAL; **permitted use:** Enhancement only.
- **Mandatory audit control:** DAVE is an enhancement linked to a qualifying PSTC parent claim and applies to its defined labour base; it is not a standalone 16% credit on all VFX/post spend.
- **Jurisdiction:** British Columbia; country Canada; region/state British Columbia.
- **Workstream / instrument:** VFX/CGI / Refundable tax credit.
- **Headline only:** 16%; basis: 16% qualifying BC digital animation / VFX labour bonus. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible BC production corporation; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** May stack with BC PSTC basic where both sets of rules are met. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Apply only to the DAVE labour base; not all BC spend.
- **Evidence:** [official source](https://creativebc.com/motion-picture-tax-credits/production-services-tax-credit/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-BC-FIBC — Film Incentive BC - basic

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Confirm Canadian-content ownership/control, qualified BC labour, certification, current fee and assistance interactions. Treat any DAVE amount as a linked enhancement.
- **Jurisdiction:** British Columbia; country Canada; region/state British Columbia.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 40%; basis: 40% qualified BC labour for productions starting after 31 Dec 2024. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Canadian-owned and controlled BC corporation; pre-approval Yes; test Canadian content route; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Regional, distant, training, scriptwriting and DAVE bonuses use distinct bases and conditions.
- **Evidence:** [official source](https://creativebc.com/motion-picture-tax-credits/film-incentive-bc/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-BC-FIBC-DAVE — Film Incentive BC DAVE bonus

- **Audit classification:** CRITICAL; **permitted use:** Enhancement only.
- **Mandatory audit control:** DAVE is a linked enhancement to Film Incentive BC and applies to a defined labour base. Do not model it as an independent programme on the whole work package.
- **Jurisdiction:** British Columbia; country Canada; region/state British Columbia.
- **Workstream / instrument:** VFX/CGI / Refundable tax credit.
- **Headline only:** 16%; basis: 16% qualifying BC digital animation / VFX labour bonus. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Canadian-owned and controlled BC corporation; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** May stack with Film Incentive BC basic where eligible. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Apply only to qualifying DAVE labour.
- **Evidence:** [official source](https://creativebc.com/motion-picture-tax-credits/film-incentive-bc/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-AB-FTTC — Alberta Film and Television Tax Credit

- **Audit classification:** HIGH; **permitted use:** Conditional and capacity-limited.
- **Mandatory audit control:** Confirm the appropriate 22% or 30% stream, eligibility for the higher rate, minimum total production cost, financing/distribution evidence and current programme budget. The headline rate alone is insufficient.
- **Jurisdiction:** Alberta; country Canada; region/state Alberta.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 30%; basis: 22% all-spend base; 30% for qualifying Alberta-owned, treaty co-production or rural/remote route. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 499,999; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Alberta corporation; pre-approval Yes; test Economic and ownership/location criteria; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** No CAD 10m project cap. Apply within 120 days after principal photography starts; at least 50% financing required.
- **Evidence:** [official source](https://www.alberta.ca/system/files/jet-fttc-program-guidelines.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-ON-OFTTC — Ontario Film and Television Tax Credit

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Apply the Canadian-content and Ontario qualified-labour rules, certificate, assistance interactions and project-specific thresholds. Do not use as an all-spend rate.
- **Jurisdiction:** Ontario; country Canada; region/state Ontario.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 35%; basis: 35% eligible Ontario labour. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Canadian-controlled Ontario corporation; pre-approval Yes; test Ontario labour and domestic-production criteria; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Domestic-content route; confirm regional/first-time producer bonuses and expenditure periods.
- **Evidence:** [official source](https://www.ontariocreates.ca/our-sectors/film-tv/tax-credits); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-ON-OPSTC — Ontario Production Services Tax Credit

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Apply the minimum production-cost/episode thresholds and the labour-adequacy rule. Where Ontario labour is below 25% of Ontario expenditure, the eligible all-spend base is capped by the labour-based formula. Confirm federal stacking and assistance interactions.
- **Jurisdiction:** Ontario; country Canada; region/state Ontario.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 21.5%; basis: 21.5% qualifying Ontario production expenditures. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Ontario corporation; pre-approval Yes; test Production services and minimum-cost tests; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Available to qualifying domestic and foreign productions; confirm thresholds and excluded costs.
- **Evidence:** [official source](https://www.ontariocreates.ca/our-sectors/film-tv/tax-credits); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-ON-OCASE — Ontario Computer Animation and Special Effects Tax Credit

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Apply 18% only to qualifying Ontario labour for eligible animation/VFX activities and confirm the qualifying corporation, activity, certificate and interaction with other credits.
- **Jurisdiction:** Ontario; country Canada; region/state Ontario.
- **Workstream / instrument:** VFX/CGI / Refundable tax credit.
- **Headline only:** 18%; basis: 18% eligible Ontario labour for digital animation / VFX. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Ontario corporation; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** May complement qualifying Ontario production credits subject to rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Apply only to eligible OCASE labour.
- **Evidence:** [official source](https://www.ontariocreates.ca/our-sectors/film-tv/tax-credits); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-MB-ALL — Manitoba Film and Video Production Tax Credit - all-spend election

- **Audit classification:** CRITICAL; **permitted use:** Election; do not stack with labour route.
- **Mandatory audit control:** The 30% all-spend election and the labour-based election are alternatives, not additive provincial incentives. Model both and select the eligible route.
- **Jurisdiction:** Manitoba; country Canada; region/state Manitoba.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 30%; basis: 30% eligible Manitoba production costs. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Manitoba production corporation; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Alternative to the Manitoba labour-cost election. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Eligible costs include labour, goods, services and specified accommodation. Claim through corporate return after certification.
- **Evidence:** [official source](https://www.gov.mb.ca/finance/business/ccredits.html); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-MB-LAB — Manitoba Film and Video Production Tax Credit - labour election

- **Audit classification:** CRITICAL; **permitted use:** Election; do not stack with all-spend route.
- **Mandatory audit control:** The labour-based credit and 30% all-spend credit are alternative elections. Confirm the applicable bonuses and calculate the chosen route only.
- **Jurisdiction:** Manitoba; country Canada; region/state Manitoba.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 65%; basis: 45% eligible salaries; conditional bonuses can raise rate to 65%. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Manitoba production corporation; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Alternative to the Manitoba all-spend election. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Frequent-filming 10%, Manitoba producer 5%, and rural/northern 5% bonuses are conditional.
- **Evidence:** [official source](https://www.gov.mb.ca/finance/business/ccredits.html); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-NB-LIFT-MAJOR — LIFT major production stream

- **Audit classification:** HIGH; **permitted use:** Selective and capacity-limited.
- **Mandatory audit control:** Treat as limited/selective funding subject to current deadlines and available budget; do not assume an award or full headline percentage.
- **Jurisdiction:** New Brunswick; country Canada; region/state New Brunswick.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 35%; basis: Up to 25% eligible NB spend plus bonuses, capped at 35%. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company NB-established applicant with at least 50% NB ownership; pre-approval Yes; test Selective assessment and market readiness; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; 2026 deadline 27 August; limited budget and competitive review.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** For budgets over CAD 400k; service productions and co-productions may be eligible.
- **Evidence:** [official source](https://www.gnb.ca/fr/sujet/culture-patrimoine/subventions-financier/investissement-production.html); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-NB-LIFT-MICRO — LIFT micro-production stream

- **Audit classification:** HIGH; **permitted use:** Selective and capacity-limited.
- **Mandatory audit control:** Treat as limited/selective funding subject to current deadlines, available budget and the micro-stream cap; do not assume an award.
- **Jurisdiction:** New Brunswick; country Canada; region/state New Brunswick.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 30%; basis: Up to 30% forecast NB spend. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field CAD 100,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company NB-established applicant with at least 50% NB ownership; pre-approval Yes; test Selective assessment; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; 2026 deadline 27 August; limited budget and competitive review.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** For total production budgets below CAD 400k; maximum contribution CAD 100k.
- **Evidence:** [official source](https://www.gnb.ca/fr/sujet/culture-patrimoine/subventions-financier/investissement-production.html); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-NL-ALL — All-Spend Film and Video Production Tax Credit

- **Audit classification:** HIGH; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Confirm pre-production application, the CAD 20 million annual-per-project limit and mutual exclusivity with the older provincial tax-credit/equity programme.
- **Jurisdiction:** Newfoundland and Labrador; country Canada; region/state Newfoundland and Labrador.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 40%; basis: 40% eligible Newfoundland and Labrador production costs. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field CAD 20,000,000; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible NL corporation; pre-approval Part I before production begins; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Maximum credit CAD 20m annually per project. Cannot combine with the legacy labour credit or provincial equity programme for the same production.
- **Evidence:** [official source](https://www.gov.nl.ca/fin/tax-programs-incentives/business/all-spend-film-and-video-production-tax-credit/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-NS-I — Film & Television Production Incentive Fund - Stream I

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Nova Scotia; country Canada; region/state Nova Scotia.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 42%; basis: 26% eligible NS costs plus conditional rural, duration, content and distant-location additions. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 25,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Permanent establishment in Nova Scotia; pre-approval Yes; test 50-100% NS ownership and HOD requirements; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Distant-location incentive adds 7% or 10% on the relevant prorated basis; do not assume the full 16% uplift on all spend.
- **Evidence:** [official source](https://cch.novascotia.ca/gd/film-and-television-production-incentive-fund); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### CAN-NS-II — Film & Television Production Incentive Fund - Stream II

- **Audit classification:** HIGH; **permitted use:** Selective funding only.
- **Mandatory audit control:** Do not treat this as automatic. Confirm the live call, assessment, available budget, contract, drawdown and recoupment.
- **Jurisdiction:** Nova Scotia; country Canada; region/state Nova Scotia.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 41%; basis: 25% eligible NS costs plus conditional rural, duration, content and distant-location additions. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 25,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Permanent establishment in Nova Scotia; pre-approval Yes; test Service/ownership and HOD requirements; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Application is required before principal photography; additions have separate criteria and prorating.
- **Evidence:** [official source](https://cch.novascotia.ca/gd/film-and-television-production-incentive-fund); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### CAN-PE-FUND — PEI Film Production Fund

- **Audit classification:** HIGH; **permitted use:** Selective and capacity-limited.
- **Mandatory audit control:** Treat as a selective fund subject to current guidelines, scoring, available budget, contract, payment and recoupment terms.
- **Jurisdiction:** Prince Edward Island; country Canada; region/state Prince Edward Island.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 35%; basis: 32% eligible PEI costs; 1% PEI producer and 2% series bonuses. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 25,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Canadian-incorporated production company; pre-approval Before production begins; test Commercial licence and programme eligibility; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; 2026 guidelines published 13 February 2026; subject to available budget.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Eligible spend must arise from work completed in PEI; deemed non-resident labour is capped and pre-approved.
- **Evidence:** [official source](https://www.princeedwardisland.ca/sites/default/files/publications/prince_edward_island_film_production_fund_guidelines_0.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### CAN-QC-SERVICE — Quebec Production Services Tax Credit

- **Audit classification:** CRITICAL; **permitted use:** Conditional calculation only.
- **Mandatory audit control:** Apply the 25% basic service credit to its defined eligible base and calculate the 16% VFX/animation component only as an enhancement on eligible labour. Apply the combined-credit cap and SODEC fees.
- **Jurisdiction:** Quebec; country Canada; region/state Quebec.
- **Workstream / instrument:** Principal photography / Refundable tax credit.
- **Headline only:** 25%; basis: 25% eligible Quebec production costs. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 250,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Quebec production/service corporation; pre-approval Yes; test SODEC certification and eligible production; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Eligible base combines qualifying labour and goods rendered/provided in Quebec. Cannot combine with other Quebec film credits except eligible dubbing costs.
- **Evidence:** [official source](https://sodec.gouv.qc.ca/wp-content/uploads/fact-sheet-quebec-pstc-2026-march.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-QC-VFX — Quebec VFX and computer animation enhancement

- **Audit classification:** CRITICAL; **permitted use:** Enhancement only.
- **Mandatory audit control:** The 16% VFX/animation amount is an enhancement on eligible labour within a qualifying Quebec service claim, not a standalone 16% of the VFX work package. Apply the combined-credit cap and fees.
- **Jurisdiction:** Quebec; country Canada; region/state Quebec.
- **Workstream / instrument:** VFX/CGI / Refundable tax credit.
- **Headline only:** 16%; basis: 16% enhancement on the specified eligible VFX/animation labour base. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 250,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Quebec production/service corporation; pre-approval Yes; test SODEC certification and eligible VFX/animation; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** May enhance the Quebec service credit on its distinct VFX labour base. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** The VFX labour base includes 65% of specified contract costs; do not apply 16% to all Quebec spend.
- **Evidence:** [official source](https://sodec.gouv.qc.ca/wp-content/uploads/fact-sheet-quebec-pstc-2026-march.pdf); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-SK-DOM — Creative Saskatchewan Feature Film & TV Grant - Saskatchewan Stream

- **Audit classification:** HIGH; **permitted use:** Selective and capacity-limited.
- **Mandatory audit control:** Applications are accepted only while programme funds remain. Confirm the correct Saskatchewan stream, base, bonuses, eligible spend, contract and current allocation before modelling.
- **Jurisdiction:** Saskatchewan; country Canada; region/state Saskatchewan.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 40%; basis: Up to 30% eligible Saskatchewan expenditure; conditional bonuses capped at 40%. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Saskatchewan applicant / SPPC as required; pre-approval Yes; test Market trigger and selective assessment; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Continuous 2026-27 intake until funds are exhausted.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Frequent filming, rural and Saskatchewan post bonuses are conditional. Requests over CAD 5m require consultation.
- **Evidence:** [official source](https://www.creativesask.ca/our-support/film-tv/feature-film-tv-production/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-SK-SERVICE — Creative Saskatchewan Feature Film & TV Grant - Service Stream

- **Audit classification:** HIGH; **permitted use:** Selective and capacity-limited.
- **Mandatory audit control:** Applications are accepted only while funds remain. Confirm service-stream base, bonuses, eligible spend, contract and current allocation before modelling.
- **Jurisdiction:** Saskatchewan; country Canada; region/state Saskatchewan.
- **Workstream / instrument:** Principal photography / Grant.
- **Headline only:** 35%; basis: Up to 25% eligible Saskatchewan expenditure; conditional bonuses capped at 35%. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Eligible Saskatchewan applicant / SPPC as required; pre-approval Yes; test Service production and selective assessment; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Continuous 2026-27 intake until funds are exhausted.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Award is discretionary; confirm available funding and eligible expenditure.
- **Evidence:** [official source](https://www.creativesask.ca/our-support/film-tv/feature-film-tv-production/); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-NWT-SCRIPT — NWT Film Rebate - scripted

- **Audit classification:** CRITICAL; **permitted use:** Selective and capacity-limited.
- **Mandatory audit control:** Include the CAD 1 million annual programme budget and apply the separate travel enhancement only to eligible travel. Funding is available only until the annual allocation is committed.
- **Jurisdiction:** Northwest Territories; country Canada; region/state Northwest Territories.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 40%; basis: 40% NWT business goods/services and resident labour for scripted projects. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 100,000; project field Not established; annual field CAD 1,000,000; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Registered/licensed in NWT before funded activity; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Open 1 April-31 March until annual budget is allocated.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Separate 50% rebate may apply to eligible scheduled intra-NWT air travel.
- **Evidence:** [official source](https://www.iti.gov.nt.ca/en/services/nwt-film-rebate-program); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-NWT-NONSCRIPT — NWT Film Rebate - non-scripted

- **Audit classification:** CRITICAL; **permitted use:** Selective and capacity-limited.
- **Mandatory audit control:** Include the CAD 1 million annual programme budget and apply the separate travel enhancement only to eligible travel. Funding is available only until the annual allocation is committed.
- **Jurisdiction:** Northwest Territories; country Canada; region/state Northwest Territories.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 30%; basis: 30% NWT business goods/services and resident labour for non-scripted projects. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 100,000; project field Not established; annual field CAD 1,000,000; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Registered/licensed in NWT before funded activity; pre-approval Yes; test Economic / programme test; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Open 1 April-31 March until annual budget is allocated.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Annual programme budget CAD 1m; preference applies to projects with strong economic/professional benefit.
- **Evidence:** [official source](https://www.iti.gov.nt.ca/en/services/nwt-film-rebate-program); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.

### CAN-NU-I — Nunavut Spend Incentive - Stream I

- **Audit classification:** HIGH; **permitted use:** Conditional and capacity-limited.
- **Mandatory audit control:** Confirm the current Nunavut guidelines, eligible applicant, local spend, Inuit/Nunavut participation, available allocation, agreement and drawdown before presenting value.
- **Jurisdiction:** Nunavut; country Canada; region/state Nunavut.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 30%; basis: 27% eligible Nunavut costs plus up to 3% key-creative training enhancement. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 25,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Majority Nunavut-owned applicant with Nunavut head office; pre-approval Yes; test Ownership/control and key creative requirements; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Original Inuktut-language support is separate: 10% of Nunavut spend up to CAD 40k. Series support declines by season.
- **Evidence:** [official source](https://www.nunavutfilm.ca/nunavut-spend-incentive-program); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### CAN-NU-II — Nunavut Spend Incentive - Stream II

- **Audit classification:** HIGH; **permitted use:** Conditional and capacity-limited.
- **Mandatory audit control:** Confirm the current Nunavut stream, eligible applicant, local spend, Inuit/Nunavut participation, available allocation, agreement and drawdown before presenting value.
- **Jurisdiction:** Nunavut; country Canada; region/state Nunavut.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 20%; basis: 17% eligible Nunavut costs plus up to 3% key-creative training enhancement. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend CAD 25,000; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Nunavut-registered applicant with resident participation; pre-approval Yes; test Ownership/control and key creative requirements; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; Current official programme page reviewed 2026-08-21.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Inuktut versioning/original-language incentives use separate caps and conditions. Broadcaster/distributor evidence applies to larger Stream II projects.
- **Evidence:** [official source](https://www.nunavutfilm.ca/nunavut-spend-incentive-program); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-21; original confidence High.

### CAN-YT-PROD — Yukon Media Production Fund

- **Audit classification:** CRITICAL; **permitted use:** Selective and capacity-limited.
- **Mandatory audit control:** Funding is available only until allocated. Confirm Yukon-company eligibility, required key positions, market demand and financing evidence; a comfort letter and final approval use different financing thresholds.
- **Jurisdiction:** Yukon; country Canada; region/state Yukon.
- **Workstream / instrument:** Principal photography / Cash rebate.
- **Headline only:** 40%; basis: 25% approved Yukon spend; 2% per additional Yukon key position up to 10%, plus up to 5% ownership bonus. Never treat this field alone as net value.
- **Recorded thresholds/limits:** minimum spend Not established; project field Not established; annual field Not established; minimum local spend Not established. Confirm whether every limit is a benefit cap, eligible-base cap, budget cap or programme appropriation.
- **Eligibility gates:** local company Yukon-incorporated production company; pre-approval Yes; test Market demand and minimum three Yukon key positions; ATL/cast See current programme rules.
- **Workstream flags:** post Subject to rules; VFX/animation Subject to rules; virtual production Subject to rules; AI/R&D Not established. “Subject to rules” is unresolved, not affirmative eligibility.
- **Monetisation flags:** cash-flowable Subject to lender; assignable Subject to rules. Unknown Stage 2 inputs: payment lag, lender advance, finance rate, transfer haircut, application/audit/legal cost, local-company cost.
- **Lifecycle / capacity:** Active; 2026-27 intake opened 7 April 2026 and closes when funds are allocated.
- **Stacking note:** Confirm current stacking rules. Do not stack unless an official interaction rule is established.
- **Stage 2 note:** Maximum potential rebate is 40% of approved Yukon spend; full financing and project delivery conditions apply.
- **Evidence:** [official source](https://yukon.ca/en/apply-production-funds-professional-film-television-digital-media-project); original tier Tier 1; source snapshot 2026-08-21; audit checked 2026-08-26; original confidence High.


## Declared coverage gaps

A gap means no core official programme record was loaded in Stage 2. It does not prove that no programme exists.

- **ESP-AND — Andalusia (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-ARA — Aragon (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-AST — Principality of Asturias (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-BAL — Balearic Islands (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-CNT — Cantabria (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-CYL — Castile and León (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-CLM — Castilla-La Mancha (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-CAT — Catalonia (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-MAD — Community of Madrid (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-EXT — Extremadura (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-GAL — Galicia (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-RIO — La Rioja (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-MUR — Region of Murcia (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-VAL — Valencian Community (Spain, Autonomous community):** Research current official regional/local programmes and availability
- **ESP-CEU — Ceuta (Spain, Autonomous city):** Research current official regional/local programmes and availability
- **ESP-MEL — Melilla (Spain, Autonomous city):** Research current official regional/local programmes and availability
- **GBR-ENG — England (United Kingdom, Nation):** Research current official regional/local programmes and availability
- **GBR-SCT — Scotland (United Kingdom, Nation):** Research current official regional/local programmes and availability
- **GBR-WLS — Wales (United Kingdom, Nation):** Research current official regional/local programmes and availability
- **GBR-NIR — Northern Ireland (United Kingdom, Nation):** Research current official regional/local programmes and availability
- **AUS-ACT — Australian Capital Territory (Australia, Territory):** Research current official regional/local programmes and availability
- **FRA-REG — All metropolitan and overseas regions / territories (France, Regional / territorial):** Research current official regional/local programmes and availability
- **DEU-BW — Baden-Württemberg (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-BY — Bavaria (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-BE — Berlin (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-BB — Brandenburg (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-HB — Bremen (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-HH — Hamburg (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-HE — Hesse (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-NI — Lower Saxony (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-MV — Mecklenburg-Western Pomerania (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-NW — North Rhine-Westphalia (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-RP — Rhineland-Palatinate (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-SL — Saarland (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-SN — Saxony (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-ST — Saxony-Anhalt (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-SH — Schleswig-Holstein (Germany, Land):** Research current official regional/local programmes and availability
- **DEU-TH — Thuringia (Germany, Land):** Research current official regional/local programmes and availability
- **BEL-GER — German-speaking Community (Belgium, Community):** Research current official regional/local programmes and availability
- **ITA-REG — All regions and autonomous provinces (Italy, Regional / local):** Research current official regional/local programmes and availability

## Source-refresh protocol

Before a client-facing or financing decision:

1. Open the current official source and any linked operative guidance/legislation.
2. Record verification date, effective date, sunset/end date, application window and capacity.
3. Confirm exact rate denominator, tiers, eligible-base limits, benefit caps and intensity limits.
4. Confirm applicant, format, workstream, territorial spend, personnel and certification conditions.
5. Confirm stacking/election/dependency with every other proposed programme.
6. Obtain current fees, audit requirements, payment timetable, transfer terms and lender terms.
7. Save the source and change log; downgrade confidence if any material point is unresolved.

## Release control

This document is approved for private GPT knowledge upload as a **screening and controlled-analysis source**. It is not approved as a self-executing tax calculation engine. A GPT using it must browse/reverify current authoritative sources and must not issue a final Green recommendation while any critical eligibility, availability, stacking, financing, FX or source question remains unresolved.


# 22. Saracen Bridge Analytics master report template — extracted visible content

The following is the human-readable text/table extraction of the uploaded master DOCX. The original DOCX remains the authoritative layout/style asset for report production.

```text
[REPORT TITLE]
[PROJECT / CLIENT]
CONFIDENTIALITY NOTICE
This report contains confidential analytical material prepared by Saracen Bridge Analytics. It is intended solely for authorised recipients and must not be distributed without permission.
Contents
The table of contents updates automatically in Microsoft Word. Right-click the contents and select “Update Field” after the report is complete.
DOCUMENT CONTROL
1. Executive Summary
KEY REPORT METRICS
1.1 Principal Findings
[Finding one: the most decision-relevant commercial or creative point.]
[Finding two: the most material financial, market or execution point.]
[Finding three: the principal dependency, condition or next step.]
1.2 Recommendation
[State the recommended course of action, the conditions on which it depends and the immediate decision required from the authorised recipient.]
2. Project / Transaction Overview
Use this section for film, television, corporate finance, investment, production, distribution or transaction-level reporting. Retain only the fields relevant to the mandate.
2.1 Scope and Mandate
[Define what has been assessed, which materials were reviewed, the questions the report answers and any explicit exclusions.]
2.2 Core Assumptions
[Assumption one – clearly distinguish confirmed facts from working assumptions.]
[Assumption two – identify any external dependency or market variable.]
[Assumption three – state the currency, timing and valuation basis where applicable.]
3. Analysis and Findings
3.1 Analytical Assessment
[Present the core analysis in a logical sequence. Use short paragraphs, evidence-led conclusions and clear distinctions between fact, estimate, judgement and assumption.]
3.2 Comparative / Benchmark Analysis
3.3 Interpretation
[Explain what the evidence means for the project or transaction. Avoid merely repeating table data. Identify the commercial consequence.]
4. Commercial and Financial Assessment
4.1 Scenario Analysis
4.2 Commercial Drivers
[Driver one – cast, intellectual property, market access, distribution, customer demand or financing structure.]
[Driver two – timing, delivery, incentive, pre-sale, platform or counterparty dependency.]
[Driver three – execution capability, production value, competitive differentiation or downside protection.]
4.3 Sensitivities
[Identify the variables most capable of changing the result. Quantify the movement where data permits and explain the practical trigger.]
5. Risk and Opportunity Assessment
5.1 Principal Risks
5.2 Opportunities
6. Recommendations and Next Steps
6.1 Priority Action Plan
6.2 Conditions to Proceed
[Condition precedent or minimum requirement one.]
[Condition precedent or minimum requirement two.]
[Condition precedent or minimum requirement three.]
6.3 Final Recommendation
COMMERCIAL READINESS SCORE
7. Methodology, Sources and Limitations
7.1 Methodology
[Describe the analytical method, valuation basis, scoring framework, benchmarking approach and any scenario methodology used.]
7.2 Sources Reviewed
7.3 Limitations and Reliance
This report is a commercial and analytical assessment prepared from the information available at the date stated. Forecasts, valuations and sales estimates are indicative and may change with market conditions, package elements, contractual terms, timing and verification of underlying information. Saracen Bridge Analytics does not provide legal, tax or accounting advice. Appropriate professional advice and independent verification should be obtained before any binding commitment is made.
7.4 Confidentiality
This report contains confidential analytical material prepared by Saracen Bridge Analytics. It is intended solely for authorised recipients and must not be distributed without permission.
PREPARED BY

[TABLE 1]


[TABLE 2]
PREPARED FOR | [CLIENT / AUTHORISED RECIPIENT]
PREPARED BY | Saracen Bridge Analytics
REPORT DATE | [D MONTH YYYY]
VERSION | [FINAL / V1.0]
CLASSIFICATION | CONFIDENTIAL

[TABLE 3]
1. Executive Summary | 2
2. Project / Transaction Overview | 3
3. Analysis and Findings | 4
4. Commercial and Financial Assessment | 5
5. Risk and Opportunity Assessment | 6
6. Recommendations and Next Steps | 7
7. Methodology, Sources and Limitations | 8

[TABLE 4]
DOCUMENT STANDARD / All final reports must preserve the cover, header, footer, typography, gold/charcoal palette, confidentiality language and table styles in this master document.

[TABLE 5]
Version | Date | Prepared by | Status
V1.0 | [D MONTH YYYY] | Saracen Bridge Analytics | Final
 |  |  | 
 |  |  | 

[TABLE 6]
EXECUTIVE CONCLUSION / [Insert a concise, decision-led conclusion. State the central commercial view, viability position or recommendation in direct terms.]

[TABLE 7]
Overall assessment | Commercial readiness | Risk profile | Recommendation
[STRONG / MIXED / WEAK] | [0–100] | [LOW / MEDIUM / HIGH] | [PROCEED / REVISE / DECLINE]

[TABLE 8]
DECISION REQUIRED / [Insert the exact decision, approval or instruction required.]

[TABLE 9]
TITLE / PROJECT | [PROJECT TITLE]
REPORT TYPE | [SCRIPT COVERAGE / SALES ESTIMATES / FINANCE / CASTING / DUE DILIGENCE / MEETING BRIEF]
GENRE / SECTOR | [GENRE, SUBGENRE OR SECTOR]
BUDGET / TRANSACTION SIZE | [AMOUNT AND CURRENCY AS SUPPLIED]
COUNTRY / STRUCTURE | [COUNTRY OF ORIGIN, CO-PRODUCTION OR LEGAL STRUCTURE]
KEY PARTIES | [PRODUCERS, FINANCIERS, CAST, DIRECTOR, CLIENT OR COUNTERPARTIES]
STATUS | [DEVELOPMENT / PACKAGING / FINANCING / PRODUCTION / DELIVERY / ACTIVE TRANSACTION]
MANDATE | [PRECISE PURPOSE AND SCOPE OF THE REPORT]

[TABLE 10]
KEY ANALYTICAL INSIGHT / [Insert the single most important insight arising from the analysis, together with its practical implication.]

[TABLE 11]
Comparable / Benchmark | Relevance | Scale / Budget | Outcome / Value | Analytical Use
[COMPARABLE 1] | [HIGH / MEDIUM / LOW] | [VALUE] | [RESULT] | [WHY IT MATTERS]
[COMPARABLE 2] | [HIGH / MEDIUM / LOW] | [VALUE] | [RESULT] | [WHY IT MATTERS]
[COMPARABLE 3] | [HIGH / MEDIUM / LOW] | [VALUE] | [RESULT] | [WHY IT MATTERS]
[COMPARABLE 4] | [HIGH / MEDIUM / LOW] | [VALUE] | [RESULT] | [WHY IT MATTERS]

[TABLE 12]
Scenario | Key Assumptions | Gross Value / Revenue | Costs / Deductions | Net Position
Low / Conservative | [ASSUMPTIONS] | [AMOUNT] | [AMOUNT] | [AMOUNT]
Base / Expected | [ASSUMPTIONS] | [AMOUNT] | [AMOUNT] | [AMOUNT]
High / Upside | [ASSUMPTIONS] | [AMOUNT] | [AMOUNT] | [AMOUNT]

[TABLE 13]
COMMERCIAL POSITION / [Summarise whether the current package or transaction supports the proposed budget, valuation, financing requirement or market expectation.]

[TABLE 14]
Risk | Likelihood | Impact | Mitigation / Condition | Residual Rating
[RISK 1] | [LOW / MEDIUM / HIGH] | [LOW / MEDIUM / HIGH] | [ACTION OR CONDITION] | [RATING]
[RISK 2] | [LOW / MEDIUM / HIGH] | [LOW / MEDIUM / HIGH] | [ACTION OR CONDITION] | [RATING]
[RISK 3] | [LOW / MEDIUM / HIGH] | [LOW / MEDIUM / HIGH] | [ACTION OR CONDITION] | [RATING]
[RISK 4] | [LOW / MEDIUM / HIGH] | [LOW / MEDIUM / HIGH] | [ACTION OR CONDITION] | [RATING]

[TABLE 15]
Opportunity | Value Potential | Required Action | Timing
[OPPORTUNITY 1] | [LOW / MEDIUM / HIGH] | [ACTION] | [IMMEDIATE / SHORT / MEDIUM TERM]
[OPPORTUNITY 2] | [LOW / MEDIUM / HIGH] | [ACTION] | [IMMEDIATE / SHORT / MEDIUM TERM]
[OPPORTUNITY 3] | [LOW / MEDIUM / HIGH] | [ACTION] | [IMMEDIATE / SHORT / MEDIUM TERM]

[TABLE 16]
RISK CONCLUSION / [State whether the identified risks are manageable, financeable and proportionate to the opportunity. Specify any non-negotiable conditions.]

[TABLE 17]
Priority | Action | Owner | Timing | Evidence / Completion Test
1 | [ACTION 1] | [OWNER] | [DATE / PERIOD] | [DOCUMENT, APPROVAL OR RESULT]
2 | [ACTION 2] | [OWNER] | [DATE / PERIOD] | [DOCUMENT, APPROVAL OR RESULT]
3 | [ACTION 3] | [OWNER] | [DATE / PERIOD] | [DOCUMENT, APPROVAL OR RESULT]
4 | [ACTION 4] | [OWNER] | [DATE / PERIOD] | [DOCUMENT, APPROVAL OR RESULT]
5 | [ACTION 5] | [OWNER] | [DATE / PERIOD] | [DOCUMENT, APPROVAL OR RESULT]

[TABLE 18]
FINAL RECOMMENDATION / [Insert the final recommendation in one decisive paragraph. Include the basis, conditions and immediate instruction.]

[TABLE 19]
Category | Package | Market | Finance | Execution | Overall
Score / 100 | [ ] | [ ] | [ ] | [ ] | [ ]

[TABLE 20]
Source / Material | Date / Version | Use in Analysis
[SOURCE 1] | [DATE / VERSION] | [PURPOSE]
[SOURCE 2] | [DATE / VERSION] | [PURPOSE]
[SOURCE 3] | [DATE / VERSION] | [PURPOSE]
[SOURCE 4] | [DATE / VERSION] | [PURPOSE]

[TABLE 21]
SARACEN BRIDGE ANALYTICS | REPORT DATE
[ANALYST / EXECUTIVE] / Saracen Bridge Analytics | [D MONTH YYYY]
```