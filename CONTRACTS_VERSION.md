# CONTRACTS_VERSION

```
semver=2.0.0
created_at=2026-02-24T00:00:00Z
ssot_version=1.2.0
breaking_change=true
breaking_change_summary=payment_status APPROVED+EXPIRED kaldırıldı; IBAN dekont kanalı in-app upload; drone_type enum drone-agnostik; payment_intent.v2 yeni zorunlu alanlar
migration_guide=docs/migration_guides/payment_intent_v1_to_v2.md
```

## Değişiklik Özeti

Bu versiyon SSOT 1.2.0 ile tam uyumludur.

### Breaking Changes (MAJOR bump gerekçesi)

1. `payment_status` enum: `APPROVED` ve `EXPIRED` değerleri kaldırıldı
2. `payment_method` IBAN_TRANSFER: dekont kanalı e-posta → uygulama içi upload
3. `payment_intent.v2`: `admin_note` ve `rejection_reason` zorunlu admin alanları eklendi

### Consumer Repo Güncelleme Talimatı

Platform, Edge ve Worker repo'larında `CONTRACTS_VERSION.md` aşağıdaki değerle güncellenmelidir:

```
contracts_version=2.0.0
contracts_sha256=<tools/pin_version.py ile hesaplanacak>
```

## SHA-256

> Bu değer `tools/pin_version.py` ile hesaplanır ve otomatik güncellenir.
> Manuel değiştirmeyin.

```
sha256=PENDING_CALCULATION
```

## İlişki

- platform/CONTRACTS_VERSION.md → Bu dosyadaki değeri kopyalar
- edge/CONTRACTS_VERSION.md → Bu dosyadaki değeri kopyalar  
- worker/CONTRACTS_VERSION.md → Bu dosyadaki değeri kopyalar
- tools/pin_version.py → Bu dosyayı otomatik günceller
