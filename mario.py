import tensorflow as tf
import cv2
import multiprocessing as _mp
import pyrealsense2 as rs  # 添加 RealSense SDK
import numpy as np
from src.utils import load_graph, mario, detect_hands, predict
from src.config import ORANGE, RED, GREEN
import win32gui  # 用于设置窗口最顶层
import win32con  # 用于设置窗口属性

tf.compat.v1.flags.DEFINE_integer("width", 640, "Screen width")
tf.compat.v1.flags.DEFINE_integer("height", 480, "Screen height")
tf.compat.v1.flags.DEFINE_float("threshold", 0.6, "Threshold for score")
tf.compat.v1.flags.DEFINE_float("alpha", 0.3, "Transparent level")
tf.compat.v1.flags.DEFINE_string("pre_trained_model_path", "src/pretrained_model.pb", "Path to pre-trained model")

FLAGS = tf.compat.v1.flags.FLAGS


def main():
    graph, sess = load_graph(FLAGS.pre_trained_model_path)

    # 初始化 RealSense 管道
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, FLAGS.width, FLAGS.height, rs.format.bgr8, 30)
    pipeline.start(config)

    mp = _mp.get_context("spawn")
    v = mp.Value('i', 0)
    lock = mp.Lock()
    process = mp.Process(target=mario, args=(v, lock))
    process.start()

    try:
        while True:
            key = cv2.waitKey(10)
            if key == ord("q"):
                break

            # 从 RealSense 获取帧
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                print("Warning: No color frame detected. Skipping...")
                continue

            # 转换为 NumPy 数组
            frame = np.asanyarray(color_frame.get_data())

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
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
