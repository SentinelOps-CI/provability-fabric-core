# PCS trace_certificate to PF-Core mapping

Reference mapping for Phase 7 PR-1 (pcs-core). Authoritative hash vectors live in
`adapters/pcs/tests/fixtures/hash_vectors/`.

## Field mapping

| PCS `trace_certificate` | PF-Core artifact | Notes |
|-------------------------|------------------|-------|
| `certificate_id` | `certificate.certificate_id` | Stable identifier |
| `schema_version` | `certificate.schema_version` | PCS vs PF-Core version strings differ |
| `trace_hash` | `trace.trace_hash`, `certificate.trace_hash` | Must bind; accept `sha256:` prefix at boundary |
| `spec_hash` | `certificate.contract_hash` | Contract digest, not trace digest |
| `property_id` | (none) | PCS-only; document policy cross-ref in pcs-core |
| `checker` | `certificate.checker` | e.g. `lean4` |
| `checker_version` | `certificate.checker_version` | Pinned toolchain |
| `status` | `certificate.safe` | `CertificateChecked` + `safe: true` |
| `counterexample_ref` | (none) | PCS-only counterexample pointer |
| `created_at` | (none) | Organizational metadata |
| `producer` | `certificate.created_by` | Optional |
| `producer_version` | (none) | Organizational metadata |
| `source_repo` | `certificate.proof_ref` | Different semantics; cross-reference only |
| `source_commit` | (none) | Document cross-ref to `proof_ref` |
| `signature_or_digest` | (none) | PIP bundle integrity layer |

## Event / trace derivation

PCS LabTrust release replay produces a two-event PF-Core trace when QC verification passes:

1. Read `trace_certificate.valid.json`, `verification_result.valid.json`, and
   `science_claim_bundle.certified.valid.json` from the labtrust release directory.
2. Map `property_id` → `policy_ref` (`policy/{property_id}.v0`).
3. Map `spec_hash` → `certificate.contract_hash` (recorded as `pcs_spec_hash_hint` during normalization).
4. Map `trace_hash` from certificate when present (`pcs_trace_hash_hint`); compute PF trace hash from events.
5. Emit QC gate `file.read` event (when verification status is `ProofChecked`), then `lab.release` allow.
6. Compute `event_hash` and `trace_hash` per `pf-core/docs/certificate-semantics.md`.

Reference implementation: `adapters/pcs/normalize_release.py`.

## Hash rules

- Canonical JSON: sorted keys, no whitespace, UTF-8.
- Event hash payload excludes `event_hash`.
- Trace hash payload excludes `trace_hash`.
- Storage is lowercase hex64; `normalize_hash` accepts `sha256:` URI prefix.

## Cross-references

- [`pf-core/docs/certificate-semantics.md`](certificate-semantics.md)
- [`docs/pf-core/phase7-pcs-checklist.md`](../../docs/pf-core/phase7-pcs-checklist.md)
- [`adapters/pcs/tests/test_trace_certificate_mapping.py`](../../adapters/pcs/tests/test_trace_certificate_mapping.py)
