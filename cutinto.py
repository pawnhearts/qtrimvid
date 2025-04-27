#!/usr/bin/env python
import sys, os
from pathlib import Path
from subprocess import Popen, PIPE

import cv2

def compare(img1, img2):

    # Convert it to HS
    img1_hsv = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
    img2_hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

    # Calculate the histogram and normalize it
    hist_img1 = cv2.calcHist([img1_hsv], [0,1], None, [180,256], [0,180,0,256])
    cv2.normalize(hist_img1, hist_img1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX);
    hist_img2 = cv2.calcHist([img2_hsv], [0,1], None, [180,256], [0,180,0,256])
    cv2.normalize(hist_img2, hist_img2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX);

    # find the metric value
    return cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_BHATTACHARYYA)


fpath = sys.argv[-1]
tmp_path = Path(fpath)
tmp_path = str(tmp_path.parent / f'_{tmp_path.name}')
cap = cv2.VideoCapture(fpath)
fps = cap.get(cv2.CAP_PROP_FPS)

res, frame = cap.read()
prev = None
count = 0

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        #cv2.imwrite('frame{:d}.jpg'.format(count), frame)
        if prev is not None and compare(prev, frame) > 0.9:
            #print(f'Frame {count} compareHist :{compare(prev, frame)}')
            print('Cutting first', count//fps)
            ps = Popen(['ffmpeg',
                     '-i',
                   fpath,
                     '-ss',
                    str(count//fps),
                     '-vcodec',
                     'copy',
                     '-acodec',
                     'copy',
                     tmp_path], stdout=PIPE)
            ret = ps.wait()
            if ret == 0:
                os.rename(tmp_path, fpath)
            elif os.path.exists(tmp_path):
                os.unlink(tmp_path)

            sys.exit(ret)

        count += fps # i.e. at 30 fps, this advances one second
        cap.set(cv2.CAP_PROP_POS_FRAMES, count)
        prev = frame
        if count//fps > 20:
            sys.exit(1)
    else:
        cap.release()
        break
