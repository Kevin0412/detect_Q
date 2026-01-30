import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from typing import Tuple

__all__ = ["detect_Q", "detect_q"]


def detect_Q(img: np.ndarray, m: int = 2, n: int = 2, show: bool = False) -> Tuple[int, float]:
    """
    检测前台角色能量条的充能边界。

    参数:
    - img: 已截取的包含能量环区域的 BGR 图像。
    - m, n: 边界裁剪参数（用于忽略顶部/底部若干行）。
    - show: 若为 True，会显示中间可视化结果（用于调试）。

    返回:
    - (index, score): index 为亮度突变位置的行索引（以裁切后图像为准），
      score 为该突变相对于均值的标准化强度（越大表示突变越明显）。

    说明: 输入图像在函数内部不会被原位修改（使用副本处理）。
    """
    # 使用副本以避免修改调用者传入的原图
    img_proc = img.copy()

    # 可选可视化：显示 Canny 边缘用于调试
    if show:
        edges = cv2.Canny(cv2.resize(img_proc, (32, 32)), 100, 200)
        cv2.imshow("edges", edges)

    # 将环形沿高度方向展开为“线性”结构（保持原有思路，只在副本上操作）
    h, w = img_proc.shape[0], img_proc.shape[1]
    for i in range(h):
        left = int(h / 2 - ((h - i) * i) ** 0.5)
        right = int(h / 2 + ((h - i) * i) ** 0.5) + 1
        # 裁剪边界保护
        left = max(0, left)
        right = min(w, right)

        for ch in range(3):
            row = img_proc[i, left:right, ch]
            if row.size == 0:
                # 若切片为空，退回到中点像素
                row = np.array([img_proc[i, w // 2, ch]])
            # 将行片段按高度拉伸为列并赋值回去（与原实现行为保持一致）
            resized = cv2.resize(row.reshape(1, -1), (1, h), interpolation=cv2.INTER_LINEAR).reshape(h)
            img_proc[i, :, ch] = resized

    if show:
        cv2.imshow("img_proc", img_proc)
        hsv = cv2.cvtColor(img_proc, cv2.COLOR_BGR2HSV)
        cv2.imshow("hsv", hsv)
        cv2.waitKey(1)

    # 统计每一行在三个通道上的平均亮度
    X = np.linspace(m, h - n - 1, h - n - m)
    r = np.zeros((h - n - m), np.float64)
    g = np.zeros((h - n - m), np.float64)
    b = np.zeros((h - n - m), np.float64)
    for x in range(m, h - n):
        for y in range(h):
            b[x - m] += img_proc[x][y][0] / h
            g[x - m] += img_proc[x][y][1] / h
            r[x - m] += img_proc[x][y][2] / h

    # 转换为灰度亮度曲线
    a = 0.299 * r + 0.587 * g + 0.114 * b

    if show:
        plt.subplot(2, 1, 1)
        plt.plot(X, b, color="blue")
        plt.plot(X, g, color="green")
        plt.plot(X, r, color="red")
        plt.plot(X, a, color="grey")

    # 一阶差分用于检测亮度突变
    c = a[1: h - n - m] - a[0: h - n - m - 1]

    if show:
        plt.subplot(2, 1, 2)
        plt.plot(X[0: h - n - m - 1], c)
        plt.plot(X[0: h - n - m - 1], np.zeros((h - n - m - 1), np.float64) + np.mean(c))
        plt.plot(X[0: h - n - m - 1], np.zeros((h - n - m - 1), np.float64) + np.mean(c) + np.std(c))
        plt.show()

    # 若标准差为 0，返回 (0,0) 否则返回最大突变位置与标准化分数
    if np.std(c) > 0:
        return int(np.argmax(c) + m), float((np.max(c) - np.mean(c)) / np.std(c))
    else:
        return 0, 0.0


def detect_q(img: np.ndarray, show: bool = False) -> float:
    """
    判断一个小图标（元素爆发图标）是否存在/就绪的匹配打分。

    参数:
    - img: 已裁切的小图（BGR），函数会内部缩放到 32x32 后进行匹配。
    - show: 若为 True，会显示中间可视化窗口（用于调试）。

    返回:
    - 匹配得分（float），越大表示越像平均 Q 图标（具体阈值需根据样本调整，历史上临界范围约在 [0.30,0.40]）。
    """
    if show:
        cv2.imshow("img", img)

    img32 = cv2.resize(img, (32, 32))
    edges = cv2.Canny(img32, 100, 200)

    # 尝试从模块目录读取 avg_Q.png（如果不存在，退回到全白权重以避免除 0）
    script_dir = os.path.dirname(__file__)
    avg_path = os.path.join(script_dir, "templates/avg_Q.png")
    avg_img = None
    if os.path.exists(avg_path):
        avg_img = cv2.imread(avg_path, 0)
    if avg_img is None:
        weights = np.ones((32, 32), np.uint8) * 255
    else:
        weights = cv2.inRange(avg_img, 175, 255)

    edges2 = np.zeros((32, 32), np.uint8)
    # 用边缘图与权重相乘的方式得到加权边缘
    for x in range(32):
        for y in range(32):
            edges2[x][y] = int(edges[x][y] / 255 * (weights[x][y] / 255)) * 255

    if show:
        cv2.imshow("weights", weights)
        cv2.imshow("edges", edges)
        cv2.imshow("edges2", edges2)
        cv2.waitKey(0)

    denom = np.sum(weights)
    if denom == 0:
        return 0.0
    return float(np.sum(edges2) / denom)


if __name__ == '__main__':
    # 示例/调试主入口
    # 说明：模块导出 `detect_Q` 和 `detect_q`，正常使用时请通过
    #    from detect import *
    # 然后在代码中直接调用 `detect_Q(img)` 与 `detect_q(img)`，其中 img 是已裁切好的截图区域。

    # 以下演示代码用于本地快速调试：遍历 data/1、data/0 两个文件夹，
    # 分别寻找最小/最大的 detect_q 得分并可视化（用于确定阈值）。
    folder_path = "data/1"
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".png"):
                file_list.append(os.path.join(root, file))

    min_q = 1.0
    for file in file_list:
        img = cv2.imread(file)
        score = detect_q(img)
        if min_q >= score:
            print(score)
            min_q = detect_q(img, show=True)

    folder_path = "data/0"
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".png"):
                file_list.append(os.path.join(root, file))

    max_q = 0.0
    for file in file_list:
        img = cv2.imread(file)
        score = detect_q(img)
        if max_q <= score:
            print(score)
            max_q = detect_q(img, show=True)

    print(min_q)
    print(max_q)