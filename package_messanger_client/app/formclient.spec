# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['formclient.py'],
             pathex=['/home/groofi/Work_Git/PyQt/package_messanger_client'],
             binaries=[],
             datas=[('log', 'log'), ('clientcls.py', 'clientcls'), ('storagesqlite.py', 'storagesqlite'), ('service.py', 'service')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='formclient',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='formclient')