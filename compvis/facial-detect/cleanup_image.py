import gc
import os
import mtcnn
import cv2
import imghdr
import tensorflow.keras.backend as K
from os.path import join as path_join
from uuid import uuid1

RAW_PATH = path_join(os.getcwd(), "rawphotos") 
DATA_PATH = path_join(os.getcwd(), "training") 
INPUT_SIZE = (200, 200)

# We do this to not memory leak
def clear_oom():
    print("Clearing the Cache and running Garbage Collection")
    gc.collect()
    K.clear_session()

def assert_path(path) -> bool:
    is_path = os.path.isdir(path)
    if not is_path:
        os.mkdir(path)
    return is_path

print(RAW_PATH)

# Remove Smelly images
whitelist = ("jpg", "jpeg", "png")
trash_path = path_join(os.getcwd(), "img_trash")
assert_path(trash_path)
for root, paths, files in os.walk(RAW_PATH):
    for name in files:
        filepath = os.path.join(root, name)
        img_type = imghdr.what(filepath)
        if img_type is None or img_type not in whitelist:
            print(f"{filepath} is a smelly image")
            os.rename(filepath, path_join(trash_path, name))

assert_path(path_join(RAW_PATH))
cycles = 0
# Crop all the images to fit just the faces
for _class in os.listdir(RAW_PATH):
    print(f"Class => {_class}")
    # MTCNN face detector
    detector = mtcnn.MTCNN()
    assert_path(path_join(RAW_PATH, _class))
    clear_oom()
    cycles = 0
    for img in os.listdir(path_join(RAW_PATH, _class)):
        print(_class, "=>", img)
        if cycles >= 100:
            clear_oom()
            cycles = 0
        # Load image and detect faces
        pic = cv2.cvtColor(cv2.imread(path_join(RAW_PATH, _class, img)), cv2.COLOR_BGR2RGB)
        roi = detector.detect_faces(pic)
        
        # If there are no faces or more than one, discard the image
        if not roi or len(roi) > 1:
            os.rename(path_join(RAW_PATH, _class, img), path_join(trash_path, img))
            continue

        # Create a new picture cropping only the face
        x1, y1, width, height = roi[0]["box"]
        x2, y2 = x1 + width, y1 + height
        # Resize to input into our model
        resized = cv2.resize(pic[y1:y2, x1:x2], INPUT_SIZE, interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(path_join(DATA_PATH, _class, f"{uuid1()}.{img.split('.')[-1]}"), cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
        cycles += 1

clear_oom()
