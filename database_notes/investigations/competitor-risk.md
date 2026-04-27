# Competitor Risk Strategy

Read this only for questions about:
- which customer is most likely to defect
- cheaper / low-cost / tactical competitors
- what happens if Northstar misses a milestone

## Goal

Pick the single strongest at-risk customer, then pull the exact next milestone from that same customer.

## Preferred Sequence

1. Start with `competitor_research` artifacts when the question asks about a cheaper or tactical competitor.
2. Use narrow evidence queries first. Good anchors are:
   - `buy time`
   - `low-cost`
   - `cheaper`
   - `tactical layer`
   - `tactical fallback`
3. Compare only the small set of competitor-research rows returned by those anchors.
4. Choose the winner from competitor evidence before reading calls, retros, or escalation threads.
5. After the winner is known, fetch one milestone/proof excerpt for that same customer.
6. Prefer a `proof-of-fix`, `proof plan`, or similarly explicit milestone over a broader remediation or acceptance plan.
7. If the user asks what the milestone exactly is, prefer an artifact with explicit timeline and validation sections over a Slack summary thread.

## Anti-Patterns

- Do not start with broad `customers` / `scenarios` candidate tables if the question already asks about cheaper/tactical competitor language.
- Do not open escalation calls or customer calls before choosing the winner from `competitor_research` evidence.
- Do not compare many customers deeply. Compare the summary-level fallback language first, pick one winner, then verify one milestone.
- Do not answer with a generic “within 10 business days” milestone if the artifact provides a more exact sequence and metric.
- Do not stop on the first Slack-thread proof summary if a retrospective or internal document for the same customer is likely to contain timeline and validation sections.
- Do not compress a numbered milestone into a generic paraphrase when the excerpt includes concrete step dates or a named validation cohort.

## Ranking Heuristic

Stronger evidence:
- competitor is described as low-cost or cheaper
- competitor is described as tactical
- artifact explicitly says it can `buy time`
- artifact ties that fallback to missing a Northstar milestone
- artifact pair is: competitor-research fallback evidence + customer-specific proof/milestone artifact

Weaker evidence:
- generic PoC mention
- general procurement pressure
- generic RFP threat
- broad remediation or acceptance milestones without a proof-of-fix / proof-plan framing

## Query Shape

- First query should identify the strongest competitor-risk artifact from `artifacts_fts -> artifacts`, filtered to `artifact_type='competitor_research'` when possible
- A good first-pass query is one that combines competitor-risk language such as `buy AND time` or `low-cost AND tactical`
- If several customers match, compare only those competitor-research rows and prefer the one with both fallback language and a proof-of-fix style next milestone
- Then use one customer-specific artifact query for the next milestone / proof plan
- For exact milestone wording, prefer a customer-specific retrospective, internal document, or proof-plan artifact whose text contains section anchors like `Proof-of-Fix plan`, `Steps & timeline`, or `Validation metrics`
- If a proof-plan artifact exposes an exact section header such as `Short-term mitigation (Proof-of-Fix plan)`, anchor the excerpt on that header instead of a generic `Proof` token
- If the excerpt contains numbered steps, carry the dated sequence into the answer rather than summarizing it as only a duration
- If the validation line names a specific cohort or scope, include that scope in the answer

### Recommended Workflow

1. Run one FTS query against `competitor_research` artifacts for fallback language.
2. Compare the returned `summary` fields first. Do not open customer calls yet.
3. Pick the single winner from summary-level evidence:
   - prefer rows whose summary contains both tactical/low-cost language and buy-time language
4. Run one customer-specific FTS query for `proof`, `proof-of-fix`, or `milestone`.
5. Prefer the artifact that looks like a retrospective, internal document, or proof-plan doc over a Slack summary if both match.
6. Fetch one targeted excerpt from that proof/milestone artifact starting at the exact proof-plan section header when possible.
7. Answer and stop.

### Example Query Pattern

```sql
SELECT a.artifact_id, a.customer_id, a.title, a.created_at, a.summary
FROM artifacts_fts
JOIN artifacts a ON a.artifact_id = artifacts_fts.artifact_id
WHERE a.artifact_type = 'competitor_research'
  AND artifacts_fts MATCH 'buy AND time'
ORDER BY a.created_at DESC
LIMIT 10;
```

Then:

```sql
SELECT a.artifact_id, a.title, a.created_at, a.summary
FROM artifacts_fts
JOIN artifacts a ON a.artifact_id = artifacts_fts.artifact_id
WHERE a.customer_id = '<winner_customer_id>'
  AND artifacts_fts MATCH 'proof OR milestone'
ORDER BY a.created_at DESC
LIMIT 10;
```

## Stop Condition

Once you know:
- the winning customer
- the exact cheaper/tactical fallback evidence
- the exact next milestone with dates/sequence/primary metric

answer directly and stop.
