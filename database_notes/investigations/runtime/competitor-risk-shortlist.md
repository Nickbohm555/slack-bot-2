# Competitor Risk Shortlist

Runtime-generated from the DB for competitor-risk questions.
Use this as a shortlist only. Verify the winner and the exact milestone from the referenced artifacts.

Ranking heuristic:
- stronger fallback language: `buy time`, `low-cost`, `cheaper`, `tactical`
- stronger milestone language: `proof-of-fix`, `proof plan`, explicit validation/milestone wording

Top candidates:
## 1. BlueHarbor Logistics
- Competitor: NoiseGuard
- Score: 14
- Fallback evidence artifact: art_c9970c1dc932 — Competitor report: NoiseGuard
- Fallback summary: NoiseGuard (cmp_88dc528f7db7) is being evaluated by BlueHarbor as a low-cost, tactical dedupe layer to buy time after taxonomy-induced search degradation. NoiseGuard can suppress duplicate alerts quickly but lacks schema-aware query semantics and integration depth with Northstar's EN features. For BlueHarbor's executive goal (40% reduction in manual triage), NoiseGuard alone is unlikely to meet targets; our recommended play is a short-term tuning + mapping proof and a conditional commercial concession to retain the account.
- Candidate milestone/proof artifacts:
  - art_bd3560dfe194 — Retro: BlueHarbor taxonomy rollout -> Event Nexus search relevance degradation | Post-incident retro summarizing root cause, short-term mitigations, proof plan, and recommended medium-term fixes for BlueHarbor Logistics following their taxonomy change on 2026-02-20 that impacted Event Nexus search relevance. Primary goal: deliver proof-of-fix within 10 business days to secure renewal/expansion.
  - art_3e9031389474 — Slack thread: BlueHarbor renewal — proof-of-fix for search relevance after taxonomy change | Agreed to run a 7-10 business day proof: tuning + mapping layer for Event Nexus; PS engagement offered at $48k (30% discount if Orchestrator expansion committed). Conditional one-quarter credit if proof fails. Customer to send schema export and anonymized logs by 2026-03-19 EOD.
  - art_0bccc580184e — Renewal Negotiation call with BlueHarbor Logistics | Renewal/expansion call with VP Ops and SREs. Customer pressed for a short-term plan to restore search relevance within 4 weeks to satisfy an executive mandate to reduce manual work. Northstar team proposed an immediate tuning patch (schema mapping and weight adjustments), scoped a targeted reindex (3 months of data) as contingency, and offered a 90-day professional services engagement for implementation and runbook training. Customer raised pricing and risk objections and asked for a proof-of-fix within 10 business days.

## 2. HelioFab Systems
- Competitor: NoiseGuard
- Score: 2
- Fallback evidence artifact: art_e2727db588de — Competitor report: NoiseGuard
- Fallback summary: NoiseGuard is a focused alert deduplication/suppression tool (cmp_88dc528f7db7). For HelioFab's issue (taxonomy-driven relevance degradation), NoiseGuard would be insufficient: it lacks schema-aware indexing, entity graphs, and reindex/recalibration tooling. Event Nexus's strengths (temporal correlator, entity graph capability, and integration hub) are decisive once we fix the indexing/weighting mismatch. Key risk: if we fail to restore confidence quickly, customer may select NoiseGuard for tactical dedupe and separate tooling for correlation.
- Candidate milestone/proof artifacts:
  - art_e20b32ed9bb7 — Post-Mortem & Immediate Playbook: HelioFab taxonomy v2 — relevance degradation | Root cause: cache invalidation gap between SI-SCHEMA-REG version bump and EN-CORRELATOR per-tenant weight manifest refresh. Impact: search relevance fell 40-60% beginning 2026-03-11 after HelioFab's taxonomy v2 rollout (03-10). Immediate mitigations, medium-term fix, and process changes outlined.
  - art_3fbda14b69dd — Slack thread: HelioFab search relevance after taxonomy v2 — triage and mitigation | Decided to (1) create field aliases and adjust suppression rules as immediate mitigation, (2) push cache invalidation hotfix, (3) schedule weight recalibration/reindex on 2026-03-23. Owners assigned and customer to provide validation queries by 03-20.

## 3. Arcadia Cloudworks
- Competitor: NoiseGuard
- Score: 2
- Fallback evidence artifact: art_5a9a5459f84a — Competitor report: NoiseGuard
- Fallback summary: NoiseGuard (cmp_88dc528f7db7) provides tactical alert deduplication and suppression that Arcadia evaluated prior to selecting Event Nexus. NoiseGuard is easy to deploy and effective at surface-level noise reduction but lacks the schema-aware correlation and enrichment needed to handle taxonomy-driven search regressions. For Arcadia's requirements (canonicalization across schema changes, low-latency correlation, and runbook-driven enrichment) Event Nexus + Orchestrator is a stronger fit.

## 4. CedarWind Renewables
- Competitor: NoiseGuard
- Score: 2
- Fallback evidence artifact: art_bc5dd34a792f — Competitor report: NoiseGuard
- Fallback summary: NoiseGuard (cmp_88dc528f7db7) is the incumbent tactical suppression tool at CedarWind. Strengths: quick deployment and simple suppression rules. Weaknesses: poor schema-awareness and limited ability to carry forward enriched attributes post-taxonomy changes, which increases maintenance burden and fails to guarantee search index compatibility. Event Nexus offers richer schema registry integration and index-weight control that address CedarWind's pain point more robustly.
- Candidate milestone/proof artifacts:
  - art_03d9a25a52e2 — Technical Validation call with CedarWind Renewables | Technical validation call to triage degraded search relevance. Confirmed root cause is mismatched index weighting vs updated taxonomy, walked through mapping files, proposed soft reindex and schema-aware weighting adjustments using Event Nexus' Schema Registry integration. Customer pressed on non-disruption, rollback plan, and overlap with NoiseGuard.

## 5. Province of Laurentia — Department of Public Works
- Competitor: MetricLens
- Score: 0
- Fallback evidence artifact: art_4e37ef635818 — Competitor report: MetricLens
- Fallback summary: MetricLens is the primary competitor in Laurentia's renewal evaluation. MetricLens offers strong dashboarding and a user-friendly query builder but lacks an integrated high-fidelity ingestion pipeline and orchestration automation. For Laurentia-East, MetricLens' approach would require the customer to deploy or pay for a separate ingestion layer; this increases TCO and complicates compliance for region-based data residency. Northstar's combined Signal Ingest + Orchestrator provides a single-vendor path that preserves schema controls, runbook automation, and compliance evidence exports (SIQ-EVIDENCE-EXPORT).

