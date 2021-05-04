from pdf2image import convert_from_path
import os
import cv2
import numpy as np
from cv2 import VideoWriter, VideoWriter_fourcc
# import moviepy.editor as mpy

def colorLerp(a: list, b: list, t: float):
    if len(a) != len(b):
        raise ValueError("array size mismatch")
    out = []
    for i in range(len(a)):
        out.append( int(b[i] + (( a[i] - b[i] )*t)) )
    return out

# convert pages of pdf to images
pdfPages = convert_from_path("Symphony_Orchestra_Concert.pdf")
images = []
for i in range(len(pdfPages)):
    pageFile = 'page'+ str(i) +'.jpg'
    pdfPages[i].save(pageFile, 'JPEG')
    img = cv2.imread(pageFile)
    if len(img) == 0:
        print ("error")
        exit()
    images.append(img)

# all images are assumed to be the same size, so get dimensions from last page thats still in memory
imgH = len(img)
imgW = len(img[0])

color_correct = 0
# color correction
if color_correct == 1:
    for img in range(len(images)):
        for y in range(len(images[img])):
            for x in range(len(images[img][y])):
                v = images[img][y][x]
                sum = 0
                for colors in v:
                    sum = sum + colors
                color = int(255 - (sum/3))
                images[img][y][x] = [0,0,color]
        print("corrected page ", img+1, "/", len(images), sep='')
        cv2.imwrite("./colored_page" + str(img) + ".jpg", images[img])

images = []
for i in range(len(pdfPages)):
    pageFile = "./colored_page" + str(i) + ".jpg"
    img = cv2.imread(pageFile)
    if not img.any():
        print ("error, cannot open colored images")
        exit()
    images.append(img)

image_trim = 1
# image trimming : (topTrim, bottomTrim)
if image_trim == 1:
    imageTrimTuple = [ (0,200), (250,300), (50,400), (0,0), (0,1000) ]

    for i in images:
        print(i.shape)

    i = 0
    for t in imageTrimTuple:
        images[i] = images[i][t[0]:len(images[i])-t[1]]
        i = i+1
    print("----")
    for i in images:
        print(i.shape)

width = 1920
height = 1080
FPS = 30
# seconds = 10

fourcc = VideoWriter_fourcc(*'mp4v')
video = VideoWriter('./output3.mp4', fourcc, float(FPS), (width, height))

background = np.zeros((height, width, 3), dtype = np.uint8)
# background.fill(255)

backgroundOffset = int((width-imgW)/2)
verticalShift = 0
verticalSpeed = 3

currentImage = 0
foreground = np.zeros( (height, imgW, 3), dtype = np.uint8 )  # initialize to blank image

endFlag = False
while True:
    if verticalShift + height > len(foreground): # check bounds
        if endFlag: # if we reach end of foreground after reaching the final image, complete 
            break
        print("translating page ", currentImage+1, "/", len(images), sep='')    #log
        if currentImage == len(pdfPages)-1:    # check for last image, draw blank screen
            foreground = np.concatenate( (foreground, np.zeros( (height, imgW, 3), dtype = np.uint8 )), axis = 0)
            endFlag = True
        else:   # if there is another image to display, append to foreground
            foreground = np.concatenate( (foreground, images[currentImage]), axis = 0)
            currentImage = currentImage + 1
    # write frame to video, translating foreground each iteration
    frame = np.concatenate( (background[:, :backgroundOffset, :], foreground[verticalShift : (height + verticalShift), :, :], background[:, (backgroundOffset+imgW):, :]), axis = 1)
    video.write(frame)
    verticalShift = verticalShift + verticalSpeed

video.release()

# # clean up, delete image files
# for i in range(len(images)):
#     os.remove('page'+ str(i) +'.jpg')