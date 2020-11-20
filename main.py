from PIL import Image

im = Image.open("sample.jpg")
width,height = im.size #width = im.size[0], height = im.size[1]
copy = im.copy()
pix = copy.load() #pix 2d-array of rgb (rep as tuple ex [r,g,b])
avg = 0 #average pixel value of the full image
threshold = 0.8 #amount that avg is scaled by to determine what is excluded

for i in range(width):
    for j in range(height):
        avg += sum(pix[i,j])
avg = avg/(3*width*height)

print(avg)
for i in range(width):
    for j in range(height):
        if sum(pix[i,j])/3 < avg*threshold:#if below threshold, replace w black
            pix[i,j] = (0,0,0)
        else:
            pix[i,j] = (255,255,255)
rotated = copy.rotate(-5)
copy.show()
rotated.show()
