from PIL import Image
from PIL import ImageFilter
import random as r
import math as m
import time
import tkinter as tk
from tkinter import Label
from tkinter import filedialog
import tkinter.scrolledtext as tkst
import tkinter.font as tkFont
import os
import clipboard

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
    for i in range(-20,21):
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
def copy(text,copy_b): #called when copy button is pressed
    clipboard.copy(text)
    copy_b.config(text='Copied!')
def save(text,save_b): #called when save as txt button is pressed
    f = filedialog.asksaveasfilename(title = 'Select save location',filetypes=(("Text Files", "*.txt"),("All Files", "*.*")),defaultextension = '.*')
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    f = open(f,'w')
    f.write(text)
    f.close()
    save_b.config(text='Saved!')
def upload(): #called when upload button is pressed
    filename = filedialog.askopenfilename(initialdir = "/",title = "Select a File",filetypes =[("All image types", ".png .jpg .jpeg")])
    file_l.configure(text="File Opened: "+filename)
    file_l.configure(font = font12)
def convert(): #called when convert button is pressed
    path = file_l.cget('text')[13:]
    print('convert',path)
    start = time.time()
    im = Image.open(path)
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

    output = """He stopped the car and went out with her to the edge of the field to look at the magpies, which foraged on the ground until they got quite close, at which point they flew off to some trees in the distance. Then they went down a riverbed that was practically dried up, with only a thin stream of water flowing down the center. But it was a northern river all the same, and so they picked up small chilly smooth stones from the riverbed and pitched them in, watching the cloudy yellow water gush out of the holes they broke in the thin ice. They passed a small town and spent a while at the market there. She knelt down by a goldfish vendor, the fish in their glass bowls like liquid flames under the sun, and wouldn’t leave. He bought her two and put them, water and all, in plastic bags on the backseat of the car. They entered a hamlet, but found nothing that felt like the countryside. The houses and compounds were brand new, cars were parked outside of many of the gates, the cement roads were wide, and people were dressed no differently than in the cities—a few girls were even stylish. Even the dogs were the same long-haired, short-legged parasites found in the cities. More interesting was the large stage at the entrance to the village—they marveled at how such a small village could have such an immense stage. It was empty, so with some effort he climbed up and—looking down at his lone audience member—sang a verse from “Tonkaya Ryabina” about the slender hawthorn tree. At noon, they ate in another town, where the food was more or less the same as in the city, only the portions were about twice as large. After lunch, they sat drowsily in the warmth of the sun on a bench outside the town hall, and then drove onward with no direction in mind.
    """
    output_text = '----'
    output_l = tkst.ScrolledText(master = text_frame, wrap = tk.WORD, width = 40, height = 8)
    output_l.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    output_l.insert(tk.INSERT,output)
    output_l.config(state='disabled')
    output_l.place(relx = 0.5, rely = 0.8, anchor = 'center')

    copy_b = tk.Button(window,text = 'Copy text',font = font12, width = 13, command = lambda:copy(output,copy_b))
    copy_b.place(relx = 0.35, rely = 0.95, anchor = 'center')

    save_b = tk.Button(window,text = 'Save as .txt',font = font12, width = 13, command = lambda:save(output,save_b))
    save_b.place(relx = 0.65, rely = 0.95, anchor = 'center')

window = tk.Tk()
text_frame = tk.Frame(master = window)
text_frame.pack(fill='both', expand='yes')
window.geometry("500x600")
window.winfo_toplevel().title("OCR")

font30 = tkFont.Font(family="Lucida Grande", size=30)
font20 = tkFont.Font(family="Lucida Grande", size=20)
font15 = tkFont.Font(family="Lucida Grande", size=15)
font12 = tkFont.Font(family="Lucida Grande", size=12)

title_l = Label(window,text = 'Optical Character \nRecognition',font = font30)
title_l.place(relx = 0.5, rely = 0.1, anchor = 'center')

instructions_l = Label(window,text='Choose an image file to convert to text.',font = font15)
instructions_l.place(relx = 0.5,rely = 0.25,anchor = 'center')

file_text = 'No file chosen'
file_l = Label(window,text='No file chosen',font = font15)
file_l.place(relx = 0.5, rely = 0.51, anchor = 'center')

upload_b = tk.Button(window,text = 'Open File',font = font20, width = 13, command = upload)
upload_b.place(relx = 0.5, rely = 0.4, anchor = 'center')

convert_b = tk.Button(window,text = 'Convert',font = font20, width = 10, command = convert)
convert_b.place(relx = 0.5, rely = 0.6, anchor = 'center')
window.mainloop()
