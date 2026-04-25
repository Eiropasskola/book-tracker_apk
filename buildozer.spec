[app]

# Aplikācijas pamatinformācija
title = Gramatu izsekotajs
package.name = booktracker
package.domain = lv.konst.booktracker

# Avota faili
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json
source.include_patterns = assets/*,assets/fonts/*,kv/*,core/*,screens/*
source.exclude_dirs = tests,bin,venv,build,dist,__pycache__,.buildozer
source.exclude_patterns = license,books.db,*.spec,*.bat,*.zip

# Versija
version = 1.0.0

# Atkarības - bez matplotlib! Grafikus zīmējam ar Pillow.
# python3, kivy ir obligāti pirmie.
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow,requests,certifi,urllib3,charset-normalizer,idna

# Orientācija un izskats
orientation = portrait
fullscreen = 0

# Ikona un splash screen (nedefinēts - var pievienot vēlāk)
# icon.filename = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/presplash.png

# Atļaujas
android.permissions = INTERNET

# Android API versijas
android.api = 34
android.minapi = 21
android.ndk_api = 21

# Arhitektūras - sākam tikai ar arm64-v8a, lai būve būtu ātrāka.
# Vēlāk vari pievienot armeabi-v7a (vecākiem tālruņiem), bet tas dubultos būves laiku.
android.archs = arm64-v8a

# Ļauj backup
android.allow_backup = True

# Pieņem licences automātiski (vajadzīgs CI vidē)
android.accept_sdk_license = True

# Bootstrap - kā kompilēt
p4a.bootstrap = sdl2

[buildozer]

# Logu līmenis (2 = INFO, kas ir piemērots CI)
log_level = 2

# Brīdinājums uz root - izslēgts CI vidē
warn_on_root = 0
