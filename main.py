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

def find_angle(pix,samples):#given black and white pixels and list of samples, returns angle to rotate by
    #to go r distance in the direction theta add r*cos(theta) to x val, and r*sin(theta) to y val
    #(100,100). (100+r*cos(30),100+r*sin(30))
    r = [1,2,3,4,5,6,7,8,9,10]
    angle = 0
    for i in r:
        pass
    for sample in samples:
        pass
    return -5#angle/len(samples)

black = []
im = Image.open("sample2.jpg")
copy,pix = convert_to_bw(im)

samples = r.sample(black,50) #Random Sample of black pixels

rotated = copy.rotate(-1)#find_angle(pix,samples))
#rotated.show()
width,height = rotated.size
pix = rotated.load()
threshold = 0.02
for y in range(height):
    black = 0
    for x in range(width):
        if pix[x,y] == (0,0,0):
            black += 1
    print('a',black/width)
    if black/width < threshold:
        for x in range(width):
            pix[x,y] = (255,0,255)
rotated.show()
