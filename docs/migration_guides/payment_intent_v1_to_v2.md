# Migration Guide: PaymentIntent v1 → v2

**Kapsam:** `schemas/platform/payment_intent.v1.schema.json` → `payment_intent.v2.schema.json`  
**Tarih:** 2026-02-24  
**SSOT Uyum:** 1.2.0  
**KR Referans:** KR-033  
**Breaking-change:** EVET — `payment_status.v1.json` + `payment_intent.v1` kullanan tüm consumer'lar etkilenir

---

## Özet: Ne Değişti?

| Alan / Enum | v1 | v2 | Eylem |
|---|---|---|---|
| `status: APPROVED` | Vardı | **KALDIRILDI** | → `PAID` ile değiştir |
| `status: EXPIRED` | Vardı | **KALDIRILDI** | → `CANCELLED` ile değiştir; otomatik expire kaldırıldı |
| `status: REFUNDED` | Yoktu | **EKLENDİ** | v2 yeni durum |
| `receipt_blob_id` | Opsiyonel | **ZORUNLU** alan (null izinli) | Şema'da zorunlu; null geçirilebilir |
| `field_id` | Yoktu | Eklendi (null izinli) | IBAN eşleştirme için |
| `admin_user_id` | Yoktu | Eklendi (null izinli) | Audit log zorunluluğu |
| `rejected_at` | Yoktu | Eklendi (null izinli) | Zaman damgası takibi |
| `refunded_at` | Yoktu | Eklendi (null izinli) | Zaman damgası takibi |
| IBAN dekont kanalı | e-posta | **Uygulama içi yükleme** | `POST /payments/intents/{id}/upload-receipt` |

---

## Adım Adım Migration

### 1. Veritabanı

```sql
-- APPROVED → PAID migration
UPDATE payment_intents
SET status = 'PAID'
WHERE status = 'APPROVED';

-- EXPIRED → CANCELLED migration
-- Not: Gerçek EXPIRED kayıtları iş kararıyla değerlendirilmeli;
-- admin kararıyla CANCELLED yapılabilir.
UPDATE payment_intents
SET status = 'CANCELLED',
    admin_note = 'Auto-migrate: EXPIRED → CANCELLED (SSOT 1.2.0)'
WHERE status = 'EXPIRED';

-- Yeni kolonlar ekle
ALTER TABLE payment_intents
    ADD COLUMN IF NOT EXISTS field_id UUID,
    ADD COLUMN IF NOT EXISTS admin_user_id VARCHAR,
    ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS refunded_at TIMESTAMPTZ;

-- receipt_blob_id zaten varsa NULL constraint'i kaldırma (nullable kalacak)
-- Eğer yoksa ekle:
ALTER TABLE payment_intents
    ADD COLUMN IF NOT EXISTS receipt_blob_id VARCHAR;
```

### 2. Uygulama Kodu

```python
# ÖNCE (v1 - yanlış)
if intent.status == "APPROVED":
    activate_subscription(intent.target_id)

# SONRA (v2 - doğru)
if intent.status == "PAID":
    activate_subscription(intent.target_id)
```

```python
# ÖNCE (v1 - yanlış)
if intent.status == "EXPIRED":
    notify_user("Intent süresi doldu")

# SONRA (v2 - doğru)
# Otomatik expire yoktur. Admin CANCELLED yapar.
# Bu kod bloğunu kaldır.
```

### 3. PaymentStateMachine

APPROVED ve EXPIRED geçişlerini state machine'den kaldır:

```python
# Kaldırılacak geçişler:
# PAYMENT_PENDING → APPROVED  (silindi)
# PAYMENT_PENDING → EXPIRED   (silindi — otomatik expire yok)

# Mevcut kalacak geçişler:
VALID_TRANSITIONS = {
    "PAYMENT_PENDING": ["PAID", "REJECTED", "CANCELLED"],
    "PAID":            ["REFUNDED"],
}
```

### 4. Admin Panel

IBAN_TRANSFER dekont kanalı güncelleme:

```
ÖNCE: "Kullanıcı dekontu odeme@tarlaanaliz.com adresine e-posta ile gönderir"
SONRA: "Kullanıcı dekontu POST /payments/intents/{id}/upload-receipt ile uygulama içinden yükler"
```

Admin eşleştirme akışı değişmedi. Tarla ID üzerinden otomatik eşleştirme korunur.

### 5. Bildirim Şablonları

```
APPROVED durumu kaldırıldı → PAID bildirimini kullan:
"Ödemeniz onaylandı. Talebiniz işleme alındı."

EXPIRED durumu kaldırıldı → bildirim gönderilmez (otomatik expire yok).
Admin CANCELLED yaparsa mevcut CANCELLED bildirimi gönderilir.
```

### 6. API Endpoint Güncellemesi

Yeni endpoint eklendi (önceden yoktu):
```
POST /payments/intents/{id}/upload-receipt
```

Admin endpointleri — `admin_note` zorunluluğu eklendi:
```json
POST /admin/payments/intents/{id}/mark-paid
{ "admin_note": "zorunlu alan" }

POST /admin/payments/intents/{id}/reject
{ "rejection_reason": "zorunlu alan" }
```

---

## Rollback Planı

1. v2 şemasını deploy'dan önce v1 şemasıyla paralel çalıştır (dual-write).
2. `APPROVED`/`EXPIRED` değerleri DB'de `PAID`/`CANCELLED`'a dönüştürüldükten sonra v1 kodu devre dışı bırakılabilir.
3. Rollback gerekeceğinde: DB'deki yeni sütunlar DROP edilmeden, sadece `status` enum'u genişlet (APPROVED/EXPIRED geri ekle).

---

## Doğrulama Testleri

- [ ] `APPROVED` status değeri `validate.py` tarafından reddediliyor
- [ ] `EXPIRED` status değeri `validate.py` tarafından reddediliyor
- [ ] `REFUNDED` sadece `PAID` sonrası geçiş yapılabiliyor (PaymentStateMachine testi)
- [ ] `mark-paid` endpoint'i `admin_note` olmadan `HTTP 422` dönüyor
- [ ] `reject` endpoint'i `rejection_reason` olmadan `HTTP 422` dönüyor
- [ ] `receipt_blob_id` upload endpoint'i çalışıyor (POST /payments/intents/{id}/upload-receipt)
- [ ] DB'de APPROVED/EXPIRED kayıt kalmadı (migration sonrası kontrol)
- [ ] Example JSON'lar (`payment_intent_*.example.json`) v2 şemasına uyuyor

---

## İlgili Dosyalar

- `schemas/platform/payment_intent.v2.schema.json` — yeni şema
- `enums/payment_status.v2.json` — güncel enum
- `enums/payment_method.v1.json` — IBAN açıklaması güncellendi
- `docs/examples/payment_intent_iban_pending.example.json`
- `docs/examples/payment_intent_iban_paid.example.json`
- `docs/examples/payment_intent_creditcard_paid.example.json`
- `docs/ssot/kr_registry.md` — KR-033 normatif metin
