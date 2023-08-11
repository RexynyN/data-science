# %%
import tensorflow as tf
import os

tf.__version__ 

# %%
# Avoid OOM errors by setting GPU memory consumption growth
gpus = tf.config.experimental.list_physical_devices("GPU")

for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


# %%
# Remove dodgy images
import cv2
import imghdr
import matplotlib.pyplot as plt
from os.path import join

data_dir = join("data", "img_data")

# %%
# Image extensions
image_exts = ['jpeg','jpg', 'bmp', 'png', 'gif']

# # Exclude bad images
# for image_class in os.listdir(data_dir): 
#     for image in os.listdir(os.path.join(data_dir, image_class)):
#         image_path = os.path.join(data_dir, image_class, image)
#         try: 
#             img = cv2.imread(image_path)
#             tip = imghdr.what(image_path)
#             if tip not in image_exts: 
#                 print('Image not in ext list {}'.format(image_path))
#                 os.remove(image_path)
#         except Exception as e: 
#             print('Issue with image {}'.format(image_path))
#             # os.remove(image_path)

# %%
import numpy as np 
import matplotlib.pyplot as plt

data = tf.keras.utils.image_dataset_from_directory(data_dir)

# %%
# Creat an iterator
data_iterator = data.as_numpy_iterator()

# Get another batch from the iterator
batch = data_iterator.next()

# Plot the images
fig, ax = plt.subplots(ncols=4, figsize=(20,20))
for idx, img in enumerate(batch[0][:4]):
    ax[idx].imshow(img.astype(int))
    ax[idx].title.set_text(batch[1][idx])



# %% [markdown]
# ## Preprocess Data :D 
# 

# %%
# Normalize the pixels values
data = data.map(lambda x, y: (x / 255, y))

# Get the iterator 
scaled_iterator = data.as_numpy_iterator()

# Get a batch
batch = scaled_iterator.next()

# %%
# Plot it
fig, ax = plt.subplots(ncols=4, figsize=(20,20))
for idx, img in enumerate(batch[0][:4]):
    ax[idx].imshow(img)
    ax[idx].title.set_text(batch[1][idx])

# %%
# Split the data
train_size = int(len(data)*.7)
val_size = int(len(data)*.2) + 1
test_size = int(len(data)*.1) + 1

# Get the data
train = data.take(train_size)
val = data.skip(train_size).take(val_size)
test = data.skip(train_size + val_size).take(test_size)


# %% [markdown]
# ## Deep Model
# 

# %%
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout

# %%
# Create the model :)

model = Sequential()

model.add(Conv2D(16, (3,3), 1, activation='relu', input_shape=(256,256,3)))
model.add(MaxPooling2D())

model.add(Conv2D(32, (3,3), 1, activation='relu'))
model.add(MaxPooling2D())

model.add(Conv2D(16, (3,3), 1, activation='relu'))
model.add(MaxPooling2D())

model.add(Flatten())

model.add(Dense(256, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# %%
model.compile("adam", loss=tf.losses.BinaryCrossentropy(), metrics=['accuracy'])


# %%
model.summary()

# %%
log_dir = "logs"

tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)

hist = model.fit(train, epochs=10, validation_data=val, callbacks=[tensorboard_callback])


# Save it :)
model.save(os.path.join('models', 'MemoryGarbageModel-v1.1.h5'))


# %%
fig = plt.figure()

plt.plot(hist.history['loss'], color='teal', label='loss')
plt.plot(hist.history['val_loss'], color='orange', label='val_loss')
fig.suptitle('Loss', fontsize=20)
plt.legend(loc="upper left")
plt.show()

# %%
fig = plt.figure()

plt.plot(hist.history['accuracy'], color='teal', label='accuracy')
plt.plot(hist.history['val_accuracy'], color='orange', label='val_accuracy')
fig.suptitle('Accuracy', fontsize=20)
plt.legend(loc="upper left")
plt.show()

# %% [markdown]
# ## Evaluate Performance

# %%
from tensorflow.keras.metrics import Precision, Recall, BinaryAccuracy

# %%
# Instantiate the metrics
pre = Precision()
re = Recall()
acc = BinaryAccuracy()

# %%
# Use the test data
for batch in test.as_numpy_iterator():
    X, y = batch
    yhat = model.predict(X)
    pre.update_state(y, yhat)
    re.update_state(y, yhat)
    acc.update_state(y, yhat)

print(f"Precision: {pre.result().numpy()}, Recall: {re.result().numpy()}, Accuracy: {acc.result().numpy()}")


# %%
# Test the model
import cv2

img = cv2.imread(r"/home/breno/codes/data-science/img_data/garbage/IMG-20180512-WA0026.jpg")
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.show()

# %%
resize = tf.image.resize(img, (256,256))
plt.imshow(resize.numpy().astype(int))

# %%
yhat = model.predict(np.expand_dims(resize/255, 0))
yhat

# %%


if yhat > 0.5:
    print("This image is a memory")
else:
    print("This image is garbage")

# %% [markdown]
# ## Save this model
# 

# %%
from tensorflow.keras.models import load_model

# %%
# Load model :)
new_model = load_model(os.path.join('models', 'MemoryGarbageModel-v1.1.h5'))

yhat = new_model.predict(np.expand_dims(resize/255, 0))

if yhat > 0.5:
    print("This image is a memory")
else:
    print("This image is garbage")


