import numpy as np
from nes_py.wrappers import JoypadSpace
import gym
import gym_super_mario_bros
from gym_super_mario_bros.actions import COMPLEX_MOVEMENT
import tensorflow as tf
from time import sleep
from src.config import HAND_GESTURES
import cv2  # 用于调整窗口大小
import ctypes  # 用于获取屏幕分辨率

def load_graph(path):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        graph_def = tf.compat.v1.GraphDef()
        with tf.compat.v1.gfile.GFile(path, 'rb') as fid:
            graph_def.ParseFromString(fid.read())
            tf.import_graph_def(graph_def, name='')
        sess = tf.compat.v1.Session(graph=detection_graph)
    return detection_graph, sess


def detect_hands(image, graph, sess):
    input_image = graph.get_tensor_by_name('image_tensor:0')
    detection_boxes = graph.get_tensor_by_name('detection_boxes:0')
    detection_scores = graph.get_tensor_by_name('detection_scores:0')
    detection_classes = graph.get_tensor_by_name('detection_classes:0')
    image = image[None, :, :, :]
    boxes, scores, classes = sess.run([detection_boxes, detection_scores, detection_classes],
                                      feed_dict={input_image: image})
    return np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes)


def predict(boxes, scores, classes, threshold, width, height, num_hands=2):
    count = 0
    results = {}
    for box, score, class_ in zip(boxes[:num_hands], scores[:num_hands], classes[:num_hands]):
        if score > threshold:
            y_min = int(box[0] * height)
            x_min = int(box[1] * width)
            y_max = int(box[2] * height)
            x_max = int(box[3] * width)
            category = HAND_GESTURES[int(class_) - 1]
            results[count] = [x_min, x_max, y_min, y_max, category]
            count += 1
    return results

def mario(v, lock):
    env = gym_super_mario_bros.make('SuperMarioBros-1-1-v0')
    env = JoypadSpace(env, COMPLEX_MOVEMENT)
    done = True

    # 获取屏幕分辨率
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # 创建全屏窗口
    cv2.namedWindow("Super Mario Bros", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Super Mario Bros", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        if done:
            env.reset()
            with lock:
                v.value = 0
        with lock:
            u = v.value
        _, _, done, _ = env.step(u)

        # 渲染帧并调整为全屏
        frame = env.render(mode='rgb_array')  # 获取渲染帧
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # 转换为 BGR 格式以保持颜色一致
        frame_resized = cv2.resize(frame_bgr, (screen_width, screen_height))  # 调整为屏幕分辨率
        cv2.imshow("Super Mario Bros", frame_resized)  # 显示全屏窗口

        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        sleep(0.01)

    env.close()
    cv2.destroyAllWindows()
