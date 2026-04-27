# Querying Guide

Read this file first. Then read `investigations/question-routing.md`. Then switch to SQL.

## Hard Rules

- Do not use `ls`, `glob`, or `grep` on `database_notes/`.
- Do not search notes for seeded facts such as customer names, dates, or rollout details.
- Read `schema/relationships.md` only if one exact join or schema caveat question remains.
- Skip `sql_db_list_tables` and `sql_db_schema` when the question already implies `customers`, `scenarios`, `artifacts`, `artifacts_fts`, `competitors`, or `products`.

## SQL Defaults

- Named account: first SQL is usually `customers.name LIKE '%term%'` or direct artifact search.
- Exact procedure / proof plan / milestone / workshop / fast fix: find the artifact first, then fetch one targeted excerpt.
- Cohort or recurring pattern: define the cohort in `customers` + `scenarios` first, then use at most one artifact query for plain-English evidence.

## FTS Rule

Use this shape exactly:

```sql
SELECT a.artifact_id, a.artifact_type, a.title, a.created_at, a.summary
FROM artifacts_fts
JOIN artifacts a ON a.artifact_id = artifacts_fts.artifact_id
WHERE artifacts_fts MATCH 'term1 AND term2'
ORDER BY a.created_at DESC
LIMIT 10;
```

Keep `artifacts_fts` spelled out in the `MATCH` clause.

## Stop Condition

Once you know:
- the anchor table
- the safest join path
- the likely final evidence location

move to SQL immediately.
