# Notebook created by Breno Nogueira <RexynyN>

import os
import imghdr
import gc
import mtcnn
import cv2
import matplotlib.pyplot as plt 
from os.path import join as path_join 

# Prevent GPU memory blow-ups 
# (Must run it before importing any tensorflow package)
os.environ['TF_GPU_ALLOCATOR'] = 'cuda_malloc_async'

import tensorflow as tf

# Disable the logs
tf.keras.utils.disable_interactive_logging()


# Must have only folders of images (one per class)
IMG_PATH = path_join("/mnt/c/Users/Admin/Desktop/fotos/") # BACKUP THESE IMAGES, THEY CAN BE DAMAGED
N_CLASSES = len(os.listdir(IMG_PATH))

# Where preprocessed images will be stored
DATA_PATH = path_join("/mnt/c/Users/Admin/Desktop/result/")

# Where invalid or smelly images are sent
TRASH_PATH = path_join("/mnt/c/Users/Admin/Desktop/result/trash/")

# Image's input size (width, height)
# > Tweaking down this value uses less memory (especially if using GPU)
INPUT_SIZE = (224, 224)


# Asserts that the given path exists
def assert_path(path) -> bool:
    is_path = os.path.isdir(path)
    if not is_path:
        os.mkdir(path)
    return is_path

# Remove smelly images
def remove_smelly_images():
    assert_path(TRASH_PATH)
    # All extensions accepted by tensorflow
    whitelist = ("jpg", "jpeg", "png", "bmp", "gif")
    for root, _, files in os.walk(IMG_PATH):
        for name in files:
            filepath = os.path.join(root, name)
            # Guesses what type of image it is
            img_type = imghdr.what(filepath)
            if img_type is None or img_type not in whitelist:
                print(f"{filepath} is a smelly image")
                # Moves to the "trash" directory
                os.rename(filepath, path_join(TRASH_PATH, name))

remove_smelly_images()

# We do this to not memory leak
def clear_oom():
    print("Clearing the Cache and running Garbage Collection")
    gc.collect()
    tf.keras.backend.clear_session()

# Crop all the images to fit just the faces
def classify_dataset():
    # Grants that the trash path exists
    assert_path(TRASH_PATH)
    assert_path(DATA_PATH)

    # Garbage Collection Countdown (no C compiler here for now xD)
    gcc = 0
    for _class in os.listdir(IMG_PATH):
        assert_path(path_join(DATA_PATH, _class))
        print(f"Class => {_class}")
        # MTCNN face detector (we reinstantiate it before every reading loop to avoid OOM errors)
        detector = mtcnn.MTCNN()
        clear_oom()
        for img in os.listdir(path_join(IMG_PATH, _class)):
            print(img)
            # Garbage collect and reinstantiate
            if gcc == 300:
                clear_oom()
                detector = mtcnn.MTCNN()
                gcc = 0

            # Load image and detect faces
            pic = cv2.cvtColor(cv2.imread(path_join(IMG_PATH, _class, img)), cv2.COLOR_BGR2RGB)
            roi = detector.detect_faces(pic)
            
            # TODO: Once the model is bootstrapped, we could detect who each person is when len > 1, thus
            # creating an even larger dataset;
            # If there are no faces or more than one, discard the image
            if not roi:
                os.rename(path_join(IMG_PATH, _class, img), path_join(TRASH_PATH, img))
                continue

            for idx, face in enumerate(roi):
                # Create a new picture cropping only the face
                x1, y1, width, height = face["box"]
                x2, y2 = x1 + width, y1 + height
                # Resize to input into our model
                resized = cv2.resize(pic[y1:y2, x1:x2], INPUT_SIZE, interpolation=cv2.INTER_LANCZOS4)

                # Save the image
                name_tokens = img.split(".")
                img_name = name_tokens[0] + f"-{idx + 1}." + name_tokens[-1]
                cv2.imwrite(path_join(DATA_PATH, _class, img_name), cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
                gcc += 1
    
    clear_oom()

classify_dataset()