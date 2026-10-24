#!/bin/bash

PROJECT_PATH="$(pwd)"
DESKTOP_FILE="$HOME/.local/share/applications/mst_studio.desktop"
MIME_FILE="$HOME/.local/share/mime/packages/application-x-mst.xml"

# 1. Özel MIME Türü Tanımlama (.mst)
mkdir -p "$HOME/.local/share/mime/packages"
cat << XML > "$MIME_FILE"
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-mst">
    <comment>MST Studio Proje Dosyasi</comment>
    <glob pattern="*.mst"/>
    <icon name="document-open"/>
  </mime-type>
</mime-info>
XML

# 2. Masaüstü Başlatıcısı Kaydı (%f parametresi ile dosya yolunu aktarır)
mkdir -p "$HOME/.local/share/applications"
cat << DESK > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Name=MST Studio
Comment=Professional Visual Application Builder
Exec=python3 "$PROJECT_PATH/main.py" %f
Path=$PROJECT_PATH
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Development;IDE;
MimeType=application/x-mst;
DESK

# 3. MIME Veritabanı ve Varsayılan Uygulama Güncellemesi
update-mime-database "$HOME/.local/share/mime" 2>/dev/null || true
xdg-mime default mst_studio.desktop application/x-mst

echo "🎉 .mst dosya ilişkilendirmesi başarıyla tamamlandı!"
