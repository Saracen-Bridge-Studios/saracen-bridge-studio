"""Builds tools/producer_fees.json: Saracen Bridge's producer-fee allowance table for incentive eligibility.

Source: Jon Chadwick (Director, Saracen Bridge Ltd), sent to Tim on 4 Nov 2026: "the maximum producer or
executive-producer fee that can count as qualifying expenditure for a film incentive", across the countries in the
budgeting and scheduling rate cards, sources checked 21 October 2026. The `allowance` and `apply` texts are his; `calc`
is how the Studio applies them (engine/studio/producerfee.py). His notes on each route stay with it. "Confirm" means he
couldn't establish a reliable numerical maximum for that route; it is not uncapped.

Rule 1 (4 Nov 2026), checked against current sources, all consistent with his table:
  - New Zealand: the cap on above-the-line claims is removed from 1 January 2026 (NZFC).
  - Louisiana: the 40% above-the-line cap stays; the $3 million individual salary cap is eliminated for productions
    applying after 1 July 2025 (Louisiana Economic Development).
  - Montana: no credit for productions filming after 2024; the first available credit is in 2031 (Montana DoR).
  - Australia: the Producer Offset's 20% above-the-line cap is pending removal for projects starting principal
    photography from 1 July 2024, but the legislation has not passed (Screen Australia).
  - Germany: the DFFF I bands (EUR 15,000 / 25,000 / 5% capped at EUR 250,000) are in the 2026 guideline, in force
    1 Jan - 31 Dec 2026 (FFA). The DFFF II figure was not visible in the excerpt read; kept as Jon has it.
  - Ireland: 15% where eligible expenditure is "in excess of" 80% of the global budget, 10% where "less than"; exactly
    80% is in neither (Revenue Tax and Duty Manual 15-02-04).
  - Georgia: $500,000 per person for W-2; no cap for 1099, personal services or loan-out (georgia.org, 2026).
  - Texas: "First $1 million of each Texas Resident" for projects starting after 1 Sep 2025 (Texas Film Commission).

    python scripts/build_producer_fees.py      (writes tools/producer_fees.json; a test checks it's current)
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tools" / "producer_fees.json"


def r(id, area, country, regions, route, status, currency, allowance, apply, source, calc=None, programmes=()):
    return {"id": id, "area": area, "country": country, "regions": regions, "route": route, "status": status,
            "currency": currency, "programmes": list(programmes), "allowance": allowance, "apply": apply,
            "source": source, "calc": calc or {}}


ROUTES = [
    # ------------------------------------------------------------------ Europe
    r("UK-AVEC", "Europe", "United Kingdom", "England, Scotland, Wales, Northern Ireland", "AVEC", "actual", "GBP",
      "No fixed producer-specific percentage identified for AVEC.",
      "Claim only the qualifying production-related portion. HMRC requires allocation between development and qualifying "
      "production phases; a fee covering the whole project is not automatically wholly eligible.",
      "GOV.UK", programmes=("GBR-AVEC", "GBR-AVEC-ANI", "GBR-IFTC")),
    r("IE-481", "Europe", "Ireland", "All regions", "Section 481", "rule", "EUR",
      "Normally 10% or 15% of the global budget, shared between producer, co-producer, EP fees and production/corporate "
      "overheads.",
      "Revenue normally accepts 15% where eligible expenditure exceeds 80% of the global budget, and 10% where it is below "
      "80%. These are acceptance benchmarks: higher amounts can be substantiated. Exactly 80% needs clarification because "
      "the guidance's wording does not resolve that boundary.",
      "revenue.ie", {"ireland": True, "shares_with": ["overheads"]}, ("IRL-481",)),
    r("DE-DFFF-I", "Europe", "Germany", "All Länder", "DFFF I", "rule", "EUR",
      "For budgets above €500,000: 5% of production costs excluding the producer fee, capped at €250,000.",
      "Smaller-budget limits are €15,000 for budgets up to €300,000 and €25,000 for budgets above €300,000–€500,000. "
      "Exceptions require approval. This is a recognised-cost ceiling; German territorial eligibility still applies.",
      "FFA", {"bands": [{"up_to": 300000, "cap": 15000}, {"up_to": 500000, "cap": 25000},
                        {"pct": 0.05, "base": "production_costs_ex_fee", "cap": 250000}]}, ("DEU-DFFF-I",)),
    r("DE-DFFF-II", "Europe", "Germany", "All Länder", "DFFF II service-production route", "rule", "EUR",
      "5% of the production costs for which the service producer is responsible, excluding its fee; maximum €350,000.",
      "This concerns the production-service-provider fee, not an unrestricted additional foreign EP fee. Regional funds "
      "have separate conditions.",
      "FFA", {"pool": {"pct": 0.05, "base": "local_spend_ex_fee", "cap": 350000}}, ("DEU-DFFF-II",)),
    r("HU", "Europe", "Hungary", "All regions", "Hungarian Film Incentive", "rule", "EUR",
      "4% of the Hungarian budget, pooled across producer fees.",
      "Includes line, co-, executive and other producers. NFI also excludes purchases of goods/services from the foreign "
      "producer or co-producer, so a foreign company's fee needs particular scrutiny.",
      "Nemzeti Filmiroda", {"pool": {"pct": 0.04, "base": "local_budget"}}, ("HUN-FILM",)),
    r("IT-INTL", "Europe", "Italy", "All regions", "Incoming / international tax-credit route", "zero", "EUR",
      "0% for producer fees and general company overheads under this route's eligible-cost rules.",
      "The separate 30% overall ATL ceiling does not make producer fees eligible. Domestic production credits and regional "
      "grants require separate assessment.",
      "italyformovies.com", programmes=("ITA-INTL",)),
    r("MT-ATL", "Europe", "Malta", "Malta, Gozo and Comino", "Individual ATL remuneration", "confirm", "EUR",
      "Shared ATL allowance of €1 million or 30% of total Malta eligible spend, under the applicable approved option.",
      "Shared with directors, cast and stunts; line producers are excluded from this ATL category. Only Malta-attributable "
      "work qualifies. The guidelines also cap the rebate generated by ATL expenditure at €5 million. Confirm the option "
      "with the Commission before budgeting it.",
      "Malta Film Commission guidelines", {"options": [{"label": "€1 million option", "amount": 1000000},
                                                       {"label": "30% of Malta eligible spend", "pct": 0.30, "base": "local_spend"}],
                                           "shares_with": ["other_atl"]}),
    r("MT-SVC", "Europe", "Malta", "Malta, Gozo and Comino", "Local production-service / co-production company fee", "rule",
      "EUR", "Lower of €100,000 or 20% of final actual Malta spend.",
      "This is a separate fee category from the individual producer's ATL remuneration.",
      "Malta Film Commission guidelines", {"lower_of": [{"amount": 100000}, {"pct": 0.20, "base": "local_spend"}]}),
    r("ES-ICAA", "Europe", "Spain", "National framework, including mainland regions, Balearics and Canaries",
      "National recognised-cost framework (ICAA)", "rule", "EUR",
      "Executive-producer remuneration: 5% of the film's recognised realisation cost under ICAA cost-recognition rules.",
      "Do not automatically apply this as the foreign-production tax-credit allowance. The Article 36.1/36.2 route and the "
      "fee's classification must be checked. A higher Canary Islands incentive rate does not itself increase the "
      "producer-fee allowance.",
      "spainfilmcommission.com", {"pool": {"pct": 0.05, "base": "worldwide_budget"}}, ("ESP-NAT-DOM",)),
    r("ES-FOREIGN", "Europe", "Spain", "Mainland, Balearics and Canaries", "Foreign-production tax credit (Article 36.2)",
      "confirm", "EUR",
      "Do not automatically apply the ICAA 5% executive-producer allowance to this route.",
      "The Article 36.1/36.2 route and the fee's classification must be checked. A higher Canary Islands incentive rate "
      "does not itself increase the producer-fee allowance.",
      "spainfilmcommission.com", programmes=("ESP-NAT-FOR", "ESP-CAN-FOR")),
    r("ES-NAV-65", "Europe", "Spain", "Navarra", "Article 65.1 route", "rule", "EUR",
      "Executive-producer remuneration up to the higher of 10% of production cost or €100,000, limited to the actual "
      "qualifying fee.",
      "This is specific to that route; it should not be copied automatically into Navarra's foreign-service-production "
      "calculation.",
      "lexnavarra.navarra.es", {"higher_of": [{"pct": 0.10, "base": "worldwide_budget"}, {"amount": 100000}]},
      ("ESP-NAV-DOM",)),
    r("ES-NAV-FOREIGN", "Europe", "Spain", "Navarra", "Foreign-service-production route", "confirm", "EUR",
      "The Article 65.1 allowance should not be copied automatically into this calculation.",
      "Confirm the fee treatment for Navarra's foreign-service-production route.",
      "lexnavarra.navarra.es", programmes=("ESP-NAV-FOR",)),
    r("ES-BASQUE", "Europe", "Spain", "Basque Country: Bizkaia, Gipuzkoa and Álava", "Provincial tax routes", "confirm",
      "EUR", "Confirm separately for each provincial tax route.",
      "No universal producer-fee percentage has been verified across these three regimes.",
      "Provincial tax authorities", programmes=("ESP-BAS-ARA", "ESP-BAS-BIZ", "ESP-BAS-GIP")),
    r("FR-TRIP", "Europe", "France", "National, across rate-card regions", "TRIP", "confirm", "EUR",
      "Confirm the fee classification; no blanket producer-fee percentage verified.",
      "The rules identify eligible production payroll and services, with territorial and nationality/residency conditions. "
      "They do not justify inserting an automatic percentage for a foreign producer's corporate fee.",
      "bofip.impots.gouv.fr", programmes=("FRA-TRIP",)),
    r("CZ", "Europe", "Czech Republic", "All regions", "Czech audiovisual incentive", "actual", "CZK",
      "No fixed producer-specific percentage verified.",
      "Actual qualifying Czech expenditure must be established. Fundraising activities, certain development costs, unpaid "
      "own contributions and remuneration for statutory company-office duties are excluded.",
      "Czech Film Commission", programmes=("CZE-PROD", "CZE-DIGITAL")),
    # ------------------------------------------------------------------ Australia and New Zealand
    r("AU-PO", "Australia & New Zealand", "Australia", "All states and territories", "Producer Offset", "rule", "AUD",
      "For non-documentaries, 20% of total film expenditure is the shared ATL/development ceiling in the published "
      "guidance checked.",
      "Producers share this allowance with other covered ATL expenditure. Documentaries are exempt from this cap. The "
      "announced removal should not be assumed effective without checking the applicable enacted rules.",
      "screenaustralia.gov.au", {"pool": {"pct": 0.20, "base": "worldwide_budget"}, "shares_with": ["other_atl"],
                                 "documentary_exempt": True}, ("AUS-PROD-FEAT", "AUS-PROD-OTHER")),
    r("AU-LOC", "Australia & New Zealand", "Australia", "All states and territories", "Location Offset", "actual", "AUD",
      "No fixed individual EP percentage identified. Corporate production-company/service fees are excluded as such.",
      "An individual EP's actual services in Australia may qualify where they concern making the film. Fees solely for "
      "financing or distribution are excluded. Separately identifiable qualifying services can be assessed individually.",
      "arts.gov.au", {"individuals_only": True}, ("AUS-LOC",)),
    r("AU-STATE", "Australia & New Zealand", "Australia", "State and territory grants and top-ups", "State programmes",
      "confirm", "AUD", "Confirm against the particular programme and approved budget.",
      "The federal Producer Offset's 20% figure is not a universal producer-fee allowance for every state grant.",
      "State screen agencies", programmes=("AUS-NSW-FIN", "AUS-QLD-INC", "AUS-VIC-INC", "AUS-SA-PROD", "AUS-WA-WAPAI",
                                           "AUS-TAS-PROD", "AUS-NT-FUND")),
    r("NZ-INTL", "Australia & New Zealand", "New Zealand", "All regions", "International rebate (NZSPR)", "actual", "NZD",
      "Former 20% ATL cap removed for productions starting principal photography/eligible PDV from 1 January 2026.",
      "This permits assessment of actual eligible expenditure, not an arbitrary budget percentage. Non-resident non-cast "
      "personnel must generally work in New Zealand for at least 14 days in aggregate.",
      "Rebate for International Productions (NZFC)", {"since": "2026-01-01"}),
    # ------------------------------------------------------------------ Canada
    r("CA-FED", "Canada", "Canada", "Federal", "CPTC / PSTC (CRA producer-fee policy)", "benchmark", "CAD",
      "The federal CRA's 10% × actual B+C producer-fee reference applies to specified related-party, ownership and "
      "financier-associated fees. CRA expressly says it is not a maximum.",
      "Higher fees can be justified; arm's-length contractual fees are assessed differently. Provincial eligibility remains "
      "a separate calculation. B+C means production plus post-production costs, excluding the ATL and other budget sections.",
      "Canada.ca", {"benchmark": {"pct": 0.10, "base": "bc"}}, ("CAN-FED-CPTC", "CAN-FED-PSTC")),
    r("CA-BC", "Canada", "Canada", "British Columbia: Vancouver, regional BC and Vancouver Island", "BC tax credits",
      "benchmark", "CAD",
      "BC expressly refers applicants to the CRA producer-fee policy.",
      "Apply the qualifying BC labour rules; 10% of B+C is not a hard provincial budget cap.",
      "Province of British Columbia", {"benchmark": {"pct": 0.10, "base": "bc"}},
      ("CAN-BC-PSTC", "CAN-BC-PSTC-DAVE", "CAN-BC-FIBC", "CAN-BC-FIBC-DAVE")),
    r("CA-ON", "Canada", "Canada", "Ontario: GTA, regional and northern Ontario", "Ontario credits", "confirm", "CAD",
      "Use the federal benchmark where applicable, but confirm the provincial fee allowance and labour/service allocation "
      "under the selected Ontario credit.", "",
      "Ontario Creates", {"benchmark": {"pct": 0.10, "base": "bc"}}, ("CAN-ON-OFTTC", "CAN-ON-OPSTC", "CAN-ON-OCASE")),
    r("CA-MB", "Canada", "Canada", "Manitoba: Winnipeg and regional Manitoba", "Manitoba credit", "confirm", "CAD",
      "Confirm for the labour-based or cost-of-production route selected.",
      "Do not treat the federal 10% benchmark as a universal provincial ceiling.",
      "Manitoba Film & Music", programmes=("CAN-MB-ALL", "CAN-MB-LAB")),
    r("CA-QC", "Canada", "Canada", "Québec: Montréal, Québec City and regional Québec", "Production-services credit",
      "actual", "CAD",
      "0% for a non-Québec-resident producer's remuneration under the relevant producer provision.",
      "Qualifying producer remuneration requires the individual to be Québec resident when providing the services. No "
      "separate fixed percentage verified for eligible resident fees.",
      "sodec.gouv.qc.ca", {"residents_only": True}, ("CAN-QC-SERVICE",)),
    r("CA-AB", "Canada", "Canada", "Alberta: Calgary, Edmonton and regional Alberta", "Alberta credit", "benchmark", "CAD",
      "10% of actual B+C is a general reasonableness reference, rather than an absolute maximum.",
      "Higher fees require support.", "alberta.ca", {"benchmark": {"pct": 0.10, "base": "bc"}}, ("CAN-AB-FTTC",)),
    r("CA-SK", "Canada", "Canada", "Saskatchewan", "Creative Saskatchewan grant", "rule", "CAD",
      "Producer fees normally 10% of B+C; 15% for qualifying documentaries below C$2.5 million.",
      "Corporate overhead has its own corresponding allowance. Exceptions are discretionary.",
      "creativesask.ca", {"pool": {"pct": 0.10, "base": "bc", "documentary_pct": 0.15, "documentary_budget_under": 2500000}},
      ("CAN-SK-DOM", "CAN-SK-SERVICE")),
    r("CA-NS", "Canada", "Canada", "Nova Scotia: Halifax and regional areas", "Production Incentive Fund", "rule", "CAD",
      "Eligible compensation is limited by C$150,000 of incentive per individual, not C$150,000 of fee.",
      "Thus the fee ceiling is C$150,000 ÷ applicable incentive rate: at 25%, C$600,000. Resident-labour and "
      "additional-role restrictions also apply.",
      "cch.novascotia.ca", {"incentive_cap_per_person": 150000}, ("CAN-NS-I", "CAN-NS-II")),
    r("CA-NL", "Canada", "Canada", "Newfoundland and Labrador", "Labour-based and all-spend routes", "confirm", "CAD",
      "Confirm separately for the labour-based and all-spend routes.",
      "No reliable producer-specific numerical ceiling established in this review.", "",
      programmes=("CAN-NL-ALL",)),
    r("CA-YT", "Canada", "Canada", "Yukon", "Media Production Fund", "rule", "CAD",
      "Combined producer fees and corporate overhead: 30% of B+C for budgets up to C$500,000; above that, 20% of B+C, "
      "capped at C$2 million, under the published business guidelines.",
      "Treaty co-productions use the Canadian share.", "yukon.ca",
      {"pool": {"pct": 0.20, "base": "bc", "cap": 2000000, "small_budget": 500000, "small_pct": 0.30},
       "shares_with": ["overheads"]}, ("CAN-YT-PROD",)),
    r("CA-NWT", "Canada", "Canada", "Northwest Territories", "Territorial rebate", "confirm", "CAD",
      "Confirm the approved territorial rebate cost schedule.", "No numerical producer-fee maximum verified.", "",
      programmes=("CAN-NWT-SCRIPT", "CAN-NWT-NONSCRIPT")),
    r("CA-NU", "Canada", "Canada", "Nunavut", "Nunavut Spend Incentive", "confirm", "CAD",
      "Confirm the approved Nunavut-spend allocation.",
      "Producer residency, ownership, control and reasonable remuneration are reviewed; no universal percentage verified.",
      "Nunavut Film Development Corporation", programmes=("CAN-NU-I", "CAN-NU-II")),
    # ------------------------------------------------------------------ United States (a per-person ceiling covers the person's combined roles)
    r("US-CA", "United States", "United States", "California: Los Angeles and outside the zone", "California credit", "zero",
      "USD", "0% for ATL producer/EP fees.",
      "Limited qualifying BTL work by someone also credited as a producer is a separate exception, capped at $100,000 for "
      "the specified roles.", "film.ca.gov"),
    r("US-NY", "United States", "United States", "New York: NYC and upstate", "Film tax credit", "rule", "USD",
      "Fees for no more than two producers, within a shared ATL pool of 40% of all other qualified production costs.",
      "This is not 40% of the total budget.", "NYSenate.gov",
      {"max_people": 2, "pool": {"pct": 0.40, "base": "other_qualified_costs"}, "shares_with": ["other_atl"]},
      ("USA-NY-IND",)),
    r("US-NJ", "United States", "United States", "New Jersey: inside and outside the 30-mile zone", "General route", "rule",
      "USD", "General route: $750,000 per individual.",
      "Studio/film-lease routes have additional ATL allowances. Certain qualifying partner productions can also include "
      "apportioned out-of-state producer fees within a 7.5% pool shared with rights fees and production insurance.",
      "njeda.gov", {"per_person_cap": 750000}, ("USA-NJ-FILM",)),
    r("US-GA", "United States", "United States", "Georgia", "Entertainment Industry Investment Act", "rule", "USD",
      "$500,000 per person for W-2 compensation.",
      "The same salary ceiling does not apply to qualifying loan-out/other eligible payment arrangements; Georgia work and "
      "tax requirements still apply.", "georgia.org", {"salary_cap_per_person": 500000}, ("USA-GA-FILM",)),
    r("US-LA", "United States", "United States", "Louisiana", "Motion picture production credit", "rule", "USD",
      "Shared ATL ceiling of 40% of Louisiana expenditure.",
      "The former $3 million individual compensation limit was removed for the applicable post-July 2025 regime.",
      "opportunitylouisiana.gov", {"pool": {"pct": 0.40, "base": "local_spend"}, "shares_with": ["other_atl"]}),
    r("US-IL", "United States", "United States", "Illinois", "Film production credit", "rule", "USD",
      "$500,000 per individual, also constrained by 40% of Illinois production spending for all ATL, and 12% for "
      "related-party ATL in aggregate.", "Limited exceptions exist to the 40% rule.", "Illinois Department of Revenue",
      {"per_person_cap": 500000, "pool": {"pct": 0.40, "base": "local_spend"}, "shares_with": ["other_atl"],
       "related_pool": {"pct": 0.12, "base": "local_spend"}}),
    r("US-TX", "United States", "United States", "Texas", "Moving Image Industry Incentive", "rule", "USD",
      "Published programme guidance: $1 million total compensation per Texas-resident worker per project.",
      "Non-resident producer wages do not qualify under that resident-payroll provision.", "gov.texas.gov",
      {"residents_only": True, "per_person_cap": 1000000}),
    r("US-NC", "United States", "United States", "North Carolina", "Film and entertainment grant", "rule", "USD",
      "First $1 million per individual; excess compensation is excluded.", "", "ncleg.gov", {"per_person_cap": 1000000}),
    r("US-SC", "United States", "United States", "South Carolina", "Payroll provision", "rule", "USD",
      "Payroll provision excludes an employee's salary where it is $1 million or more.",
      "This is an exclusion threshold, not simply a rebate on the first $1 million.", "law.justia.com",
      {"exclude_at_or_above": 1000000}),
    r("US-OK", "United States", "United States", "Oklahoma", "Film incentive", "rule", "USD",
      "Producer fees share the 25% ATL ceiling on statutory qualifying production expenditure.",
      "Relevant Oklahoma taxpayer/loan-out requirements apply.", "oscn.net",
      {"pool": {"pct": 0.25, "base": "local_spend"}, "shares_with": ["other_atl"]}),
    r("US-KY", "United States", "United States", "Kentucky", "Film incentive", "rule", "USD",
      "First $1 million per ATL employee, resident or non-resident, subject to qualifying Kentucky services.", "",
      "law.justia.com", {"per_person_cap": 1000000}),
    r("US-OR", "United States", "United States", "Oregon", "OPIF", "rule", "USD",
      "OPIF rules exclude compensation paid to an individual receiving more than $1 million.",
      "Treat this as a potential whole-payment exclusion, not merely a cap on the excess.", "Oregon Film",
      {"exclude_above": 1000000}),
    r("US-WA", "United States", "United States", "Washington", "Washington Filmworks", "actual", "USD",
      "0% for non-resident ATL producers.", "Resident qualifying wages can be considered; no separate producer percentage "
      "established.", "washingtonfilmworks.org", {"residents_only": True}),
    r("US-PR", "United States", "United States", "Puerto Rico", "Film incentive", "rule", "USD",
      "Producer fees up to 10% of total Puerto Rico production expenditure, restricted to Puerto Rico-resident producers, "
      "with payment and tax evidence.", "", "docs.pr.gov", {"residents_only": True, "pool": {"pct": 0.10, "base": "local_spend"}}),
    r("US-MA", "United States", "United States", "Massachusetts", "Payroll and production-expense credits", "confirm", "USD",
      "Route-dependent.",
      "The payroll-credit exclusion for compensation of $1 million or more must be distinguished from the production-expense "
      "credit, which can have different treatment. Confirm before assigning a maximum.", "Mass.gov"),
    r("US-MT", "United States", "United States", "Montana", "MEDIA Act credit", "unavailable", "USD",
      "Do not assume a currently available award: the state has paused new certification applications and says the first "
      "available credit is in 2031.", "Existing certifications need separate review.", "Montana Department of Revenue"),
    r("US-NM", "United States", "United States", "New Mexico", "Film production credit", "confirm", "USD",
      "Confirm resident/non-resident status and ordinary versus Film Partner treatment.",
      "No single current maximum verified for both routes.", ""),
    r("US-PA", "United States", "United States", "Pennsylvania", "Film production credit", "confirm", "USD",
      "Confirm producer-specific treatment.",
      "The commonly quoted principal-cast ceiling should not be used as a producer-fee allowance.", ""),
    r("US-UT", "United States", "United States", "Utah", "Motion picture incentive", "confirm", "USD",
      "Confirm current individual compensation treatment in the approved incentive agreement.",
      "No current numerical maximum verified.", ""),
    r("US-CO", "United States", "United States", "Colorado", "Film incentive", "confirm", "USD",
      "Confirm the approved qualifying compensation and fee allocation.", "No producer-specific percentage verified.", ""),
    r("US-OH", "United States", "United States", "Ohio", "Motion picture credit", "confirm", "USD",
      "Confirm qualifying Ohio services and fee classification.", "No producer-specific percentage verified.", ""),
    r("US-AZ", "United States", "United States", "Arizona", "Film incentive", "confirm", "USD",
      "Confirm qualifying Arizona production labour and fee classification.", "No producer-specific percentage verified.", ""),
    r("US-HI", "United States", "United States", "Hawaiʻi: Oʻahu and neighbour islands", "Film credit", "confirm", "USD",
      "Confirm qualifying producer compensation.",
      "Different island incentive rates do not themselves establish a different producer-fee allowance.", ""),
]

DOC = {
    "source": "Saracen Bridge Ltd (Jon Chadwick, Director): producer-fee allowance for incentive eligibility",
    "checked": "2026-10-21",
    "received": "2026-11-04",
    "notes": [
        "The figures concern eligible expenditure, before applying the rebate or tax-credit rate.",
        "\"Confirm\" means a reliable numerical maximum could not be established for that route; it should not be treated "
        "as uncapped.",
        "Calculate the eligible producer fee first, then express it as a percentage of the worldwide budget.",
        "Where the cap is shared with other ATL costs or overheads, subtract those qualifying costs before calculating the "
        "remaining producer-fee allowance.",
        "A contractual EP fee can exceed the eligible amount; the excess simply should not be included in the incentive "
        "calculation.",
        "Have the local incentive accountant confirm the selected route and any entries marked \"confirm\" before locking "
        "the finance plan.",
    ],
    "routes": ROUTES,
}


def build() -> str:
    return json.dumps(DOC, ensure_ascii=False, indent=1) + "\n"


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT, len(ROUTES), "routes")
