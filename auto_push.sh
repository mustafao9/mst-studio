#!/bin/bash
# MST Studio Automatic GitHub Push Script

MESSAGE=${1:-"update: automatic sync from MST Studio"}

echo "📦 Otomatik Git Gönderimi Başlatılıyor..."
git add .
git commit -m "$MESSAGE"
git push origin main --tags

echo "🎉 GitHub Senkronizasyonu Başarıyla Tamamlandı!"
