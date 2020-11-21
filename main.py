from PIL import Image
from PIL import ImageFilter
import random as r
import math as m
import time

def get_threshold(im): #determines the average value of a cropped image for convert_to_bw
    width,height = im.size
    pix = im.load()
    out = 0
    for w in range(width):
        for h in range(height):
            out += sum(pix[w,h])/3
    return out/(width*height)
def convert_to_bw(im,size):#returns image and list of pixels
    im = im.filter(ImageFilter.GaussianBlur(radius=1))
    pix = im.load()
    new = Image.new(mode = "RGB", size = (im.size[0], im.size[1]))
    new_pix = new.load()
    width,height = im.size
    local_w,local_h = [int(width/size),int(height/size)]
    thresholds = []
    for x in range(size):
        t = []
        for y in range(size):
            t.append(get_threshold(im.crop((x*local_w,y*local_h,(x+1)*local_w,(y+1)*local_h))))
        thresholds.append(t)
    for x in range(width):
        for y in range(height):
            t = thresholds[int(x*size/width)][int(y*size/height)]
            if sum(pix[x,y]) > 2.7*t:
                new_pix[x,y] = (255,255,255)
            else:
                new_pix[x,y] = (0,0,0)
    return new
def find_angle(im):  # given image, returns angle to rotate by finding scores of a sequence of angles
    newsize = (int(im.size[0]/4),int(im.size[1]/4))
    new = im.resize(newsize)
    pix = new.load()
    width,height = new.size
    out = {}
    for i in range(-5,6):
        rotated = new.rotate(i/2,fillcolor = 'white')
        result = find_lines(rotated,int(rotated.size[0]/100),int(rotated.size[1]/100),True,False)
        out[i/2] = result
    return max(out, key=out.get)
def filter(dict,min): #removes lines that are too close to each other from initial find_lines
    done = False
    while not done:
        done = True
        list = []
        for key in dict.keys():
            list.append(key)
        for i in range(len(list)-1):
            if list[i+1]-list[i]<min:
                done = False
                if list[i+1] in dict and list[i] in dict:
                    if dict[list[i+1]]>dict[list[i]]:
                        del dict[list[i]]
                    else:
                        del dict[list[i+1]]
    return dict
def find_lines(im,search,threshold,angle_flag = False,draw = False): #finds lines from rotated bw image. also outputs how good the lines are
    out = {}
    counts = []
    score = 0
    if draw:
        new = Image.new(mode = "RGB", size = (im.size[0], im.size[1]))
        new_pix = new.load()
    pix = im.load()
    width,height = im.size
    for h in range(height):
        count = 0
        for w in range(width):
            if pix[w,h] != (255,255,255):
                count += 1
        counts.append(count)
        if draw:
            for i in range(count):
                new_pix[i,h] = (255,0,0)
    if angle_flag:
        mean = sum(counts) / len(counts)
        return sum((i - mean) ** 2 for i in counts) / len(counts)
    for i in range(len(counts)-2):
        if counts[i] > counts[i+1] and counts[i+1] <= counts[i+2]:
            top = 0
            bot = height
            if i-search+1 > 0:
                top = i-search+1
            if i+search + 2<height:
                bot = i+search + 2
            #print(top,bot,counts[top:bot],counts[i+1],i+1)
            if counts[i+1] != 0:
                if max(counts[top:bot])/counts[i+1] > threshold:
                    out[i+1] = max(counts[top:bot])/counts[i+1]
            else:
                out[i+1] = max(counts[top:bot])
    out = filter(out,int(height/50))

    if draw:
        for el in out:
          for x in range(width):
              pix[x,el] = (255,0,0)
              new_pix[x,el] = (255,255,255)
        im.show()
        new.show()
    return list(out.keys())
def make_histogram(im,lines,draw = False):#returns 2d-array which is histogram of each line, also show convenient picture
    out = []
    if draw:
        new = Image.new(mode = "RGB", size = (im.size[0], im.size[1]))
        new_pix = new.load()
    pix = im.load()
    for i in range(len(lines)-1):
        list = []
        for x in range(im.size[0]):
            count = 0
            for y in range(lines[i],lines[i+1]):
                if pix[x,y] == (0,0,0):
                    count += 1
            list.append(count)
            if draw:
                for j in range(count):
                    new_pix[x,lines[i+1]-j] = (255,0,0)
        out.append(list)
    if draw:
        new.show()
    return out
def segment_line(line): #doesn't work, tries to get words from line
    out = []
    avg = int(sum(line)/len(line))
    open = False
    top,bot = [0,0]
    for h in range(len(line)):
        if not open and line[h] < avg:
            top = h
            open = True
        if open and line[h] > avg:
            bot = h
            #if bot-top > len(line)/50:
            out.append(int((top+bot)/2))
            open = False
    return out

start = time.time()
im = Image.open("sample3.jpg")
bw = convert_to_bw(im,10)

print("Covert to bw done in:",time.time() - start)
start = time.time()

angle = find_angle(bw)

print("Find angle",angle,"in:",time.time() - start)
start = time.time()

rotated = bw.rotate(angle,fillcolor = 'white')#rotates bw image
width,height = im.size
lines = find_lines(rotated,int(height/100),int(height/100),False,True)#y values of lines

print("Rotate and find lines done in:",time.time() - start)
start = time.time()

hist = make_histogram(rotated,lines)#list of histograms of each lines

print("Make histogram done in:",time.time() - start)
start = time.time()

'temp debugging'
'''for i in range(4):
    out = segment_line(hist[i])
    line_image = rotated.crop((0,lines[i],width,lines[i+1]))
    line_pix = line_image.load()
    for o in out:
        for h in range(line_image.size[1]):
            line_pix[o,h] = (255,0,0)
    line_image.show()
'''
