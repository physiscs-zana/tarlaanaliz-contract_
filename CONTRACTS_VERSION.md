# TarlaAnaliz Contracts Version Lock

## Version: 2.0.0

**Release Date:** 2026-03-06T04:29:08.936927Z  
**Breaking Change:** YES  
**Contracts Checksum (SHA-256):** `296746214c058421d2a91c8d2a09595fede847af9cdf83e5013f526c8b360905`

---

## Version Policy

This file locks the contract version for all consumers (platform, edge, worker).
Consumers MUST validate the contracts checksum before use.

**Semantic Versioning:**
- **MAJOR** (breaking): Incompatible schema changes (field removal, type change, enum removal)
- **MINOR** (non-breaking): New optional fields, new enums, new schemas
- **PATCH** (fixes): Documentation updates, examples, metadata

**Breaking Change Rules:**
- Field removal or rename → MAJOR
- Required field addition → MAJOR
- Type change → MAJOR
- Enum value removal → MAJOR
- Schema removal → MAJOR

**Non-Breaking Changes:**
- Optional field addition → MINOR
- New enum value → MINOR
- New schema → MINOR
- Description/example update → PATCH

---

## File Checksums (SHA-256)

Individual file hashes for verification:

### Shared Schemas

- `schemas/shared/address.v1.schema.json`  
  `9edecd639a7a4440f66c887aedeab9f255208d0f9e50723f08905023cf398665`
- `schemas/shared/geojson.v1.schema.json`  
  `2fe6dfa92852ce5cd836448a57d9385ba718bd6821c3e3e27347dc6665e69265`
- `schemas/shared/money.v1.schema.json`  
  `64fc425b2c734fd51c79bf43fa4a3f85572b4c48fcbead8215e506202250ec2e`

### Core Schemas

- `schemas/core/field.v1.schema.json`  
  `72d9102e7817a9961687c33d8e7fd601c10d20696b205501b64d915c4de3bd8d`
- `schemas/core/mission.v1.schema.json`  
  `83b1e4fd1e64b5c19b5de4cde67f19e687fa074fc92f6a169fdd678e0e27fe25`
- `schemas/core/user.v1.schema.json`  
  `0802c8ef44ffd24ee7ad7900acc28f19e9d9de8e24d58d6d1d5860ba5d6c6634`
- `schemas/core/user_pii.v1.schema.json`  
  `8308a63f302188db2ab1ec7be1f34ad0cf14bb74426c2d4a09860d18193af2b6`

### Edge Schemas

- `schemas/edge/calibration_result.v1.schema.json`  
  `cf67bfa0642dc24e0745ed4fd32cf12c1190206e36684a06c7127d3c816c58be`
- `schemas/edge/dataset_manifest.v1.schema.json`  
  `b5a6f03d6aae2dc3e39605e1b2bf80729abcdfe3ebc73c6099747cf44127c5be`
- `schemas/edge/edge_metadata.v1.schema.json`  
  `d081229b4092d67d1a38e61b994a8d4a83010d695c6b0769c3e31ac80312f851`
- `schemas/edge/intake_manifest.v1.schema.json`  
  `d9a0a83bddabde90cb49f6355cb6bc9c9b70d2b5e89328787a401810488f5417`
- `schemas/edge/qc_report.v1.schema.json`  
  `4193e9c6d73ddd98bf62ba5b2ea034263cb9a86b69f6c549e7d77ed5bc93d219`
- `schemas/edge/quarantine_event.v1.schema.json`  
  `8ea1bf0eea7409b4cbfdc5608cda4689970a24eae7bbbfe251b7d66790e6bc94`
- `schemas/edge/scan_report.v1.schema.json`  
  `edd65c986c8d64b159f3943959bd34d6b19bff4a42b5d880add1f7e69e3e82f0`
- `schemas/edge/transfer_batch.v1.schema.json`  
  `805c9db4eb773adfe95d2be8961190612b316c0a5cb89a11adda150ab422bb75`
- `schemas/edge/verification_report.v1.schema.json`  
  `aa84f86d4ca03b515af8fc551ab66197f46e6dd532f6b48601f591e2be197d42`

### Worker Schemas

- `schemas/worker/analysis_job.v1.schema.json`  
  `426db4ed780e5bb0a7e8bb53fd5ea6564fe02139f96f91102e3e457a92180331`
- `schemas/worker/analysis_result.v1.schema.json`  
  `69af83931b8f8ae66f4f2981362e772a54073f44de6b680c4bf9c32c3ae9f5af`
- `schemas/worker/thermal_analysis_result.v1.schema.json`  
  `3a9f522b453656dfb7bce8b1897a3de4a8b3cfd1fedccd9a8bd780562ee75c66`

### Events

- `schemas/events/analysis_completed.v1.schema.json`  
  `6f093470ce2644ffff3bb1e05c9148a2650723e7f4420dcddd81f228006a4db6`
- `schemas/events/dataset_analyzed.v1.schema.json`  
  `049a728eb4e7202cd49e4d1ad18622625bfdcb7909b8622ab266f9dedd598273`
- `schemas/events/dataset_calibrated.v1.schema.json`  
  `480f0b2edf024d90596678eeeb4864bf97ca4d9f45343d739ee92410a4db4921`
- `schemas/events/dataset_dispatched.v1.schema.json`  
  `42b6069f9bfceb7f1315b1e7273b8564dd60cc5fb6da208221a7d3fdc79eae5d`
- `schemas/events/dataset_ingested.v1.schema.json`  
  `81257f505033cb665a276c785689afb14eb509214fdd549900f2ccc8da7f91e4`
- `schemas/events/dataset_scanned.v1.schema.json`  
  `4384dbd2033556844b63e4b45a761d6be03369a1097309062117262bc86586f2`
- `schemas/events/dataset_verified.v1.schema.json`  
  `fd575c29f35f636f847b64925f44bca2d5961c9c47e8221fd66599d07f141852`
- `schemas/events/derived_published.v1.schema.json`  
  `97b80c38d43b761677ca32bf66f05381eddc7445088096962b18efdf354bf07a`
- `schemas/events/field_created.v1.schema.json`  
  `9fb0649f1d2e214553f4afc4148cf3ebf6358e9f9dcb0effd83188f0370e1035`
- `schemas/events/mission_assigned.v1.schema.json`  
  `6a3d4a6cb0b286cfa4f35fa8cab41a8d5fe04c410c90f8bb83a59cdeee77f2c3`

### Platform

- `schemas/platform/calibrated_dataset_manifest.v1.schema.json`  
  `4cad336bb3edfb05be2345707c5e98a02c6386d3ca480f7dac677a32f81dca17`
- `schemas/platform/calibration_result.v1.schema.json`  
  `c51b377e0aa6922d0b86f4cf9076093d66fc4c13a747f44da3f7059c40a73038`
- `schemas/platform/evidence_bundle_ref.v1.schema.json`  
  `e427500cb72ccf47ef16deca8e4453930f03acd520b328e8310a4be6f8d2b90b`
- `schemas/platform/layer_registry.v1.schema.json`  
  `5d011bbb71c6cb236a163205b8ad9b159db3f66ae5ce8002b6f8d71412635eb9`
- `schemas/platform/payment_intent.v1.schema.json`  
  `ec1223135e451b17a76dd8fedd8f36b9ecda47cdd2f8688afce32f3e6455069d`
- `schemas/platform/payment_intent.v2.schema.json`  
  `ff6a6bfc5758be191b996cfd28d6f6e53d8dfbc1d10c9f135157023f5dd522cd`
- `schemas/platform/payroll.v1.schema.json`  
  `72817e6ee06fd533dbeede4127cd024f71ad59c2572a5de2c42d78066590bc1c`
- `schemas/platform/pricing.v1.schema.json`  
  `b6270875d14eeedd116024443cd4681de803974ef1495e41f970a1ba782ef778`
- `schemas/platform/qc_report.v1.schema.json`  
  `0709dd9c98ebaa11c45924bf571b0cfb6291af16711fbb133e1e2e7b3d97a538`
- `schemas/platform/subscription.v1.schema.json`  
  `04c5e4e852bf1011dd2af2b879c24e836585a69ef64142c3898cb941ee14dfd5`
- `schemas/platform/training_feedback.v1.schema.json`  
  `e3eee12e9627709d2c9b507a4c9b928aeb2e427d613d7ec9256b60da1461a902`

### API Components

- `api/components/parameters.yaml`  
  `19cc0b99a8ec6873037c48b5d80e90b6d1443aca4137e6a474fb3660c5932092`
- `api/components/responses.yaml`  
  `c88266b02303eb6b621b7cd6df20385963c2c8ed2864fd84d24e18ae24f93140`
- `api/components/schemas.yaml`  
  `543636cb3d3cdc2ef9ed09dd973a3a65113915917d786f98b3ac5af8d7ab8059`
- `api/components/security_schemes.yaml`  
  `9d45e3181a4b847b617a0553c72458650aa9c3deacf38cbed67c5c12db3e1c79`

### API Specs

- `api/edge_local.v1.yaml`  
  `510fac0f988752927353a6ec0fe431fe0098fbec2600074a39ca96103f040ccd`
- `api/platform_internal.v1.yaml`  
  `f253f4b68be11f4a1f65416827a6482106017a63c940c39e46eb90e69232cbb7`
- `api/platform_public.v1.yaml`  
  `2333e431478cf8c66b50d93ea7fc6a969fbfba20cc828cbd58b0ae1c6547b400`

---

## Changelog

### v2.0.0 (2026-03-06)

**Breaking:** YES

Version 2.0.0: schema compliance fixes, enhanced validation

---

## Verification

Consumers MUST verify contracts checksum:

### Python
```python
import hashlib
import json

def verify_contracts(expected_checksum: str) -> bool:
    # Compute actual checksum from schemas
    actual_checksum = compute_contracts_checksum()
    return actual_checksum == expected_checksum

assert verify_contracts("296746214c058421d2a91c8d2a09595fede847af9cdf83e5013f526c8b360905"), "Contracts checksum mismatch!"
```

### Node.js
```javascript
const crypto = require('crypto');
const assert = require('assert');

function verifyContracts(expectedChecksum) {
  const actualChecksum = computeContractsChecksum();
  return actualChecksum === expectedChecksum;
}

assert(verifyContracts("296746214c058421d2a91c8d2a09595fede847af9cdf83e5013f526c8b360905"), "Contracts checksum mismatch!");
```

### CI/CD Integration

Add to `.github/workflows/validate.yml`:

```yaml
- name: Verify Contracts Version
  run: |
    python3 tools/pin_version.py --verify
```

---

## Consumer Integration

### Platform Service (platform repo)
```bash
# In platform repo
git submodule add https://github.com/tarlaanaliz/contracts contracts
git submodule update --remote
python3 contracts/tools/pin_version.py --verify
```

### Edge Station (edge repo)
```bash
# In edge repo
git submodule add https://github.com/tarlaanaliz/contracts contracts
git submodule update --remote
./contracts/tools/sync_to_repos.sh --target edge
```

### Worker Service (worker repo)
```bash
# In worker repo
git submodule add https://github.com/tarlaanaliz/contracts contracts
git submodule update --remote
./contracts/tools/sync_to_repos.sh --target worker
```

---

## Notes

- **Immutable:** Once released, versions are immutable. Create new version for changes.
- **CI Enforcement:** All PRs MUST pass `tools/validate.py` and checksum verification.
- **Breaking Changes:** Require major version bump and consumer coordination.
- **Hash Algorithm:** SHA-256 (collision-resistant, FIPS 140-2 compliant)
- **Timestamp:** ISO 8601 UTC format

**Last Updated:** 2026-03-06T04:29:08.936927Z
