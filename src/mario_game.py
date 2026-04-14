"""
独立的马里奥游戏进程模块
这个文件只被子进程使用，不包含TensorFlow等重依赖
"""
import numpy as np
import cv2
import ctypes
from time import sleep
from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros
from gym_super_mario_bros.actions import COMPLEX_MOVEMENT


def run_mario_game(v, lock):
    """运行马里奥游戏（子进程专用）"""
    # 创建环境并解包以避免API冲突
    env = gym_super_mario_bros.make('SuperMarioBros-1-1-v0')
    
    # 解包获取原始环境
    while hasattr(env, 'env'):
        env = env.env
    env = JoypadSpace(env, COMPLEX_MOVEMENT)
    
    done = True

    # 获取屏幕分辨率
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # 创建全屏窗口
    cv2.namedWindow("Super Mario Bros", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Super Mario Bros", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    try:
        while True:
            if done:
                env.reset()
                with lock:
                    v.value = 0
            
            with lock:
                u = v.value
            
            _, _, done, _ = env.step(u)

            # 渲染帧并调整为全屏
            frame = env.render(mode='rgb_array')
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame_resized = cv2.resize(frame_bgr, (screen_width, screen_height))
            cv2.imshow("Super Mario Bros", frame_resized)

            # 按下 'q' 键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            sleep(0.01)
    finally:
        env.close()
        cv2.destroyAllWindows()
