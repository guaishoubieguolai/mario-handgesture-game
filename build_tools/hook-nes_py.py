"""
PyInstaller hook for nes_py
"""
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs
import os
import glob

# 收集所有nes_py文件
datas, binaries, hiddenimports = collect_all('nes_py')

# 额外确保.pyd文件被收集为二进制文件（放到nes_py目录）
try:
    import nes_py
    nes_path = os.path.dirname(nes_py.__file__)
    # 查找所有.pyd文件
    pyd_files = glob.glob(os.path.join(nes_path, '*.pyd'))
    for pyd in pyd_files:
        binaries.append((pyd, 'nes_py'))
except:
    pass

# 添加隐式导入
hiddenimports += [
    'nes_py.nes_env',
    'nes_py.wrappers',
    'nes_py.wrappers.joypad_space',
    'nes_py._rom',
    'nes_py._image_viewer',
]
