import sys
import os
import warnings

# ========== 抑制警告信息 ==========
# 抑制TensorFlow警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 只显示ERROR
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # 关闭oneDNN优化警告

# 抑制gym和其他库的警告
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# ========== 关键：检测multiprocessing子进程 ==========
_is_child_process = any('--multiprocessing-fork' in arg or '--multiprocessing' in arg for arg in sys.argv)

if _is_child_process:
    # 子进程：只导入必需模块
    import multiprocessing
    multiprocessing.freeze_support()
    # 导入游戏模块（不含TensorFlow）
    from src.mario_game import run_mario_game
    import cv2
    import numpy as np
    # 子进程到此结束，等待被调用
else:
    # 主进程：导入所有模块（包括TensorFlow）
    import tensorflow as tf
    import cv2
    import multiprocessing as _mp
    import numpy as np
    from src.utils import load_graph, detect_hands, predict
    from src.config import ORANGE, RED, GREEN
    from src.mario_game import run_mario_game  # 使用独立的游戏模块
    import win32gui
    import win32con



# 获取打包后的资源路径
def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容打包和开发环境）"""
    try:
        # PyInstaller打包后的临时目录
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 主进程才定义TensorFlow flags和主函数
if not _is_child_process:
    tf.compat.v1.flags.DEFINE_integer("width", 0, "Screen width (0 for auto-detect max resolution)")
    tf.compat.v1.flags.DEFINE_integer("height", 0, "Screen height (0 for auto-detect max resolution)")
    tf.compat.v1.flags.DEFINE_float("threshold", 0.6, "Threshold for score")
    tf.compat.v1.flags.DEFINE_float("alpha", 0.3, "Transparent level")
    tf.compat.v1.flags.DEFINE_string("pre_trained_model_path", "src/pretrained_model.pb", "Path to pre-trained model")
    tf.compat.v1.flags.DEFINE_integer("camera_id", 0, "Camera device ID (default: 0)")

    FLAGS = tf.compat.v1.flags.FLAGS


def try_open_camera(max_attempts=3):
    """自动尝试打开摄像头（依次尝试 0, 1, 2...）
    
    策略：
    1. 先使用常规方法（默认后端）- 兼容大多数电脑
    2. 失败后使用CAP_DSHOW后端 - 兼容联想Y7000等特殊设备
    
    Args:
        max_attempts: 最大尝试数量（默认3个）
    
    Returns:
        (cap, camera_id) 或 (None, -1)
    """
    print("正在搜索可用摄像头...")
    
    for camera_id in range(max_attempts):
        print(f"尝试摄像头 {camera_id}...", end=" ")
        
        # 策略1：先尝试常规方法（默认后端，适用于大多数电脑）
        cap = cv2.VideoCapture(camera_id)
        
        if cap.isOpened():
            ret, frame = cap.read()
            
            if ret and frame is not None:
                brightness = frame.mean()
                
                if brightness > 10:
                    print(f"[OK] 成功！亮度={brightness:.1f} (默认后端)")
                    return cap, camera_id
                else:
                    print(f"[INFO] 默认后端画面全黑，尝试CAP_DSHOW...")
                    cap.release()
                    
                    # 策略2：尝试CAP_DSHOW后端（兼容Y7000等设备）
                    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
                    
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.mean() > 10:
                            brightness = frame.mean()
                            print(f"[OK] 成功！亮度={brightness:.1f} (CAP_DSHOW后端)")
                            return cap, camera_id
                        else:
                            print(f"[FAIL] CAP_DSHOW也不可用")
                            cap.release()
            else:
                print("[FAIL] 无法读取帧")
                cap.release()
        else:
            print("[FAIL] 无法打开")
    
    return None, -1


def get_camera_max_resolution(cap, camera_id):
    """安全地获取摄像头支持的最大分辨率"""
    # 获取默认分辨率
    default_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    default_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"摄像头默认分辨率: {default_width}x{default_height}")
    
    # 尝试常见的高分辨率（从高到低）
    test_resolutions = [
        (2560, 1440),  # 2K QHD
        (1920, 1080),  # Full HD
        (1280, 720),   # HD
        (800, 600),    # SVGA
        (640, 480),    # VGA
    ]
    
    max_resolution = (default_width, default_height)
    
    for w, h in test_resolutions:
        # 尝试设置分辨率
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        
        # 等待一下让摄像头适应
        import time
        time.sleep(0.1)
        
        # 获取实际设置的分辨率
        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 尝试读取一帧验证
        ret, frame = cap.read()
        
        if ret and frame is not None:
            if actual_w * actual_h > max_resolution[0] * max_resolution[1]:
                max_resolution = (actual_w, actual_h)
                print(f"检测到支持分辨率: {actual_w}x{actual_h}")
            
            # 如果达到了目标分辨率，可以提前返回
            if actual_w == w and actual_h == h:
                break
    
    # 恢复到最大分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, max_resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, max_resolution[1])
    
    # 验证最终分辨率
    final_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    final_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    return final_w, final_h


def main():
    # 获取模型文件的正确路径（兼容打包和开发环境）
    model_path = get_resource_path(FLAGS.pre_trained_model_path)
    
    print(f"加载模型: {model_path}")
    graph, sess = load_graph(model_path)

    # 初始化摄像头（支持自动尝试多个摄像头）
    cap = None
    camera_id = FLAGS.camera_id
    
    # 如果用户指定了摄像头ID，只尝试那个
    if camera_id != 0 or (FLAGS.width != 0 and FLAGS.height != 0):
        print(f"使用指定摄像头: {camera_id}")
        
        # 先尝试默认后端
        cap = cv2.VideoCapture(camera_id)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None and frame.mean() > 10:
                print(f"[OK] 默认后端可用")
            else:
                # 默认后端失败，尝试CAP_DSHOW
                print("[INFO] 默认后端不可用，尝试CAP_DSHOW...")
                cap.release()
                cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.mean() > 10:
                        print(f"[OK] CAP_DSHOW后端可用")
                    else:
                        print("错误: 摄像头无法正常工作!")
                        cap.release()
                        return
                else:
                    print(f"错误: 无法打开摄像头 {camera_id}!")
                    return
        else:
            # 默认后端打开失败，尝试CAP_DSHOW
            print("[INFO] 默认后端无法打开，尝试CAP_DSHOW...")
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
            
            if not cap.isOpened():
                print(f"错误: 无法打开摄像头 {camera_id}!")
                return
            
            ret, frame = cap.read()
            if not ret or frame is None or frame.mean() < 10:
                print("错误: 摄像头无法正常工作!")
                cap.release()
                return
    else:
        # 自动尝试多个摄像头
        cap, camera_id = try_open_camera(max_attempts=3)
        
        if cap is None:
            print("\n错误: 未找到可用摄像头!")
            print("请检查：")
            print("  1. 摄像头是否连接")
            print("  2. 是否被其他应用占用")
            print("  3. 尝试手动指定 --camera_id 参数")
            return
    
    print(f"\n使用摄像头 {camera_id}")
    
    # 自动检测最大分辨率
    if FLAGS.width == 0 or FLAGS.height == 0:
        print("正在检测摄像头最大分辨率...")
        FLAGS.width, FLAGS.height = get_camera_max_resolution(cap, camera_id)
        print(f"使用摄像头最大分辨率: {FLAGS.width}x{FLAGS.height}")
    else:
        # 用户手动指定分辨率
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FLAGS.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FLAGS.height)
        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"摄像头分辨率: {actual_w}x{actual_h}")
        FLAGS.width = actual_w
        FLAGS.height = actual_h

    mp = _mp.get_context("spawn")
    v = mp.Value('i', 0)
    lock = mp.Lock()
    # 使用独立模块的函数，避免子进程重新导入此文件
    process = mp.Process(target=run_mario_game, args=(v, lock))
    process.start()

    try:
        while True:
            key = cv2.waitKey(10)
            if key == ord("q"):
                break

            # 从普通摄像头获取帧
            ret, frame = cap.read()
            if not ret:
                print("警告: 无法从摄像头读取帧!")
                continue

            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes, scores, classes = detect_hands(frame, graph, sess)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            results = predict(boxes, scores, classes, FLAGS.threshold, FLAGS.width, FLAGS.height)

            if len(results) == 1:
                x_min, x_max, y_min, y_max, category = results[0]
                x = int((x_min + x_max) / 2)
                y = int((y_min + y_max) / 2)
                cv2.circle(frame, (x, y), 5, RED, -1)

                if category == "Open" and x <= FLAGS.width / 3:
                    action = 7  # Left jump
                    text = "Jump left"
                elif category == "Closed" and x <= FLAGS.width / 3:
                    action = 6  # Left
                    text = "Run left"
                elif category == "Open" and FLAGS.width / 3 < x <= 2 * FLAGS.width / 3:
                    action = 5  # Jump
                    text = "Jump"
                elif category == "Closed" and FLAGS.width / 3 < x <= 2 * FLAGS.width / 3:
                    action = 0  # Do nothing
                    text = "Stay"
                elif category == "Open" and x > 2 * FLAGS.width / 3:
                    action = 2  # Right jump
                    text = "Jump right"
                elif category == "Closed" and x > 2 * FLAGS.width / 3:
                    action = 1  # Right
                    text = "Run right"
                else:
                    action = 0
                    text = "Stay"
                with lock:
                    v.value = action
                cv2.putText(frame, "{}".format(text), (x_min, y_min - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 2)
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (int(FLAGS.width / 3), FLAGS.height), ORANGE, -1)
            cv2.rectangle(overlay, (int(2 * FLAGS.width / 3), 0), (FLAGS.width, FLAGS.height), ORANGE, -1)
            cv2.addWeighted(overlay, FLAGS.alpha, frame, 1 - FLAGS.alpha, 0, frame)
            # 设置窗口为最顶层
            cv2.namedWindow('Detection', cv2.WINDOW_NORMAL)
            hwnd = win32gui.FindWindow(None, 'Detection')
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            cv2.imshow('Detection', frame)

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    # Windows多进程必须调用freeze_support
    _mp.freeze_support()
    
    # 只有在主模块才运行main
    main()
