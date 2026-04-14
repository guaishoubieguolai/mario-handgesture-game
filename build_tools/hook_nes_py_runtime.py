"""
PyInstaller runtime hook for nes_py
确保nes_py库能找到.pyd文件
"""
import sys
import os

# 在导入nes_py之前，确保临时目录在搜索路径中
if hasattr(sys, '_MEIPASS'):
    # PyInstaller打包后的临时目录
    temp_dir = sys._MEIPASS
    # 确保nes_py目录存在
    nes_py_dir = os.path.join(temp_dir, 'nes_py')
    if os.path.exists(nes_py_dir):
        # 将nes_py目录添加到DLL搜索路径
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(nes_py_dir)
            except:
                pass
        # Windows: 添加到PATH
        os.environ['PATH'] = nes_py_dir + os.pathsep + os.environ.get('PATH', '')
