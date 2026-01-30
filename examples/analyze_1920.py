"""示例：基于 1920x1080 的裁切坐标封装检测流程。

用法示例：
    python3 examples/analyze_1920.py path/to/screenshot.png

导入示例：
    from examples.analyze_1920 import analyze_1920_frame
    result = analyze_1920_frame(cv2.imread('s.png'))

返回值示例：
    {
      'slots': [True, False, False, True],            # 四个后台位元素爆发是否就绪
      'foreground': {
         'ready': True,
         'index': 12,
         'score': 5.2,
         'charge_pct': 0.86
      }
    }

说明：此文件仅为演示/封装，不修改 `detect.py`，且使用了示例阈值（可按需调整）。
"""

import sys
from typing import Dict, Any, List, Tuple
import cv2
import numpy as np

from detect import detect_Q, detect_q

# 1920x1080 下的示例裁切坐标（取自 README / 项目默认）
_FOREGROUND_BOX = (916, 1763, 1028, 1875)  # y1, x1, y2, x2 -> img[y1:y2, x1:x2]
_BACKGROUND_BOXES = [
    (242, 1591, 295, 1644),
    (338, 1591, 391, 1644),
    (434, 1591, 487, 1644),
    (530, 1591, 583, 1644),
]

# 默认阈值（可调整）
_DETECT_Q_THRESHOLD = 0.35   # detect_q 匹配得分阈值，历史上临界 ~0.30-0.40
_DETECT_Q_FOREGROUND_CONFIRM = 0.35
_DETECT_Q_INDEX_TO_PCT = lambda idx: max(0.0, min(1.0, -0.00855878 * idx + 0.968064109))
# detect_Q 返回的 score 历史临界区间参考: [4.59,6.21]
_DETECT_Q_SCORE_THRESHOLD = 4.59


def _read_img(img_or_path: Any) -> np.ndarray:
    if isinstance(img_or_path, str):
        img = cv2.imread(img_or_path)
        if img is None:
            raise FileNotFoundError(f"cannot read image: {img_or_path}")
        return img
    if isinstance(img_or_path, np.ndarray):
        return img_or_path
    raise TypeError("img_or_path must be a file path or numpy.ndarray")


def analyze_1920_frame(img_or_path: Any) -> Dict[str, Any]:
    """对 1920x1080 截图进行预定义裁切并返回检测结果。

    参数：
      img_or_path: 图像路径或 numpy.ndarray（BGR）

    返回：
      字典，包括：
        - 'slots': 长度为 4 的布尔列表，表示四个后台位元素爆发是否就绪
        - 'foreground': 包含前台就绪（bool）、index、score、charge_pct
    """
    img = _read_img(img_or_path)
    h, w = img.shape[:2]
    if (w, h) != (1920, 1080):
        # 只作为示例：如果分辨率非 1920x1080，仍尝试按相对坐标裁切并警告
        print(f"警告：输入分辨率为 {w}x{h}，示例裁切基于 1920x1080，结果可能不准确")

    # 裁切前台
    y1, x1, y2, x2 = _FOREGROUND_BOX
    fg = img[y1:y2, x1:x2].copy()

    # 裁切后台四位
    backs = [img[y1:y1_2, x1:x1_2].copy() for (y1, x1, y1_2, x1_2) in _BACKGROUND_BOXES]

    # 后台检测
    slots_ready: List[bool] = []
    slots_scores: List[float] = []
    for b in backs:
        score = detect_q(b)
        ready = score >= _DETECT_Q_THRESHOLD
        slots_ready.append(bool(ready))
        slots_scores.append(float(score))

    # 前台检测：使用 detect_Q 获取 index 和 score
    idx, score_fg = detect_Q(fg)
    # 计算充能百分比（基于拟合公式）
    charge_pct = _DETECT_Q_INDEX_TO_PCT(idx)
    # 使用 detect_q 对前台裁切做模板匹配以做二次确认
    fg_match = detect_q(fg)
    fg_ready = (score_fg >= _DETECT_Q_SCORE_THRESHOLD) or (fg_match >= _DETECT_Q_FOREGROUND_CONFIRM)

    result = {
        'slots': slots_ready,
        'slots_scores': slots_scores,
        'foreground': {
            'ready': bool(fg_ready),
            'index': int(idx),
            'score': float(score_fg),
            'charge_pct': float(charge_pct),
            'match_score': float(fg_match),
        }
    }
    return result


def _main(argv: List[str]):
    if len(argv) < 2:
        print("Usage: python3 examples/analyze_1920.py path/to/screenshot.png")
        sys.exit(1)
    path = argv[1]
    res = analyze_1920_frame(path)
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    _main(sys.argv)
