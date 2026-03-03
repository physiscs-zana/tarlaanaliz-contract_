# SDLC Gate Checklists

**Kapsam:** PR → CI → Release kapıları — tek normatif doküman.  
**SSOT Uyum:** 1.2.0 (2026-02-24)  
**KR Referanslar:** KR-041 (SDLC Kapıları), KR-081 (Contract-First), KR-033 (Ödeme)

> Bu dosya üç aşamalı kalite kapısını tek kaynakta toplar.  
> Eski `PR_GATE_CHECKLIST.md`, `CI_GATE_CHECKLIST.md`, `RELEASE_GATE_CHECKLIST.md` dosyaları bu dosya ile değiştirilmiştir.

---

# GATE 1 — PR (Pull Request)

Her PR açılmadan önce geliştirici tarafından yapılacak kontroller.

## 1A) Schema + Enum Doğrulama

- [ ] `python tools/validate.py` hatasız çalışıyor
- [ ] Tüm JSON Schema dosyaları `"$schema": "https://json-schema.org/draft/2020-12/schema"` içeriyor
- [ ] Object tipli şemalarda `unevaluatedProperties: false` var
- [ ] Tekrarlı alt tipler `$defs` + `$ref` ile tanımlanmış

## 1B) Forbidden-Field Guard

- [ ] Hiçbir şema/enum/API alanında `email`, `tckn`, `otp` string'i geçmiyor
- [ ] `user_pii.v1` dışında hiçbir şemada telefon numarası zorunlu alan değil
- [ ] **[SSOT 1.2.0]** `payment_status` alanlarında `APPROVED` veya `EXPIRED` değeri YOK
- [ ] **[SSOT 1.2.0]** IBAN_TRANSFER akışında "e-posta" / "odeme@tarlaanaliz.com" referansı YOK

## 1C) Breaking-Change Kontrolü

- [ ] `python tools/breaking_change_detector.py` çalıştırıldı
- [ ] Breaking-change tespit edilmişse:
  - [ ] MAJOR versiyon bump yapıldı (`CONTRACTS_VERSION.md`)
  - [ ] Migration guide yazıldı (`docs/migration_guides/`)
  - [ ] `CHANGELOG.md` güncellendi

## 1D) Contracts Versiyonlama

- [ ] `CONTRACTS_VERSION.md` güncel (semver + sha256)
- [ ] Consumer repo'lar (platform/edge/worker) bu versiyon ile senkronize

## 1E) Ödeme Kontrolleri (KR-033) — [SSOT 1.2.0]

- [ ] `PaymentStateMachine` servisi bypass etmeyen tek yol; doğrudan status update kodu YOK
- [ ] `mark-paid` endpoint'i `admin_note` zorunluluğunu uyguluyor
- [ ] `reject` endpoint'i `rejection_reason` zorunluluğunu uyguluyor
- [ ] `PAYMENT.MARK_PAID` ve `PAYMENT.REJECTED` audit olaylarında `admin_user_id` zorunlu
- [ ] `receipt_blob_id` upload endpoint'i (`POST /payments/intents/{id}/upload-receipt`) tanımlı
- [ ] Sezonluk Paket `PAID` olmadan `ACTIVE` olamıyor (scheduler gate)
- [ ] Mission `PAID` olmadan `ASSIGNED` olamıyor (assignment gate)

## 1F) Drone Registry Kontrolü — [SSOT 1.2.0]

- [ ] Yeni drone modeli eklendiyse `enums/drone_type.enum.v1.json` güncellendi
- [ ] `drone_registry.yaml` ile `drone_type.enum.v1.json` senkronize
- [ ] `intake_manifest.v1`: `drone_model` alanı DroneType enum değerlerinden biri
- [ ] Eski DJI-only kısıtlaması kaldırıldı (tek model whitelist YOK)

## 1G) Örnekler + Testler

- [ ] `docs/examples/` altındaki tüm örnek JSON'lar ilgili şemaya uyuyor
- [ ] `python -m pytest tests/` tüm testleri geçiyor
  - `test_validate_all_schemas.py`
  - `test_examples_match_schemas.py`
  - `test_no_breaking_changes.py`

## 1H) SSOT Senkronizasyon

- [ ] `docs/ssot/kr_registry.md` bu PR'ın etkilediği KR'lerle uyumlu
- [ ] `docs/ssot/contracts_ssot.md` güncel uygulama notları içeriyor

---

# GATE 2 — CI (Continuous Integration)

Her PR'da CI pipeline'ında otomatik koşacak kontroller.

## 2A) Schema Validation (`tools/validate.py`)

```
BEKLENEN: EXIT 0
KONTROLLER:
  ✓ JSON Schema Draft 2020-12 format doğrulama (tüm schemas/*.json)
  ✓ unevaluatedProperties:false policy (object tipli şemalar)
  ✓ Forbidden-field guard: email/tckn/otp → FAIL
  ✓ [SSOT 1.2.0] payment_status guard: APPROVED/EXPIRED değerleri → FAIL
  ✓ [SSOT 1.2.0] drone_model değerleri drone_registry.yaml ile eşleşiyor → FAIL yoksa
  ✓ Enum dosyaları format + benzersizlik kontrolü
  ✓ OpenAPI lint + schema reference bütünlüğü
```

## 2B) Örnek Doğrulama (`tests/test_examples_match_schemas.py`)

```
BEKLENEN: TÜM TESTLER PASS
KONTROLLER:
  ✓ docs/examples/field.example.json → schemas/core/field.v1.schema.json
  ✓ docs/examples/mission.example.json → schemas/core/mission.v1.schema.json
  ✓ docs/examples/intake_manifest.example.json → schemas/edge/intake_manifest.v1.schema.json
  ✓ docs/examples/analysis_job.example.json → schemas/worker/analysis_job.v1.schema.json
  ✓ docs/examples/analysis_result.example.json → schemas/worker/analysis_result.v1.schema.json
  ✓ [SSOT 1.2.0] docs/examples/payment_intent_iban_pending.example.json → payment_intent.v2
  ✓ [SSOT 1.2.0] docs/examples/payment_intent_iban_paid.example.json → payment_intent.v2
  ✓ [SSOT 1.2.0] docs/examples/payment_intent_creditcard_paid.example.json → payment_intent.v2
```

## 2C) Breaking-Change Detector (`tests/test_no_breaking_changes.py`)

```
BEKLENEN: Breaking-change yoksa PASS; varsa semver MAJOR bump kontrolü
KONTROLLER:
  ✓ Önceki versiyonla şimdiki şemalar diff'lendi
  ✓ Breaking-change var ama MAJOR bump yok → FAIL
  ✓ Migration guide eksik → WARN
```

## 2D) Ödeme Durum Makinesi Guard — [SSOT 1.2.0]

```
BEKLENEN: EXIT 0
KONTROLLER:
  ✓ enums/payment_status.v1.json: APPROVED yok, EXPIRED yok → yoksa FAIL
  ✓ enums/payment_status.v2.json: APPROVED yok, EXPIRED yok → yoksa FAIL
  ✓ payment_intent.v1 + v2 status enum: PAID kanonik → değilse FAIL
```

## 2E) Drone Registry Senkronizasyon — [SSOT 1.2.0]

```
BEKLENEN: EXIT 0
KONTROLLER:
  ✓ enums/drone_type.enum.v1.json değerleri drone_registry.yaml ile eşleşiyor
  ✓ DJI-only kısıtlaması içeren herhangi bir kod/şema → WARN
```

## CI Failure Tablosu

| Hata | Eylem |
|---|---|
| validate.py FAIL | PR merge engellenir |
| test_examples FAIL | PR merge engellenir |
| breaking-change FAIL | PR merge engellenir; MAJOR bump gerekli |
| payment guard FAIL | PR merge engellenir |
| drone registry FAIL | PR merge engellenir |

---

# GATE 3 — Release

Yayın (release) öncesi yapılacak son kontroller.

## 3A) Versiyon + Changelog

- [ ] `CONTRACTS_VERSION.md` doğru semver içeriyor
  - Breaking-change varsa: MAJOR bump yapıldı (örn: v1.x.x → v2.0.0)
  - Non-breaking değişiklik: MINOR veya PATCH
- [ ] `CONTRACTS_VERSION.md` sha256 hash güncel (tüm şema dosyaları dahil)
- [ ] `CHANGELOG.md` bu release için tüm değişiklikleri kapsıyor:
  - `### Breaking Changes` bölümü (varsa)
  - `### Added / Changed / Fixed` bölümleri

## 3B) Migration Guide

- [ ] Breaking-change varsa `docs/migration_guides/` altında migration guide hazır
- [ ] **[SSOT 1.2.0]** `payment_intent_v1_to_v2.md` mevcut ve güncel
- [ ] Migration guide içeriyor: DB değişiklikleri, kod değişiklikleri, rollback planı, test kriterleri

## 3C) Consumer Repo Senkronizasyon

- [ ] `tools/sync_to_repos.sh` çalıştırıldı
- [ ] platform repo: `CONTRACTS_VERSION.md` bu release ile eşleşiyor
- [ ] edge repo: `CONTRACTS_VERSION.md` bu release ile eşleşiyor
- [ ] worker repo: `CONTRACTS_VERSION.md` bu release ile eşleşiyor
- [ ] Tüm consumer'larda SHA-256 hash uyumu doğrulandı

## 3D) SSOT 1.2.0 Özgül Kontroller — [YENİ]

- [ ] `enums/payment_status.v1.json`: APPROVED ve EXPIRED değerleri yok
- [ ] `enums/payment_status.v2.json`: APPROVED ve EXPIRED değerleri yok, REFUNDED var
- [ ] `enums/drone_type.enum.v1.json`: Tüm desteklenen modeller mevcut
- [ ] `schemas/platform/payment_intent.v2.schema.json`: receipt_blob_id, admin_note, rejection_reason, admin_user_id alanları mevcut
- [ ] `schemas/edge/intake_manifest.v1.schema.json`: drone_model DroneType enum'una bağlı
- [ ] `docs/examples/payment_intent_*.example.json` dosyaları mevcut ve v2 şemasına uyuyor

## 3E) Son Testler

- [ ] `python -m pytest tests/ -v` — tüm testler PASS
- [ ] `python tools/validate.py` — EXIT 0
- [ ] `python tools/breaking_change_detector.py` — rapor incelendi

## 3F) SSOT Dokümantasyon

- [ ] `docs/ssot/kr_registry.md` son KR Registry versiyonu (v8+)
- [ ] `docs/ssot/GOVERNANCE_PACK_v1_0_1.md` güncel
- [ ] `docs/ssot/contracts_ssot.md` bu release ile uyumlu
