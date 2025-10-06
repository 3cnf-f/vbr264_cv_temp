import cv2
import os

folder = "../145147cfr_mkv_test_few/"

x=780
w=1150-x
y=1100
h=1060-y
timestamp_coords= (760,1000,1150,1060)

folder_contents= os.listdir(folder)
file = folder_contents[0]
img = cv2.imread(folder + file)
timestamp_cropped_img= img[y:y+h, x:x+w]
cv2.namedWindow(file+"-cropped",cv2.WINDOW_NORMAL)
cv2.imshow(file+"-cropped", timestamp_cropped_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
# 760 100 / 1150 1060
