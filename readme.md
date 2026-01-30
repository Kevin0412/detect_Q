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
├── src/                 # 核心模块（可通过 from src import detect_Q, detect_q 导入）
│   ├── __init__.py      # 模块入口，导出检测函数
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
  └── 其他由 src/add_data.py 生成的平均模板（按需）
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

- **data/**：已按类别整理好的小图标（模板库），用于生成平均模板或直接匹配。
- **screenshots/**：大截图与样本存档，按用途分类：
  - validation/：用于验证的随机游戏截图集合（用于快速检验检测效果）。
  - env_variations/：在不同环境/设置下采集的截图，用于测试环境鲁棒性。
  - fitting/：用于拟合（fitting）的截图集。文件命名格式为 `{元素能量}_{总元素能量}.png`（例如 `25_80.png`），这些样本通过追忆套等可重复流程采集，用于校准模板与能量映射关系。
  - author_icons/：作者本人全角色的元素爆发小图标集合（用于计算均值并做匹配）。采集流程示例：使用雷电将军对"公义"进行充能，以标准化充能过程。
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

