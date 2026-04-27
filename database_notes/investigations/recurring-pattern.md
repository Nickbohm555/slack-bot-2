# Recurring Pattern Strategy

Read this only for questions asking whether an issue is recurring across accounts.

## Goal

Use structured fields to identify the full account set first, then give a plain-English shared pattern.

## Preferred Sequence

1. Use `customers` + `scenarios`.
2. Narrow by structured hints from the question, such as:
   - geography like `Canada`
   - name family like `Maple...`
   - pain point like approval workflow failures
   - trigger event like migration from legacy workflow tooling
3. Return the customer names directly from the structured query.
4. Summarize the shared failure pattern in plain English from the structured pain-point / trigger-event pattern.
5. Use at most one artifact query only if the structured fields are not enough to describe the shared pattern clearly.
6. If one structured query already returns a coherent cohort with the same pain point and trigger event, answer immediately and stop.

## Anti-Patterns

- Do not start with FTS
- Do not call schema tools first when the question already implies `customers` + `scenarios`
- Do not inspect each customer one by one before defining the full set
- Do not overfit to one named example when the question asks whether the issue is recurring
- Do not narrow the cohort with artifact terms like `approval bypass` if the structured query already captured the full recurring set

## Stop Condition

Once you know the full account set and the shared pattern, answer and stop.
