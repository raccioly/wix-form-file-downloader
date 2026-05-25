# Supply-Chain Security Audit Report - 2026-05-25

## Summary
The read-only supply-chain security audit has been completed for this repository according to `SUPPLY-CHAIN-AUDIT.md`.

**Overall Status**: 1 HIGH severity finding.

---

## Audit Phases

### Phase 1: Known-Bad Packages
**Status**: PASS
**Findings**: No package lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `requirements*.txt`, `poetry.lock`, `pyproject.toml`) exist in the repository. No known-bad packages detected.

### Phase 2: IOCs on Disk
**Status**: PASS
**Findings**: No IOCs detected.
- No worm loaders found (`router_init.js`, `router_runtime.js`, `setup.mjs`).
- No C2 domains found in the codebase.
- No persistence mechanisms detected.
- No malicious git artifacts (no `shai-hulud` remotes or commits by `claude <claude@users.noreply.github.com>`).

### Phase 3: Slopsquatting
**Status**: PASS
**Findings**: No direct dependencies present.

### Phase 4: Freshness Violations
**Status**: PASS
**Findings**: No direct dependencies present, therefore no freshness violations or floating version ranges.

### Phase 5: Install-Script Exposure
**Status**: PASS
**Findings**: No `package.json` or `.npmrc` files present. No install-script exposure detected.

### Phase 6: CI/CD Attack Surface
**Status**: **HIGH SEVERITY FINDING**
**Findings**:
- **HIGH**: The workflow `.github/workflows/supply-chain.yml` uses a third-party action (`google/osv-scanner-action/.github/workflows/osv-scanner-reusable-pr.yml@v2.3.8` and `google/osv-scanner-action/.github/workflows/osv-scanner-reusable.yml@v2.3.8`) that is pinned to a tag (`@v2.3.8`) instead of a 40-char commit SHA.
- No `pull_request_target` + checkout of PR code found.
- No `secrets.*` exposed in PR workflows.
- `permissions:` block is present in the workflow.

---

## Remediation Required
- **Phase 6**: Pin third-party actions in `.github/workflows/supply-chain.yml` to a 40-char commit SHA.