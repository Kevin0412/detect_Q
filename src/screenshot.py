import cv2
import numpy as np
import pyautogui

screenshot = pyautogui.screenshot()
# 将截图转换为OpenCV图像
frame = np.array(screenshot)

b,g,r = cv2.split(frame)
frame1= cv2.merge([r,g,b])

cv2.imshow("frame",frame1)
cv2.waitKey(0)