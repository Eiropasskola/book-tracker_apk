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
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow,requests,certifi,urllib3,charset-normalizer,idna

# Orientācija un izskats
orientation = portrait
fullscreen = 0

# Atļaujas
android.permissions = INTERNET

# Android API versijas - SVARĪGI: konkrētas versijas, ko Buildozer Action atbalsta out-of-the-box
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Arhitektūras - tikai arm64-v8a, lai būve būtu 2x ātrāka.
android.archs = arm64-v8a

# Ļauj backup
android.allow_backup = True

# Pieņem licences automātiski
android.accept_sdk_license = True

# Bootstrap
p4a.bootstrap = sdl2

# p4a fork - jaunākais stabilais
p4a.branch = master

[buildozer]

log_level = 2
warn_on_root = 0
