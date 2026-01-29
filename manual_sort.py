import cv2
import numpy as np

import detect

for n in range(1,26):
    dirname="images_6"
    filename=str(n)+".png"
    img=cv2.imread(dirname+"/"+filename)
    imgs=[
        img[242:295,1591:1644],
        img[338:391,1591:1644],
        img[434:487,1591:1644],
        img[530:583,1591:1644]
    ]
    if detect.detect_Q(img[916:1028,1763:1875])[1]<5.4:
        img=cv2.imread(dirname+"/"+filename)
        imgs.append(img[916:1028,1763:1875])
    
    i=0
    for im in imgs:
        cv2.imshow('img',im)
        cv2.imshow('edges',cv2.Canny(cv2.resize(im,(32,32)), 100, 200))
        key=cv2.waitKey(0)&0xFF
        if key==ord('1'):
            cv2.imwrite("data/0/"+dirname+"_"+filename+"_"+str(i)+".png",im)
        elif key==ord('2'):
            cv2.imwrite("data/1/"+dirname+"_"+filename+"_"+str(i)+".png",im)
        i+=1