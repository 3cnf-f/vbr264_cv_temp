import cv2
import os

folder = "../145147cfr_mkv_test_few/"


timestamp_coords= (760,1000,1150,1060)

folder_contents= os.listdir(folder)
file = folder_contents[0]
img = cv2.imread(folder + file)
cv2.namedWindow(file,cv2.WINDOW_NORMAL)
cv2.imshow(file, img)
cv2.waitKey(0)
cv2.destroyAllWindows()
# 760 100 / 1150 1060
