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
