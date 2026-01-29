import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def detect_Q(img,m=2,n=2,show=False):
    if show:
        edges = cv2.Canny(cv2.resize(img,(32,32)), 100, 200)
        cv2.imshow("edges",edges)

    for i in range(img.shape[0]):
        img[i,:,0:1]=cv2.resize(img[i,int(img.shape[0]/2-((img.shape[0]-i)*i)**0.5):int(img.shape[0]/2+((img.shape[0]-i)*i)**0.5)+1,0],(1,img.shape[0]))
        img[i,:,1:2]=cv2.resize(img[i,int(img.shape[0]/2-((img.shape[0]-i)*i)**0.5):int(img.shape[0]/2+((img.shape[0]-i)*i)**0.5)+1,1],(1,img.shape[0]))
        img[i,:,2:3]=cv2.resize(img[i,int(img.shape[0]/2-((img.shape[0]-i)*i)**0.5):int(img.shape[0]/2+((img.shape[0]-i)*i)**0.5)+1,2],(1,img.shape[0]))
    if show:
        cv2.imshow("img",img)
        hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        cv2.imshow("hsv",hsv)
        cv2.waitKey(1)
    X=np.linspace(m, img.shape[0]-n-1, img.shape[0]-n-m)
    r=np.zeros((img.shape[0]-n-m),np.float64)
    g=np.zeros((img.shape[0]-n-m),np.float64)
    b=np.zeros((img.shape[0]-n-m),np.float64)
    for x in range(m,img.shape[0]-n):
        for y in range(img.shape[0]):
            b[x-m]+=img[x][y][0]/img.shape[0]
            g[x-m]+=img[x][y][1]/img.shape[0]
            r[x-m]+=img[x][y][2]/img.shape[0]
    a=0.299*r+0.587*g+0.114*b
    if show:
        plt.subplot(2, 1, 1)
        plt.plot(X, b,color='blue')
        plt.plot(X, g,color='green')
        plt.plot(X, r,color='red')
        plt.plot(X, a,color='grey')
    c=a[1:img.shape[0]-n-m]-a[0:img.shape[0]-n-m-1]
    if show:
        plt.subplot(2, 1, 2)
        plt.plot(X[0:img.shape[0]-n-m-1], c)
        plt.plot(X[0:img.shape[0]-n-m-1], np.zeros((img.shape[0]-n-m-1),np.float64)+np.mean(c))
        plt.plot(X[0:img.shape[0]-n-m-1], np.zeros((img.shape[0]-n-m-1),np.float64)+np.mean(c)+np.std(c))
        plt.show()
    #第二个值的临界区间为[4.59,6.21]
    #经计算器拟合，y=-0.00855878*x+0.968064109
    if np.std(c)>0:
        return np.argmax(c)+m,(np.max(c)-np.mean(c))/np.std(c)
    else:
        return 0,0

def detect_q(img,show=False):#临界范围[0.30,0.40]
    if show:
        cv2.imshow("img",img)
    img=cv2.resize(img,(32,32))
    edges = cv2.Canny(img, 100, 200)
    weights=cv2.inRange(cv2.imread("avg_Q.png",0),175,255)
    edges2=np.zeros((32,32),np.uint8)
    for x in range(32):
        for y in range(32):
            edges2[x][y]=int(edges[x][y]/255*weights[x][y])
    if show:
        #hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        cv2.imshow("weights",weights)
        #cv2.imshow("hsv",hsv)
        cv2.imshow("edges",edges)
        cv2.imshow("edges2",edges2)
        cv2.waitKey(0)
    return np.sum(edges2)/np.sum(weights)

if __name__=='__main__':
    #3雷 4火 6风 23水 29岩 51草 79冰
    #img=cv2.imread("images/1 (2).png")
    #img=cv2.imread("images_4/15_60.png")
    '''img=cv2.imread("images_5/1.png")
    print(detect_Q(img[916:1028,1763:1875]))

    print(detect_q(img[242:295,1591:1644]))
    print(detect_q(img[338:391,1591:1644]))
    print(detect_q(img[434:487,1591:1644]))
    print(detect_q(img[530:583,1591:1644]))'''

    '''for n in range(1,84):
        img=cv2.imread("images/1 ("+str(n)+").png")
        print(n)
        #print(detect_Q(img[916:1028,1763:1875]))
        print(detect_q(img[242:295,1591:1644]))
        print(detect_q(img[338:391,1591:1644]))
        print(detect_q(img[434:487,1591:1644]))
        print(detect_q(img[530:583,1591:1644]))'''
    
    folder_path = "data/1" # 将此处替换为要读取的文件夹路径
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".png"):
                file_list.append(os.path.join(root, file))
    min_q=1
    for file in file_list:
        img=cv2.imread(file)
        #print(detect_q(img))
        if min_q>=detect_q(img):
            print(detect_q(img))
            min_q=detect_q(img,show=True)
    folder_path = "data/0" # 将此处替换为要读取的文件夹路径
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".png"):
                file_list.append(os.path.join(root, file))
    max_q=0
    for file in file_list:
        img=cv2.imread(file)
        #print(detect_q(img))
        if max_q<=detect_q(img):
            print(detect_q(img))
            max_q=detect_q(img,show=True)
    print(min_q)
    print(max_q)