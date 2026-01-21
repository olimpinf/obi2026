#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
#from scipy import signal
import sys

import cv2
import numpy as np
import peakutils
import scipy
import scipy.cluster.hierarchy as sch
import zbar

DRAW_CONTOURS = False
# expected sizes
HEIGHT_ANSWERS = 815
WIDTH_ANSWERS = 920
HEIGHT_REGISTRATION = 388
WIDTH_REGISTRATION = {3:172,4:228,5:284,6:340,7:420}
MIN_BAG = 3
EPSILON = 3
DEBUG = False
MIN_RADIUS = 9
MAX_RADIUS = 14
VSPACE = 35
HSPACE = 35

class Bag():
    def __init__(self,key,x,y,r):
        self.key = key
        self.x = x
        self.y = y
        self.r = r

def debug(s):
    if DEBUG:
        print(s)

def extract_qr(image):
    from PIL import Image
    # blur to smooth
    gray = cv2.GaussianBlur(image, (3, 3), 0)
    qr_num_digits=0
    qr_num_questions=0
    qr_id_check=False

    raw = Image.fromarray(gray)
    width, height = raw.size
    img = raw.tobytes()
    qrimage = zbar.Image(width, height, 'Y800', img)
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    scanner.scan(qrimage)
    data = ""
    for symbol in qrimage:
        #print('type =',symbol.type)
        #print('data =',symbol.data)
        #results
        if str(symbol.type)!='QRCODE':
            continue
        data=symbol.data
    # clean up
    del(qrimage)
    return data

def extract_qr_bottom(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    #cv2.imshow("blurred.png",gray)
    #cv2.waitKey(0)

    data = extract_qr(gray)
    data = data.split(';')
    if len(data)!=3:
        return 0,0,False
    qr_num_questions=int(data[0])
    qr_num_digits=int(data[1])
    qr_id_check=data[2]
    if qr_id_check=='Y':
        idcheck=True
    else:
        idcheck=False
    return qr_num_digits, qr_num_questions, qr_id_check

def get_id_from_qrcode(image):
    data = extract_qr(image)
    return data

def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y

def clean_circles(circles,output):
    import matplotlib.pyplot as plt

    xbags,ybags = {},{}
    # find max in x and y
    xmax,ymax = 0,0
    for (x, y, r) in circles:
        if x > xmax:
            xmax = x
        if y > ymax:
            ymax = y
    # build histogram in x and y
    # make a larger array so that peakutils works...
    xvals = np.zeros(xmax+100)
    yvals = np.zeros(ymax+100)
    #print(len(circles))
    for (x, y, r) in circles:
        xvals[x] += 1
        yvals[y] += 1
    #plt.plot(xvals)
    #plt.show()
    # find peaks
    MIN_DIST = 25
    xpeakind = peakutils.indexes(xvals, thres=0.1, min_dist=MIN_DIST)
    #plt.plot(xvals)
    #plt.plot(xpeakind, xvals[xpeakind], "x")
    #plt.show()
    ypeakind = peakutils.indexes(yvals, thres=0.1,min_dist=MIN_DIST)
    #plt.plot(yvals)
    #plt.plot(ypeakind, yvals[ypeakind], "x")
    #plt.show()

    #for x in xpeakind:
    #    for y in ypeakind:
    #        cv2.circle(output, (x, y), 11, (0,0,0), 1)
    #cv2.imshow("output.png",output)
    #cv2.waitKey(0)

    # build grid of circles to group ane existing neighbour circles
    grid = [[None for x in xpeakind] for y in ypeakind]
    avg_radius = 0
    avg_num = 0
    circles.sort()

    #for (x, y, r) in circles:
    #        cv2.circle(output, (x, y), 11, (0,0,0), 1)
    #cv2.imshow("output.png",output)
    #cv2.waitKey(0)

    #print(xpeakind)
    #print(ypeakind)
    MIN_DIST = 8
    for (x, y, r) in circles:
        foundx,foundy = -1,-1
        for i in range(len(xpeakind)):
            if (x <= (xpeakind[i]+MIN_DIST)) and (x >= xpeakind[i]-MIN_DIST):
                foundx = i
                break
        if foundx == -1:
            continue  # ignore this circle
        for j in range(len(ypeakind)):
            if (y <= (ypeakind[j]+MIN_DIST)) and (y >= ypeakind[j]-MIN_DIST):
                foundy = j
                break
        if foundy == -1:
            continue  # ignore this circle
        avg_radius += r 
        avg_num += 1 
        if grid[foundy][foundx] == None:
            grid[foundy][foundx] = (x, y, r)
        else:   
            # if more than one circle at close distance, choose one
            if (abs(x-xpeakind[foundx]) + abs(y-ypeakind[foundy])) <  (abs(grid[foundy][foundx][0]-xpeakind[foundx]) + abs(grid[foundy][foundx][1]-ypeakind[foundy])):
                # update
                grid[foundy][foundx] = (x, y, r)
                
    avg_radius = avg_radius/avg_num

    cleaned_circles = []
    for i in range(len(xpeakind)):
        for j in range(len(ypeakind)):
            if grid[j][i]:
                cleaned_circles.append((grid[j][i][0],grid[j][i][1],avg_radius))
                #cleaned_circles.append((xpeakind[i],ypeakind[j],avg_radius))
            else:
                cleaned_circles.append((xpeakind[i],ypeakind[j],avg_radius))

    #for (x, y, r) in cleaned_circles:
    #    cv2.circle(output, (x, y), 11, (255,0,0), 2)
    #for (x, y, r) in circles:
    #    cv2.circle(output, (x, y), 11, (0,255,0), 2)
    #cv2.imshow("output.png",output)
    #cv2.waitKey(0)
                
    return cleaned_circles

def confidence(a):
    dim=len(a)
    indexed_a=np.argsort(a)[::-1]
    best = indexed_a[0]
    D=scipy.zeros([dim,dim])
    # calculate distances
    for i in range(dim):
        for j in range(dim):
            D[i,j]=abs(a[i]-a[j])
    #links=sch.linkage(D,method="average")
    #links=sch.linkage(D,method="centroid")
    #links=sch.linkage(D,method="ward")
    links=sch.linkage(D,method="weighted")
    #links=sch.linkage(D,method="single")
    cdim=len(links)
    dist01=links[cdim-1][2] # distance singleton to last formed cluster
    #ret_conf=0.0
    ret_conf=dist01
    #print(dist01)
    #print >> sys.stderr, 'a', a
    #print >> sys.stderr, 'links ------------------', links[cdim-1][0]
    #for i in range(cdim):
    #    print >> sys.stderr,  links[i]
    if dist01<100: # empirical value! 
        debug(' * bad1, not enough difference from singleton to cluster ')
        return -1
    if links[cdim-1][0]>=dim:
        debug(' * bad2, cluster singleton number is not that of an element ')
        return -1
    if best!=links[cdim-1][0]:
        debug(' * bad3, best is not the singleton element ')
        return -1
    #if links[cdim-1][2]<3*links[cdim-2][2]:
    if 2*links[cdim-1][2]<3*links[cdim-2][2]:
        debug(' * bad 4, not enough distance between first and second ')
        return -1
    #print(ret_conf)
    return best

def rectify(h):
    h = h.reshape((4,2))
    hnew = np.zeros((4,2),dtype = np.float32)
    add = h.sum(1)
    hnew[0] = h[np.argmin(add)]
    hnew[2] = h[np.argmax(add)]
    diff = np.diff(h,axis = 1)
    hnew[1] = h[np.argmin(diff)]
    hnew[3] = h[np.argmax(diff)]
    return hnew

def detect_circles(dst):
    # detect circles in the image
    blurred = cv2.GaussianBlur(dst, (5, 5), 0)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 25,param1=40,param2=25,minRadius=MIN_RADIUS,maxRadius=MAX_RADIUS)
 
    # convert the (x, y) coordinates and radius of the circles to integers
    circles = np.round(circles[0, :]).astype("int")
    # return tuples so that sort works as expected
    circle_tuples = []
    for x,y,r in circles:
        circle_tuples.append((x,y,r))
    return circle_tuples

def detect_rectangles(image, numdig):
    # resize to original size
    image = cv2.resize(image, (1240, 1753))
    orig = image.copy()
    # convert to grayscale and blur to smooth
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    #blurred = cv2.medianBlur(gray, 5)

    # apply Canny Edge Detection
    edged = cv2.Canny(blurred, 0, 50)
    orig_edged = edged.copy()

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    (im, contours, hier) = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # get approximate contour for answer_area (largest)
    expected_area_answers = HEIGHT_ANSWERS*WIDTH_ANSWERS
    c_answer_area_idx = -1
    for c in contours:
        c_answer_area_idx += 1
        p = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * p, True)

        if len(approx) == 4:
            a = cv2.contourArea(approx)
            if a > 1.4*expected_area_answers: # rectangle is maybe the whole page?
                continue
            c_answer_area = c
            break
    target = approx
    #print(approx)
    #print(cv2.contourArea(approx),expected_area_answers)

    largest_area = cv2.contourArea(approx)
    # mapping target points to original dimensions (WIDTH_ANSWERSxHEIGHT_ANSWERS) 
    approx = rectify(approx)
    if numdig > 7:
        numdig = 7
    pts2 = np.float32([[0,0],[WIDTH_ANSWERS,0],[WIDTH_ANSWERS,HEIGHT_ANSWERS],[0,HEIGHT_ANSWERS]])
    M = cv2.getPerspectiveTransform(approx,pts2)
    dst1 = cv2.warpPerspective(orig,M,(WIDTH_ANSWERS,HEIGHT_ANSWERS))

    if DRAW_CONTOURS:
        cv2.drawContours(image, [target], -1, (0, 255, 0), 2)
        cv2.imshow("contours_answers.png",image)
        cv2.waitKey(0)

    # get approximate contour for registration_area (second largest)
    #print('idx',c_answer_area_idx)
    for c in contours[c_answer_area_idx+1:]:
        p = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * p, True)
        #cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)

        if len(approx) == 4:
            tmp = cv2.contourArea(approx)
            if tmp < largest_area*1.2 and tmp > largest_area*0.8:
                continue            # is same region as largest
            target = approx
            break
    if DRAW_CONTOURS:
        cv2.drawContours(image, [target], -1, (0, 255, 0), 2)
        cv2.imshow("contours_reg.png",image)
        cv2.waitKey(0)

    # mapping target points to original dimensions (WIDTH_ANSWERSxHEIGHT_ANSWERS) 
    approx = rectify(target)
    pts2 = np.float32([[0,0],[WIDTH_REGISTRATION[numdig],0],[WIDTH_REGISTRATION[numdig],HEIGHT_REGISTRATION],[0,HEIGHT_REGISTRATION]])
    M = cv2.getPerspectiveTransform(approx,pts2)
    dst2 = cv2.warpPerspective(orig,M,(WIDTH_REGISTRATION[numdig],HEIGHT_REGISTRATION))
    #cv2.imshow("contours.png",dst2)
    #cv2.waitKey(0)

    return cv2.cvtColor(dst1, cv2.COLOR_BGR2GRAY),cv2.cvtColor(dst2, cv2.COLOR_BGR2GRAY)

def get_id_column(column, circles, thresh_img, output):
    avalues = []
    for i in range(0,10):
        x, y, r = circles[column*10+i]
            #print('draw circle',x,y,r)
        #cv2.circle(output, (x, y), r, (255, 255, 255), 1)
        #cv2.rectangle(output, (x-r-EPSILON, y-r-EPSILON),(x+r+EPSILON,y+r+EPSILON), (0, 0, 255), 1)
        #cv2.imshow("output.png", output)
        #cv2.waitKey(0)
        crop = thresh_img[ y-r-EPSILON:EPSILON+r+y,x-r-EPSILON:EPSILON+r+x]
        h,w = crop.shape[:2]
        avalues.append(int(np.sum(crop)/(h*w)))
    best = confidence(avalues)
    return(best)

def get_id_from_circles(num_digits, id_check, circles, thresh_img, output):
    if id_check=='Y':
        check = 1
    else:
        check = 0
    if (num_digits+check)*10 != len(circles):
        print('incorrect number of circles found', num_digits, id_check ,len(circles))
        return ''
    id_vals = []
    for i in range(num_digits+check):
        id_vals.append(get_id_column(i,circles,thresh_img,output))
    id = ''
    for i in range(num_digits):
        id += chr(ord('0')+id_vals[i])
    if id_check=='Y':
        id += "-"+chr(ord('A')+id_vals[-1])
    return id

def get_answers_batch(rows, start, num, circles, thresh_img, output):
    answers = []
    for i in range(num):
        avalues = []
        for j in range(0,5):
            x, y, r = circles[start+i+num*j*rows]
            #print('draw circle',x,y,r)
            #cv2.circle(output, (x, y), r, (255, 255, 255), 1)
            #cv2.rectangle(output, (x-r-EPSILON, y-r-EPSILON),(x+r+EPSILON,y+r+EPSILON), (0, 0, 255), 1)
            #cv2.imshow("output.png", output)
            #cv2.waitKey(0)
            crop = thresh_img[ y-r-EPSILON:EPSILON+r+y,x-r-EPSILON:EPSILON+r+x]
            h,w = crop.shape[:2]
            avalues.append(int(np.sum(crop)/(h*w)))
        #print(avalues)
        debug("%d" % (i+1))
        best = confidence(avalues)
        answers.append(best)
    return(answers)

def get_answers(num_questions, circles, thresh_img, output):
    # sheet with 25, 50 and 70 questions are not full, but circles are added in processing
    num_expected_circles = {5:25,10:50,15:75,20:100,25:150,30:150,40:200,50:300,60:300,70:400,80:400}
    if num_expected_circles[num_questions] != len(circles):
        print('incorrect number of circles found', num_questions,len(circles))
        sys.exit(-1)
    answers = []
    if num_questions == 10:
        # 1-10
        answers += get_answers_batch(1, 0, 10, circles, thresh_img, output)
    elif num_questions == 15:
        # 1-5
        answers += get_answers_batch(1, 0, 5, circles, thresh_img, output)
        # 6-10
        answers += get_answers_batch(1, 25, 5, circles, thresh_img, output)
        # 11-15
        answers += get_answers_batch(1, 50, 5, circles, thresh_img, output)
    elif num_questions == 20:
        # 1-10
        answers += get_answers_batch(1, 0, 10, circles, thresh_img, output)
        # 11-20
        answers += get_answers_batch(1, 50, 10, circles, thresh_img, output)
    elif num_questions == 25:
        # 1-10
        answers += get_answers_batch(1, 0, 10, circles, thresh_img, output)
        # 11-20
        answers += get_answers_batch(1, 50, 10, circles, thresh_img, output)
        # 21-25
        answers += get_answers_batch(1, 100, 5, circles, thresh_img, output)
    elif num_questions == 30:
        # 1-10
        answers += get_answers_batch(1, 0, 10, circles, thresh_img, output)
        # 11-20
        answers += get_answers_batch(1, 50, 10, circles, thresh_img, output)
        # 21-30
        answers += get_answers_batch(1, 100, 10, circles, thresh_img, output)
    elif num_questions == 40:
        # 1-10
        answers += get_answers_batch(2, 0, 10, circles, thresh_img, output)
        # 11-20
        answers += get_answers_batch(2, 100, 10, circles, thresh_img, output)
        # 21-30
        answers += get_answers_batch(2, 10, 10, circles, thresh_img, output)
        # 11-40
        answers += get_answers_batch(2, 110, 10, circles, thresh_img, output)
    elif num_questions == 50:
        # 1-10
        answers += get_answers_batch(2, 0, 10, circles, thresh_img, output)
        # 11-20
        answers += get_answers_batch(2, 100, 10, circles, thresh_img, output)
        # 21-30
        answers += get_answers_batch(2, 200, 10, circles, thresh_img, output)
        # 31-40
        answers += get_answers_batch(2, 10, 10, circles, thresh_img, output)
        # 41-50
        answers += get_answers_batch(2, 210, 10, circles, thresh_img, output)
    elif num_questions == 60:
        # 1-10
        answers += get_answers_batch(2, 0, 10, circles, thresh_img, output)
        # 11-20
        answers += get_answers_batch(2, 100, 10, circles, thresh_img, output)
        # 21-30
        answers += get_answers_batch(2, 200, 10, circles, thresh_img, output)
        # 31-40
        answers += get_answers_batch(2, 10, 10, circles, thresh_img, output)
        # 41-50
        answers += get_answers_batch(2, 110, 10, circles, thresh_img, output)
        # 51-60
        answers += get_answers_batch(2, 210, 10, circles, thresh_img, output)
    elif num_questions == 70:
        # 1-10
        answers += get_answers_batch(2, 0, 10, circles, thresh_img, output)
        # 11-20
        answers += get_answers_batch(2, 100, 10, circles, thresh_img, output)
        # 21-30
        answers += get_answers_batch(2, 200, 10, circles, thresh_img, output)
        # 31-40
        answers += get_answers_batch(2, 300, 10, circles, thresh_img, output)
        # 41-50
        answers += get_answers_batch(2, 10, 10, circles, thresh_img, output)
        # 51-60
        answers += get_answers_batch(2, 110, 10, circles, thresh_img, output)
        # 61-70
        answers += get_answers_batch(2, 210, 10, circles, thresh_img, output)
    elif num_questions == 80:
        # 1-10
        answers += get_answers_batch(2, 0, 10, circles, thresh_img, output)
        # 11-20
        answers += get_answers_batch(2, 100, 10, circles, thresh_img, output)
        # 21-30
        answers += get_answers_batch(2, 200, 10, circles, thresh_img, output)
        # 31-40
        answers += get_answers_batch(2, 300, 10, circles, thresh_img, output)
        # 41-50
        answers += get_answers_batch(2, 10, 10, circles, thresh_img, output)
        # 51-60
        answers += get_answers_batch(2, 110, 10, circles, thresh_img, output)
        # 61-70
        answers += get_answers_batch(2, 210, 10, circles, thresh_img, output)
        # 71-80
        answers += get_answers_batch(2, 310, 10, circles, thresh_img, output)
    else:
        print('not implemented',num_questions)
    return answers

def process(expected_num_questions, image):
    # get bottom qr and extract sheet info
    (h,w,d) = image.shape
    crop = image[3*h/4:,:w/3,:]
    #cv2.imshow("output.png",crop)
    #cv2.waitKey(0)
    num_digits, num_questions, id_check = extract_qr_bottom(crop)
    if num_digits == 0:  # try rotating the sheet
        M = cv2.getRotationMatrix2D((w/2,h/2),180,1)
        dst = cv2.warpAffine(image,M,(w,h))
        crop = dst[3*h/4:,:w/4,:]
        #cv2.imshow("output.png",crop)
        #cv2.waitKey(0)
        num_digits, num_questions, id_check = extract_qr_bottom(crop)
        image = dst
    if num_digits == 0:  # bail out
        return '00000','erro ao processar a folha, falta qrcode'
    if num_questions != expected_num_questions:  # bail out
        return '00000','erro ao processar a folha, numero de questoes inesperado'
    if id_check=='Y':
        ndig = num_digits+1
    else:
        ndig = num_digits
    # detect two main rectangles
    answer_area,reg_area = detect_rectangles(image,ndig)

    ###################################################
    # process registration id
    if ndig > 7:
        id = get_id_from_qrcode(reg_area)
    else:
        #output = reg_area.copy()
        #cv2.imshow("output.png",output)
        #cv2.waitKey(0)
        circles_reg_area = detect_circles(reg_area)
        #output = cv2.cvtColor(reg_area, cv2.COLOR_GRAY2RGB)
        #for x,y,r in circles_reg_area:
        #    cv2.circle(output, (x, y), r, (0,0,0), 2)
        #print('circles in reg area')
        #cv2.imshow("output.png",output)
        #cv2.waitKey(0)
        #print('found',len(circles_reg_area))
        reg_circles = clean_circles(circles_reg_area,reg_area)
        #print('after first clean',len(reg_circles))
        #for x,y,r in reg_circles:
        #    cv2.circle(output, (x, y), r, (0,0,0), 2)
        #cv2.imwrite("output.png", output)
        #cv2.imshow("output.png",output)
        #cv2.waitKey(0)
        thresh_val,thresh_img = cv2.threshold(reg_area, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        #cv2.imshow("orig.png",thresh_img)
        #cv2.waitKey(0)
        # erase circunferences
        for x,y,r in reg_circles:
            cv2.circle(thresh_img, (x, y), r, (0,0,0), 2)
        #cv2.imshow("circles.png",thresh_img)
        #cv2.waitKey(0)
        # erode and dilate to clean up
        kernel = np.ones((3,3), np.uint8)
        thresh_img = cv2.erode(thresh_img, kernel, iterations=1)
        #cv2.imshow("erosion.png",thresh_img)
        #cv2.waitKey(0)
        thresh_img = cv2.dilate(thresh_img, kernel, iterations=2)
        #cv2.imshow("dilate.png",thresh_img)
        #cv2.waitKey(0)
        id = get_id_from_circles(num_digits, id_check, reg_circles, thresh_img, reg_area)
        #cv2.imwrite("output.png", output)
        #cv2.imshow("output.png",output)
        #cv2.waitKey(0)
    #print('id',id)

    ###################################################
    # process answers
    output = cv2.cvtColor(answer_area, cv2.COLOR_GRAY2RGB)
    circles_answer_area = detect_circles(answer_area)
    #print('found',len(circles_answer_area))
    #for x,y,r in circles_answer_area:
    #    cv2.circle(output, (x, y), r, (0,0,0), 2)
    #cv2.imshow("output.png",output)
    #cv2.waitKey(0)
    answer_circles = clean_circles(circles_answer_area,output)
    #print('after first clean',len(answer_circles))
    #answer_circles = clean_circles(answer_circles,output)
    #output = answer_area.copy()
    #for x,y,r in answer_circles:
    #    cv2.circle(output, (x, y), r, (0,0,0), 2)
    #cv2.imshow("output.png",output)
    #cv2.waitKey(0)
    thresh_val,thresh_img = cv2.threshold(answer_area, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    #cv2.imshow("orig.png",thresh_img)
    #cv2.waitKey(0)
    # erase circunferences
    for x,y,r in answer_circles:
        cv2.circle(thresh_img, (x, y), r, (0,0,0), 2)
    #cv2.imshow("circles.png",thresh_img)
    #cv2.waitKey(0)
    # erode and dilate to clean up
    kernel = np.ones((3,3), np.uint8)
    thresh_img = cv2.erode(thresh_img, kernel, iterations=1)
    #cv2.imshow("erosion.png",thresh_img)
    #cv2.waitKey(0)
    thresh_img = cv2.dilate(thresh_img, kernel, iterations=2)
    answers = get_answers(num_questions, answer_circles, thresh_img, output)
    for x,y,r in answer_circles:
        cv2.circle(thresh_img, (x, y), r, (255,255,255), 1)
    #cv2.imshow("dilate.png",thresh_img)
    #cv2.waitKey(0)
    #cv2.imwrite("output.png", output)
    #cv2.imshow("output.png",output)
    #cv2.waitKey(0)
    i = 1
    result = {-1:'X', 0:'A', 1:'B', 2:'C', 3:'D', 4:'E' }
    result_txt=''
    for a in answers:
        result_txt += '{}. {}\n'.format(i, result[a])
        i += 1
    return id,result_txt

def usage():
    print('usage: %s ' % sys.argv[0])
    sys.exit(-1)

if __name__=="__main__":

    if len(sys.argv) < 2:
        usage()
    try:
        num_questions = int(sys.argv[1])
    except:
        usage()

    for infile in sys.argv[2:]:
        #log('Processing %s' % infile)
        image = cv2.imread(infile)
        print("processing {} ...".format(infile),file=sys.stderr)
        try:
            id, result_log = process(num_questions, image)
        except:
            result_log = "Erro ao processar arquivo {}".format(infile)
            id = '000000'
            print("******ERROR", file=sys.stderr)
        print("id={}, result_log={}".format(id,result_log), file=sys.stderr)
        homedir=os.path.dirname(infile)
        if homedir=='':
            homedir='.'
        resultdir=os.path.join(homedir, "result")
        if not os.path.exists(resultdir):
            try:
                os.mkdir(resultdir)
            except:
                print("cannot create result dir!!",file=sys.stderr)
                sys.exit(-1)
        
        if id.find('*') >= 0:
            num_id = '000000'
        else:
            num_id = id
        name = os.path.splitext(os.path.basename(infile))[0]
        result_name='%s_%s.txt' % (num_id,name)
        with open(os.path.join(resultdir,result_name),'w') as tmpf:
            tmpf.write('RA {}\n'.format(id)+result_log)
