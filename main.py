from PIL import Image
from PIL import ImageFilter
import random as r
import math as m

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
    #im.show()
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
def find_angle(pix, samples):  # given black and white pixels and list of samples, returns angle to rotate by
    # to go r distance in the direction theta add r*cos(theta) to x val, and r*sin(theta) to y val
    # (100,100). (100+r*cos(30),100+r*sin(30))
    #pix[x,y]
    r = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    angles = [i for i in range(361)]
    sample_size = 50
    percent = 0
    bool_list =[]
    ang_bool_list = [0] * 360
    samp_list = [0] * sample_size
    for samp in samples:
        for ang in angles:
            boolean = True
            for i in r:
                if pix((round(i * m.cos(m.radians(ang))) + samp[0]), (round(i * m.sin(m.radians(ang))) + samp[0])) == (
                        0, 0, 0):
                    boolean = False
            bool_list.append(boolean)
            if bool_list[ang - 1]:
                ang_bool_list[ang] += 1
        samp_list[samp] += ang_bool_list[samp]
    elm_num = samp_list.index(max(samp_list))
    return angles[elm_num]
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
def find_lines(im,search,threshold): #finds lines from rotated bw image
    out = {}
    counts = []
    new = Image.new(mode = "RGB", size = (im.size[0], im.size[1]))
    new_pix = new.load()
    pix = im.load()
    width,height = im.size
    for h in range(height):
        count = 0
        for w in range(width):
            if pix[w,h] == (0,0,0):
                count += 1
        counts.append(count)
        for i in range(count):
            new_pix[i,h] = (255,0,0)
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
    for el in out:
      for x in range(width):
          pix[x,el] = (255,0,0)
          new_pix[x,el] = (255,255,255)
    im.show()
    new.show()
    return list(out.keys())
def make_histogram(im,lines):#returns 2d-array which is histogram of each line, also show convenient picture
    out = []
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
            for j in range(count):
                new_pix[x,lines[i+1]-j] = (255,0,0)
        out.append(list)
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

im = Image.open("sample2.jpeg")
width,height = im.size
rotated = convert_to_bw(im,10).rotate(-1,fillcolor = 'white')#rotated manually for now
lines = find_lines(rotated,int(height/100),int(height/100))#y values of lines
hist = make_histogram(rotated,lines)#list of histograms of each line
for i in range(4):
    out = segment_line(hist[i])
    line_image = rotated.crop((0,lines[i],width,lines[i+1]))
    line_pix = line_image.load()
    for o in out:
        for h in range(line_image.size[1]):
            line_pix[o,h] = (255,0,0)
    line_image.show()
