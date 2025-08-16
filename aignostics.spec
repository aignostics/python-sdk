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
    optimize=2 if platform.system() == "Darwin" else 0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')], # https://github.com/numpy/numpy/issues/13248
    exclude_binaries=True,
    name='aignostics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True if platform.system() == "Darwin" else False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True if platform.system() == "Darwin" else False,
    upx=True,
    upx_exclude=[],
    name='aignostics',
)
app = BUNDLE(
    coll,
    name='aignostics.app',
    icon='logo.ico',
    bundle_identifier='com.aignostics.launchpad',
    version='0.2.146',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': []
    },
)
