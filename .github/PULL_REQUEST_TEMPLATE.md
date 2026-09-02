<!--
Exowatt x AWS x NVIDIA Omniverse - pull request template

This is a private POC repository tied to an active customer engagement.
Keep PRs scoped to one logical concern; large reorgs go in their own PR.
-->

## What this changes

<!-- 1-2 sentences. What is different after this PR is merged? -->

## Why

<!-- The customer ask, standup action item, or POC milestone that motivated this. -->

## Verification

- [ ] `make verify` passes on a clean checkout (offline, no AWS spend, no GPU)
- [ ] Any new live path is a gated TODO, not an executed launch
- [ ] No production claims added (see [LICENSE](../LICENSE) framing: POC only)
- [ ] No secrets added: no `*.env`, `*.pem`, `*.key`, NGC keys, or AWS keys
- [ ] Dates are ISO 8601
- [ ] Sentence-case headings

## Customer-facing impact

<!--
Who notices this change?
- Kamel Boussaid (Exowatt engineering lead) - drives the standup
- Jingchao "JC" Yang (AWS SA) - quota + account
- AWS / NVIDIA reviewers of the POC
- Internal only (no customer impact)
-->

## Tracking

- Related issue:
- POC milestone:
