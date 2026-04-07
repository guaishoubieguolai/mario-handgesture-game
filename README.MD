# 手势控制超级马里奥游戏

通过手势玩经典游戏！无需键盘鼠标，隔空控制马里奥。

**支持普通摄像头或 Intel RealSense 摄像头**

---

## 功能特点

- 🎮 完全脱离键盘鼠标
- 👋 隔空手势控制游戏角色
- 📹 支持普通USB摄像头
- 🖥️ 全屏显示，自动适应屏幕分辨率

---

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
conda create -n mario-game python=3.9
conda activate mario-game

# 安装依赖
pip install -r requirements.txt
```

### 2. 测试摄像头

```bash
# 测试默认摄像头
python test_camera.py

# 扫描所有摄像头
python test_camera.py --scan
```

### 3. 运行游戏

```bash
# 默认摄像头(ID 0)
python mario.py

# 指定摄像头
python mario.py --camera_id 1

# 降低分辨率(如果卡顿)
python mario.py --width 320 --height 240
```

按 `Q` 键退出游戏。

---

## 控制说明

屏幕分为左、中、右三个区域：

| 区域 | 手势 | 动作 |
|------|------|------|
| 左侧 | 张开手掌 | 向左跳跃 |
| 左侧 | 握拳 | 向左奔跑 |
| 中间 | 张开手掌 | 跳跃 |
| 中间 | 握拳 | 保持不动 |
| 右侧 | 张开手掌 | 向右跳跃 |
| 右侧 | 握拳 | 向右奔跑 |

**最佳实践**: 光线充足、背景简单、手部距离摄像头 50-100cm

---

## 项目结构

```
mario-handgesture-game/
├── mario.py                # 主程序
├── test_camera.py          # 摄像头测试工具
├── README.MD               # 说明文档
├── requirements.txt        # 依赖列表
├── src/
│   ├── config.py           # 配置
│   ├── utils.py            # 工具函数
│   └── pretrained_model.pb # 手势模型(18MB)
└── resources/              # 资源文件
```

---

## 硬件要求

- Python 3.9+
- Windows 10/11
- 8GB+ RAM
- 普通USB摄像头 或 Intel RealSense D400

---

## 常见问题

**摄像头无法打开**
- 关闭其他使用摄像头的程序
- 运行 `python test_camera.py --scan` 查看可用设备
- 尝试 `--camera_id 1` 或其他数字
- 检查Windows摄像头权限设置

**画面卡顿**
- 降低分辨率: `python mario.py --width 320 --height 240`
- 确保光线充足
- 关闭后台程序

**手势识别不准**
- 保持 50-100cm 距离
- 光线充足均匀
- 背景简单纯色
- 手势动作要清晰

**TensorFlow 加载模型失败**
- 检查 `src/pretrained_model.pb` 是否存在(约18MB)

**Gym API 报错**
- 项目已修复 gym 0.26 兼容性问题

---

## 技术栈

- **TensorFlow 2.10+**: 手势识别模型推理
- **OpenCV 4.5.5**: 视频处理与显示
- **gym-super-mario-bros 7.4.0**: 马里奥游戏环境
- **pygame 2.6.1**: 游戏渲染
- **Python 3.9+**: 开发语言

---

## 许可证

本项目仅供学习和研究使用。