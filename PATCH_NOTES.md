# PATCH NOTES — Dataset Lifecycle Layer

## v1.0.0 (2026-03-03) — İlk Oluşturma (KR-072/073 Kurtarma)

Bu dosyalar robocopy /MIR ile yanlışlıkla silinen ve KR-072/073 spesifikasyonlarından yeniden oluşturulan dataset lifecycle layer dosyalarıdır.

### Oluşturulan Dosyalar

#### Enums (4 dosya)
- `enums/dataset_status.enum.v1.json` — Dataset yaşam döngüsü state machine (10 durum)
- `enums/qc_status.enum.v1.json` — QC sonuç durumları (PASS/WARN/FAIL)
- `enums/scan_stage.enum.v1.json` — AV tarama aşamaları (AV1_EDGE/AV2_PLATFORM)
- `enums/verification_status.enum.v1.json` — Hash doğrulama sonuçları (ACCEPT/REJECT)

#### Schemas — datasets/ (9 dosya)
- `attestation.v1` — Kanıt zinciri onay belgesi
- `calibration_certificate.v1` — Radyometrik kalibrasyon sertifikası
- `dataset.v1` — Dataset ana varlık şeması
- `dataset_manifest.v1` — Dosya hash manifest
- `evidence_bundle_ref.v1` — Kanıt paketi referansı
- `qc_report.v1` — Kalite kontrol raporu
- `scan_report.v1` — AV tarama raporu
- `transfer_batch.v1` — Veri transfer partisi
- `verification_report.v1` — Hash/imza doğrulama raporu

#### Schemas — edge/ (6 dosya)
- Edge tarafı versiyonları: calibration_result, dataset_manifest, qc_report, scan_report, transfer_batch, verification_report

#### Schemas — events/ (7 dosya)
- Dataset lifecycle event'leri: ingested, scanned, verified, calibrated, dispatched, analyzed, derived_published

#### Schemas — platform/ (1 dosya)
- `evidence_bundle_ref.v1` — Platform tarafı kanıt paketi

#### Tools (1 dosya)
- `verify_contracts_datasets_layer.py` — Dataset layer doğrulama aracı

#### Generated (4 dosya)
- `generated/python/field.py` + `__init__.py`
- `generated/typescript/field.d.ts` + `index.d.ts`

#### Examples (2 dosya)
- `dataset.example.json` — RAW_INGESTED durumunda örnek dataset
- `dataset_manifest.example.json` — Dosya hash manifest örneği

### KR Referansları
- **KR-072:** Dataset Lifecycle + Kanıt Zinciri
- **KR-073:** Untrusted File Handling + AV1/AV2
- **KR-018:** Radyometrik Kalibrasyon Hard Gate
- **KR-071:** One-way Data Flow

### Notlar
- Tüm şemalar JSON Schema Draft 2020-12 uyumludur
- $ref bağlantıları mevcut enum dosyalarına işaret eder
- Bu dosyalar daha önce sadece yerel çalışma klasöründe (arcanzana_tarım) mevcuttu, git repo'ya hiç commit edilmemişti
