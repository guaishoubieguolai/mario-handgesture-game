# 手势控制超级马里奥游戏

通过手势玩经典游戏，如超级马里奥兄弟！无需键盘或鼠标输入。这是一种有趣且未来感十足的方式，重温旧游戏。

使用 **Python 3.9+** 开发，需要Python 3.9及以上版本以及必要的软件包、Intel RealSense 摄像头。

---

## 功能特点

- **无需外设**: 完全脱离键盘和鼠标
- **手势控制**: 隔空手势控制游戏角色
- **实时性**: 基于 Intel RealSense 摄像头实时捕捉
- **全屏显示**: 游戏画面自动适应屏幕分辨率

---

## 硬件要求

- Python 3.9+
- Intel RealSense 摄像头 (D400系列或更高型号)
- Windows 10/11
- 8GB+ RAM

---

## 控制说明

屏幕水平分为三等份，通过识别手部位置和手势来控制马里奥：

| 区域 | 手势 | 动作 |
|------|------|------|
| 左侧 1/3 | 张开手掌 | 向左跳跃 |
| 左侧 1/3 | 握拳 | 向左奔跑 |
| 中间 1/3 | 张开手掌 | 跳跃 |
| 中间 1/3 | 握拳 | 保持不动 |
| 右侧 1/3 | 张开手掌 | 向右跳跃 |
| 右侧 1/3 | 握拳 | 向右奔跑 |

**注意**: 手势识别需要在充足的光线环境下进行，手部应在摄像头前方约 0.5-1 米范围内。

---

## 技术架构

### 系统架构

```
┌────────────────────────────────────────────────────────────────────┐
│                         硬件层                                     │
│  ┌─────────────────┐                    ┌─────────────────────┐  │
│  │ Intel RealSense │                    │     计算机屏幕      │  │
│  │    摄像头       │                    │   (游戏显示输出)   │  │
│  └────────┬────────┘                    └──────────┬──────────┘  │
└───────────┼───────────────────────────────────────┼──────────────┘
            │                                       │
            ▼                                       ▼
┌────────────────────────────────────────────────────────────────────┐
│                         软件层                                      │
│                                                                    │
│  ┌─────────────────────┐       ┌─────────────────────────────┐   │
│  │     主进程          │       │        子进程               │   │
│  │  (手势检测与控制)  │       │      (游戏模拟循环)         │   │
│  │                     │       │                             │   │
│  │ • RealSense捕获    │       │ • Gym游戏环境初始化         │   │
│  │ • TensorFlow推理   │  ──▶  │ • 接收动作指令              │   │
│  │ • 动作映射逻辑     │  IPC  │ • 渲染游戏画面              │   │
│  │ • OpenCV可视化     │       │ • 全屏显示                  │   │
│  └─────────────────────┘       └─────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 技术栈

| 类别 | 技术 | 版本 | 用途 |
|-----|------|------|------|
| 语言 | Python | 3.9+ | 开发语言 |
| 深度学习 | TensorFlow | 2.10.0+ | 手势识别模型推理 |
| 计算机视觉 | OpenCV | 4.5.5.64 | 视频处理与显示 |
| 深度摄像头 | Intel RealSense SDK | 2.53.1.4623 | 手势捕捉 |
| 游戏环境 | gym-super-mario-bros | 7.4.0 | 超级马里奥游戏模拟 |
| 强化学习环境 | gym | 0.26.1+ | 环境接口标准 |
| GUI | pygame | 2.6.1 | 游戏渲染 |

### 进程间通信

项目采用多进程架构实现并行处理：

```python
# 使用 multiprocessing 实现进程间通信
mp = _mp.get_context("spawn")
v = mp.Value('i', 0)      # 共享变量存储动作
lock = mp.Lock()           # 互斥锁保护共享变量
process = mp.Process(target=mario, args=(v, lock))
```

---

## 安装步骤

### 1. 克隆或下载项目

```bash
cd mario-handgesture-game
```

### 2. 创建Conda环境（推荐）

```bash
conda create -n mario-game python=3.9
conda activate mario-game
```

### 3. 安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 运行游戏

```bash
python mario.py
```

启动后，RealSense 摄像头开始工作，屏幕显示实时手势检测画面。按 `Q` 键退出游戏。

---

## 项目结构

```
mario-handgesture-game/
├── mario.py                    # 主程序入口
├── README.MD                   # 项目说明
├── requirements.txt            # 依赖包列表
├── src/
│   ├── config.py               # 配置常量
│   ├── utils.py                # 工具函数 (手势检测、游戏循环)
│   └── pretrained_model.pb     # 预训练手势模型
└── resources/                  # 资源文件夹
```

---

## 核心代码说明

### 手势检测流程

1. 加载预训练 TensorFlow 模型 (`src/pretrained_model.pb`)
2. RealSense 摄像头捕获视频帧
3. TensorFlow 推理识别手势类别 (Open/Closed)
4. 根据手部位置和手势类型映射为游戏动作

### 游戏循环

1. 创建 gym 环境: `gym_super_mario_bros.make('SuperMarioBros-1-1-v0')`
2. 使用 `unwrap_to_nes_env()` 解包环境以绕过API差异
3. 应用 JoypadSpace 包装器
4. 循环: 接收动作 → 执行步骤 → 渲染帧 → 全屏显示
5. 每秒约 100 帧 (sleep 0.01)

---

## Python 软件包

核心依赖：
- cv2 / opencv-python
- tensorflow >= 2.10.0
- numpy >= 1.21.6
- gym >= 0.26.1
- gym_super_mario_bros == 7.4.0
- nes-py == 8.2.1
- pygame
- pyrealsense2

---

## 版本兼容性说明

### 已知问题及解决方案

#### 1. Gym API 版本差异

**问题**: gym 0.26 与 gym-super-mario-bros 的 API 不兼容
- gym 0.26 的 `step()` 返回 5 个值: `(obs, reward, terminated, truncated, info)`
- nes-py 使用旧版 API 返回 4 个值: `(obs, reward, done, info)`

**解决方案**: 在 `src/utils.py` 中添加了 `unwrap_to_nes_env()` 函数：
```python
def unwrap_to_nes_env(env):
    """解包环境以获取原始nes-py环境（绕过gym 0.26的API差异）"""
    while hasattr(env, 'env'):
        env = env.env
    return env
```

#### 2. TensorFlow 版本升级

**变化**: 从 TensorFlow 1.15.0 升级到 2.10.0+
- 旧版: TensorFlow 1.15.0
- 新版: TensorFlow 2.10.0+

**兼容性**: 代码使用 `tf.compat.v1` API，保持向后兼容：
```python
tf.compat.v1.flags.DEFINE_integer("width", 640, "Screen width")
tf.compat.v1.gfile.GFile(path, 'rb')
```

#### 3. NumPy 版本

当前使用 NumPy 1.21.6，与原计划的 1.19.5 相比，新版本向后兼容，无已知问题。

---

## 注意事项

1. **硬件依赖**: 必须连接 Intel RealSense 摄像头才能运行
2. **环境光线**: 手势识别需要在充足的光线环境下进行
3. **手势距离**: 手部应在摄像头前方约 0.5-1 米范围内
4. **模型限制**: 当前模型仅识别"张开"和"握拳"两种手势
5. **非独立程序**: 需要 Python 3.9+ 和相关开发环境

---

## 故障排除

### 常见问题

**Q: 运行时提示 `ValueError: not enough values to unpack`**
A: 这是 gym API 版本差异导致，确保 `src/utils.py` 中包含 `unwrap_to_nes_env()` 函数，且在创建环境时正确调用。

**Q: TensorFlow 加载模型失败**
A: 检查模型文件 `src/pretrained_model.pb` 是否存在（约18MB），如缺失请重新下载。

**Q: RealSense 摄像头未检测到**
A: 
- 检查 USB 连接
- 确认已安装 RealSense SDK
- 尝试使用 RealSense Viewer 验证摄像头工作状态

**Q: GPU 未被 TensorFlow 识别**
A: 项目会自动降级到 CPU 模式运行，不影响功能。如需 GPU 加速，请安装 CUDA 11.2和 cuDNN 8.1。

---

## 技术亮点

- TensorFlow 2.x 向后兼容实现
- 多进程架构实现并行处理
- Gym API 版本兼容性修复
- RealSense 深度摄像头应用
- OpenCV 可视化与全屏渲染
- Gym 环境集成经典游戏

---

## 更新日志

### 2026-04-08
- 更新 TensorFlow 从 1.15.0 到 2.10.0+
- 更新 gym 从 0.21.0 到 0.26.1
- 添加 `unwrap_to_nes_env()` 函数修复 API 兼容性
- 更新 Python 版本要求到 3.9+
- 添加版本兼容性说明和故障排除指南