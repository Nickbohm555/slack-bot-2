# Question Routing

Read this after `querying_guide.md`. Then go to SQL.

## Named Account

- Anchor: `customers`
- Usual path: `customers -> scenarios -> artifacts`
- First SQL: resolve the customer with `name LIKE '%term%'` if needed
- Do not search notes for the account name

## Exact Procedure

- Anchor: `artifacts`
- Path: `artifacts_fts -> artifacts`
- Use `summary` only to pick the best artifact
- Then fetch one excerpt around the relevant section, such as `Rollback`, `Live Patch`, or `Command`
- If both a procedural playbook/internal document and a Slack thread appear, prefer the procedural playbook/internal document first for rollback steps, commands, and maintenance windows
- For rollback + patch-window questions, try to answer from one playbook artifact using two targeted excerpts: one around `Live Patch` and one around `Rollback`
- Use `content_text`, not guessed body/content column names

## Proof Plan, Milestone, Workshop Output, Fast Fix

- Anchor: `artifacts`
- Path: `artifacts_fts -> artifacts`
- Use one customer-specific artifact, not many
- Then fetch one excerpt around `Proof`, `Milestone`, `Workshop`, `Action Items`, or `Proposed actions`
- Do not answer from summary alone if the user asks for exact deliverables, dates, or success criteria
- Prefer one targeted excerpt, not the whole artifact body, when a section like `Proof-of-Fix plan`, `Validation metrics`, or `Workshop` should contain the answer
- When a proof-plan artifact exposes an exact section header, anchor the excerpt on that exact header rather than a generic `Proof` or `Milestone` token
- Answer with only the requested fields. For proof plans, default to: customer, time window, exact steps, and success metric
- For proof-plan questions, stop after scope, dated proof steps, and the primary validation metric. Do not carry forward rollout/monitoring or secondary checks unless asked.
- If the proof scope names a specific validation cohort, preserve that exact cohort name in the answer
- Do not append nearby pricing, rollout, monitoring, contingency, or staffing details unless the question asks for them
- If the question includes a date, use that date as a fact to verify in artifacts, not as a raw hyphenated FTS token
- For workshop-output questions, capture both the agenda items (`agree`, `define`) and the deliverable line (`deliverable`, `output`, `produce`) if both are present
- If the user asks what a workshop is supposed to produce, still include both what the workshop must agree/define and the concrete deliverable it must produce
- For transform questions, include explicit mappings, coercions, and preserved key fields when the source lists them
- For fast-fix questions, if the source pairs an immediate config/mapping change with tracing or instrumentation needed to verify the bottleneck, include both parts
- Do not collapse a bundled fast fix down to only the sub-step that bypasses the external blocker if the source presents tracing/instrumentation as part of the same immediate proposal
- For fast-fix questions, prefer one internal recovery-plan or proposed-actions artifact over Slack when the summary already names the immediate fix bundle
- If the fast-fix artifact starts with a problem statement followed by `Proposed actions`, fetch one top-of-document or `Proposed actions` excerpt instead of probing many small keywords

## Cohort Or Classification

- Anchor: `customers` or `scenarios`
- First SQL: define the cohort from structured fields
- Use artifacts only if you need plain-English explanation after the cohort is already known
- For region/product cohort split questions, read `investigations/cohort-classification.md` before SQL

## Recurring Pattern

- First SQL should define the full account set from structured fields such as country, region, name family, pain point, or trigger event
- Do not start with FTS when `customers` + `scenarios` can define the complete cohort
- For recurring-pattern questions, read `investigations/recurring-pattern.md` before SQL

Example:

```sql
SELECT c.customer_id, c.name, c.country, c.region, s.pain_point, s.trigger_event
FROM customers c
JOIN scenarios s ON s.scenario_id = c.scenario_id
WHERE c.country = 'Canada'
  AND s.pain_point LIKE '%approval workflow failures%';
```

## Competitor Risk

- For competitor-risk questions, read `investigations/competitor-risk.md` before SQL
- If the question explicitly asks about a cheaper or tactical competitor, start with `competitor_research` artifacts for those phrases rather than broad customer/scenario candidate tables
- Use structured `customers` / `scenarios` filters only as fallback if the competitor-research search does not produce a clear small candidate set
- Choose the winning account from competitor-research evidence first
- Then fetch one milestone excerpt for that same account
- Prefer the account whose artifact evidence explicitly frames the competitor as a cheaper or low-cost tactical fallback that can buy time if Northstar misses
- Phrases like `buy time`, `low-cost`, `tactical layer`, or `fallback while we miss` are stronger evidence than generic PoC or general retention-risk language
- Do not choose a customer just because they have a competitor PoC or acceptance milestone; the winning account must have both explicit cheaper/tactical fallback pressure and a clearly promised next milestone
- After finding the likely winner, fetch the milestone/proof excerpt from that same customer rather than switching to a different candidate
- If one candidate has a proof-of-fix / proof plan milestone and another has only generic remediation or acceptance milestones, prefer the proof-of-fix / proof plan candidate when the cheaper/tactical fallback evidence is also stronger
- When the user asks `what exactly is that milestone`, prefer a retrospective, internal document, or proof-plan artifact with explicit timeline/validation sections over a Slack thread summary when both exist
- For exact milestone questions, prefer one excerpt starting at the exact proof-plan section header so the answer can preserve both scope and dated steps in one read
- Include the concrete milestone timeline and primary success metric from the excerpt, not a shortened paraphrase

## Stop Condition

Once you know the anchor table, join path, and evidence location, stop reading notes and move to SQL.
