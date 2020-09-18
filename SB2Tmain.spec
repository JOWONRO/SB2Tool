# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['SB2Tmain.py'],
             pathex=['D:\\coding\\git\\SB2Tool'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PIL', 'pandas', 'numpy', 'tcl', 'scipy', 'opencv-python', 'cv2'],
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
          name='SB2Tool',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='D:\\coding\\git\\SB2Tool\\favicon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SB2Tool')