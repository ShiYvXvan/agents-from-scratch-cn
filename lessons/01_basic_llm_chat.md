# 第 01 课 - 与模型对话

## 我们在回答什么问题？

**"我到底该怎么跟一个语言模型对话？"**

这是最基础的一步。在构建 agent 之前，我们需要理解最简单的交互形式：文本输入，文本输出。

## 你将构建什么

一个最简交互，它将：
- 加载一个本地 LLM
- 向它发送文本
- 接收返回的文本

仅此而已。没有魔法。没有框架。只有基础。

## 引入的新概念

### 1. Prompt

**prompt** 就是你发送给模型的文本。它可以是一个问题（比如"什么是 AI agent？"）、一条指令（比如"解释量子计算"）、或者一个请求（比如"写一首关于海洋的诗"）。模型会基于它在训练中学到的模式来补全或回应这段文本。

### 2. Token

模型并不是把文本当作词语来看——它们看到的是 **token**。token 是文本片段（通常是单词或子词）。例如，"Hello world" 可能是 2 个 token，而 "artificial intelligence" 根据模型不同可能是 2 到 4 个 token。

这一点很重要，因为模型有 token 限制（context window），生成速度以每秒 token 数来衡量，更长的 prompt 会消耗更多的 token，留给回复的空间就更少。

### 3. Context

**context** 是模型一次能"看到"的全部内容。它包括你的 prompt、之前的对话以及系统指令。模型有一个 **context window**（例如 2048 个 token）。如果你超过了这个限制，模型就看不到更早的文本了。

## 我们（暂时）不做什么

- 不使用 system prompt（[第 02 课](02_system_prompt#!/usr/bin/env python3
import cv2
import numpy as np
import threading
import time
import queue
import yaml
from rknnlite.api import RKNNLite
from flask import Flask, Response

# ── 配置 ─────────────────
MODEL_PATH   = 'yolov8n-rk3588.rknn'
LABEL_PATH   = 'metadata.yaml'
CAMERA_DEV   = '/dev/video-usbcamera0'
INPUT_SIZE   = (640, 640)
CONF_THRESH  = 0.25
NMS_THRESH   = 0.5
MAX_DET      = 300
JPEG_QUALITY = 80

# ── 颜色池 ──────────────
COLOR_POOL = [
    (0, 255, 0), (255, 0, 0), (0, 0, 255), (0, 255, 255),
    (255, 0, 255), (255, 255, 0), (128, 0, 128), (0, 128, 128),
    (128, 128, 0), (0, 0, 128), (128, 0, 0), (0, 128, 0),
] * 5

# ── 加载标签 ────────────
def load_labels(path):
    if path.endswith('.yaml') or path.endswith('.yml'):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict) and 'names' in data:
            return data['names']
        if isinstance(data, list):
            return data
        raise ValueError(f"无法从 {path} 解析标签列表")
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

labels = load_labels(LABEL_PATH)
print(f"标签加载完成，共 {len(labels)} 类")

# ── 摄像头 ──────────────
cap = cv2.VideoCapture(CAMERA_DEV, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
assert cap.isOpened(), "无法打开摄像头"

# ── 异步队列 ────────────
frame_queue = queue.Queue(maxsize=1)         # 摄像头 → 推理线程（只保留最新帧）
result_queue = queue.Queue(maxsize=3)        # 推理线程 → 推流（收集三个核心的结果）

# ── 字母框预处理 ────────
def letterbox(img, new_shape=(640, 640), color=(114, 114, 114)):
    h, w = img.shape[:2]
    r = min(new_shape[0] / h, new_shape[1] / w)
    new_unpad = (int(round(w * r)), int(round(h * r)))
    dw = new_shape[1] - new_unpad[0]
    dh = new_shape[0] - new_unpad[1]
    dw /= 2; dh /= 2
    if (w, h) != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    return cv2.copyMakeBorder(img, top, bottom, left, right,
                              cv2.BORDER_CONSTANT, value=color)

# ── 摄像头采集线程 ──────
def capture_thread():
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue
        # 只保留最新帧，丢弃旧帧
        while not frame_queue.empty():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                break
        frame_queue.put(frame)

# ── 推理＋后处理线程 ────
def infer_thread(core_id):
    core_mask = [RKNNLite.NPU_CORE_0, RKNNLite.NPU_CORE_1, RKNNLite.NPU_CORE_2][core_id]
    rknn = RKNNLite()
    assert rknn.load_rknn(MODEL_PATH) == 0, f"[Core{core_id}] 模型加载失败"
    assert rknn.init_runtime(core_mask=core_mask) == 0, f"[Core{core_id}] Runtime 初始化失败"
    print(f"Core{core_id} 推理线程就绪")

    # 轻微错开启动，避免三个线程完全同步抢帧
    time.sleep(core_id * 0.005)

    while True:
        frame = frame_queue.get()               # 阻塞等待最新帧

        t0 = time.time()

        # 预处理
        img_padded = letterbox(frame, INPUT_SIZE)
        img_rgb = cv2.cvtColor(img_padded, cv2.COLOR_BGR2RGB)
        img_rgb = np.ascontiguousarray(img_rgb, dtype=np.uint8)
        input_tensor = np.expand_dims(img_rgb, 0)

        # 推理
        outputs = rknn.inference(inputs=[input_tensor])
        infer_ms = (time.time() - t0) * 1000

        # 解码
        pred = np.squeeze(outputs[0], 0).T             # (8400, 84)
        cx = pred[:, 0]
        cy = pred[:, 1]
        w  = pred[:, 2]
        h  = pred[:, 3]
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2
        boxes = np.stack([x1, y1, x2, y2], axis=-1)
        scores = pred[:, 4:]
        max_scores = np.max(scores, axis=1)
        class_ids = np.argmax(scores, axis=1)
        mask = max_scores > CONF_THRESH

        draw = img_padded.copy()

        if mask.any():
            valid_boxes = boxes[mask].astype(np.float32)
            valid_scores = max_scores[mask]
            valid_cls = class_ids[mask]

            valid_boxes[:, 0] = np.clip(valid_boxes[:, 0], 0, INPUT_SIZE[0] - 1)
            valid_boxes[:, 1] = np.clip(valid_boxes[:, 1], 0, INPUT_SIZE[1] - 1)
            valid_boxes[:, 2] = np.clip(valid_boxes[:, 2], 0, INPUT_SIZE[0] - 1)
            valid_boxes[:, 3] = np.clip(valid_boxes[:, 3], 0, INPUT_SIZE[1] - 1)

            indices = cv2.dnn.NMSBoxes(valid_boxes.tolist(),
                                       valid_scores.tolist(),
                                       CONF_THRESH, NMS_THRESH,
                                       top_k=MAX_DET)

            if len(indices) > 0:
                for i in indices.flatten():
                    if np.any(np.isnan(valid_boxes[i])) or np.any(np.isinf(valid_boxes[i])):
                        continue
                    x1_i, y1_i, x2_i, y2_i = [int(v) for v in valid_boxes[i]]
                    cls_id = int(valid_cls[i])
                    conf = float(valid_scores[i])

                    color = COLOR_POOL[cls_id % len(COLOR_POOL)]
                    cv2.rectangle(draw, (x1_i, y1_i), (x2_i, y2_i), color, 2)

                    cls_name = labels[cls_id] if cls_id < len(labels) else f"id{cls_id}"
                    label = f"{cls_name} {conf:.2f}"
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    label_y = max(y1_i - th - 4, 0)
                    cv2.rectangle(draw, (x1_i, label_y), (x1_i + tw, y1_i), color, -1)
                    cv2.putText(draw, label, (x1_i, y1_i - 2 if y1_i >= 2 else label_y + th),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # 放入结果队列（若队列满则丢弃最旧的一帧，保证推流始终拿到较新的结果）
        if result_queue.full():
            try:
                result_queue.get_nowait()
            except queue.Empty:
                pass
        result_queue.put(draw)

# ── Flask 视频流（含总体FPS计算） ─────────
app = Flask(__name__)

# 推流线程专属的 FPS 统计变量
total_fps_time = time.time()
total_frame_cnt = 0
total_show_fps = 0.0

def generate_frames():
    global total_fps_time, total_frame_cnt, total_show_fps
    while True:
        try:
            draw = result_queue.get(timeout=0.1)   # 等待最新处理结果
        except queue.Empty:
            time.sleep(0.01)
            continue

        # 更新整体 FPS（每秒刷新一次数字）
        total_frame_cnt += 1
        if (elapsed := time.time() - total_fps_time) >= 1.0:
            total_show_fps = total_frame_cnt / elapsed
            total_frame_cnt = 0
            total_fps_time = time.time()

        # 在图像上绘制稳定的整体帧率
        cv2.putText(draw, f"FPS:{total_show_fps:.1f}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', draw,
                                 [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ret:
            continue
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''<html><head><title>RK3588 YOLOv8 三核</title></head>
<body><h1>RK3588 YOLOv8 三核推理（错开显示）</h1>
<img src="/video_feed" width="640" height="640"></body></html>'''

if __name__ == '__main__':
    # 采集线程
    threading.Thread(target=capture_thread, daemon=True).start()
    # 3 个推理线程，分别绑定三个 NPU 核心
    for core_id in range(3):
        threading.Thread(target=infer_thread, args=(core_id,), daemon=True).start()
    # Flask 推流（主线程）
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True).md)）
- 不使用结构化输出（[第 03 课](03_structured_output.md)）
- 不使用工具（[第 05 课](05_tools.md)）
- 不使用 agent（[第 06 课](06_agent_loop.md)）
- 不使用记忆（[第 07 课](07_memory.md)）

本课刻意保持最简。

## 代码

查看 `agent/agent.py`，找到 `simple_generate()` 方法：

```python
def simple_generate(self, user_input: str) -> str:
    """
    Simplest possible interaction - just pass text to the LLM.
    """
    return self.llm.generate(user_input)
```

就是这样。一行代码。没有任何复杂性。

## 如何运行

查看 `complete_example.py`，找到 `lesson_01_basic_chat()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

response = agent.simple_generate("What is an AI agent?")
print(response)
```

## 内部发生了什么？

1. 你的文本被转换成 token
2. token 被发送给模型
3. 模型预测下一个 token
4. 重复直到满足停止条件（结束 token、最大长度等）
5. token 被转换回文本
6. 文本返回给你

## 关键洞见

### 并不存在"理解"

模型并不"理解"你的问题。相反，它识别 token 中的模式，预测可能的延续，并生成概率性的文本。这很重要：**模型是模式匹配器，不是思维体。**

### 它是概率性的

对同一个 prompt 运行两次，你可能会得到不同的回复。这是因为模型在生成时使用了随机性（temperature），并且存在多个合理的延续可能。不存在唯一"正确"的答案——只有概率性的输出。

### 文本输入 = 文本输出

仅此而已。我们之后构建的一切（agent、工具、记忆）都是建立在这个简单基础之上的。

## 常见问题

**"回复被截断了"**
- 在 `shared/llm.py` 中增大 `max_tokens`

**"模型在自我重复"**
- 这对补全模型来说是正常现象
- 我们将在[第 02 课](02_system_prompt.md)中通过更好的 prompt 来解决

**"回复与 prompt 不匹配"**
- 有些模型需要特定格式
- 我们将在[第 02 课](02_system_prompt.md)和[第 03 课](03_structured_output.md)中添加结构化

## 练习

1. 尝试不同的 prompt，观察回复的变化
2. 在 `shared/llm.py` 中修改 `temperature`（0.0 = 确定性，1.0 = 创造性）
3. 使用 `max_tokens` 控制回复长度

## 接下来是什么？

在[第 02 课](02_system_prompt.md)中，我们将添加 **system prompt** 来塑造模型的行为。这将把随机的文本补全转变为一致、有用的回复。

---

**核心要点：** LLM 只是一个文本补全引擎。我们构建的一切都是与这个简单机制的结构化交互。