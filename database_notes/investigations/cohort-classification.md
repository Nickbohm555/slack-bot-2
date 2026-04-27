# Cohort Classification Strategy

Read this only for region/product cohort questions such as:
- split accounts into group A vs group B
- which accounts in a region/product cohort have one pain point vs another

## Goal

Define the cohort entirely from structured fields first, then split it by structured scenario fields.

## Preferred Sequence

1. Use `customers` + `scenarios` + `products`.
2. Define the cohort with fields like:
   - `customers.region`
   - `customers.country`
   - `products.name`
   - `scenarios.primary_product_id`
3. Split the cohort using `scenarios.pain_point` and, if needed, `scenarios.trigger_event`.
4. Answer directly from the structured query results.
5. Use artifacts only if the user explicitly needs extra plain-English evidence after the cohort split is already known.

## Common Split Types

- taxonomy / search semantics:
  use pain-point language about search relevance degradation after taxonomy changes
- duplicate-action:
  use pain-point language about deduplication drift, duplicate incident generation, or repeated playbook executions

## Anti-Patterns

- Do not start with FTS
- Do not inspect many artifacts before defining the full cohort
- Do not mix product-led and artifact-led retrieval before the cohort is known

## Stop Condition

Once the structured cohort and split are known, answer and stop.
