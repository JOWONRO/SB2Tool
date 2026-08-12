# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['SB2Tool.py'],
             # 절대경로를 박아두면 다른 PC에서 빌드할 때 깨진다.
             # (5.0 전에는 'D:\coding\git\SB2Tool'로 고정돼 있었다)
             pathex=[],
             binaries=[],
             # 아이콘을 번들에 포함시킨다. 예전에는 datas가 비어 있어서
             # 빌드 후 dist\SB2Tool\icons\ 에 손으로 복사해야 했다.
             datas=[('icons', 'icons')],
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
          icon='icons/new_logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SB2Tool')
