# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import copy_metadata

# Build via make dist_native

# START INJECTED
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
# END INJECTED

import platform

datas = []
binaries = []
hiddenimports = []

# core
hiddenimports += ['pythonnet']
datas += copy_metadata('aignostics', recursive=False)
tmp_ret = collect_all('aignostics')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# layer gui
datas += collect_data_files('nicegui')

# module platform
datas += collect_data_files('rfc3987_syntax')

# module wsi
binaries += collect_dynamic_libs('openslide_bin')

# module dataset
datas += collect_data_files('idc_index_data')
datas += collect_data_files('s5cmd')

# module notebook
datas += collect_data_files('marimo', subdir='_static')
hiddenimports += ['IPython']
tmp_ret = collect_all('cloudpathlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pymdownx')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['src/aignostics.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2 if platform.system() == "Darwin" else 1,
)

pyz = PYZ(a.pure)

# Platform-specific configuration
is_windows = platform.system() == "Windows"
is_darwin = platform.system() == "Darwin"
use_splash = is_windows  # Splash only on Windows (disabled on Linux for Python 3.14 compatibility)
use_strip = is_darwin    # Strip symbols only on macOS

# Splash screen (Windows only)
splash = None
if use_splash:
    splash = Splash('logo.png',
        binaries=a.binaries,
        datas=a.datas,
        text_pos=(170, 400),
        text_size=12,
        text_color='white',
        text_default='Loading application ...'
    )

# Build EXE arguments dynamically
exe_args = [pyz]
if splash:
    exe_args.append(splash)
exe_args.extend([
    a.scripts,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],  # https://github.com/numpy/numpy/issues/13248
])

exe = EXE(
    *exe_args,
    exclude_binaries=True,
    name='aignostics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=use_strip,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)

# Build COLLECT arguments dynamically
collect_args = [exe]
if splash:
    collect_args.append(splash.binaries)
collect_args.extend([a.binaries, a.datas])

coll = COLLECT(
    *collect_args,
    strip=use_strip,
    upx=True,
    upx_exclude=[],
    name='aignostics',
)

# macOS app bundle
if is_darwin:
    app = BUNDLE(
        coll,
        name='aignostics.app',
        icon='logo.ico',
        bundle_identifier='com.aignostics.launchpad',
        version='1.0.2',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDocumentTypes': []
        },
    )
