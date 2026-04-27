# Relationships

Read this only when one exact join or schema caveat question remains after the first two note reads.

## Core Foreign Keys

- `customers.scenario_id -> scenarios.scenario_id`
- `implementations.scenario_id -> scenarios.scenario_id`
- `implementations.customer_id -> customers.customer_id`
- `implementations.product_id -> products.product_id`
- `artifacts.scenario_id -> scenarios.scenario_id`
- `artifacts.customer_id -> customers.customer_id`
- `artifacts.product_id -> products.product_id`
- `artifacts.competitor_id -> competitors.competitor_id`
- `scenarios.primary_product_id -> products.product_id`
- `scenarios.secondary_product_id -> products.product_id`
- `scenarios.primary_competitor_id -> competitors.competitor_id`

## Caveats Worth Remembering

- `implementations.customer_id` is not unique by schema. In this DB it currently behaves one-to-one, but do not assume that without checking your subset.
- `scenarios.secondary_product_id` is optional.
- `artifacts.competitor_id` is optional. Many artifact rows omit it.
- `implementations.status` is messy. Match families of values, not one exact string.

## Join Defaults

- Use `scenario_id` for the cleanest framing-to-evidence path.
- Use `customer_id` when the question is account-led and the customer row is already known.
- Use `product_id` for capability-led or implementation-led questions.
- Use `competitor_id` only for explicitly competitive questions.

`products -> scenarios -> implementations -> artifacts`

Use this when the question is product-led and asks:
- what kinds of situations a product appears in
- which implementations are tied to a product
- which artifacts contain product-specific evidence

### Internal ownership lookup

`employees <- artifacts`

Use this when the question asks:
- who likely owns a domain
- who participated in a remediation path
- which internal role is associated with an issue

The link is often indirect through text or `metadata_json`, not a strict foreign key.

## Safe Assumptions

- It is safe to assume the foreign keys listed above are the stable join backbone.
- It is safe to assume artifacts are the final evidence layer.
- It is not safe to assume optional joins are populated.
- It is not safe to assume customer-to-implementation is one-to-one.
- It is not safe to assume implementation status values are standardized.

## Stop Condition

Once this file has told you:
- which keys connect the relevant tables
- which joins are optional
- which cardinality assumptions are safe

move to `investigations/question-routing.md` and then to SQL planning.
