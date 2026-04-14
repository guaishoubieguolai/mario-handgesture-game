# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs, collect_data_files

# 获取当前Python环境的site-packages路径
site_packages = None
for path in sys.path:
    if 'site-packages' in path:
        site_packages = path
        break

print(f"Site-packages path: {site_packages}")

# ========== 收集所有必需的数据文件 ==========
datas = [('resources', 'resources'), ('src', 'src')]
binaries = []

# ========== 关键：手动收集nes_py的.pyd文件 ==========
print("\nCollecting nes_py library files...")
nes_py_path = os.path.join(site_packages, 'nes_py') if site_packages else None

if nes_py_path and os.path.exists(nes_py_path):
    # 查找所有.pyd文件
    import glob as glob_module
    pyd_files = glob_module.glob(os.path.join(nes_py_path, '*.pyd'))
    
    for pyd_file in pyd_files:
        # 将.pyd文件放到nes_py目录下
        binaries.append((pyd_file, 'nes_py'))
        print(f"  [OK] Collecting .pyd file: {os.path.basename(pyd_file)}")
    
    # 收集nes_py的所有其他文件
    try:
        nes_all = collect_all('nes_py')
        # datas: (源路径, 目标路径)
        for data_item in nes_all[0]:
            # 确保数据文件放到正确的位置
            datas.append(data_item)
        # binaries: (源路径, 目标路径)
        for binary_item in nes_all[1]:
            binaries.append(binary_item)
        print(f"  [OK] nes_py data files: {len(nes_all[0])}")
        print(f"  [OK] nes_py binary files: {len(nes_all[1])}")
    except Exception as e:
        print(f"  [WARN] collect_all failed: {e}")
        # 回退：手动添加所有文件
        for root, dirs, files in os.walk(nes_py_path):
            for f in files:
                if not f.endswith(('.pyd', '.pyc')):
                    src = os.path.join(root, f)
                    rel_dir = os.path.relpath(root, nes_py_path)
                    dst = os.path.join('nes_py', rel_dir) if rel_dir != '.' else 'nes_py'
                    datas.append((src, dst))
else:
    print("  [WARN] nes_py path not found, trying collect_dynamic_libs")
    try:
        nes_binaries = collect_dynamic_libs('nes_py')
        binaries.extend(nes_binaries)
        print(f"  [OK] nes_py dynamic libs: {len(nes_binaries)}")
    except Exception as e:
        print(f"  [ERROR] nes_py dynamic libs failed: {e}")

# ========== 收集gym_super_mario_bros ==========
print("\nCollecting gym_super_mario_bros...")
try:
    mario_all = collect_all('gym_super_mario_bros')
    datas.extend(mario_all[0])
    binaries.extend(mario_all[1])
    print(f"  [OK] gym_super_mario_bros: {len(mario_all[0])} data files")
except Exception as e:
    print(f"  [WARN] gym_super_mario_bros failed: {e}")
    # 手动收集ROM文件
    mario_path = os.path.join(site_packages, 'gym_super_mario_bros') if site_packages else None
    if mario_path and os.path.exists(mario_path):
        for root, dirs, files in os.walk(mario_path):
            for f in files:
                if f.endswith(('.nes', '.txt')):
                    src = os.path.join(root, f)
                    rel_dir = os.path.relpath(root, mario_path)
                    dst = os.path.join('gym_super_mario_bros', rel_dir) if rel_dir != '.' else 'gym_super_mario_bros'
                    datas.append((src, dst))
                    print(f"    [OK] {f}")

# ========== 收集pygame和pyglet ==========
print("\nCollecting pygame and pyglet...")
try:
    pygame_data = collect_data_files('pygame')
    datas.extend(pygame_data)
    print(f"  [OK] pygame data files: {len(pygame_data)}")
except Exception as e:
    print(f"  [WARN] pygame failed: {e}")

try:
    pyglet_data = collect_data_files('pyglet')
    datas.extend(pyglet_data)
    print(f"  [OK] pyglet data files: {len(pyglet_data)}")
except Exception as e:
    print(f"  [WARN] pyglet failed: {e}")

# ========== 定义所有隐式导入 ==========
hiddenimports = [
    # 主要依赖
    'tensorflow',
    'cv2',
    'numpy',
    
    # 游戏环境
    'gym',
    'gym_super_mario_bros',
    'nes_py',
    'nes_py.nes_env',
    'nes_py.wrappers',
    'nes_py.wrappers.joypad_space',
    
    # 图形和音频
    'pygame',
    'pyglet',
    'PIL',
    
    # Windows特定
    'win32gui',
    'win32con',
    'pywintypes',
    'pythoncom',
    
    # 多进程
    'multiprocessing',
    'multiprocessing.spawn',
    
    # 项目模块
    'src.mario_game',
    'src.utils',
    'src.config',
]

print("\n" + "="*50)
print("Package Configuration Summary")
print("="*50)
print(f"Total data files: {len(datas)}")
print(f"Total binary files: {len(binaries)}")
print(f"Total hidden imports: {len(hiddenimports)}")
print("="*50 + "\n")

# 使用自定义hooks目录
hookspath = ['build_tools']
runtime_hooks = ['build_tools/hook_nes_py_runtime.py']

a = Analysis(
    ['mario.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=hookspath,
    hooksconfig={},
    runtime_hooks=runtime_hooks,
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MarioHandGesture',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 调试模式：显示控制台输出，方便排查问题
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
