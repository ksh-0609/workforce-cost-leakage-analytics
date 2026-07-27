# Problem Statement — Workforce Cost Leakage Analytics

## Business Context
This project simulates a 5-location retail chain with approximately 100 employees,
spread across departments such as Sales Floor, Stockroom, and Customer Service.

## The Problem
Labor is typically the largest controllable cost line for a retail business, yet most
staffing decisions are made on gut feel or manual spreadsheets. This creates six
recurring, quantifiable sources of cost leakage:

1. **Overtime creep** — small, repeated unscheduled clock-in/clock-out extensions that
   silently accumulate into real monthly cost
2. **Clopening** — an employee closes one night and opens again the next morning with
   insufficient rest between shifts (compliance and burnout risk)
3. **Missed breaks** — long shifts recorded without a compliant break
4. **Overstaffing** — more labor-hours scheduled than actual demand requires
5. **Understaffing** — fewer labor-hours scheduled than demand requires
6. **Swap-driven overtime** — shift swaps that push the covering employee into unplanned
   overtime

## What This System Should Enable
- Flag high-risk shifts for unplanned overtime before they happen
- Recommend optimal headcount per hour based on a demand forecast
- Surface compliance risk (missed breaks, clopenings) for manager review
- Quantify the dollar impact of every leakage category

## Target KPIs
- Total overtime $ identified per month
- % of shifts overstaffed / understaffed
- Demand forecast accuracy (MAPE) vs. a naive baseline
- Overtime-risk classifier precision/recall
- Number of compliance-risk shifts flagged

## Ground-Truth Validation Approach
All data in this project is synthetically generated, with known anomalies deliberately
injected during generation. Every detection query and model can therefore be scored
against a known-correct answer — precision/recall numbers reported anywhere in this
project are measured, not estimated.