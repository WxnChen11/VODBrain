import os
import sys
from datetime import datetime
import subprocess
import cv2
# from matplotlib import pyplot as plt
import numpy as np
import math

def generate_thumbs(date):
    if os.path.isdir("clips/" + str(date.date())):
        l = os.listdir("clips/" + str(date.date()))
        for f in l:
            if '_trim.mp4' not in f and '.jpeg' not in f:
                name = f[:-4]+"_thumb.jpeg"
                input = f[:-4] + "_trim.mp4"
                args = ['ffmpeg','-i', input, '-r', '1', '-vframes', '1', '-s', '1280x720', '-f', 'image2', name]
                p = subprocess.Popen(args, cwd="clips/" + str(date.date()))
                p.communicate()

def generate_thumb_from_file(filename, cwd="clips/"):
    name = filename + "_thumb.jpeg"
    input = filename + "_trim.mp4"
    args = ['ffmpeg','-i', input, '-r', '1', '-vframes', '1', '-s', '1280x720', '-f', 'image2', name]
    p = subprocess.Popen(args, cwd=cwd)
    p.communicate()
    return name
                   
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_thumbnail.py [yyyy-mm-dd]")
    else:
        y,m,d = map(int, sys.argv[1].split('-'))
        generate_thumbs(datetime(y,m,d))
