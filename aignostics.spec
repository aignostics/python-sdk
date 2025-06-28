# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

# Build
## uv run pyi-makespec --windowed --onedir --copy-metadata="aignostics" --collect-all="nicegui" --collect-all="aignostics" --collect-data="idc_index_data" --name="aignostics" --osx-bundle-identifier com.aignostics.launchpad --icon logo.ico --hidden-import pythonnet src/aignostics.py
## Inject
## make dist_native

# START INJECTED
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
# END INJECTED

datas = []
binaries = []
hiddenimports = ['pythonnet']
datas += collect_data_files('idc_index_data')
datas += copy_metadata('aignostics', recursive=False)
tmp_ret = collect_all('nicegui')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('aignostics')
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
    noarchive=True,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='aignostics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
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
    strip=True,
    upx=True,
    upx_exclude=[],
    name='aignostics',
)
app = BUNDLE(
    coll,
    name='aignostics.app',
    icon='logo.ico',
    bundle_identifier='com.aignostics.launchpad',
    version='0.2.87',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': []
    },
)
