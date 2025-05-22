# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[('app/pagopa.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AS-DynApp',
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
    icon=['pagopa512x512.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AS-DynApp',
)
app = BUNDLE(
    coll,
    name='AS-DynApp.app',
    icon='pagopa512x512.icns',
    bundle_identifier='it.pagopa.assistenza.as-dynapp',
    info_plist={
        'CFBundleName': 'AS-DynApp',
        'CFBundleDisplayName': 'AS-DynApp',
        'CFBundleGetInfoString': 'AS-DynApp 2.1.0047',
        'CFBundleShortVersionString': '2.1.0047',
        'CFBundleVersion': '2.1.0047',
        'CFBundleIdentifier': 'it.pagopa.assistenza.as-dynapp',
    }
)
