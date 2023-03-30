from tensorflow.keras.models import load_model
import numpy as np
import os
import cv2
import tensorflow as tf

path = r"C:\Users\Admin\Desktop\WhatsApp Images"

# import the model from file
model = load_model(os.path.join('models', 'MemoryGarbageModel.h5'))

for file in os.listdir(path):
    img_path = os.path.join(path, file)
    if os.path.isdir(img_path):
        continue

    img = cv2.imread(img_path)
    resize = tf.image.resize(img, (256,256))
    yhat = model.predict(np.expand_dims(resize/255, 0))

    if yhat > 0.5:
        print("This image is a memory")
        os.rename(img_path, os.path.join(os.getcwd(), "memories", file))
    else:
        print("This image is garbage")
        os.rename(img_path, os.path.join(os.getcwd(), "garbage", file))

# import os
# import random

# rand = 523
# while rand != 0:    
#     files = os.listdir("poop")
#     choose = files[random.randint(0, len(files) - 1)]
#     os.rename(os.path.join("poop", choose), os.path.join("garbage", choose))
#     rand -= 1
