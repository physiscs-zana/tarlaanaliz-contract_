# Contracts — Component SSOT (Filtered View)

**SSOT Uyum:** 1.2.0 (güncellendi: 2026-02-24)  
**Değişiklikler:** Drone-agnostik mimari (KR-034), Sezonluk Paket terminolojisi, KR-033 ödeme senkronizasyonu, KR-081 cross-ref eklendi

---

## KR Domain Paketleri İndeksi (Navigasyon)

**Not:** Bu bölüm sadece navigasyon içindir. Normatif metin `ssot/kr_registry.md`'dedir.

### A) Security & Isolation
- KR-070 — Worker Isolation & Egress Policy
- KR-071 — One-way Data Flow + Allowlist Yerleşimi (Ingress)
- KR-073 — Untrusted File Handling + AV1/AV2 + Sandbox

### B) Data Lifecycle & Evidence (Chain of Custody)
- KR-072 — Dataset Lifecycle + Kanıt Zinciri (manifest/hash/signature/verification)
- KR-018 — Radiometric Calibration Hard Gate (QC + Certificate)
- KR-081 — Contract-First / Schema Gates (CI)

### C) Orchestration & Operations
- KR-017 — YZ Analiz Hattı (Şemsiye KR: 070–073 ayrıştırması)
- KR-015 — Pilot kapasite/planlama alt kuralları (drone-agnostik)

### D) Payments & Governance
- KR-033 — Ödeme + Manuel Onay + Audit (Sezonluk Paket + tek seferlik Mission)

---

**Bu dosya ne yapar?** Bu bileşen için geçerli KR'leri listeler ve bileşen-özel uygulama notlarını toplar.  
**Bu dosya ne yapmaz?** Yeni KR üretmez; normatif metin için `docs/ssot/kr_registry.md` kanoniktir.

---

## Kapsam

Bu doküman, `tarlaanaliz-contracts` tarafında API/JSON Schema sözleşmelerini etkileyen kuralları içerir.

## Bu bileşende geçerli KR listesi

| KR | Başlık | Kısa normatif özet |
|---|---|---|
| [KR-017](kr_registry.md#kr-017) | YZ Modeli ile Analiz | Veri Akışı: FieldID + bitki türü + MissionID; PII yok |
| [KR-018](kr_registry.md#kr-018) | Tam Radyometrik Kalibrasyon Zorunluluğu | Training-serving parity zorunluluğu; hard gate |
| [KR-029](kr_registry.md#kr-029) | YZ Eğitim Geri Bildirimi (Training Feedback Loop) | Uzman düzeltmelerini modele geri beslemek |
| [KR-032](kr_registry.md#kr-032) | Training Export Standardı | Uzman feedback'lerini standart formatta export |
| [KR-033](kr_registry.md#kr-033) | Ödeme ve Manuel Onay | Sezonluk Paket + tek seferlik Mission; PAID kanonik; PaymentStateMachine bypass yasak |
| [KR-040](kr_registry.md#kr-040) | Güvenlik Kabul Kriterleri (SDLC) | Defense-in-depth; PR/CI/Release/Ops kapıları tüm bileşenleri kapsar |
| [KR-041](kr_registry.md#kr-041) | SDLC Kapıları (Gate) | Contracts pinleme: CONTRACTS_VERSION + SHA256; breaking-change kontrolü |
| [KR-043](kr_registry.md#kr-043) | Test Checklist (Senaryo Bazlı) | Senaryo bazlı kabul kriterleri |
| [KR-072](kr_registry.md#kr-072) | Dataset Lifecycle + Kanıt Zinciri | Dataset state machine + manifest/hash/signature + AV1/AV2 |
| [KR-073](kr_registry.md#kr-073) | Untrusted File Handling + Malware | Sandbox parse; iki aşamalı tarama; quarantine |
| [KR-080](kr_registry.md#kr-080) | Ana İş Akışları Teknik Kurallar | Teknik spesifikasyonda eklenen/sertleştirilen kurallar |
| [KR-081](kr_registry.md#kr-081) | Contract-First / Schema Gates (CI) | JSON Schema + örnekler + CI doğrulama |
| [KR-084](kr_registry.md#kr-084) | Termal Veri İşleme ve Sulama Stresi | LWIR bant → termal pipeline; CWSI, canopy temp; THERMAL_STRESS LayerCode |

---

## Bu bileşenin "tek doğru çıktısı"

- OpenAPI (public/internal)
- JSON Schema (AnalysisJob, CalibratedDatasetManifest, PaymentIntent vb.)
- CI doğrulamaları (schema validation, backwards compatibility)

---

## Uygulama Notları

### KR-033 — Ödeme ve Manuel Onay (SSOT 1.2.0 güncel)

- **Amaç:** Sezonluk Paket Subscription ve tek seferlik Mission ödemelerini kontratlaştırmak.
- **Şemalar:** `schemas/platform/payment_intent.v2.schema.json` (kanonik), `payment_intent.v1.schema.json` (deprecated)
- **Enumlar:** `enums/payment_status.enum.v2.json`, `enums/payment_method.enum.v1.json`
- **Hard gate:** `PaymentIntent.status == PAID` olmadan Mission ASSIGNED veya Subscription ACTIVE olamaz.
- **Kanonik durum:** `PAID` — `APPROVED` kullanılmaz.
- **Otomatik expire:** YOK — `PAYMENT_PENDING` admin kararıyla `CANCELLED` yapılır.
- **IBAN dekont kanalı:** `POST /payments/intents/{id}/upload-receipt` — e-posta değil.
- **State machine:** Tüm geçişler `PaymentStateMachine` üzerinden; bypass `PaymentTransitionError` döner.
- **Log/Audit:** `PAYMENT.INTENT_CREATED`, `PAYMENT.MARK_PAID`, `PAYMENT.WEBHOOK_PAID`, `PAYMENT.REJECTED`, `PAYMENT.CANCELLED`, `PAYMENT.REFUNDED` — `correlation_id` zorunlu, PII yok.
- **Test/Acceptance:** `docs/examples/payment_intent_*.example.json` v2 şemasına uyuyor; `APPROVED`/`EXPIRED` değerleri CI'da FAIL.
- **Cross-refs:** [KR-027] (Sezonluk Paket scheduler), [KR-028] (Mission lifecycle)

---

### KR-072 — Dataset Lifecycle + Kanıt Zinciri

- **Amaç:** Veri akışını sözleşmeye bağlamak; tamper/malware tartışmalarını teknik kanıtla çözmek.
- **Dataset durumları (enum, zorunlu):**
  `RAW_INGESTED`, `RAW_SCANNED_EDGE_OK`, `RAW_HASH_SEALED`, `CALIBRATED`, `CALIBRATED_SCANNED_CENTER_OK`, `DISPATCHED_TO_WORKER`, `ANALYZED`, `DERIVED_PUBLISHED`, `ARCHIVED`, `REJECTED_QUARANTINE`
- **Zorunlu şemalar:**
  - `schemas/edge/intake_manifest.v1.schema.json`
  - `schemas/platform/calibrated_dataset_manifest.v1.schema.json`
  - `schemas/platform/calibration_result.v1.schema.json`
  - `schemas/platform/qc_report.v1.schema.json`
- **Hard gate:** `analysis_job.v1` yalnızca `CALIBRATED_SCANNED_CENTER_OK` dataset_ref kabul eder.

---

### KR-081 — Contract-First / Schema Gates

- **Amaç:** Kodlamadan önce ortak dili makine-doğrulanabilir hale getirmek.
- **Hard gate:** CI'da `validate.py` + `breaking_change_detector.py` — FAIL ise merge engellenir.
- **Test/Acceptance:** `tests/test_validate_all_schemas.py`, `test_examples_match_schemas.py`, `test_no_breaking_changes.py`

---

### KR-073 — Untrusted File Handling + AV1/AV2

- **scan_report.v1 (zorunlu alanlar):** engine_id, signatures_version, started_at/ended_at, scanned_files[{path,size,sha256}], result(PASS/FAIL), findings[], quarantined
- **verification_report.v1 (zorunlu alanlar):** manifest_hash, computed_hashes, mismatches[], decision(ACCEPT/REJECT), reason
- **Hard gate:** PASS olmadan dataset durum ilerleyemez; decision REJECT → `REJECTED_QUARANTINE`.

---

### KR-084 — Termal Veri İşleme ve Sulama Stresi Analizi

- **Amaç:** LWIR bant mevcut olduğunda sulama stresi analizi; yoksa graceful degradation.
- **Şemalar:** `schemas/worker/thermal_analysis_result.v1.schema.json` (kanonik)
- **Tetikleme koşulu:** `intake_manifest.available_bands[]` içinde `LWIR` bant tanımı varsa termal pipeline etkinleşir.
- **Termal kalibrasyon kanıtı:** `calibration_result.json` içinde `thermal_calibration` bölümünde tutulur.
- **Çıktılar:** Canopy sıcaklık haritası (°C), CWSI (0.0–1.0), canopy-soil sıcaklık deltası, sulama etkinliği göstergesi.
- **Katman kodu:** `THERMAL_STRESS` (KR-064 Layer Registry).
- **Hata modları:** Kalibrasyon kanıtı eksik → `THERMAL.QC_FAIL` → termal pipeline devre dışı, MS pipeline normal devam.
- **Cross-refs:** [KR-018/KR-082] (radyometri), [KR-017] (şemsiye), [KR-072] (dataset lifecycle), [KR-064] (layer registry)
