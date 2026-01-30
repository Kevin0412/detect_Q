import cv2
import numpy as np
import detect

#img=cv2.imread("avg_2.png")

img=cv2.imread("images_7/2.png")

#cv2.imshow("img",img[200:1000,2000:2560])

img1=img[323:394,2121:2192]
img2=img[451:522,2121:2192]
img3=img[579:650,2121:2192]
img4=img[707:778,2121:2192]

#img1=img[242:295,1591:1644]
#img2=img[338:391,1591:1644]
#img3=img[434:487,1591:1644]
#img4=img[530:583,1591:1644]

cv2.imshow("img1",img1)
cv2.imshow("img2",img2)
cv2.imshow("img3",img3)
cv2.imshow("img4",img4)

#img=cv2.imread("avg_3.png")

cv2.imshow("img",img[1222:1371,2351:2500])

cv2.waitKey(0)

imgs=[img[1222:1371,2351:2500],img1,img2,img3,img4]
for img5 in imgs:
    print(detect.detect_q(img5,show=True))

