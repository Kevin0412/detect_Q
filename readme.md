# Detect_Q

## Genshin Impact 元素爆发检测（原型）

### 项目简介

本仓库为基于 UI 图像分析的原神元素爆发（Q，元素爆发）与能量条检测原型，侧重在不依赖简单颜色阈值或圆检测的条件下，通过投影、差分与模板匹配判断充能比例与爆发就绪状态。

---

### 快速概览

- 前台角色：通过对环形能量条做径向展开并降为一维亮度曲线，检测亮度突变位置并映射为充能百分比。
- 后台角色：用平均模板和边缘/匹配方法判断元素爆发图标是否存在（就绪）。

---

### 项目结构

```
detect_Q/
├── src/                 # 核心模块
│   ├── detect.py        # 检测逻辑主脚本（能量条检测 + 后台元素爆发匹配）
│   ├── add_data.py      # 生成平均模板的工具
│   ├── read_avg.py      # 读取并处理平均图像
│   ├── locate.py        # 手动定位元素爆发图标
│   ├── manual_sort.py   # 人工分类截图工具
│   └── screenshot.py    # 屏幕截图采集脚本
├── examples/            # 示例与演示脚本
│   └── analyze_1920.py  # 基于 1920x1080 的完整分析示例（推荐使用）
├── data/                # 已标注的小图标（模板库）
├── screenshots/         # 截图存档（按功能分类）
│   ├── validation/      # 验证用截图
│   ├── env_variations/  # 环境变化截图
│   ├── fitting/         # 拟合用截图（{energy}_{max_energy}.png）
│   ├── author_icons/    # 作者全角色爆发图标
│   └── archive/         # 历史归档
└── 平均模板文件（示例）
  ├── avg_Q.png        # 当前用于后台爆发匹配的平均模板（由 src/add_data.py 生成）
  └── 其他生成的平均模板（试验品）
```

### 主要文件说明

- **src/detect.py**：检测逻辑核心，导出 `detect_Q`（前台能量条）与 `detect_q`（后台爆发图标）。
- **src/add_data.py**：对一组小图标做逐像素累加/平均，生成 `avg_Q.png` 等平均模板。
- **src/read_avg.py**：读取并处理已生成的平均图像（配合 add_data.py）。
- **src/locate.py**：手动或半自动定位元素爆发图标位置，便于裁切与采样。
- **src/manual_sort.py**：人工对截图进行是否含有元素爆发的分类整理。
- **src/screenshot.py**：屏幕截图采集脚本。
- **examples/analyze_1920.py**：推荐使用的高层封装，基于 1920x1080 输入完整截图，返回四个后台位就绪状态、前台就绪与充能百分比。

### 数据与目录说明

- **data/**：已按类别整理好的小图标（模板库），用于生成平均模板或者深度学习（感觉模板足够了，没有深度学习）。
- **screenshots/**：大截图与样本存档，按用途分类：
  - validation/：用于验证的随机游戏截图集合（用于快速检验检测效果）。
  - env_variations/：在不同环境/设置下采集的截图，用于测试环境鲁棒性。
  - fitting/：用于拟合（fitting）的截图集。文件命名格式为 `{元素能量}_{总元素能量}.png`（例如 `25_80.png`），这些样本通过追忆套等可重复流程采集，用于校准模板与能量映射关系。
  - author_icons/：作者本人全角色的元素爆发小图标集合（用于计算均值并做匹配）。采集流程示例：使用雷电将军进行充能，以标准化充能过程。
  - archive/：历史截图与其他类别样本归档。
**平均模板说明**

- 当前用于后台爆发匹配的模板文件为 `avg_Q.png`，该文件位于仓库根目录（由 `src/add_data.py` 生成）。

生成原理（简述）：

1. 从 `data/` 或指定的样本文件夹中读取若干已裁切的小图标（每张图均为元素爆发小图）。
2. 将每张小图统一缩放为 32×32（`cv2.resize`），以便对齐像素位置进行统计。
3. 对每张缩放后的图像使用 Canny 边缘检测（或类似的二值边缘提取），得到边缘二值图。
4. 对所有边缘二值图像逐像素累加（或按权重累加），然后除以样本数得到平均边缘热度图。
5. 将平均边缘图保存为 `avg_Q.png`（灰度或二值格式），后续 `detect_q` 通过与该模板做加权匹配/乘积来计算匹配得分。

该流程的作用是把不同样本中稳定出现的边缘结构“强化”为模板，从而提升对噪声与细微位置偏移的鲁棒性。

**截图区域与快速示例**

 - 建议的元素能量条与元素爆发裁切（基于 1920x1080）：
   - 前台能量环（示例，用于 `detect_Q`）：img[916:1028,1763:1875]（请以 `locate.py` 输出为准）。
  - 后台角色元素爆发位置（示例，用于 `detect_q`）：
    - img[242:295,1591:1644]
    - img[338:391,1591:1644]
    - img[434:487,1591:1644]
    - img[530:583,1591:1644]

- 模块使用示例（在代码中导入并调用）：

```python
from src.detect import detect_Q, detect_q
import cv2

# 假设已经用 screenshot.py 截好图并按坐标裁切
img_foreground = cv2.imread('crop_foreground.png')
index, score = detect_Q(img_foreground)

img_back = cv2.imread('crop_back.png')
match_score = detect_q(img_back)

print('foreground index:', index, 'score:', score)
print('background match score:', match_score)
```

- 或使用高层示例（推荐）：

```python
from examples.analyze_1920 import analyze_1920_frame
import cv2

# 输入完整 1920x1080 截图，自动裁切并返回所有检测结果
result = analyze_1920_frame(cv2.imread('screenshot.png'))
print('后台四位就绪状态:', result['slots'])
print('前台充能百分比:', result['foreground']['charge_pct'])
```

- 注意：`detect_Q` 与 `detect_q` 都需要输入已裁切好的小图（函数不负责在完整屏幕上搜索）。

---

## 检测效果示例与说明

### 测试用例 1：正常充能（能量条边缘清晰）

命令：
```bash
python3 examples/analyze_1920.py screenshots/fitting/35_50.png
```

输出：
```json
{
  "slots": [true, true, true, false],
  "slots_scores": [0.3505859375, 0.330078125, 0.3408203125, 0.0],
  "foreground": {
    "ready": false,
    "index": 31,
    "score": 7.470289062289192,
    "charge_pct": 0.7027419289999999,
    "match_score": 0.1611328125
  }
}
```

**说明**：前台角色当前元素能量为 35（满能量为 50），检测结果计算得出充能百分比为 0.703，误差仅 0.003（≈ 35/50=0.7）。同时正确检测出后台一、二、三号位元素爆发已就绪（slots 前三项为 true）。

---

### 测试用例 2：能量为空（无显著边缘突变，通过模板匹配判定）

命令：
```bash
python3 examples/analyze_1920.py screenshots/validation/1\ \(1\).png
```

输出：
```json
{
  "slots": [false, false, false, false],
  "slots_scores": [0.0, 0.2099609375, 0.01953125, 0.0],
  "foreground": {
    "ready": false,
    "index": 14,
    "score": 2.9782583219302503,
    "charge_pct": 0.0,
    "match_score": 0.0771484375
  }
}
```

**说明**：`detect_Q` 无法找到显著的亮度突变（score 低于阈值 4.59），因此无法直接计算充能百分比。系统通过 `detect_q` 对前台与后台爆发模板的匹配，确认元素能量为空（match_score 较低），故 `ready` 为 false，`charge_pct` 为 0.0。

---

### 测试用例 3：能量满充（无显著边缘突变，通过模板匹配判定）

命令：
```bash
python3 examples/analyze_1920.py screenshots/validation/1\ \(3\).png
```

输出：
```json
{
  "slots": [false, false, false, false],
  "slots_scores": [0.0966796875, 0.0, 0.0, 0.0146484375],
  "foreground": {
    "ready": true,
    "index": 76,
    "score": 3.2825119952857467,
    "charge_pct": 1.0,
    "match_score": 0.33203125
  }
}
```

**说明**：同样无法找到显著亮度突变（score 低于阈值），但通过 `detect_q` 模板匹配（match_score 较高），确认前台元素能量已充满，故 `ready` 为 true，`charge_pct` 为 1.0。

---

### 总结与建议

- **能量条边缘突变清晰时**：`detect_Q` 直接计算充能百分比。
- **能量为空或满充时**：由于能量条边缘不明显，`detect_Q` 的 score 低于阈值，此时系统使用 `detect_q` 与后台爆发图标模板比对作二次确认，判断充能是否满。
- **CD 中的情况**：建议结合文字识别或其他辅助判断方式。