# CLAUDE.md — AI Assistant Guide for tarlaanaliz-contracts

## Project Overview

**tarlaanaliz-contracts** is the single source of truth (SSOT) for all data contracts across the TarlaAnaliz agricultural analysis platform. It follows a **contract-first architecture**: no service (platform, edge, worker) defines its own API or data structures — all definitions originate from this repository.

**Domain**: Drone-based agricultural field analysis in Turkey's GAP (Southeastern Anatolia) region. Farmers request aerial analysis missions; drone pilots capture multispectral imagery; workers process it with AI models; results are delivered as map layers.

**Primary language of documentation**: Turkish, with English used in schema descriptions and code.

## Repository Structure

```
tarlaanaliz-contracts/
├── schemas/            # JSON Schema definitions (Draft 2020-12)
│   ├── core/           # Field, Mission, User, UserPII
│   ├── edge/           # Edge station intake, metadata, quarantine
│   ├── events/         # Event payloads (field_created, mission_assigned, analysis_completed)
│   ├── platform/       # Pricing, Payroll, LayerRegistry, PaymentIntent, QC, Calibration
│   ├── shared/         # GeoJSON, Money, Address (reusable types)
│   └── worker/         # AnalysisJob, AnalysisResult
├── enums/              # Canonical enum definitions (single source)
├── api/                # OpenAPI 3.1 specs
│   ├── platform_public.v1.yaml
│   ├── platform_internal.v1.yaml
│   ├── edge_local.v1.yaml
│   └── components/     # Shared parameters, responses, schemas, security
├── ssot/               # KR registry and component-filtered SSOT views
│   ├── kr_registry.md  # Canonical KR (business rule) definitions
│   └── contracts_ssot.md
├── docs/
│   ├── canonical/      # v2.4 canonical product docs (.docx)
│   ├── checklists/     # PR/CI/Release gate checklists
│   ├── examples/       # Example JSON files matching schemas
│   ├── migration_guides/
│   └── versioning_policy.md
├── tools/              # Validation, type generation, sync, version pinning
├── tests/              # Python pytest-based contract tests
├── .github/workflows/  # CI: contract_validation.yml, auto_sync.yml
├── CONTRACTS_VERSION.md # SemVer + SHA-256 hash lock
├── CHANGELOG.md
├── package.json        # Node.js/TypeScript toolchain
└── pyproject.toml      # Python toolchain
```

## Tech Stack

### Node.js / TypeScript (package.json)
- **Runtime**: Node >= 18, npm >= 9
- **Module system**: ESM (`"type": "module"`)
- **Ajv** ^8.12.0 — JSON Schema Draft 2020-12 validator
- **json-schema-to-typescript** ^13.1.2 — TS type generation
- **@redocly/cli** — OpenAPI bundling and validation
- **Jest** ^29.7.0 + ts-jest — Test runner (configured in package.json)
- **ESLint** ^8.56.0 + @typescript-eslint + prettier — Linting
- **Prettier** ^3.1.1 — Formatting
- **Husky** + **lint-staged** — Pre-commit hooks

### Python (pyproject.toml)
- **Python**: >= 3.10
- **jsonschema** ^4.20.0 (with format extras) — Draft202012Validator
- **pydantic** ^2.5.3 — Data validation
- **pytest** ^7.4.3 + pytest-cov + pytest-xdist — Testing
- **black** ^23.12.1 — Code formatting (line-length: 100)
- **ruff** ^0.1.9 — Linting
- **mypy** ^1.8.0 — Type checking (strict mode)
- **datamodel-code-generator** — Python model generation from schemas

## Critical Rules — MUST Follow

### 1. JSON Schema Draft 2020-12 — Mandatory

Every schema file MUST:
- Include `"$schema": "https://json-schema.org/draft/2020-12/schema"`
- Include `"$id"` with the canonical URL pattern: `https://api.tarlaanaliz.com/schemas/{domain}/{name}.v{N}.schema.json`
- Include `"title"` and `"type"`
- Use `"unevaluatedProperties": false` on all `object` types (prevents field drift)
- Use `"$defs"` for reusable type definitions (referenced via `"$ref": "#/$defs/TypeName"`)

### 2. PII Minimization (KR-050) — Hard Security Requirement

**FORBIDDEN FIELDS** — These field names must NEVER appear in any schema:
- `email`, `e_mail`
- `tckn`, `tc_kimlik_no`
- `otp`, `one_time_password`

**Identity model**: Phone number + 6-digit PIN only. No email, no Turkish national ID, no OTP.

The validator (`tools/validate.py`) and CI workflow check for these automatically. Violating this fails the build.

### 3. Versioning (SemVer)

- **MAJOR**: Breaking changes (adding required fields, changing types, removing enum values, changing endpoints)
  - Requires migration guide in `docs/migration_guides/`
  - `breaking_change: true` in CONTRACTS_VERSION.md
- **MINOR**: Backwards-compatible additions (optional fields, new enum values, new endpoints)
- **PATCH**: Docs, descriptions, loosening constraints

### 4. Schema File Naming Convention

- Schemas: `{name}.v{version}.schema.json` (e.g., `field.v1.schema.json`)
- Enums: `{name}.enum.v{version}.json` (e.g., `crop_type.enum.v1.json`)
- Some older payment enums use `{name}.v{version}.json` without `.enum.`
- OpenAPI: `{service}_{scope}.v{version}.yaml`

### 5. KR (Business Rule) References

Business rules are referenced as `KR-NNN` throughout the codebase. The canonical source is `ssot/kr_registry.md`. Key KRs for this repo:
- **KR-050**: PII minimization (no email/TCKN/OTP)
- **KR-081**: Contract-first / Schema gates (CI)
- **KR-072**: Dataset lifecycle + chain of custody
- **KR-073**: Untrusted file handling + malware scanning
- **KR-018/082**: Radiometric calibration hard gate

## Development Commands

### Validation
```bash
# Full schema validation (Python)
python tools/validate.py

# Node.js validation scripts
npm run validate              # All validations
npm run validate:schemas      # Schemas only
npm run validate:forbidden    # Check forbidden PII fields
npm run validate:unevaluated  # Check unevaluatedProperties enforcement
```

### Testing
```bash
# Python tests (primary)
pytest tests/ -v

# Node.js tests
npm test                      # Jest with coverage
npm run test:ci               # CI mode (coverage, limited workers)
```

### Type Generation
```bash
npm run types:gen             # Generate TypeScript types
npm run types:gen:ts          # TS types only
```

### OpenAPI
```bash
npm run openapi:validate      # Lint OpenAPI specs
npm run openapi:bundle        # Bundle all OpenAPI specs to dist/
```

### Linting & Formatting
```bash
# Node.js
npm run lint                  # ESLint
npm run format                # Prettier

# Python
black .                       # Format
ruff check .                  # Lint
mypy tools/                   # Type check
```

### Full CI Gate (what runs in CI)
```bash
npm run ci:gate               # validate + test:ci + breaking-change:detect + openapi:validate
```

### Breaking Change Detection
```bash
npm run breaking-change:detect
# or
python tools/breaking_change_detector.py --old <base> --new .
```

### Version Pinning
```bash
python tools/pin_version.py          # Update CONTRACTS_VERSION.md hash
python tools/pin_version.py --verify # Verify current hash
```

## CI/CD Workflows

### contract_validation.yml (on PR to main/develop + push to main)
1. **validate-schemas** — Runs `python3 tools/validate.py`
2. **test-schemas** — Runs `pytest tests/ -v` with coverage
3. **detect-breaking-changes** — Compares PR branch against base (PR only)
4. **verify-checksums** — Verifies CONTRACTS_VERSION.md hash
5. **lint-openapi** — Spectral lint on OpenAPI specs
6. **check-forbidden-fields** — Grep-based PII field check
7. **check-draft-2020-12** — Ensures all schemas use 2020-12
8. **summary** — Aggregates results; fails if critical checks fail

### auto_sync.yml
Syncs contract changes to consumer repositories.

## Code Style & Conventions

### TypeScript / JavaScript
- Semicolons: yes
- Quotes: double
- Trailing commas: es5
- Print width: 100
- Tab width: 2
- Arrow parens: always
- End of line: LF

### Python
- Line length: 100
- Target: Python 3.10+
- Formatter: black
- Linter: ruff (pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, bugbear, etc.)
- Type checker: mypy (strict mode, `disallow_untyped_defs`)
- Tests: pytest with strict markers and `--showlocals --tb=short`

### Git Commit Messages
Follow conventional commits pattern:
- `feat(scope): description` — New features
- `fix(scope): description` — Bug fixes
- `audit: description` — Compliance/audit changes
- Scopes include: `contracts`, `geojson`, `schemas`, etc.

## Test Structure

All tests are in `tests/` and use Python's pytest:

| Test File | Purpose |
|---|---|
| `test_validate_all_schemas.py` | Draft 2020-12 compliance, unevaluatedProperties, forbidden fields, enum format |
| `test_examples_match_schemas.py` | Example JSON files validate against their schemas |
| `test_no_breaking_changes.py` | Breaking change detection between versions |

Coverage threshold: 80% (branches, functions, lines, statements) for the `tools/` directory.

## When Modifying Schemas

1. **Read the existing schema** before making changes
2. **Maintain Draft 2020-12 compliance**: `$schema`, `$id`, `title`, `type`, `unevaluatedProperties: false`
3. **Use `$defs`** for reusable types; reference with `$ref`
4. **Never add PII fields** (email, tckn, otp)
5. **Check if the change is breaking** — if adding to `required`, changing types, or removing enum values, it's a MAJOR bump
6. **Update the corresponding example** in `docs/examples/` if one exists
7. **Run validation**: `python tools/validate.py && pytest tests/ -v`

## When Adding New Schemas

1. Place in the appropriate subdirectory under `schemas/`
2. Follow naming: `{name}.v1.schema.json`
3. Include all mandatory fields: `$schema`, `$id`, `title`, `type`, `unevaluatedProperties: false`
4. Add `$defs` for complex sub-types
5. Create an example in `docs/examples/`
6. Run the full validation suite

## When Modifying Enums

1. **Adding values**: Non-breaking (MINOR). Add to the `enum` array.
2. **Removing values**: Breaking (MAJOR). Requires migration guide.
3. **Renaming values**: Breaking (MAJOR). Requires migration guide.
4. Include bilingual display names (`tr` + `en`) in metadata when applicable.

## When Modifying OpenAPI Specs

1. OpenAPI version: 3.1.0
2. Reference JSON Schemas via `$ref` where possible
3. All endpoints follow the authentication model: session token from phone + PIN login
4. Run `npm run openapi:validate` after changes
5. Shared components go in `api/components/`

## Key Domain Concepts

- **Field**: Agricultural parcel with boundary geometry, crop type, season
- **Mission**: Drone flight analysis request tied to a Field
- **Intake Manifest**: Edge station document tracking raw data ingestion with hash chain
- **Quarantine**: Failed QC/AV/hash checks result in quarantine status
- **Analysis Job/Result**: Worker processing pipeline input/output
- **Layer Registry**: Map layer definitions (NDVI, disease detection, etc.)
- **Payroll**: Pilot payment calculations
- **KR (Kural Referansı)**: Business rule identifier system used across all docs

## Consumer Repositories

This contracts repo is consumed by:
- **tarlaanaliz-platform** — Main platform backend
- **tarlaanaliz-edge** — Edge/kiosk station software
- **tarlaanaliz-worker** — AI analysis worker

Consumers pin to a specific version via `CONTRACTS_VERSION.md` + SHA-256 hash verification.
