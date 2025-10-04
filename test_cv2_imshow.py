import cv2
import lib_google_ocr as l_gocr
import json



with open('../144850_out/144850_vfr__vbr_ocr.json', 'r') as f:
    json_data = json.load(f)
    framelist=json_data

print(framelist.keys())
relevant_ocr=framelist['512']["google_ocr"]
print(relevant_ocr)
img = cv2.imread('../144850_out/144850_vfr_000512.png')
l_gocr.box_around_words(img, relevant_ocr)
cv2.imshow('test', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
