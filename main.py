from PIL import Image

im = Image.open("sample.jpg")
pix = im.load()
width,height = im.size
print(width,height)
print(pix[1,1])
print('amari can you see this')
