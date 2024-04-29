import os
from PIL import Image
from pillow_heif import register_heif_opener
from os.path import join

register_heif_opener()

path = r''

# Transforms a HEIC image (goddamnit iphone) to a jpg file
for file in os.listdir(path):
    filename, ext = file.split(".")[0], file.split(".")[-1]
    if ext != "HEIC":
        continue 
    image = Image.open(join(path, file))

    image.save(join("plop", filename + ".jpg"))