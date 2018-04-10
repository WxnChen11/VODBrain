import os
import sys
from datetime import datetime
import subprocess
import cv2
# from matplotlib import pyplot as plt
import numpy as np
import math

EUCLID_DIST_THRESHOLD = 20 #px
STRAIGHT_OFFSET_THRESHOLD = 8 #px

def analyze_thumbs(date):
    if os.path.isdir("clips/" + str(date.date())):
        l = os.listdir("clips/" + str(date.date()))
        os.chdir("clips/" + str(date.date()))

        kernel = np.ones((5,5),np.uint8)

        for f in l:
            if '.jpeg' in f:
                print(f)
                img = cv2.imread(f,1)[0:250, -200:-1]

                edges = cv2.Canny(img,15,150) #20,255
                lines = cv2.HoughLines(edges, 1, np.pi / 180, 150, None, 0, 0)
                cdst = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                cdstP = np.copy(cdst)

                
                if lines is not None:
                    for i in range(0, len(lines)):
                        rho = lines[i][0][0]
                        theta = lines[i][0][1]
                        a = math.cos(theta)
                        b = math.sin(theta)
                        x0 = a * rho
                        y0 = b * rho
                        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
                        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
                        angle = np.arctan2(pt2[1] - pt1[1], pt2[0] - pt1[0]) * 180. / np.pi
                        if angle % 90 < 1:
                            cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
                
                
                linesP = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, None, 150, 50)

                p1 = (23,8)
                p2 = (190,175)

                p1_2 = (2,10)
                p2_2 = (190,193)

                r1 = (p1[0], p1[1])
                r2 = (p2[0], p1[1])
                r3 = (p2[0], p2[1])
                r4 = (p1[0], p2[1])

                edges_satisfied = [(r1,r2),(r2,r3),(r3,r4),(r4,r1)]
                matched = set()
                matched_2 = set()

                if linesP is not None:
                    for i in range(0, len(linesP)):
                        l = linesP[i][0]
                        angle = np.arctan2(l[3] - l[1], l[2] - l[0]) * 180. / np.pi
                        if angle % 90 < 1:
                            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (255,0,255), 2, cv2.LINE_AA)
                            # if min(euclid_dist((l[0], l[1]), edges[0]), euclid_dist((l[2], l[3]), edges[0])) + min(euclid_dist((l[0], l[1]), edges[1]), euclid_dist((l[2], l[3]), edges[1])) < EUCLID_DIST_THRESHOLD:
                            # if min(l[0]-p1[0],l[0]-p2[0],l[2]-p1[0],l[2]-p2[0],l[1]-p1[1],l[1]-p2[1],l[3]-p1[1],l[3]-p2[1]) < 
                            if abs(l[0]-l[2])<5: #vertical line
                                if abs((l[0]+l[2])/2-p1[0]) < STRAIGHT_OFFSET_THRESHOLD:
                                    matched.add(0)
                                    cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                                elif abs((l[0]+l[2])/2-p2[0]) < STRAIGHT_OFFSET_THRESHOLD:
                                    matched.add(1)
                                    cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                            else:
                                if abs((l[1]+l[3])/2-p1[1]) < STRAIGHT_OFFSET_THRESHOLD:
                                    matched.add(2)
                                    cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                                elif abs((l[1]+l[3])/2-p2[1]) < STRAIGHT_OFFSET_THRESHOLD:
                                    matched.add(3)
                                    cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)

                print("MATCHES_1",len(matched))

                if linesP is not None:
                    for i in range(0, len(linesP)):
                        l = linesP[i][0]
                        angle = np.arctan2(l[3] - l[1], l[2] - l[0]) * 180. / np.pi
                        if angle % 90 < 1:
                            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (255,0,255), 2, cv2.LINE_AA)
                            # if min(euclid_dist((l[0], l[1]), edges[0]), euclid_dist((l[2], l[3]), edges[0])) + min(euclid_dist((l[0], l[1]), edges[1]), euclid_dist((l[2], l[3]), edges[1])) < EUCLID_DIST_THRESHOLD:
                            # if min(l[0]-p1_2[0],l[0]-p2_2[0],l[2]-p1_2[0],l[2]-p2_2[0],l[1]-p1_2[1],l[1]-p2_2[1],l[3]-p1_2[1],l[3]-p2_2[1]) < 
                            if abs(l[0]-l[2])<5: #vertical line
                                if abs((l[0]+l[2])/2-p1_2[0]) < STRAIGHT_OFFSET_THRESHOLD:
                                    matched_2.add(0)
                                    cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                                elif abs((l[0]+l[2])/2-p2_2[0]) < STRAIGHT_OFFSET_THRESHOLD:
                                    matched_2.add(1)
                                    cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                            else:
                                if abs((l[1]+l[3])/2-p1_2[1]) < STRAIGHT_OFFSET_THRESHOLD:
                                    matched_2.add(2)
                                    cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                                elif abs((l[1]+l[3])/2-p2_2[1]) < STRAIGHT_OFFSET_THRESHOLD:
                                    matched_2.add(3)
                                    cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)

                print("MATCHES_2",len(matched_2))

                # cv2.line(cdstP, (p1_2[0], p1_2[1]), (p1_2[0], p2_2[1]), (0,255,0), 2, cv2.LINE_AA)
                # cv2.line(cdstP, (p1_2[0], p2_2[1]), (p2_2[0], p2_2[1]), (0,255,0), 2, cv2.LINE_AA)
                # cv2.line(cdstP, (p2_2[0], p2_2[1]), (p2_2[0], p1_2[1]), (0,255,0), 2, cv2.LINE_AA)
                # cv2.line(cdstP, (p2_2[0], p1_2[1]), (p1_2[0], p1_2[1]), (0,255,0), 2, cv2.LINE_AA)

                cv2.imshow("Source", img)
                cv2.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
                cv2.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)

                k = cv2.waitKey(0)
                if k == 27:         # wait for ESC key to exit
                    cv2.destroyAllWindows()

                # return

                # plt.subplot(121),plt.imshow(img,cmap = 'gray')
                # plt.title('Original Image'), plt.xticks([]), plt.yticks([])
                # plt.subplot(122),plt.imshow(edges,cmap = 'gray')
                # plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

                # plt.show()

                # cv2.imshow('image',edges)

def analyze_thumbnail_from_file_and_delete(filename, cwd="clips/"):

    # RETURNS TRUE IF DIDN'T DELETE THE FILE

    owd = os.getcwd()
    os.chdir(cwd)
    print("FILENAME",filename, cwd)
    img = cv2.imread(filename,1)[0:250, -200:-1]

    edges = cv2.Canny(img,15,150)
    cdst = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cdstP = np.copy(cdst)
        
    linesP = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, None, 150, 50)

    p1 = (23,8)
    p2 = (190,175)

    p1_2 = (2,10)
    p2_2 = (190,193)

    r1 = (p1[0], p1[1])
    r2 = (p2[0], p1[1])
    r3 = (p2[0], p2[1])
    r4 = (p1[0], p2[1])

    edges_satisfied = [(r1,r2),(r2,r3),(r3,r4),(r4,r1)]
    matched = set()
    matched_2 = set()

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            angle = np.arctan2(l[3] - l[1], l[2] - l[0]) * 180. / np.pi
            if angle % 90 < 1:
                if abs(l[0]-l[2])<5: #vertical line
                    if abs((l[0]+l[2])/2-p1[0]) < STRAIGHT_OFFSET_THRESHOLD:
                        matched.add(0)
                        cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (255,0,0), 2, cv2.LINE_AA)
                    elif abs((l[0]+l[2])/2-p2[0]) < STRAIGHT_OFFSET_THRESHOLD:
                        matched.add(1)
                        cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,255,0), 2, cv2.LINE_AA)
                else:
                    if abs((l[1]+l[3])/2-p1[1]) < STRAIGHT_OFFSET_THRESHOLD:
                        matched.add(2)
                        cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                    elif abs((l[1]+l[3])/2-p2[1]) < STRAIGHT_OFFSET_THRESHOLD:
                        matched.add(3)
                        cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (255,255,255), 2, cv2.LINE_AA)

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            angle = np.arctan2(l[3] - l[1], l[2] - l[0]) * 180. / np.pi
            if angle % 90 < 1:
                cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (255,0,255), 2, cv2.LINE_AA)
                # if min(euclid_dist((l[0], l[1]), edges[0]), euclid_dist((l[2], l[3]), edges[0])) + min(euclid_dist((l[0], l[1]), edges[1]), euclid_dist((l[2], l[3]), edges[1])) < EUCLID_DIST_THRESHOLD:
                # if min(l[0]-p1_2[0],l[0]-p2_2[0],l[2]-p1_2[0],l[2]-p2_2[0],l[1]-p1_2[1],l[1]-p2_2[1],l[3]-p1_2[1],l[3]-p2_2[1]) < 
                if abs(l[0]-l[2])<5: #vertical line
                    if abs((l[0]+l[2])/2-p1_2[0]) < STRAIGHT_OFFSET_THRESHOLD:
                        matched_2.add(0)
                        cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                    elif abs((l[0]+l[2])/2-p2_2[0]) < STRAIGHT_OFFSET_THRESHOLD:
                        matched_2.add(1)
                        cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                else:
                    if abs((l[1]+l[3])/2-p1_2[1]) < STRAIGHT_OFFSET_THRESHOLD:
                        matched_2.add(2)
                        cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)
                    elif abs((l[1]+l[3])/2-p2_2[1]) < STRAIGHT_OFFSET_THRESHOLD:
                        matched_2.add(3)
                        cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 2, cv2.LINE_AA)

    if len(matched) < 2 and len(matched_2) < 2:
        print(filename[:-11])
        files = os.listdir()
        for f in files:
            if filename[:-11] in f:
               os.remove(f)
        os.chdir(owd)
        return False

    os.chdir(owd)
    return True

def euclid_dist(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_thumbnail.py [yyyy-mm-dd]")
    else:
        y,m,d = map(int, sys.argv[1].split('-'))
        analyze_thumbs(datetime(y,m,d))