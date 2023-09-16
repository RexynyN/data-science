import numpy as np
import os
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from tkinter.filedialog import askdirectory
from os.path import join

path = askdirectory(mustexist=True)

# import the model from file
model = load_model(os.path.join('models', 'MemoryGarbageModel-v1.1.h5'))

if not os.path.isdir(join(path, "memories")):
    os.mkdir(join(path, "memories"))
    os.mkdir(join(path, "garbage"))

for file in os.listdir(path):
    img_path = os.path.join(path, file)
    if os.path.isdir(img_path):
        continue

    try:
        img = cv2.imread(img_path)
        resize = tf.image.resize(img, (256,256))
        yhat = model.predict(np.expand_dims(resize/255, 0))
    except:
        continue
    
    if yhat > 0.8:
        print("This image is a memory")
        os.rename(img_path, join(path, "memories", file))
    else:
        print("This image is garbage")
        os.rename(img_path, join(path, "garbage", file))
