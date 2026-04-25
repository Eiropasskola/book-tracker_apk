# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specifikācijas fails Grāmatu izsekotājam.

SVARIGI: nelietojam collect_all('kivy') jo tas neizdod ar PyInstaller 6.x
un Kivy 2.3 uz Python 3.12. Tā vietā izmantojam oficialo Kivy hook,
kas tiek importēts ar 'from kivy_deps import sdl2, glew, angle'.
"""
import os
from PyInstaller.utils.hooks import collect_data_files, collect_all
from kivy_deps import sdl2, glew, angle

block_cipher = None

# ---------- Datu faili ----------
datas = []

# 1. .kv izkārtojumu faili
for kv_file in os.listdir('kv'):
    if kv_file.endswith('.kv'):
        datas.append((os.path.join('kv', kv_file), 'kv'))

# 2. Assets (ja ir ikona)
if os.path.isdir('assets'):
    datas.append(('assets', 'assets'))

# 3. KivyMD - viss paketes saturs (ikonas, fonti, default.kv)
# KivyMD strādā labi ar collect_all, tikai Kivy pati ne
try:
    kivymd_datas, kivymd_binaries, kivymd_hiddenimports = collect_all('kivymd')
    datas += kivymd_datas
except Exception as e:
    print(f'[spec] KivyMD collect_all kluda: {e}')
    kivymd_datas = []
    kivymd_binaries = []
    kivymd_hiddenimports = []

# 4. Matplotlib - DejaVu Sans fonts (mūsu latviešu fonts!)
try:
    mpl_datas = collect_data_files('matplotlib', subdir='mpl-data')
    datas += mpl_datas
except Exception as e:
    print(f'[spec] Matplotlib collect_data_files kluda: {e}')

# 5. Pillow datu faili
try:
    pil_datas = collect_data_files('PIL')
    datas += pil_datas
except Exception:
    pass

# ---------- Slēptās atkarības ----------
hiddenimports = [
    # Kivy core - manuāli, jo collect_all nedarbojas
    'kivy',
    'kivy.app',
    'kivy.uix',
    'kivy.uix.widget',
    'kivy.uix.boxlayout',
    'kivy.uix.floatlayout',
    'kivy.uix.screenmanager',
    'kivy.uix.scrollview',
    'kivy.uix.image',
    'kivy.uix.label',
    'kivy.uix.button',
    'kivy.uix.textinput',
    'kivy.lang',
    'kivy.lang.builder',
    'kivy.config',
    'kivy.clock',
    'kivy.properties',
    'kivy.graphics',
    'kivy.metrics',
    'kivy.core',
    'kivy.core.text',
    'kivy.core.text.text_sdl2',
    'kivy.core.image',
    'kivy.core.image.img_sdl2',
    'kivy.core.image.img_pil',
    'kivy.core.window',
    'kivy.core.window.window_sdl2',
    'kivy.core.audio',
    'kivy.core.video',
    'kivy.core.clipboard',
    'kivy.core.clipboard.clipboard_winctypes',
    # KivyMD
    'kivymd',
    'kivymd.app',
    'kivymd.uix',
    'kivymd.uix.boxlayout',
    'kivymd.uix.button',
    'kivymd.uix.card',
    'kivymd.uix.dialog',
    'kivymd.uix.fitimage',
    'kivymd.uix.label',
    'kivymd.uix.menu',
    'kivymd.uix.pickers',
    'kivymd.uix.progressbar',
    'kivymd.uix.screen',
    'kivymd.uix.selectioncontrol',
    'kivymd.uix.textfield',
    'kivymd.uix.toolbar',
    # Matplotlib
    'matplotlib',
    'matplotlib.backends',
    'matplotlib.backends.backend_agg',
    # Citi
    'requests',
    'urllib3',
    'PIL',
    'PIL.Image',
    'sqlite3',
] + kivymd_hiddenimports

# ---------- Bināri faili ----------
# Kivy SDL2, Glew, Angle - šos savāc kivy_deps
binaries = []
binaries += kivymd_binaries

# kivy_deps - obligāti priekš Kivy darbības Windows
sdl2_glew_bins = [Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + angle.dep_bins)]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *sdl2_glew_bins,  # SVARIGI: SDL2/Glew/Angle bibliotēkas
    [],
    name='BookTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = bez melnā komandrindas loga
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
