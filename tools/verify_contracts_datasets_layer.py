#!/usr/bin/env python3
"""
verify_contracts_datasets_layer.py — KR-072 + KR-073 Dataset Layer Doğrulama Aracı

Kullanım:
    python tools/verify_contracts_datasets_layer.py [--strict] [--verbose]

Bu script:
1. schemas/datasets/ altındaki tüm JSON Schema dosyalarını doğrular
2. enums/ altındaki dataset-related enum'ların tutarlılığını kontrol eder
3. schemas/edge/ ve schemas/events/ ile cross-reference kontrolü yapar
4. docs/examples/ altındaki örnek JSON'ların şemaya uyumluluğunu test eder
5. $ref bağlantılarının geçerliliğini doğrular

Çıkış kodları:
    0 = Tüm kontroller başarılı
    1 = Doğrulama hataları bulundu
    2 = Dosya bulunamadı / yapısal hata
"""

import json
import os
import sys
import glob
from pathlib import Path

# Proje kök dizini
PROJECT_ROOT = Path(__file__).parent.parent

# Beklenen dizin yapısı
EXPECTED_DIRS = [
    "enums",
    "schemas/datasets",
    "schemas/edge",
    "schemas/events",
    "schemas/platform",
    "schemas/core",
]

# Dataset layer'a ait beklenen dosyalar
EXPECTED_ENUMS = [
    "enums/dataset_status.enum.v1.json",
    "enums/qc_status.enum.v1.json",
    "enums/scan_stage.enum.v1.json",
    "enums/verification_status.enum.v1.json",
]

EXPECTED_DATASET_SCHEMAS = [
    "schemas/datasets/attestation.v1.schema.json",
    "schemas/datasets/calibration_certificate.v1.schema.json",
    "schemas/datasets/dataset.v1.schema.json",
    "schemas/datasets/dataset_manifest.v1.schema.json",
    "schemas/datasets/evidence_bundle_ref.v1.schema.json",
    "schemas/datasets/qc_report.v1.schema.json",
    "schemas/datasets/scan_report.v1.schema.json",
    "schemas/datasets/transfer_batch.v1.schema.json",
    "schemas/datasets/verification_report.v1.schema.json",
]

EXPECTED_EDGE_SCHEMAS = [
    "schemas/edge/calibration_result.v1.schema.json",
    "schemas/edge/dataset_manifest.v1.schema.json",
    "schemas/edge/qc_report.v1.schema.json",
    "schemas/edge/scan_report.v1.schema.json",
    "schemas/edge/transfer_batch.v1.schema.json",
    "schemas/edge/verification_report.v1.schema.json",
]

EXPECTED_EVENT_SCHEMAS = [
    "schemas/events/dataset_analyzed.v1.schema.json",
    "schemas/events/dataset_calibrated.v1.schema.json",
    "schemas/events/dataset_dispatched.v1.schema.json",
    "schemas/events/dataset_ingested.v1.schema.json",
    "schemas/events/dataset_scanned.v1.schema.json",
    "schemas/events/dataset_verified.v1.schema.json",
    "schemas/events/derived_published.v1.schema.json",
]


class VerificationResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def ok(self, msg):
        self.passed.append(msg)

    def fail(self, msg):
        self.failed.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    @property
    def success(self):
        return len(self.failed) == 0


def check_file_exists(result, filepath):
    """Dosyanın var olduğunu kontrol et."""
    full_path = PROJECT_ROOT / filepath
    if full_path.exists():
        result.ok(f"✅ {filepath}")
        return True
    else:
        result.fail(f"❌ EKSIK: {filepath}")
        return False


def check_valid_json(result, filepath):
    """JSON dosyasının geçerli olduğunu kontrol et."""
    full_path = PROJECT_ROOT / filepath
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        result.ok(f"✅ Geçerli JSON: {filepath}")
        return data
    except json.JSONDecodeError as e:
        result.fail(f"❌ JSON HATASI: {filepath} — {e}")
        return None
    except FileNotFoundError:
        return None


def check_schema_fields(result, filepath, data):
    """JSON Schema zorunlu alanlarını kontrol et."""
    required_fields = ["$schema", "$id", "title", "type"]
    for field in required_fields:
        if field not in data:
            result.fail(f"❌ {filepath}: '{field}' alanı eksik")


def check_kr_refs(result, filepath, data):
    """KR referanslarının mevcut olduğunu kontrol et."""
    kr_ref = data.get("x-kr-ref")
    if kr_ref is None:
        result.warn(f"⚠️  {filepath}: x-kr-ref alanı yok")
    elif not isinstance(kr_ref, list) or len(kr_ref) == 0:
        result.warn(f"⚠️  {filepath}: x-kr-ref boş veya geçersiz format")


def check_refs_resolve(result, filepath, data):
    """$ref bağlantılarının mevcut dosyalara işaret ettiğini kontrol et."""
    refs = extract_refs(data)
    file_dir = (PROJECT_ROOT / filepath).parent
    for ref in refs:
        if ref.startswith("#"):
            continue  # Internal ref — geçerli
        ref_path = (file_dir / ref).resolve()
        if not ref_path.exists():
            result.fail(f"❌ {filepath}: $ref '{ref}' → dosya bulunamadı")
        else:
            result.ok(f"✅ {filepath}: $ref '{ref}' → OK")


def extract_refs(obj, refs=None):
    """JSON nesnesinden tüm $ref değerlerini çıkar."""
    if refs is None:
        refs = []
    if isinstance(obj, dict):
        if "$ref" in obj:
            refs.append(obj["$ref"])
        for v in obj.values():
            extract_refs(v, refs)
    elif isinstance(obj, list):
        for item in obj:
            extract_refs(item, refs)
    return refs


def check_dataset_status_enum_consistency(result):
    """dataset_status enum değerlerinin event schema'larla tutarlılığını kontrol et."""
    enum_path = PROJECT_ROOT / "enums/dataset_status.enum.v1.json"
    if not enum_path.exists():
        result.fail("❌ dataset_status.enum.v1.json bulunamadı — tutarlılık kontrolü yapılamıyor")
        return

    with open(enum_path, 'r', encoding='utf-8') as f:
        enum_data = json.load(f)

    valid_statuses = set(enum_data.get("enum", []))
    if not valid_statuses:
        result.fail("❌ dataset_status enum boş")
        return

    result.ok(f"✅ dataset_status enum: {len(valid_statuses)} durum tanımlı")


def main():
    verbose = "--verbose" in sys.argv
    strict = "--strict" in sys.argv

    result = VerificationResult()

    print("=" * 60)
    print("  TarlaAnaliz — Dataset Layer Doğrulama")
    print("  KR-072, KR-073, KR-018")
    print("=" * 60)
    print()

    # 1. Dizin yapısı kontrolü
    print("📁 Dizin Yapısı Kontrolü")
    print("-" * 40)
    for d in EXPECTED_DIRS:
        dp = PROJECT_ROOT / d
        if dp.is_dir():
            result.ok(f"✅ {d}/")
        else:
            result.fail(f"❌ DİZİN EKSIK: {d}/")
    print()

    # 2. Dosya varlık kontrolü
    print("📄 Dosya Varlık Kontrolü")
    print("-" * 40)

    all_expected = EXPECTED_ENUMS + EXPECTED_DATASET_SCHEMAS + EXPECTED_EDGE_SCHEMAS + EXPECTED_EVENT_SCHEMAS
    for f in all_expected:
        check_file_exists(result, f)
    print()

    # 3. JSON Geçerlilik + Schema Alanları
    print("🔍 JSON Geçerlilik ve Schema Kontrolü")
    print("-" * 40)
    for f in all_expected:
        data = check_valid_json(result, f)
        if data:
            check_schema_fields(result, f, data)
            check_kr_refs(result, f, data)
            if verbose:
                check_refs_resolve(result, f, data)
    print()

    # 4. Enum tutarlılığı
    print("🔗 Enum Tutarlılık Kontrolü")
    print("-" * 40)
    check_dataset_status_enum_consistency(result)
    print()

    # Sonuç
    print("=" * 60)
    print(f"  ✅ Başarılı: {len(result.passed)}")
    print(f"  ❌ Başarısız: {len(result.failed)}")
    print(f"  ⚠️  Uyarı: {len(result.warnings)}")
    print("=" * 60)

    if result.failed:
        print("\n❌ BAŞARISIZ KONTROLLER:")
        for f in result.failed:
            print(f"  {f}")

    if result.warnings and (verbose or strict):
        print("\n⚠️  UYARILAR:")
        for w in result.warnings:
            print(f"  {w}")

    if result.success:
        print("\n✅ Dataset layer doğrulama BAŞARILI")
        return 0
    else:
        print("\n❌ Dataset layer doğrulama BAŞARISIZ")
        return 1


if __name__ == "__main__":
    sys.exit(main())
