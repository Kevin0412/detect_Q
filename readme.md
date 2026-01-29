# Detect_Q

## Genshin Impact 元素爆发检测（原型）

### 项目简介

本仓库为基于 UI 图像分析的原神元素爆发（Q，元素爆发）与能量条检测原型，侧重在不依赖简单颜色阈值或圆检测的条件下，通过投影、差分与模板匹配判断充能比例与爆发就绪状态。

---

### 快速概览

- 前台角色：通过对环形能量条做径向展开并降为一维亮度曲线，检测亮度突变位置并映射为充能百分比。
- 后台角色：用平均模板和边缘/匹配方法判断元素爆发图标是否存在（就绪）。

---

### 主要文件说明

- add_data.py：对一组小图标做逐像素累加/平均，生成模板或平均图像。
- detect.py：检测逻辑主脚本（能量条检测 + 后台元素爆发匹配）。
- locate.py：用于手动或半自动定位元素爆发图标位置，便于裁切与采样。
- manual_sort.py：人工对截图进行是否含有元素爆发的分类整理工具。
- read_avg.py：读取并处理已生成的平均图像（配合 add_data.py）。
- screenshot.py：截图采集脚本（用于样本采集）。

### 数据与目录说明

- data/：已按类别整理好的小图标（模板库），用于生成平均模板或直接匹配。
- images/：用于验证的随机游戏截图集合（用于快速检验检测效果）。
- images_2/、images_3/：在不同环境/设置下采集的截图，用于测试环境鲁棒性。
- images_4/：用于拟合（fitting）的截图集。文件命名格式为 `{元素能量}_{总元素能量}.png`（例如 `25_80.png`），这些样本通过追忆套等可重复流程采集，用于校准模板与能量映射关系。
- images_5/：备用或历史截图存档。
- images_6/：作者本人全角色的元素爆发小图标集合（用于计算均值并做匹配）。采集流程示例：使用雷电将军对“公义”进行充能，以标准化充能过程。
- images_7/：额外样本或特殊场景截图。

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
from detect import *
import cv2

# 假设已经用 screenshot.py 截好图并按坐标裁切
img_foreground = cv2.imread('crop_foreground.png')
index, score = detect_Q(img_foreground)

img_back = cv2.imread('crop_back.png')
match_score = detect_q(img_back)

print('foreground index:', index, 'score:', score)
print('background match score:', match_score)
```

- 注意：`detect_Q` 与 `detect_q` 都需要输入已裁切好的小图（函数不负责在完整屏幕上搜索）。

**建议的目录重构（仅建议，默认不移动文件）**

当前仓库根目录包含多个以 images 开头的文件夹，长期维护建议按功能分类：

- `data/` → 保留用于已标注的小图标（模板库）。
- `screenshots/` → 建议把所有未标注或大截图移动到此目录下，分子目录：
  - `screenshots/validation/`（原 `images/`）
  - `screenshots/env_variations/`（原 `images_2/`、`images_3/`）
  - `screenshots/fitting/`（原 `images_4/`，命名为 `{current}_{total}.png`）
  - `screenshots/author_icons/`（原 `images_6/`）
  - `screenshots/archive/`（原 `images_5/`、`images_7/` 可合并归档）

示例移动命令（在确认后执行）：

```bash
# 新建目录
mkdir -p screenshots/validation screenshots/env_variations screenshots/fitting screenshots/author_icons screenshots/archive
# 将文件移入对应目录（示例）
# mv images/* screenshots/validation/
# mv images_2/* screenshots/env_variations/
# mv images_3/* screenshots/env_variations/
# mv images_4/* screenshots/fitting/
# mv images_6/* screenshots/author_icons/
# mv images_5/* screenshots/archive/
# mv images_7/* screenshots/archive/
```

**关于前台满能量判断和后续改进**

- 观察：当前 `detect_Q` 的阈值判断可能在“满能量”和“空能量”都触发相同得分区间时会混淆。建议在流程中同时调用 `detect_q`（模板匹配）对前台裁切结果做二次确认——如果 `detect_Q` 的得分接近边界，再用 `detect_q` 与“满能量”或“空能量”模板比对以确认状态。
- 建议额外收集一组“前台满能量”的小图标（单独目录 `templates/foreground_full/`），用 `add_data.py` 生成专门的平均模板 `avg_foreground_full.png`，后续 `detect_q` 可支持传入不同模板路径以进行灵活匹配。

---

如果你同意目录重构，我可以先生成一份移动脚本（不自动执行），或者直接在仓库中创建 `screenshots/` 并做一次试运行（会先列出将被移动的文件供你确认）。


