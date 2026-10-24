#!/bin/bash
# MST Studio Automated Release & Semantic Versioning Script

VERSION_FILE="version.json"

# Eğer version.json yoksa varsayılan 1.0.0 ile başla
if [ ! -f "$VERSION_FILE" ]; then
    echo '{"major": 1, "minor": 0, "patch": 0}' > "$VERSION_FILE"
fi

# Mevcut Sürüm Değerlerini Okuma
MAJOR=$(python3 -c "import json; print(json.load(open('$VERSION_FILE'))['major'])")
MINOR=$(python3 -c "import json; print(json.load(open('$VERSION_FILE'))['minor'])")
PATCH=$(python3 -c "import json; print(json.load(open('$VERSION_FILE'))['patch'])")

CURRENT_VERSION="$MAJOR.$MINOR.$PATCH"

echo "======================================================"
echo "🚀 MST Studio Otomatik Sürüm & Gönderim Sihirbazı"
echo "📌 Mevcut Sürüm: v$CURRENT_VERSION"
echo "======================================================"
echo "Değişiklik Türünü Seçin:"
echo " 1) Yama / Hata Düzeltmesi (Patch)  --> v$MAJOR.$MINOR.$((PATCH+1))"
echo " 2) Genel Özellik / Yenilik (Minor) --> v$MAJOR.$((MINOR+1)).0"
echo " 3) Köklü Mantık Değişikliği (Major) --> v$((MAJOR+1)).0.0"
echo " 4) Sürüm Değiştirmeden Gönder (Aynı Sürüm)"
echo "======================================================"
read -p "Seçiminiz (1-4): " CHOICE

case $CHOICE in
    1)
        PATCH=$((PATCH+1))
        ;;
    2)
        MINOR=$((MINOR+1))
        PATCH=0
        ;;
    3)
        MAJOR=$((MAJOR+1))
        MINOR=0
        PATCH=0
        ;;
    4)
        echo "ℹ️ Sürüm numarası artırılmadan gönderiliyor..."
        ;;
    *)
        echo "❌ Geçersiz seçim! İşlem iptal edildi."
        exit 1
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

# Sürüm Dosyasını Güncelleme
echo "{\"major\": $MAJOR, \"minor\": $MINOR, \"patch\": $PATCH}" > "$VERSION_FILE"

read -p "📝 Değişiklik Özeti (Commit Mesajı): " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="update: MST Studio v$NEW_VERSION release"
fi

echo "🧹 1. Geçici Derleme Kalıntıları Temizleniyor..."
rm -rf build/ dist/ *.spec __pycache__ ui/__pycache__ core/__pycache__ preview/__pycache__

echo "📦 2. Dosyalar Hazırlanıyor ve Endeksleniyor..."
git add .

echo "💾 3. Commit Oluşturuluyor [v$NEW_VERSION]..."
git commit -m "release: v$NEW_VERSION - $COMMIT_MSG"

if [ "$CHOICE" != "4" ]; then
    echo "🏷️ 4. Yeni Git Etiketi (Tag) Ekleme: v$NEW_VERSION..."
    git tag -a "v$NEW_VERSION" -m "MST Studio Version $NEW_VERSION"
fi

echo "⬆️ 5. GitHub'a Güvenli Şekilde Gönderiliyor..."
git push origin main --tags

echo "======================================================"
echo "🎉 TEBRİKLER! MST Studio v$NEW_VERSION GitHub'a Yüklendi."
echo "🔗 Repository: https://github.com/mustafao9/mst-studio"
echo "======================================================"
