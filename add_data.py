import cv2
import numpy as np
import os

folder_path = "data/1" # 将此处替换为要读取的文件夹路径
file_list = []
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(".png"):
            file_list.append(os.path.join(root, file))
img=np.zeros((32,32),np.float)
img2=np.zeros((32,32),np.float)
for file in file_list:
    img1=cv2.imread(file)
    img1=cv2.resize(img1,(32,32))
    img1=cv2.Canny(img1,100,200)
    img+=img1.astype(np.float)
    img2+=img1.astype(np.float)*img1.astype(np.float)
img/=len(file_list)
img2/=len(file_list)
img2-=img*img
img2=np.sqrt(img2)*2
cv2.imwrite('avg_Q.png',img)
cv2.imwrite('avg1_Q.png',img2)
