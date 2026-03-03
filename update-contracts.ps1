# TarlaAnaliz Contracts — SSOT 1.2.0 Update Script
# Bu scripti repo klasörünün İÇİNDE çalıştır:
#   cd C:\Users\DELL\Desktop\tarlaanaliz-contract_
#   .\update-contracts.ps1

Write-Host "=== TarlaAnaliz Contracts SSOT 1.2.0 Guncelleme ===" -ForegroundColor Cyan
Write-Host ""

# ---- ADIM 1: Eski dosyalari sil ----
Write-Host "[1/4] Eski dosyalar siliniyor..." -ForegroundColor Yellow

$silinecekler = @(
    "docs\checklists\PR_GATE_CHECKLIST.md",
    "docs\checklists\CI_GATE_CHECKLIST.md",
    "docs\checklists\RELEASE_GATE_CHECKLIST.md",
    "docs\examples\payment_intent.example.json",
    "contracts_UPDATED_2026-02-15.md",
    "tarlaanaliz-contracts_dizin_aciklamalari_UPDATED_2026-02-15.md"
)

# Türkçe karakter içeren dosya için ayrı
$turkce_dosya = Get-ChildItem -Filter "*zet_dizin*" -ErrorAction SilentlyContinue
if ($turkce_dosya) {
    Remove-Item -Force $turkce_dosya.FullName
    Write-Host "  Silindi: $($turkce_dosya.Name)" -ForegroundColor Red
}

foreach ($dosya in $silinecekler) {
    if (Test-Path $dosya) {
        Remove-Item -Force $dosya
        Write-Host "  Silindi: $dosya" -ForegroundColor Red
    } else {
        Write-Host "  Zaten yok: $dosya" -ForegroundColor DarkGray
    }
}

# ---- ADIM 2: ZIP'i bul ve ac ----
Write-Host ""
Write-Host "[2/4] ZIP aciliyor..." -ForegroundColor Yellow

$zipYol = $null
$aramaPaths = @(
    "$env:USERPROFILE\Downloads\tarlaanaliz-update.zip",
    "$env:USERPROFILE\Downloads\tarlaanaliz-update (1).zip",
    "$env:USERPROFILE\Downloads\tarlaanaliz-update (2).zip",
    ".\tarlaanaliz-update.zip"
)

foreach ($p in $aramaPaths) {
    if (Test-Path $p) {
        $zipYol = $p
        break
    }
}

if (-not $zipYol) {
    Write-Host "  HATA: tarlaanaliz-update.zip bulunamadi!" -ForegroundColor Red
    Write-Host "  Dosyayi Claude'dan indirip Downloads klasorune koyun." -ForegroundColor Red
    Write-Host "  Veya bu script'in bulundugu klasore kopyalayin." -ForegroundColor Red
    exit 1
}

Write-Host "  ZIP bulundu: $zipYol" -ForegroundColor Green

# Geçici klasöre aç
$gecici = "$env:TEMP\tarlaanaliz-update-temp"
if (Test-Path $gecici) { Remove-Item -Recurse -Force $gecici }
Expand-Archive -Path $zipYol -DestinationPath $gecici -Force

# ---- ADIM 3: Dosyalari kopyala ----
Write-Host ""
Write-Host "[3/4] Dosyalar kopyalaniyor..." -ForegroundColor Yellow

# Recursive copy — üstüne yazar
function Copy-UpdateFiles($kaynak, $hedef) {
    Get-ChildItem -Path $kaynak -Recurse -File | ForEach-Object {
        $relPath = $_.FullName.Substring($kaynak.Length + 1)
        $hedefDosya = Join-Path $hedef $relPath
        $hedefKlasor = Split-Path $hedefDosya -Parent
        
        if (-not (Test-Path $hedefKlasor)) {
            New-Item -ItemType Directory -Path $hedefKlasor -Force | Out-Null
        }
        
        Copy-Item -Path $_.FullName -Destination $hedefDosya -Force
        
        if (Test-Path (Join-Path $hedef $relPath.Replace($_.Name, ""))) {
            Write-Host "  Guncellendi: $relPath" -ForegroundColor Green
        }
    }
}

Copy-UpdateFiles $gecici (Get-Location).Path

# Temizlik
Remove-Item -Recurse -Force $gecici

# ---- ADIM 4: Sonuc ----
Write-Host ""
Write-Host "[4/4] Kontrol..." -ForegroundColor Yellow
Write-Host ""

$kontrol = @(
    "enums\drone_type.enum.v1.json",
    "enums\payment_status.v1.json",
    "enums\payment_status.v2.json",
    "enums\payment_method.v1.json",
    "schemas\platform\payment_intent.v2.schema.json",
    "schemas\platform\payment_intent.v1.schema.json",
    "schemas\core\mission.v1.schema.json",
    "schemas\edge\intake_manifest.v1.schema.json",
    "docs\examples\payment_intent_creditcard_paid.example.json",
    "docs\examples\payment_intent_iban_paid.example.json",
    "docs\examples\payment_intent_iban_pending.example.json",
    "docs\migration_guides\payment_intent_v1_to_v2.md",
    "docs\checklists\SDLC_GATES.md",
    "ssot\kr_registry.md",
    "ssot\contracts_ssot.md",
    "ssot\GOVERNANCE_PACK_v1_0_1.md",
    "CHANGELOG.md",
    "CONTRACTS_VERSION.md"
)

$tamam = 0
$eksik = 0

foreach ($d in $kontrol) {
    if (Test-Path $d) {
        Write-Host "  OK  $d" -ForegroundColor Green
        $tamam++
    } else {
        Write-Host "  EKSIK  $d" -ForegroundColor Red
        $eksik++
    }
}

Write-Host ""
Write-Host "=== SONUC: $tamam/$($kontrol.Count) dosya tamam ===" -ForegroundColor Cyan

if ($eksik -eq 0) {
    Write-Host ""
    Write-Host "Simdi git komutlarini calistir:" -ForegroundColor White
    Write-Host '  git add -A' -ForegroundColor White
    Write-Host '  git status' -ForegroundColor White
    Write-Host '  git commit -m "feat(contracts): SSOT 1.2.0 uyum - v2.0.0"' -ForegroundColor White
    Write-Host '  git push -u origin ssot-v1.2.0-update' -ForegroundColor White
}
