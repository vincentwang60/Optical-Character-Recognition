from PIL import Image
import random as r
import math as m

def convert_to_bw(im):#returns image and list of pixels
    width,height = im.size #width = im.size[0], height = im.size[1]
    copy = im.copy()
    pix = copy.load() #pix 2d-array of rgb (rep as tuple ex [r,g,b])
    avg = 0 #average pixel value of the full image
    threshold = 0.8 #amount that avg is scaled by to determine what is excluded
    sample_size = 50
    for i in range(width):
        for j in range(height):
            avg += sum(pix[i,j])
    avg = avg/(3*width*height)

    print(avg)
    for i in range(width):
        for j in range(height):
            if sum(pix[i,j])/3 < avg*threshold:#if below threshold, replace w black
                pix[i,j] = (0,0,0)
                black.append([i,j])
            else:
                pix[i,j] = (255,255,255)
    return [copy,pix]

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

def find_lines(im):
    out = []
    width,height = im.size
    pix = im.load()
    threshold = 0.02
    check = True
    black_found = False
    skip = int(height/50)
    increment = 0
    for y in range(height):
        black = 0
        if not check:
            if increment < skip:
                increment += 1
            else:
                check = True
                increment = 0
        for x in range(width):
            if pix[x,y] == (0,0,0):
                black += 1
        if black/width > threshold:
            black_found = True
        elif check and black_found:
            for x in range(width):
                pix[x,y] = (255,0,255)
            out.append(y)
            check = False
            black_found = False
    im.show()
    return out

def make_histogram(im,lines):
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

black = []
im = Image.open("sample2.jpeg")
copy,pix = convert_to_bw(im)
samples = r.sample(black,50) #Random Sample of black pixels
rotated = copy.rotate(-1)#find_angle(pix,samples))
lines = find_lines(rotated)
hist = make_histogram(rotated,lines)
print(lines)
